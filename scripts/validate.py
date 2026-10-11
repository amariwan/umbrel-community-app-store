#!/usr/bin/env python3
"""tasiomind store validator.

Enforces official Umbrel app conventions plus store-specific safety rules:
  - store id/name, app id prefix, required manifest fields
  - unique, non-reserved UI ports
  - pinned images (no `latest`, digest required), manifest version matches image tag
  - no host ports / host networking / privileged containers
  - no hardcoded secrets; generated secrets must come from exports.sh (derive_entropy)
  - app_proxy wiring (APP_HOST points at a real compose service)
  - volumes stay inside ${APP_DATA_DIR}

Exit 0 when everything passes, 1 otherwise. CI runs this on every push/PR.
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STORE_ID = "tasiomind"
STORE_NAME = "tasiomind"

VALID_CATEGORIES = {
    "ai", "automation", "bitcoin", "crypto", "developer",
    "files", "finance", "media", "networking", "social",
}
REQUIRED_MANIFEST_FIELDS = [
    "manifestVersion", "id", "category", "name", "version", "tagline",
    "description", "developer", "website", "dependencies", "repo",
    "support", "port", "gallery", "path", "submitter", "submission",
]
RESERVED_PORTS = {80, 443, 2000}
ALLOWED_TOP_LEVEL_DIRS = {".git", ".github", "docs", "scripts"}
ALLOWED_TOP_LEVEL_FILES = {
    "umbrel-app-store.yml", "README.md", "UPSTREAM.md", "LICENSE",
    "renovate.json", ".gitignore", "package.json", "package-lock.json",
}
# cap_add allowlist: AnythingLLM's collector needs Chromium's sandbox (same as
# the official Umbrel packaging). Everything else must justify additions here.
ALLOWED_CAP_ADD = {"SYS_ADMIN"}

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL: {msg}")


def check_store_file() -> list[str]:
    store_file = ROOT / "umbrel-app-store.yml"
    if not store_file.exists():
        fail("umbrel-app-store.yml is missing")
        return []
    try:
        data = yaml.safe_load(store_file.read_text())
    except yaml.YAMLError as exc:
        fail(f"umbrel-app-store.yml is not valid YAML: {exc}")
        return []
    if not isinstance(data, dict):
        fail("umbrel-app-store.yml must be a mapping")
        return []
    if data.get("id") != STORE_ID:
        fail(f"store id must be {STORE_ID!r}, got {data.get('id')!r}")
    if data.get("name") != STORE_NAME:
        fail(f"store name must be {STORE_NAME!r}, got {data.get('name')!r}")
    if not re.fullmatch(r"[a-z][a-z-]*", str(data.get("id", ""))):
        fail("store id must contain only a-z and dashes")
    return [STORE_ID]


def discover_apps() -> list[str]:
    apps = sorted(
        p.name
        for p in ROOT.iterdir()
        if p.is_dir()
        and p.name not in ALLOWED_TOP_LEVEL_DIRS
        and not p.name.startswith(".")
    )
    # Top-level hygiene: only app dirs + allowlisted infra may exist.
    for p in ROOT.iterdir():
        if p.is_dir() and not p.name.startswith(".") and p.name not in ALLOWED_TOP_LEVEL_DIRS:
            if not (p / "umbrel-app.yml").exists():
                fail(f"top-level directory {p.name}/ is not an app package (missing umbrel-app.yml)")
        if p.is_file() and p.name not in ALLOWED_TOP_LEVEL_FILES and not p.name.startswith("."):
            fail(f"unexpected top-level file {p.name}")
    return apps


def load_manifest(app: str):
    path = ROOT / app / "umbrel-app.yml"
    if not path.exists():
        fail(f"{app}: umbrel-app.yml is missing")
        return None
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        fail(f"{app}: umbrel-app.yml is not valid YAML: {exc}")
        return None
    if not isinstance(data, dict):
        fail(f"{app}: umbrel-app.yml must be a mapping")
        return None
    return data


def load_compose(app: str):
    path = ROOT / app / "docker-compose.yml"
    if not path.exists():
        fail(f"{app}: docker-compose.yml is missing")
        return None
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        fail(f"{app}: docker-compose.yml is not valid YAML: {exc}")
        return None
    if not isinstance(data, dict) or "services" not in data:
        fail(f"{app}: docker-compose.yml must define services")
        return None
    return data


def check_manifest(app: str, m: dict) -> None:
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in m:
            fail(f"{app}: manifest is missing required field {field!r}")
    if m.get("id") != app:
        fail(f"{app}: manifest id {m.get('id')!r} must equal directory name")
    if not str(app).startswith(f"{STORE_ID}-"):
        fail(f"{app}: app id must start with {STORE_ID}-")
    if m.get("category") not in VALID_CATEGORIES:
        fail(f"{app}: unknown category {m.get('category')!r}")
    port = m.get("port")
    if not isinstance(port, int) or not 1024 <= port <= 65535:
        fail(f"{app}: port must be an int in 1024-65535, got {port!r}")
    if port in RESERVED_PORTS:
        fail(f"{app}: port {port} is reserved by umbrelOS")
    gallery = m.get("gallery")
    if not isinstance(gallery, list) or not gallery or not all(isinstance(g, str) and g for g in gallery):
        fail(f"{app}: gallery must be a non-empty list of image URLs/paths")
    version = str(m.get("version", ""))
    if not re.fullmatch(r"\d+\.\d+(\.\d+)?", version):
        fail(f"{app}: version {version!r} must be a pinned numeric release (no latest/range)")


def check_compose(app: str, c: dict, manifest_version: str) -> None:
    services = c.get("services", {})
    if "app_proxy" not in services:
        fail(f"{app}: compose must define the app_proxy service")
        return
    proxy_env = services["app_proxy"].get("environment", {})
    app_host = proxy_env.get("APP_HOST")
    app_port = proxy_env.get("APP_PORT")
    if not app_host or not app_port:
        fail(f"{app}: app_proxy must set APP_HOST and APP_PORT")
    else:
        target = str(app_host).rsplit("_1", 1)[0]
        service_name = target[len(app) + 1:] if target.startswith(app + "_") else None
        if service_name not in services:
            fail(f"{app}: APP_HOST {app_host!r} does not reference a compose service of this app")

    for svc_name, svc in services.items():
        if svc_name == "app_proxy":
            continue
        image = str(svc.get("image", ""))
        if not image:
            fail(f"{app}/{svc_name}: service has no image")
            continue
        if ":latest" in image or image.endswith(":latest"):
            fail(f"{app}/{svc_name}: unpinned 'latest' tag is forbidden: {image}")
        if "@sha256:" not in image:
            fail(f"{app}/{svc_name}: image must be digest-pinned (image:tag@sha256:...): {image}")
        else:
            tag = image.split("@")[0].rsplit(":", 1)[-1] if ":" in image.split("@")[0] else ""
            if tag and not tag.startswith(manifest_version):
                fail(
                    f"{app}/{svc_name}: image tag {tag!r} does not match "
                    f"manifest version {manifest_version!r}"
                )
        if svc.get("privileged") is True:
            fail(f"{app}/{svc_name}: privileged containers are forbidden")
        if svc.get("network_mode") == "host":
            fail(f"{app}/{svc_name}: host networking is forbidden")
        if "ports" in svc:
            fail(f"{app}/{svc_name}: host port publishing ('ports:') is forbidden; use app_proxy")
        for cap in svc.get("cap_add", []) or []:
            if cap not in ALLOWED_CAP_ADD:
                fail(f"{app}/{svc_name}: cap_add {cap!r} is not allowlisted")
        for vol in svc.get("volumes", []) or []:
            vol_str = vol if isinstance(vol, str) else str(vol.get("source", ""))
            host_part = vol_str.split(":")[0]
            if host_part and not host_part.startswith("${APP_DATA_DIR}"):
                if host_part.startswith(("/", ".", "~")) or ".." in host_part:
                    fail(f"{app}/{svc_name}: volume {vol_str!r} must stay inside ${{APP_DATA_DIR}}")


SECRET_LITERAL = re.compile(
    r"(?i)\b(password|passwd|secret|api[_-]?key|auth[_-]?token)\b\s*[:=]\s*"
    r"(?!(['\"]?\$\{))(['\"]?)(?![\"']?\s*$)([^\s\"']+)"
)


def check_secrets(app: str, c: dict) -> None:
    for svc_name, svc in c.get("services", {}).items():
        if svc_name == "app_proxy":
            continue
        for item in (svc.get("environment", []) or []) if isinstance(svc.get("environment", []), list) else []:
            line = item if isinstance(item, str) else ""
            if "${" in line:
                continue  # references a generated/provided variable, not a literal
            if SECRET_LITERAL.search(line):
                fail(f"{app}/{svc_name}: hardcoded secret in environment: {line!r}")
        env_map = svc.get("environment", {})
        if isinstance(env_map, dict):
            for key, value in env_map.items():
                if isinstance(value, str) and "${" not in value and SECRET_LITERAL.search(f"{key}={value}"):
                    fail(f"{app}/{svc_name}: hardcoded secret in environment: {key!r}")


def check_exports(app: str, c: dict) -> None:
    needed: set[str] = set()
    for svc_name, svc in c.get("services", {}).items():
        if svc_name == "app_proxy":
            continue
        env = svc.get("environment", [])
        items = env if isinstance(env, list) else [f"{k}={v}" for k, v in env.items()]
        for item in items:
            if not isinstance(item, str):
                continue
            for var in re.findall(r"\$\{(APP_[A-Za-z0-9_]+)\}", item):
                if var not in {"APP_DATA_DIR"}:
                    needed.add(var)
    exports = ROOT / app / "exports.sh"
    defined: set[str] = set()
    if needed:
        if not exports.exists():
            fail(f"{app}: compose references {sorted(needed)} but exports.sh is missing")
            return
        content = exports.read_text()
        defined = set(re.findall(r"export\s+(APP_[A-Za-z0-9_]+)=", content))
        for var in needed:
            if var not in defined:
                fail(f"{app}: ${{{var}}} used in compose but not defined in exports.sh")
        for var in defined:
            if re.search(r"(PASSWORD|SECRET|KEY|SALT)", var):
                block = "\n".join(l for l in content.splitlines() if var in l)
                if "derive_entropy" not in block:
                    fail(f"{app}: secret {var} must be generated with derive_entropy, not hardcoded")


def main() -> int:
    check_store_file()
    apps = discover_apps()
    if not apps:
        fail("store contains no apps")
    seen_ports: dict[int, str] = {}
    for app in apps:
        manifest = load_manifest(app)
        compose = load_compose(app)
        if manifest is None or compose is None:
            continue
        check_manifest(app, manifest)
        check_compose(app, compose, str(manifest.get("version", "")))
        check_secrets(app, compose)
        check_exports(app, compose)
        port = manifest.get("port")
        if isinstance(port, int):
            if port in seen_ports:
                fail(f"{app}: port {port} already used by {seen_ports[port]}")
            else:
                seen_ports[port] = app
    print(f"\nValidated {len(apps)} app(s): {', '.join(apps) if apps else 'none'}")
    if errors:
        print(f"{len(errors)} problem(s) found.")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

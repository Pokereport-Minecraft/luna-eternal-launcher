"""Package private staff entry separately from the normal Unix launcher."""
import hashlib, pathlib, re, sys, zipfile
source = (pathlib.Path(__file__).resolve().parents[1] / "CMakeLists.txt").read_text()
version = ".".join(re.search(r"set\(Launcher_VERSION_" + part + r"\s+(\d+)\)", source).group(1)
                   for part in ("MAJOR", "MINOR", "PATCH"))
if sys.argv[1:] == ["--version"]:
    print(version)
    raise SystemExit(0)
platform = sys.argv[1]
assert platform in {"linux-x64", "macos-x64", "macos-arm64"}
dist = pathlib.Path("dist")
if platform == "linux-x64":
    body = '#!/bin/sh\nset -eu\nbase=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexport POKEREPORT_STAFF_TOOLS=1\nexec "$base/luna-launcher-linux-x64-VERSION.AppImage" "$@"\n'.replace("VERSION", version)
    filename = "PokeReport-Staff.sh"
else:
    body = '#!/bin/sh\nset -eu\nbase=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\napp="$base/LunaEternal.app"\nif [ ! -d "$app" ]; then app="/Applications/LunaEternal.app"; fi\nexport POKEREPORT_STAFF_TOOLS=1\nexec "$app/Contents/MacOS/lunaeternal" "$@"\n'
    filename = "PokeReport-Staff.command"
with zipfile.ZipFile(dist / f"PokeReport-Staff-{version}-{platform}.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    entry = zipfile.ZipInfo(filename)
    entry.create_system = 3
    entry.external_attr = 0o100755 << 16
    archive.writestr(entry, body)
    if platform == "linux-x64":
        binary = dist / f"luna-launcher-linux-x64-{version}.AppImage"
        info = zipfile.ZipInfo(binary.name)
        info.create_system = 3
        info.external_attr = 0o100755 << 16
        archive.writestr(info, binary.read_bytes())
    else:
        with zipfile.ZipFile(dist / f"PokeReport-Launcher-{version}-{platform}.zip") as normal:
            for info in normal.infolist():
                archive.writestr(info, normal.read(info))
    archive.writestr("LEEME.txt", "Acceso Staff privado. Extrae este acceso junto al launcher normal. En Mac también puede usar /Applications/LunaEternal.app. El rol de servidor se asigna por separado.\n")
lines = []
staff_lines = []
for path in sorted(dist.iterdir()):
    if path.is_file() and path.name != "SHA256SUMS":
        if path.name.startswith("SHA256SUMS"):
            continue
        line = hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name
        (staff_lines if path.name.startswith("PokeReport-Staff-") else lines).append(line)
(dist / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
(dist / "SHA256SUMS-STAFF").write_text("\n".join(staff_lines) + "\n", encoding="utf-8")

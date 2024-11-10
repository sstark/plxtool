from pathlib import Path
from subprocess import run, CalledProcessError


def overlay_mount(src: Path, target: Path) -> bool:
    if not src.exists():
        print(f"{src} does not exist")
        return False
    if not target.exists():
        print(f"Mountpoint {target} does not exist")
        return False
    originals = next(src.rglob("originals"), None)
    if originals is None:
        print('"originals" folder not found')
        return False
    archive = next(src.rglob("archive"), None)
    if archive is None:
        print('"archive" folder not found')
        return False
    if originals.parent != archive.parent:
        print(f"{archive} and {originals} are not in same directory")
        return False
    cmd = [
        "sudo",
        "mount",
        "-t",
        "overlay",
        "overlay",
        f"-olowerdir={originals}:{archive}",
        target,
    ]
    try:
        run(cmd, check=True)
        print(f"Mount successful. You can access your documents under {target}")
        return True
    except CalledProcessError as e:
        print(f"Mounting returned an error: {e}")
        return False

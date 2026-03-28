from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from shutil import which

SOURCE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SOURCE_ROOT.parent
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from tiktok_fps_bypasser import APP_NAME, COMPANY_NAME, EXECUTABLE_NAME, FILE_DESCRIPTION, __version__

PACKAGE_NAME = "tiktok_fps_bypasser"
ASSETS_DIR = SOURCE_ROOT / "assets"
ICON_PATH = ASSETS_DIR / "tiktok_fps_bypasser.ico"
BUILD_ROOT = SOURCE_ROOT / "build" / "protected"
STAGE_DIR = BUILD_ROOT / "stage"
OBFUSCATED_DIR = BUILD_ROOT / "obfuscated"
PYINSTALLER_WORK_DIR = BUILD_ROOT / "pyinstaller_work"
SPEC_DIR = BUILD_ROOT / "spec"
DIST_DIR = PROJECT_ROOT
VERSION_FILE = SOURCE_ROOT / "build_tools" / "version_info.txt"
ICON_GENERATOR = SOURCE_ROOT / "build_tools" / "generate_icon.py"
PYARMOR_HOME = SOURCE_ROOT / ".pyarmor"
PYARMOR_BUG_LOG = SOURCE_ROOT / "pyarmor.bug.log"


def run(command, cwd=SOURCE_ROOT):
    env = dict(**os.environ, PYARMOR_HOME=str(PYARMOR_HOME))
    subprocess.run(command, check=True, cwd=cwd, env=env)


def remove_path(path: Path):
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def ensure_build_environment():
    missing = [tool for tool in ("pyinstaller",) if which(tool) is None]
    if missing:
        raise RuntimeError(f"Missing required build tools: {', '.join(missing)}")

    if which("pyarmor") is None and importlib.util.find_spec("python_minifier") is None:
        raise RuntimeError("Install pyarmor or python-minifier to obfuscate the Python sources.")

    PYARMOR_HOME.mkdir(parents=True, exist_ok=True)

    if which("cl") is None:
        raise RuntimeError(
            "Microsoft Visual C++ 14.0 or newer is required to compile the Cython module. "
            "Install the Microsoft C++ Build Tools and run the build again."
        )


def ensure_icon():
    if not ICON_PATH.exists():
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        run([sys.executable, str(ICON_GENERATOR)])


def compile_cython():
    run([sys.executable, "setup.py", "build_ext", "--inplace"])
    compiled = sorted((SOURCE_ROOT / PACKAGE_NAME).glob("secure_core*.pyd"))
    if not compiled:
        raise RuntimeError("Compiled secure_core extension not found.")
    return compiled[0]


def prepare_stage(compiled_extension: Path):
    remove_path(STAGE_DIR)
    STAGE_DIR.mkdir(parents=True, exist_ok=True)

    stage_package = STAGE_DIR / PACKAGE_NAME
    shutil.copytree(
        SOURCE_ROOT / PACKAGE_NAME,
        stage_package,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "*.pyx", "*.c", "*.pyd"),
    )
    shutil.copy2(compiled_extension, stage_package / compiled_extension.name)
    shutil.copy2(SOURCE_ROOT / "tiktok_fps_bypasser_gui.py", STAGE_DIR / "tiktok_fps_bypasser_gui.py")
    shutil.copy2(PROJECT_ROOT / "patcher.py", STAGE_DIR / "patcher.py")


def obfuscate_sources(compiled_extension: Path):
    if which("pyarmor") is None:
        obfuscate_sources_with_minifier(compiled_extension)
        return

    try:
        obfuscate_sources_with_pyarmor(compiled_extension)
    except subprocess.CalledProcessError:
        if PYARMOR_BUG_LOG.exists():
            PYARMOR_BUG_LOG.unlink()
        obfuscate_sources_with_minifier(compiled_extension)


def obfuscate_sources_with_pyarmor(compiled_extension: Path):
    remove_path(OBFUSCATED_DIR)
    OBFUSCATED_DIR.mkdir(parents=True, exist_ok=True)

    run(
        [
            "pyarmor",
            "gen",
            "-r",
            "-i",
            "--mix-str",
            "--obf-code",
            "2",
            "-O",
            str(OBFUSCATED_DIR),
            str(STAGE_DIR / PACKAGE_NAME),
            str(STAGE_DIR / "tiktok_fps_bypasser_gui.py"),
            str(STAGE_DIR / "patcher.py"),
        ]
    )

    obfuscated_package = OBFUSCATED_DIR / PACKAGE_NAME
    shutil.copy2(compiled_extension, obfuscated_package / compiled_extension.name)
    fallback_file = obfuscated_package / "secure_fallback.py"
    if fallback_file.exists():
        fallback_file.unlink()


def obfuscate_sources_with_minifier(compiled_extension: Path):
    import python_minifier

    remove_path(OBFUSCATED_DIR)
    shutil.copytree(STAGE_DIR, OBFUSCATED_DIR)

    for file_path in OBFUSCATED_DIR.rglob("*.py"):
        if file_path.name == "secure_fallback.py":
            file_path.unlink()
            continue

        source = file_path.read_text(encoding="utf-8")
        minified = python_minifier.minify(
            source,
            filename=str(file_path),
            remove_literal_statements=False,
            combine_imports=True,
            hoist_literals=True,
            rename_locals=True,
            rename_globals=False,
            preserve_shebang=True,
        )
        file_path.write_text(minified, encoding="utf-8")

    obfuscated_package = OBFUSCATED_DIR / PACKAGE_NAME
    shutil.copy2(compiled_extension, obfuscated_package / compiled_extension.name)


def build_executable():
    remove_path(PYINSTALLER_WORK_DIR)
    remove_path(SPEC_DIR)
    remove_path(DIST_DIR / f"{EXECUTABLE_NAME}.exe")
    SPEC_DIR.mkdir(parents=True, exist_ok=True)

    run(
        [
            "pyinstaller",
            "--noconfirm",
            "--onefile",
            "--noconsole",
            "--clean",
            "--name",
            EXECUTABLE_NAME,
            "--icon",
            str(ICON_PATH),
            "--version-file",
            str(VERSION_FILE),
            "--distpath",
            str(DIST_DIR),
            "--workpath",
            str(PYINSTALLER_WORK_DIR),
            "--specpath",
            str(SPEC_DIR),
            "--paths",
            str(OBFUSCATED_DIR),
            "--hidden-import",
            "tkinterdnd2",
            "--hidden-import",
            f"{PACKAGE_NAME}.secure_core",
            "--collect-all",
            "customtkinter",
            "--collect-all",
            "tkinterdnd2",
            str(OBFUSCATED_DIR / "tiktok_fps_bypasser_gui.py"),
        ]
    )


def main():
    print(f"Building {APP_NAME} {__version__}")
    print(f"Company: {COMPANY_NAME}")
    print(f"Description: {FILE_DESCRIPTION}")

    ensure_build_environment()
    ensure_icon()
    compiled_extension = compile_cython()
    prepare_stage(compiled_extension)
    obfuscate_sources(compiled_extension)
    build_executable()

    print(f"Build completed: {DIST_DIR / f'{EXECUTABLE_NAME}.exe'}")


if __name__ == "__main__":
    main()

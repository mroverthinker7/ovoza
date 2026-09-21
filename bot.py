"""Ovoza one-command launcher.

Run with:
    python3 bot.py

BOT_TOKEN and initial ADMIN_IDS are configured in config.py.
The launcher only prepares the virtual environment/dependencies and then
starts app.py.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / "venv"
REQ = ROOT / "requirements.txt"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)


def ensure_venv_and_dependencies() -> Path:
    py = venv_python()

    if sys.prefix == str(VENV):
        return py

    if not py.exists():
        print("[1/3] Virtual environment yaratilmoqda...")
        run([sys.executable, "-m", "venv", str(VENV)])
        py = venv_python()

    print("[2/3] Kerakli Python paketlari tekshirilmoqda/o'rnatilmoqda...")

    pip_ok = subprocess.run(
        [str(py), "-m", "pip", "--version"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0

    if not pip_ok:
        print("pip virtual environment ichida topilmadi. pip avtomatik o'rnatilmoqda...")
        try:
            run([str(py), "-m", "ensurepip", "--upgrade"])
        except subprocess.CalledProcessError:
            print("Venv pip'siz yaratilgan. Virtual environment qayta yaratilmoqda...")
            shutil.rmtree(VENV, ignore_errors=True)
            run([sys.executable, "-m", "venv", str(VENV)])
            py = venv_python()
            run([str(py), "-m", "ensurepip", "--upgrade"])

    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", "-r", str(REQ)])
    return py


def main() -> None:
    if not REQ.exists():
        raise SystemExit("requirements.txt topilmadi.")

    py = ensure_venv_and_dependencies()

    # First run app.py inside the prepared venv.
    if sys.prefix != str(VENV):
        os.execv(str(py), [str(py), str(ROOT / "bot.py"), *sys.argv[1:]])

    print("[3/3] Ovoza bot ishga tushmoqda...\n")
    os.execv(sys.executable, [sys.executable, str(ROOT / "app.py"), *sys.argv[1:]])


if __name__ == "__main__":
    main()

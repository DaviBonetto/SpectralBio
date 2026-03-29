"""Build the SpectralBio paper when a LaTeX toolchain is available."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "paper"
TEX_PATH = PAPER_DIR / "spectralbio.tex"

WINDOWS_FALLBACKS = {
    "latexmk": [
        Path(r"C:\Users\Davib\AppData\Local\Programs\MiKTeX\miktex\bin\x64\latexmk.exe"),
        Path(r"C:\Program Files\MiKTeX\miktex\bin\x64\latexmk.exe"),
        Path(r"C:\Program Files (x86)\MiKTeX\miktex\bin\x64\latexmk.exe"),
    ],
    "pdflatex": [
        Path(r"C:\Users\Davib\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"),
        Path(r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"),
        Path(r"C:\Program Files (x86)\MiKTeX\miktex\bin\x64\pdflatex.exe"),
    ],
}


def path_looks_available(path: Path) -> bool:
    try:
        return path.exists()
    except PermissionError:
        # Some sandboxed Windows environments deny stat() outside the workspace
        # even when the executable is launchable by absolute path.
        return True


def resolve_executable(env_var: str, program: str) -> str | None:
    override = os.environ.get(env_var)
    if override:
        override_path = Path(override).expanduser()
        if path_looks_available(override_path):
            return str(override_path)
        resolved = shutil.which(override)
        if resolved:
            return resolved

    resolved = shutil.which(program)
    if resolved:
        return resolved

    if os.name == "nt":
        for candidate in WINDOWS_FALLBACKS.get(program, []):
            if path_looks_available(candidate):
                return str(candidate)

    return None


def run_command(command: list[str]) -> int:
    print(f"Running build command: {' '.join(command)}")
    try:
        completed = subprocess.run(command, cwd=PAPER_DIR, check=False)
    except OSError as exc:
        print(f"Command failed to launch: {exc}")
        return 1
    print(f"Command exit code: {completed.returncode}")
    return completed.returncode


def run_pdflatex(pdflatex: str) -> int:
    print(f"Resolved pdflatex executable: {pdflatex}")
    command = [pdflatex, "-interaction=nonstopmode", TEX_PATH.name]
    first_pass = run_command(command)
    if first_pass != 0:
        return first_pass
    print("Running second pdflatex pass for references.")
    return run_command(command)


def main() -> int:
    latexmk = resolve_executable("LATEXMK", "latexmk")
    pdflatex = resolve_executable("PDFLATEX", "pdflatex")

    if latexmk:
        print(f"Resolved latexmk executable: {latexmk}")
        command = [latexmk, "-pdf", "-interaction=nonstopmode", TEX_PATH.name]
        latexmk_result = run_command(command)
        if latexmk_result == 0:
            return 0
        if pdflatex:
            print("latexmk failed; attempting pdflatex fallback.")
            return run_pdflatex(pdflatex)
        return latexmk_result

    if pdflatex:
        return run_pdflatex(pdflatex)

    print("No LaTeX toolchain found. Set LATEXMK/PDFLATEX or install MiKTeX on PATH.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

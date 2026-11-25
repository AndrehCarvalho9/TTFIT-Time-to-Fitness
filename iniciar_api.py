from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
REQUIREMENTS = ROOT / "backend" / "requirements.txt"


def main() -> int:
    if not VENV_PYTHON.exists():
        print("Ambiente Python do TTFIT não encontrado. Criando...")
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(ROOT / ".venv")], cwd=ROOT, check=True
            )
        except subprocess.CalledProcessError:
            print("Não foi possível criar o ambiente virtual do TTFIT.")
            return 1

    dependencies = subprocess.run(
        [str(VENV_PYTHON), "-c", "import fastapi, uvicorn, mysql.connector, dotenv, itsdangerous"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if dependencies.returncode != 0:
        print("Instalando dependências da API...")
        try:
            subprocess.run(
                [str(VENV_PYTHON), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
                cwd=ROOT,
                check=True,
            )
        except subprocess.CalledProcessError:
            print("Falha ao instalar dependências. Confira sua conexão com a internet.")
            return 1

    print("Iniciando API em http://127.0.0.1:8000")
    print("A documentação fica em http://127.0.0.1:8000/docs")
    print("Mantenha esta janela aberta. Pressione Ctrl+C para encerrar.")
    try:
        return subprocess.call(
            [
                str(VENV_PYTHON),
                "-m",
                "uvicorn",
                "main:app",
                "--app-dir",
                "backend",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--reload",
            ],
            cwd=ROOT,
        )
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

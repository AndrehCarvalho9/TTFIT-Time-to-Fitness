from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
REQUIREMENTS = ROOT / "backend" / "requirements.txt"


def run_setup_command(command: list[str], description: str) -> None:
    print(f"\n{description}...", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    print("=" * 54)
    print(" TTFIT - Inicializador")
    print("=" * 54)

    if not (ROOT / "frontend" / "index.html").exists() or not (ROOT / "backend" / "main.py").exists():
        print("ERRO: nao encontrei frontend/index.html e backend/main.py.")
        print("Coloque este arquivo na pasta principal do projeto TTFIT.")
        input("Pressione Enter para sair...")
        return

    if not VENV_PYTHON.exists():
        try:
            run_setup_command([sys.executable, "-m", "venv", str(ROOT / ".venv")], "Criando ambiente virtual (primeira execucao)")
        except subprocess.CalledProcessError:
            print("Nao foi possivel criar o ambiente virtual usando este Python.")
            input("Pressione Enter para sair...")
            return

    python = str(VENV_PYTHON)

    # Instala as dependencias apenas quando FastAPI ou Uvicorn ainda nao estao instalados.
    check = subprocess.run(
        [python, "-c", "import fastapi, uvicorn"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if check.returncode != 0:
        try:
            run_setup_command([python, "-m", "pip", "install", "--upgrade", "pip"], "Preparando pip")
            run_setup_command([python, "-m", "pip", "install", "-r", str(REQUIREMENTS)], "Instalando dependencias do TTFIT")
        except subprocess.CalledProcessError:
            print("\nERRO ao instalar dependencias. Confira sua conexao e a instalacao do Python.")
            input("Pressione Enter para sair...")
            return

    children: list[subprocess.Popen] = []
    try:
        print("\nIniciando API (porta 8000)...", flush=True)
        backend = subprocess.Popen(
            [python, "-m", "uvicorn", "main:app", "--app-dir", "backend", "--reload", "--host", "127.0.0.1", "--port", "8000"],
            cwd=ROOT,
        )
        children.append(backend)
        time.sleep(1.5)
        if backend.poll() is not None:
            print("A API nao iniciou. A porta 8000 pode estar ocupada ou ocorreu um erro acima.")
            input("Pressione Enter para sair...")
            return

        print("Iniciando site (porta 5500)...", flush=True)
        frontend = subprocess.Popen(
            [python, "-m", "http.server", "5500", "--directory", "frontend", "--bind", "127.0.0.1"],
            cwd=ROOT,
        )
        children.append(frontend)
        time.sleep(1)
        if frontend.poll() is not None:
            print("O site nao iniciou. A porta 5500 pode estar ocupada ou ocorreu um erro acima.")
            input("Pressione Enter para sair...")
            return

        print("\nTTFIT iniciado!")
        print("Site: http://127.0.0.1:5500")
        print("API:  http://127.0.0.1:8000/docs")
        print("Mantenha esta janela aberta enquanto usar o aplicativo.")
        webbrowser.open("http://127.0.0.1:5500")

        while True:
            time.sleep(1)
            if any(process.poll() is not None for process in children):
                print("\nUm dos servidores foi encerrado. Veja a mensagem de erro acima.")
                break
    except KeyboardInterrupt:
        print("\nEncerrando os servidores do TTFIT...", flush=True)
    finally:
        for process in children:
            if process.poll() is None:
                process.terminate()
        for process in children:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("Servidores encerrados.")

    input("Pressione Enter para fechar esta janela...")


if __name__ == "__main__":
    main()

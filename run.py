#!/usr/bin/env python3
"""
Script para executar a aplicação facilmente
Uso: python run.py
"""
import subprocess
import sys
import os
import webbrowser
import threading
import time
import socket


def is_port_in_use(port):
    """Verifica se a porta está em uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except OSError:
            return True


def kill_port_process(port):
    """Tenta liberar a porta matando o processo"""
    try:
        import platform
        if platform.system() == 'Windows':
            os.system(f'netstat -ano | findstr :{port} && taskkill /PID <PID> /F')
            time.sleep(1)
    except:
        pass


def main():
    print("🚀 Iniciando aplicação JSON Accelerator...")
    print("=" * 50)
    
    # Garante que estamos no diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Verifica se porta está em uso
    if is_port_in_use(8000):
        print("⚠️  Porta 8000 está em uso. Tentando liberar...")
        kill_port_process(8000)
        time.sleep(2)
    
    # Função para abrir o navegador após um delay
    def open_browser():
        time.sleep(3)  # Aguarda 3 segundos para o servidor iniciar
        url = "http://127.0.0.1:8000"
        print(f"\n🌐 Abrindo navegador em {url}...")
        try:
            webbrowser.open_new_tab(url)
        except:
            print(f"💡 Acesse manualmente: {url}")
    
    try:
        # Executa o uvicorn
        print("\n📡 Iniciando servidor backend + frontend...")
        print("🌐 Acesse: http://127.0.0.1:8000")
        print("\n💡 Dica: Pressione Ctrl+C para parar o servidor")
        print("=" * 50)
        print()
        
        # Inicia thread para abrir o navegador
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--reload",
            "--host", "127.0.0.1",
            "--port", "8000"
        ])

    except KeyboardInterrupt:
        print("\n\n👋 Servidor encerrado!")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        print("\n💡 Certifique-se de que o uvicorn está instalado:")
        print("   pip install uvicorn")
        sys.exit(1)

if __name__ == "__main__":
    main()

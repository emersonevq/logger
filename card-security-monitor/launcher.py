"""
Launcher Completo - Backend + Monitor + Navegador em um único executável
Executar com: python launcher.py (ou launcher.exe após compilação)
"""

import sys
import os
import time
import threading
import subprocess
import webbrowser
import socket
import psutil
from pathlib import Path


class FusionLauncher:
    """Gerencia execução de Backend Express + Monitor Python + Navegador"""

    def __init__(self):
        self.backend_process = None
        self.monitor_process = None
        self.backend_port = 8080
        self.backend_ready = False
        self.running = True
        self.root_dir = Path(__file__).parent.parent
        self.dist_dir = self.root_dir / "dist" / "server"
        self.node_build = self.dist_dir / "node-build.mjs"

    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ ",
            "MONITOR": "🔒",
            "BACKEND": "🚀",
            "BROWSER": "🌐",
        }.get(level, "•")

        print(f"[{timestamp}] {prefix} {message}")

    def check_port_available(self, port: int) -> bool:
        """Verifica se porta está disponível"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            return result != 0
        except:
            return True

    def kill_process_on_port(self, port: int):
        """Mata processo usando a porta (se houver)"""
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if proc.net_connections():
                        for conn in proc.net_connections():
                            if conn.laddr.port == port:
                                self.log(
                                    f"Encerrando processo na porta {port}: {proc.name()}",
                                    "WARNING",
                                )
                                proc.terminate()
                                time.sleep(1)
                                if proc.is_running():
                                    proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except:
            pass

    def ensure_port_available(self, port: int, max_wait: int = 5):
        """Garante que a porta está disponível"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.check_port_available(port):
                return True
            self.kill_process_on_port(port)
            time.sleep(0.5)
        return False

    def start_backend(self):
        """Inicia servidor Express/Node"""
        self.log("Iniciando servidor Backend...", "BACKEND")

        # Garantir que porta está livre
        if not self.ensure_port_available(self.backend_port):
            self.log(f"Porta {self.backend_port} ainda em uso!", "ERROR")
            return False

        try:
            # Se estamos em produção (.exe), use node-build.mjs
            # Se estamos em desenvolvimento, use npm run dev
            if hasattr(sys, "frozen"):  # Executando como .exe
                if self.node_build.exists():
                    self.log(f"Usando build: {self.node_build}", "BACKEND")
                    self.backend_process = subprocess.Popen(
                        [sys.executable, "-m", "subprocess", "node", str(self.node_build)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=str(self.root_dir),
                    )
                else:
                    self.log(f"Build não encontrado: {self.node_build}", "ERROR")
                    return False
            else:
                # Modo desenvolvimento
                self.log("Modo desenvolvimento: using npm run build + node", "INFO")
                # Primeiro fazer build
                self.log("Compilando projeto...", "BACKEND")
                build_result = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=str(self.root_dir),
                    capture_output=True,
                )

                if build_result.returncode != 0:
                    self.log("Erro ao compilar projeto", "ERROR")
                    return False

                self.log("Build completo! Iniciando servidor...", "BACKEND")

                # Depois iniciar servidor
                self.backend_process = subprocess.Popen(
                    ["node", str(self.node_build)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(self.root_dir),
                    env={**os.environ, "PORT": str(self.backend_port)},
                )

            self.log(f"Backend iniciado (PID: {self.backend_process.pid})", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Erro ao iniciar backend: {e}", "ERROR")
            return False

    def wait_for_backend(self, timeout: int = 30):
        """Aguarda backend ficar pronto"""
        self.log(f"Aguardando backend ficar pronto (timeout: {timeout}s)...", "BACKEND")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(("127.0.0.1", self.backend_port))
                sock.close()

                if result == 0:
                    self.log(f"Backend está pronto em http://localhost:{self.backend_port}", "SUCCESS")
                    self.backend_ready = True
                    return True
            except:
                pass

            time.sleep(1)

        self.log("Timeout aguardando backend!", "ERROR")
        return False

    def start_monitor(self):
        """Inicia monitor Python"""
        self.log("Iniciando monitor de cartão...", "MONITOR")

        try:
            monitor_script = Path(__file__).parent / "main.py"

            if hasattr(sys, "frozen"):
                # Se for .exe, executar o main.py da pasta
                self.monitor_process = subprocess.Popen(
                    [sys.executable, str(monitor_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(Path(__file__).parent),
                )
            else:
                # Modo desenvolvimento
                self.monitor_process = subprocess.Popen(
                    [sys.executable, str(monitor_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(Path(__file__).parent),
                )

            self.log(f"Monitor iniciado (PID: {self.monitor_process.pid})", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Erro ao iniciar monitor: {e}", "ERROR")
            return False

    def open_browser(self):
        """Abre navegador automaticamente"""
        self.log("Abrindo navegador...", "BROWSER")

        time.sleep(2)  # Aguardar backend estar totalmente pronto

        url = f"http://localhost:{self.backend_port}/payment-test"

        try:
            webbrowser.open(url)
            self.log(f"Navegador aberto: {url}", "SUCCESS")
        except Exception as e:
            self.log(f"Erro ao abrir navegador: {e}", "WARNING")
            self.log(f"Abra manualmente: {url}", "INFO")

    def monitor_processes(self):
        """Monitora processos em background"""
        while self.running:
            time.sleep(5)

            # Verificar backend
            if self.backend_process and self.backend_process.poll() is not None:
                self.log("Backend foi encerrado!", "ERROR")
                self.running = False
                break

            # Verificar monitor
            if self.monitor_process and self.monitor_process.poll() is not None:
                self.log("Monitor foi encerrado", "WARNING")
                # Reiniciar monitor
                self.log("Reiniciando monitor...", "INFO")
                self.start_monitor()

    def cleanup(self):
        """Encerra processos"""
        self.log("Encerrando aplicação...", "INFO")

        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                self.backend_process.kill()

        if self.monitor_process:
            try:
                self.monitor_process.terminate()
                self.monitor_process.wait(timeout=5)
            except:
                self.monitor_process.kill()

        self.log("Aplicação encerrada", "SUCCESS")

    def run(self):
        """Executa launcher completo"""
        print("\n" + "=" * 60)
        print("  🔒 CREDIT CARD SECURITY MONITOR - LAUNCHER")
        print("  Backend + Monitor + Navegador em um executável")
        print("=" * 60 + "\n")

        try:
            # 1. Iniciar backend
            if not self.start_backend():
                self.log("Falha ao iniciar backend", "ERROR")
                return False

            # 2. Aguardar backend estar pronto
            if not self.wait_for_backend():
                self.log("Backend não ficou pronto a tempo", "ERROR")
                return False

            # 3. Iniciar monitor
            if not self.start_monitor():
                self.log("Falha ao iniciar monitor", "ERROR")
                # Continua mesmo assim
                pass

            # 4. Abrir navegador
            self.open_browser()

            # 5. Monitorar processos
            self.log("\n" + "=" * 60, "INFO")
            self.log("✅ SISTEMA PRONTO!", "SUCCESS")
            self.log("=" * 60, "INFO")
            self.log("Backend:  http://localhost:8080", "INFO")
            self.log("Monitor:  Rodando em background", "INFO")
            self.log("Browser:  Aberto automaticamente", "INFO")
            self.log("\nPressione Ctrl+C para encerrar", "INFO")
            self.log("=" * 60 + "\n", "INFO")

            # Monitorar em background
            monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            monitor_thread.start()

            # Aguardar
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            self.log("\nInterrupção do usuário", "INFO")
        except Exception as e:
            self.log(f"Erro inesperado: {e}", "ERROR")
            import traceback

            traceback.print_exc()
        finally:
            self.cleanup()


def main():
    """Função principal"""
    launcher = FusionLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

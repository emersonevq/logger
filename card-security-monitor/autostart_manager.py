"""
AutoStart Manager - Versão simplificada que funciona
Gerencia inicialização automática do Windows
Protege contra múltiplas instâncias
"""

import os
import sys
import winreg


class AutoStartManager:
    """Gerencia inicialização automática no Windows"""

    APP_NAME = "WindowsSecurity"
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    OLD_NAMES = ["CardSecurityMonitor", "Security", "Monitor"]  # Nomes antigos para limpar

    def __init__(self):
        self.exe_path = self._get_exe_path()
        self._cleanup_old_entries()

    def _get_exe_path(self) -> str:
        """Retorna o caminho do executável"""
        if getattr(sys, 'frozen', False):
            # Rodando como .exe
            return os.path.abspath(sys.executable)
        else:
            # Rodando como script Python
            return f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

    def _cleanup_old_entries(self):
        """Remove entradas antigas do registry"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REG_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            for old_name in self.OLD_NAMES:
                try:
                    winreg.DeleteValue(key, old_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except:
            pass

    def is_installed(self) -> bool:
        """Verifica se autostart está ativado"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REG_PATH,
                0,
                winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except:
            return False

    def enable_autostart(self) -> tuple:
        """Ativa inicialização automática"""
        try:
            # Primeiro limpar entradas antigas
            self._cleanup_old_entries()

            # Se já existe, remover primeiro (evita duplicação)
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    self.REG_PATH,
                    0,
                    winreg.KEY_SET_VALUE
                )
                winreg.DeleteValue(key, self.APP_NAME)
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass

            # Agora criar a entrada
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REG_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(
                key,
                self.APP_NAME,
                0,
                winreg.REG_SZ,
                self.exe_path
            )
            winreg.CloseKey(key)
            return True, "Autostart ativado!"
        except Exception as e:
            return False, f"Erro: {e}"

    def disable_autostart(self) -> tuple:
        """Desativa inicialização automática"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REG_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            try:
                winreg.DeleteValue(key, self.APP_NAME)
            except FileNotFoundError:
                pass

            # Também remover entradas antigas
            for old_name in self.OLD_NAMES:
                try:
                    winreg.DeleteValue(key, old_name)
                except FileNotFoundError:
                    pass

            winreg.CloseKey(key)
            return True, "Autostart desativado!"
        except Exception as e:
            return False, f"Erro: {e}"

    def toggle_autostart(self) -> tuple:
        """Alterna estado do autostart"""
        if self.is_installed():
            return self.disable_autostart()
        else:
            return self.enable_autostart()

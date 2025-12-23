"""
AutoStart Manager - Versão simplificada que funciona
Gerencia inicialização automática do Windows
"""

import os
import sys
import winreg


class AutoStartManager:
    """Gerencia inicialização automática no Windows"""
    
    APP_NAME = "WindowsSecurity"
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def __init__(self):
        self.exe_path = self._get_exe_path()
    
    def _get_exe_path(self) -> str:
        """Retorna o caminho do executável"""
        if getattr(sys, 'frozen', False):
            # Rodando como .exe
            return os.path.abspath(sys.executable)
        else:
            # Rodando como script Python
            return f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
    
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

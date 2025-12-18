"""
AutoStart Manager - Gerencia inicialização automática com Windows
"""

import os
import sys
import winreg
from pathlib import Path


class AutoStartManager:
    """Gerencia inicialização automática no Windows"""
    
    APP_NAME = "WindowsSecurity"
    
    def __init__(self):
        self.reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        self.exe_path = self._get_exe_path()
    
    def _get_exe_path(self) -> str:
        """Retorna o caminho do executável"""
        if getattr(sys, 'frozen', False):
            # Rodando como .exe compilado
            return sys.executable
        else:
            # Rodando como script Python
            python_exe = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            return f'"{python_exe}" "{script_path}"'
    
    def is_installed(self) -> bool:
        """Verifica se está configurado para iniciar com Windows"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.reg_path,
                0,
                winreg.KEY_READ
            )
            try:
                value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception as e:
            print(f"   ⚠️ Erro ao verificar autostart: {e}")
            return False
    
    def enable_autostart(self) -> tuple:
        """Ativa inicialização automática"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.reg_path,
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
            print(f"   ✅ Autostart ativado: {self.exe_path}")
            return True, "Inicialização automática ativada!"
            
        except PermissionError:
            print("   ❌ Sem permissão para modificar registro")
            return False, "Erro: Execute como Administrador"
        except Exception as e:
            print(f"   ❌ Erro ao ativar autostart: {e}")
            return False, f"Erro: {e}"
    
    def disable_autostart(self) -> tuple:
        """Desativa inicialização automática"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.reg_path,
                0,
                winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, self.APP_NAME)
                print("   ✅ Autostart desativado")
            except FileNotFoundError:
                print("   ⚠️ Autostart já estava desativado")
            
            winreg.CloseKey(key)
            return True, "Inicialização automática desativada!"
            
        except PermissionError:
            print("   ❌ Sem permissão para modificar registro")
            return False, "Erro: Execute como Administrador"
        except Exception as e:
            print(f"   ❌ Erro ao desativar autostart: {e}")
            return False, f"Erro: {e}"
    
    def toggle_autostart(self) -> tuple:
        """Alterna estado do autostart"""
        if self.is_installed():
            return self.disable_autostart()
        else:
            return self.enable_autostart()


# Teste
if __name__ == "__main__":
    print("="*50)
    print("  Teste do AutoStart Manager")
    print("="*50)
    
    manager = AutoStartManager()
    
    print(f"\n📂 Caminho do executável:")
    print(f"   {manager.exe_path}")
    
    print(f"\n📋 Status atual:")
    if manager.is_installed():
        print("   ✅ Autostart ATIVADO")
    else:
        print("   ❌ Autostart DESATIVADO")
    
    print(f"\n🔄 Alternando estado...")
    success, message = manager.toggle_autostart()
    print(f"   {message}")
    
    print(f"\n📋 Novo status:")
    if manager.is_installed():
        print("   ✅ Autostart ATIVADO")
    else:
        print("   ❌ Autostart DESATIVADO")
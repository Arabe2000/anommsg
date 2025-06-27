#!/usr/bin/env python3
"""
Teste local da aplicação Flask
"""

import requests
import json

def test_health():
    """Testa o endpoint de saúde"""
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_create_room():
    """Testa a criação de sala"""
    try:
        data = {'user_id': 'test_user'}
        response = requests.post('http://localhost:5000/api/create-room', 
                               json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    print("Testando aplicação local...")
    print("=" * 40)
    
    print("\n1. Testando endpoint de saúde:")
    health_ok = test_health()
    
    print("\n2. Testando criação de sala:")
    room_ok = test_create_room()
    
    print("\n" + "=" * 40)
    if health_ok and room_ok:
        print("✅ Todos os testes passaram!")
    else:
        print("❌ Alguns testes falharam!") 
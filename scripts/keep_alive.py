"""Script para manter o serviço ativo via ping periódico"""
import requests
import time
import os

API_URL = os.getenv("API_URL", "https://electric-ki-investone-9623b27e.koyeb.app")

def keep_alive():
    while True:
        try:
            response = requests.get(f"{API_URL}/api/ping", timeout=10)
            print(f"✅ Keep-alive ping: {response.status_code} - {response.json().get('time')}")
        except Exception as e:
            print(f"❌ Erro no ping: {e}")
        time.sleep(300)  # A cada 5 minutos

if __name__ == "__main__":
    keep_alive()
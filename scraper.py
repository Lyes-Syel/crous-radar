import os
import cloudscraper
import requests

# Récupération du webhook sécurisé
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

# URL de recherche avec la Bounding Box centrée sur Paris et proche banlieue
CROUS_URL = "https://trouverunlogement.lescrous.fr/tools/45/search?bounds=2.2241_48.9021_2.4697_48.8155"

def send_discord_alert(message):
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": message})
    else:
        print("Erreur: Webhook introuvable.")

def check_crous():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    try:
        response = scraper.get(CROUS_URL, timeout=15)
        
        if response.status_code == 200:
            if "0 logement" not in response.text and "Aucun logement" not in response.text:
                print("Changement détecté !")
                send_discord_alert(f"🚨 **MOUVEMENT SUR LE CROUS (PARIS)** 🚨\nUn logement est potentiellement apparu dans la zone.\nClique ici vite : {CROUS_URL}")
            else:
                print("Scan terminé : 0 logement disponible.")
        else:
            print(f"Erreur serveur Crous : {response.status_code}")
            
    except Exception as e:
        print(f"Crash du scraper : {e}")

if __name__ == "__main__":
    check_crous()


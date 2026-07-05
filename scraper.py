import os
import cloudscraper
import requests
import time
import re

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
CROUS_URL = "https://trouverunlogement.lescrous.fr/tools/45/search?bounds=2.2241_48.9021_2.4697_48.8155"

def send_discord_alert(message):
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": message})

def check_crous(previous_count, is_first_run):
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    try:
        response = scraper.get(CROUS_URL, timeout=15)
        
        if response.status_code == 200:
            # Recherche dynamique du nombre exact (gère "1 logement" ou "73 logements")
            match = re.search(r'(\d+)\s+logement', response.text)
            
            if match:
                current_count = int(match.group(1))
                
                # Comportement au TOUT PREMIER lancement (Création de la baseline)
                if is_first_run:
                    print(f"Initialisation : Le compteur de départ est fixé à {current_count} logements.")
                    return current_count

                # Comportement pour les tours suivants
                if current_count > previous_count:
                    send_discord_alert(f"🚨 **NOUVEL AJOUT DETECTÉ !** 🚨\nLe stock est passé de {previous_count} à {current_count} logements.\nFonce : {CROUS_URL}")
                elif current_count < previous_count:
                    print(f"Un logement a été pris par un autre étudiant (Stock: {current_count}).")
                else:
                    print(f"Scan OK : Toujours {current_count} logements. Rien de nouveau.")
                
                return current_count
            
            # Cas où la page affiche expressément 0
            elif "Aucun logement" in response.text or "0 logement" in response.text:
                if is_first_run:
                    print("Initialisation : Le compteur de départ est fixé à 0.")
                elif previous_count > 0:
                    print("Tous les logements ont disparu ! Retour à 0.")
                return 0
                
            elif "Le dépôt des vœux est fermé" in response.text:
                print("La phase n'est pas encore ouverte.")
                return previous_count
                
    except Exception as e:
        print(f"Erreur de réseau : {e}")
        
    return previous_count

if __name__ == "__main__":
    print("Démarrage du radar continu...")
    send_discord_alert("✅ Radar activé pour 5 heures. Initialisation en cours...")
    
    current_logements = 0
    max_iterations = 100 
    
    for i in range(max_iterations):
        print(f"\n--- Boucle {i+1}/{max_iterations} ---")
        
        # On définit que le tour n°0 est le premier lancement
        is_first_run = (i == 0)
        
        # On met à jour la mémoire du robot
        current_logements = check_crous(current_logements, is_first_run)
        
        # Pause de 3 minutes (180 secondes)
        time.sleep(180)
        
    send_discord_alert("⚠️ Fin du cycle de 5h. Relance-le manuellement sur GitHub !")

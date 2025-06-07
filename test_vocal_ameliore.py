#!/usr/bin/env python3
"""
Test vocal amélioré avec calibrage et diagnostics
"""

import speech_recognition as sr
import time

def test_microphone_detailed():
    """Test microphone avec diagnostics détaillés"""
    print("🎤 TEST MICROPHONE DÉTAILLÉ")
    print("=" * 40)
    
    try:
        r = sr.Recognizer()
        
        # Lister les micros
        print("📋 Micros disponibles:")
        for i, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {i}: {name}")
        
        # Utiliser le micro par défaut
        with sr.Microphone() as source:
            print("\n🔧 Calibrage avancé...")
            r.adjust_for_ambient_noise(source, duration=3)
            
            # Paramètres optimaux
            r.energy_threshold = 300
            r.dynamic_energy_threshold = True
            r.pause_threshold = 0.8
            
            print(f"Seuil énergie: {r.energy_threshold}")
            print(f"Seuil dynamique: {r.dynamic_energy_threshold}")
            print(f"Pause threshold: {r.pause_threshold}")
            
            print("\n🔴 PARLEZ MAINTENANT - dites 'BONJOUR ASSISTANT' (10 sec)")
            print("Parlez FORT et CLAIREMENT près du microphone...")
            
            # Écoute prolongée
            audio = r.listen(source, timeout=10, phrase_time_limit=5)
        
        print("\n🤖 Reconnaissance en cours...")
        
        # Test plusieurs langues
        results = []
        
        # Français
        try:
            text_fr = r.recognize_google(audio, language="fr-FR")
            results.append(("Français", text_fr))
            print(f"🇫🇷 Français: '{text_fr}'")
        except sr.UnknownValueError:
            print("🇫🇷 Français: non compris")
        except sr.RequestError as e:
            print(f"🇫🇷 Français: erreur service - {e}")
        
        # Anglais (fallback)
        try:
            text_en = r.recognize_google(audio, language="en-US")
            results.append(("Anglais", text_en))
            print(f"🇺🇸 Anglais: '{text_en}'")
        except sr.UnknownValueError:
            print("🇺🇸 Anglais: non compris")
        except sr.RequestError as e:
            print(f"🇺🇸 Anglais: erreur service - {e}")
        
        if results:
            print(f"\n✅ Reconnaissance réussie ! {len(results)} résultat(s)")
            return True
        else:
            print("\n❌ Aucune reconnaissance réussie")
            return False
            
    except sr.WaitTimeoutError:
        print("\n⏰ Timeout - aucun son détecté")
        print("💡 Vérifiez:")
        print("  - Microphone branché et allumé")
        print("  - Permissions microphone accordées")
        print("  - Volume d'entrée suffisant")
        return False
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    print("🧪 TEST VOCAL AMÉLIORÉ")
    print("=" * 50)
    
    success = test_microphone_detailed()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST RÉUSSI ! Système vocal opérationnel.")
        print("\n🚀 Prochaines étapes:")
        print("  python main_vocal.py --console    # Mode console")
        print("  python main_vocal.py             # Mode graphique")
    else:
        print("⚠️ TEST ÉCHOUÉ. Vérifiez la configuration.")
        print("\n🔧 Solutions possibles:")
        print("  1. Vérifier permissions microphone")
        print("  2. Ajuster volume d'entrée Windows")
        print("  3. Tester avec un autre microphone")
        print("  4. Redémarrer l'application")

if __name__ == "__main__":
    main()

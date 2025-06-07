#!/usr/bin/env python3
"""
Test simple du système vocal
"""

def test_microphone():
    """Test microphone uniquement"""
    try:
        import speech_recognition as sr
        
        r = sr.Recognizer()
        
        print("🎤 Test microphone - Parlez après le bip...")
        
        with sr.Microphone() as source:
            print("Calibrage...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("PARLEZ MAINTENANT (5 secondes)...")
            audio = r.listen(source, timeout=5, phrase_time_limit=3)
        
        print("Reconnaissance en cours...")
        text = r.recognize_google(audio, language="fr-FR")
        print(f"✅ Reconnu: '{text}'")
        
        return True
        
    except sr.UnknownValueError:
        print("❓ Parole non comprise")
        return False
    except sr.RequestError as e:
        print(f"❌ Erreur service: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TEST VOCAL SIMPLE")
    print("=" * 30)
    
    success = test_microphone()
    
    if success:
        print("🎉 Test vocal réussi ! Système opérationnel.")
    else:
        print("⚠️ Test vocal échoué. Vérifiez microphone et connexion.")

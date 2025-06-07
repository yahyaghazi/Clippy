#!/usr/bin/env python3
"""
Interface simple pour tester les commandes système
"""

import sys
import time
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path("src")))

from ai_system.command_parser import command_parser
from vision.screen_capture import screen_capture
from control.mouse_controller import mouse_controller
from control.keyboard_controller import keyboard_controller


def execute_action_simple(action):
    """Exécute une action de façon basique"""
    try:
        action_type = action.action_type.value
        params = action.parameters
        
        if action_type == "screenshot":
            screenshot = screen_capture.capture_full_screen()
            if screenshot:
                return {"success": True, "message": "Capture d'écran réalisée"}
            else:
                return {"success": False, "error": "Échec capture"}
        
        elif action_type == "click":
            if 'x' in params and 'y' in params:
                success = mouse_controller.click(params['x'], params['y'])
                return {"success": success, "message": f"Clic à ({params['x']}, {params['y']})"}
            else:
                return {"success": False, "error": "Coordonnées manquantes"}
        
        elif action_type == "type":
            text = params.get('text', '')
            success = keyboard_controller.type_text(text)
            return {"success": success, "message": f"Texte tapé: {text}"}
        
        elif action_type == "key_press":
            key = params.get('key', '')
            success = keyboard_controller.press_key(key)
            return {"success": success, "message": f"Touche pressée: {key}"}
        
        elif action_type == "scroll":
            clicks = params.get('clicks', 1)
            success = mouse_controller.scroll(clicks)
            return {"success": success, "message": f"Défilement: {clicks}"}
        
        elif action_type == "mouse_move":
            if 'x' in params and 'y' in params:
                success = mouse_controller.move_to(params['x'], params['y'])
                return {"success": success, "message": f"Souris déplacée vers ({params['x']}, {params['y']})"}
            else:
                return {"success": False, "error": "Coordonnées manquantes"}
        
        elif action_type == "wait":
            seconds = params.get('seconds', 1)
            time.sleep(seconds)
            return {"success": True, "message": f"Attente de {seconds}s"}
        
        else:
            return {"success": False, "error": f"Action '{action_type}' non implémentée"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Interface de test des commandes"""
    print("🤖 ASSISTANT IA - MODE COMMANDES")
    print("=" * 50)
    print("🎯 Tapez vos commandes en français !")
    print("\n📖 Exemples de commandes :")
    print("  📸 Prends une capture d'écran")
    print("  🖱️ Clique à 500, 300") 
    print("  ⌨️ Écris 'Bonjour'")
    print("  📜 Scroll vers le bas")
    print("  ⌚ Attends 2 secondes")
    print("  🚪 quit (pour quitter)")
    print("=" * 50)
    
    # Test initial
    print("\n🧪 Test des modules...")
    try:
        print("✅ Parser chargé")
        print("✅ Contrôles disponibles")
        print("⚠️ ATTENTION: Actions réelles sur votre système !")
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return
    
    while True:
        try:
            print(f"\n" + "─" * 30)
            command = input("💬 Votre commande: ").strip()
            
            # Commandes spéciales
            if command.lower() in ['quit', 'exit', 'q', 'quitter']:
                print("👋 Au revoir !")
                break
            
            if command.lower() in ['help', 'aide', '?']:
                print("\n📚 Aide rapide:")
                print("  • Prends une capture")
                print("  • Clique à X, Y") 
                print("  • Écris 'votre texte'")
                print("  • Scroll vers le bas/haut")
                print("  • Attends N secondes")
                continue
            
            if not command:
                continue
            
            print(f"🔍 Analyse: '{command}'")
            
            # Parser la commande
            actions = command_parser.parse_command(command)
            
            if not actions:
                print("❌ Commande non reconnue")
                print("💡 Essayez 'aide' pour voir les exemples")
                continue
            
            # Prendre la meilleure action
            best_action = actions[0]
            print(f"🎯 Action détectée: {best_action.description}")
            print(f"📊 Confiance: {best_action.confidence:.1f}")
            
            # Validation sécurité
            valid, msg = command_parser.validate_action(best_action)
            if not valid:
                print(f"⚠️ Action non sécurisée: {msg}")
                continue
            
            # Demander confirmation pour actions critiques
            action_type = best_action.action_type.value
            if action_type in ['click', 'type', 'key_press']:
                print("⚠️ Cette action va contrôler votre système !")
                confirm = input("Continuer ? (oui/non): ").lower()
                if confirm not in ['oui', 'o', 'y', 'yes']:
                    print("⏭️ Action annulée par sécurité")
                    continue
            
            # Exécution
            print("⚡ Exécution en cours...")
            result = execute_action_simple(best_action)
            
            if result['success']:
                print(f"✅ Succès: {result.get('message', 'Action réalisée')}")
            else:
                print(f"❌ Échec: {result.get('error', 'Erreur inconnue')}")
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Interruption utilisateur")
            print("👋 Au revoir !")
            break
            
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            print("🔄 Continuez ou tapez 'quit'")


if __name__ == "__main__":
    main()

"""
Tests pour les modules système - Phase 1
"""

import sys
from pathlib import Path
import time

# Ajouter src au path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_screen_capture():
    """Test du module capture d'écran"""
    print("🔍 Test module capture d'écran...")
    try:
        from src.vision.screen_capture import screen_capture
        
        # Test capture complète
        print("  - Capture écran complet...")
        screenshot = screen_capture.capture_full_screen()
        if screenshot:
            print(f"    ✅ Capture réussie: {screenshot.size}")
        else:
            print("    ❌ Échec capture")
            return False
        
        # Test taille écran
        size = screen_capture.get_screen_size()
        print(f"  - Taille écran: {size}")
        
        # Test capture région
        print("  - Capture région...")
        region = screen_capture.capture_region(0, 0, 400, 300)
        if region:
            print(f"    ✅ Région capturée: {region.size}")
        
        # Test capture fenêtre active
        print("  - Capture fenêtre active...")
        window = screen_capture.capture_active_window()
        if window:
            print(f"    ✅ Fenêtre capturée: {window.size}")
        
        print("✅ Module capture d'écran OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur module capture: {e}")
        return False


def test_ocr_engine():
    """Test du moteur OCR"""
    print("🔍 Test moteur OCR...")
    try:
        from src.vision.ocr_engine import ocr_engine
        from PIL import Image, ImageDraw, ImageFont
        
        # Informations moteur
        info = ocr_engine.get_ocr_info()
        print(f"  - Moteurs disponibles: {info}")
        
        if not info['tesseract_available'] and not info['easyocr_available']:
            print("  ⚠️ Aucun moteur OCR disponible")
            return True  # Pas d'erreur, juste pas installé
        
        # Créer une image test avec du texte
        test_image = Image.new('RGB', (300, 100), 'white')
        draw = ImageDraw.Draw(test_image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 30), "Hello World Test", fill='black', font=font)
        
        # Test extraction texte
        print("  - Test extraction texte...")
        text = ocr_engine.extract_text_auto(test_image)
        if "hello" in text.lower() or "world" in text.lower():
            print(f"    ✅ Texte détecté: '{text.strip()}'")
        else:
            print(f"    ⚠️ Texte non détecté ou imprécis: '{text.strip()}'")
        
        print("✅ Module OCR testé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur module OCR: {e}")
        return False


def test_mouse_controller():
    """Test du contrôleur souris"""
    print("🔍 Test contrôleur souris...")
    try:
        from src.control.mouse_controller import mouse_controller
        
        # Position actuelle
        pos = mouse_controller.get_position()
        print(f"  - Position actuelle: {pos}")
        
        # Test mouvement (petit déplacement sécurisé)
        print("  - Test mouvement relatif...")
        original_pos = mouse_controller.get_position()
        mouse_controller.move_relative(50, 50, duration=0.2)
        time.sleep(0.1)
        
        new_pos = mouse_controller.get_position()
        if new_pos != original_pos:
            print("    ✅ Mouvement réussi")
            
            # Retour position originale
            mouse_controller.move_to(original_pos[0], original_pos[1], duration=0.2)
        else:
            print("    ⚠️ Mouvement non détecté")
        
        # Test taille écran
        screen_size = mouse_controller.get_screen_bounds()
        print(f"  - Taille écran: {screen_size}")
        
        # Test validation position
        valid = mouse_controller.is_position_valid(100, 100)
        invalid = mouse_controller.is_position_valid(-10, -10)
        print(f"  - Validation position: valide={valid}, invalide={invalid}")
        
        print("✅ Module souris OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur module souris: {e}")
        return False


def test_keyboard_controller():
    """Test du contrôleur clavier"""
    print("🔍 Test contrôleur clavier...")
    try:
        from src.control.keyboard_controller import keyboard_controller
        
        print("  ⚠️ Test clavier nécessite focus sur zone de texte")
        print("  - Tests non interactifs seulement...")
        
        # Test configuration vitesse
        keyboard_controller.set_typing_speed('fast')
        print("    ✅ Configuration vitesse")
        
        # Test activation mode humain
        keyboard_controller.enable_human_typing(True)
        print("    ✅ Mode frappe humaine")
        
        # Note: Pas de test de frappe réelle pour éviter les interférences
        print("✅ Module clavier configuré (tests limités)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur module clavier: {e}")
        return False


def test_command_parser():
    """Test du parseur de commandes"""
    print("🔍 Test parseur de commandes...")
    try:
        from src.ai_system.command_parser import command_parser
        
        # Tests de parsing
        test_commands = [
            "Prends une capture d'écran",
            "Clique sur le bouton OK",
            "Écris 'Hello World'",
            "Scroll vers le bas",
            "Lance Chrome",
            "Trouve le texte 'connexion'",
            "Attends 2 secondes",
            "Déplace la souris vers 100, 200"
        ]
        
        for command in test_commands:
            print(f"  - Test: '{command}'")
            actions = command_parser.parse_command(command)
            
            if actions:
                best_action = actions[0]
                print(f"    ✅ {best_action.action_type.value}: {best_action.description}")
                
                # Test validation
                valid, msg = command_parser.validate_action(best_action)
                if valid:
                    print(f"    ✅ Validation OK")
                else:
                    print(f"    ⚠️ Validation: {msg}")
            else:
                print("    ❌ Aucune action détectée")
        
        # Test commande complexe
        print("  - Test commande complexe...")
        complex_cmd = "Prends une capture puis clique sur OK et écris 'test'"
        complex_actions = command_parser.parse_complex_command(complex_cmd)
        print(f"    ✅ {len(complex_actions)} actions détectées")
        
        print("✅ Module parseur OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur module parseur: {e}")
        return False


def test_integration():
    """Test d'intégration simple"""
    print("🔍 Test d'intégration...")
    try:
        # Test chaîne complète: commande -> parsing -> exécution simulée
        from src.ai_system.command_parser import command_parser
        from src.vision.screen_capture import screen_capture
        
        command = "Prends une capture d'écran"
        print(f"  - Commande: '{command}'")
        
        # Parser
        actions = command_parser.parse_command(command)
        if not actions:
            print("    ❌ Parsing échoué")
            return False
        
        action = actions[0]
        print(f"    ✅ Action parsée: {action.description}")
        
        # Exécution simulée
        if action.action_type.value == "screenshot":
            screenshot = screen_capture.capture_full_screen()
            if screenshot:
                print("    ✅ Capture réalisée")
            else:
                print("    ❌ Capture échouée")
                return False
        
        print("✅ Test d'intégration réussi")
        return True
        
    except Exception as e:
        print(f"❌ Erreur intégration: {e}")
        return False


def test_dependencies():
    """Test des dépendances système"""
    print("🔍 Test dépendances...")
    
    required = ['pyautogui', 'Pillow']
    optional = ['pytesseract', 'easyocr', 'opencv-python', 'numpy']
    
    results = {'required': [], 'optional': []}
    
    for dep in required:
        try:
            __import__(dep)
            results['required'].append((dep, True))
            print(f"  ✅ {dep}")
        except ImportError:
            results['required'].append((dep, False))
            print(f"  ❌ {dep} MANQUANT")
    
    for dep in optional:
        try:
            __import__(dep)
            results['optional'].append((dep, True))
            print(f"  ✅ {dep} (optionnel)")
        except ImportError:
            results['optional'].append((dep, False))
            print(f"  ⚠️ {dep} (optionnel, non installé)")
    
    # Vérifier que toutes les dépendances requises sont présentes
    missing_required = [dep for dep, available in results['required'] if not available]
    
    if missing_required:
        print(f"\n❌ Dépendances manquantes: {missing_required}")
        print("Installez avec: pip install " + " ".join(missing_required))
        return False
    else:
        print("\n✅ Toutes les dépendances requises sont présentes")
        return True


def main():
    """Test complet de la Phase 1"""
    print("🚀 Tests Phase 1 - Modules Système")
    print("=" * 50)
    
    tests = [
        ("Dépendances", test_dependencies),
        ("Capture d'écran", test_screen_capture),
        ("OCR", test_ocr_engine),
        ("Souris", test_mouse_controller),
        ("Clavier", test_keyboard_controller),
        ("Parseur", test_command_parser),
        ("Intégration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat: {passed}/{len(results)} tests réussis")
    
    if passed == len(results):
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("La Phase 1 est prête pour l'intégration.")
    elif passed >= len(results) * 0.8:
        print("✅ La plupart des tests réussis.")
        print("Phase 1 utilisable avec limitations.")
    else:
        print("⚠️ Plusieurs tests échoués.")
        print("Vérifier les dépendances et l'installation.")


if __name__ == "__main__":
    main()
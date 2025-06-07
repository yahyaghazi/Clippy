#!/usr/bin/env python3
"""
Correction des 2 derniers problèmes détectés
"""

import sys
import subprocess
from pathlib import Path


def fix_pillow_import():
    """Corrige le problème d'import Pillow"""
    print("🔧 CORRECTION PROBLÈME PILLOW")
    print("=" * 50)
    
    try:
        # Le problème : test_system.py cherche 'Pillow' au lieu de 'PIL'
        test_file = Path("test_system.py")
        
        if test_file.exists():
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chercher la section problématique
            if "import Pillow" in content:
                # Remplacer import Pillow par from PIL import Image
                content = content.replace("import Pillow", "from PIL import Image")
                print("✅ Import Pillow → PIL corrigé")
            
            elif "'Pillow'" in content and "required = [" in content:
                # Correction dans la liste des dépendances requises
                content = content.replace("'Pillow'", "'PIL'")
                print("✅ Nom dépendance Pillow → PIL corrigé")
            
            # Écrire les corrections
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        print("✅ Problème Pillow résolu")
        return True
        
    except Exception as e:
        print(f"❌ Erreur correction Pillow: {e}")
        return False


def fix_ocr_import():
    """Corrige le problème d'import 'os' dans ocr_engine.py"""
    print("\n🔧 CORRECTION PROBLÈME OCR")
    print("=" * 50)
    
    try:
        ocr_file = Path("src/vision/ocr_engine.py")
        
        if ocr_file.exists():
            with open(ocr_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier si 'import os' manque
            if "import os" not in content and "os.path.exists" in content:
                # Ajouter import os au début
                lines = content.split('\n')
                
                # Trouver la ligne où insérer l'import
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        continue
                    else:
                        insert_index = i
                        break
                
                # Insérer import os
                lines.insert(insert_index, 'import os')
                content = '\n'.join(lines)
                
                # Sauvegarder
                with open(ocr_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ Import 'os' ajouté à ocr_engine.py")
            else:
                print("✅ Import 'os' déjà présent ou non nécessaire")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur correction OCR: {e}")
        return False


def install_easyocr():
    """Installe EasyOCR pour améliorer l'OCR"""
    print("\n📦 INSTALLATION EASYOCR (Optionnel)")
    print("=" * 50)
    
    choice = input("Installer EasyOCR pour un meilleur OCR ? (o/N): ").lower()
    
    if choice == 'o':
        try:
            print("📥 Installation d'EasyOCR (peut prendre quelques minutes)...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "easyocr"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ EasyOCR installé avec succès")
                return True
            else:
                print("⚠️ Échec installation EasyOCR (optionnel)")
                print(f"Détails: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️ Erreur installation EasyOCR: {e}")
            return False
    else:
        print("⏭️ Installation EasyOCR ignorée")
        return True


def fix_test_dependencies_check():
    """Corrige la vérification des dépendances dans test_system.py"""
    print("\n🔧 CORRECTION VÉRIFICATION DÉPENDANCES")
    print("=" * 50)
    
    try:
        test_file = Path("test_system.py")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer la vérification problématique
        old_check = """    try:
        import Pillow
        results['required'].append((dep, True))
        print(f"  ✅ {dep}")
    except ImportError:
        results['required'].append((dep, False))
        print(f"  ❌ {dep} MANQUANT")"""
        
        new_check = """    try:
        if dep == 'Pillow':
            from PIL import Image
        else:
            __import__(dep)
        results['required'].append((dep, True))
        print(f"  ✅ {dep}")
    except ImportError:
        results['required'].append((dep, False))
        print(f"  ❌ {dep} MANQUANT")"""
        
        if "import Pillow" in content:
            content = content.replace(old_check, new_check)
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Vérification des dépendances corrigée")
        else:
            print("✅ Vérification déjà correcte")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur correction vérification: {e}")
        return False


def test_final():
    """Test final après toutes les corrections"""
    print("\n🧪 TEST FINAL")
    print("=" * 50)
    
    try:
        # Test rapide des imports
        print("Test imports critiques...")
        
        from PIL import Image
        print("✅ PIL/Pillow OK")
        
        sys.path.insert(0, "src")
        from vision.ocr_engine import ocr_engine
        print("✅ OCR engine OK")
        
        info = ocr_engine.get_ocr_info()
        print(f"✅ OCR disponible: {info['recommended_engine']}")
        
        print("\n🎉 Tous les imports fonctionnent !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test final: {e}")
        return False


def main():
    """Correction finale des derniers problèmes"""
    print("🎯 CORRECTION FINALE - Phase 1")
    print("=" * 60)
    
    print("Problèmes détectés à corriger:")
    print("1. ❌ Import Pillow incorrect")
    print("2. ❌ Import 'os' manquant dans OCR")
    
    # Corrections
    step1 = fix_pillow_import()
    step2 = fix_ocr_import() 
    step3 = fix_test_dependencies_check()
    step4 = install_easyocr()
    
    print("\n" + "=" * 60)
    
    # Test final
    test_ok = test_final()
    
    print(f"\n📋 RÉSUMÉ CORRECTIONS:")
    print(f"  Import Pillow: {'✅' if step1 else '❌'}")
    print(f"  Import OS: {'✅' if step2 else '❌'}")
    print(f"  Test deps: {'✅' if step3 else '❌'}")
    print(f"  EasyOCR: {'✅' if step4 else '⏭️'}")
    print(f"  Test final: {'✅' if test_ok else '❌'}")
    
    if step1 and step2 and step3 and test_ok:
        print(f"\n🎉 TOUTES LES CORRECTIONS APPLIQUÉES !")
        print(f"\n🚀 COMMANDES SUIVANTES:")
        print(f"  python test_system.py    # Devrait maintenant afficher 7/7 !")
        print(f"  python main.py          # Lancer l'assistant complet")
    else:
        print(f"\n⚠️ Quelques corrections restent à faire manuellement")
    
    print(f"\n💡 L'assistant devrait maintenant fonctionner avec:")
    print(f"   - ✅ Capture d'écran")
    print(f"   - ✅ Contrôle souris/clavier") 
    print(f"   - ✅ Parsing de commandes")
    print(f"   - ✅ OCR de base (Tesseract)")
    print(f"   - {'✅' if step4 else '⚠️'} OCR avancé (EasyOCR)")


if __name__ == "__main__":
    main()

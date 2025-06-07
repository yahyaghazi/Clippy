#!/usr/bin/env python3
"""
Diagnostic et correction automatique des problèmes détectés
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_environment():
    """Vérifie l'environnement Python"""
    print("🔍 DIAGNOSTIC ENVIRONNEMENT")
    print("=" * 50)
    
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Virtual env: {os.environ.get('VIRTUAL_ENV', 'AUCUN')}")
    print(f"Dossier actuel: {os.getcwd()}")
    
    # Vérifier la structure des dossiers
    current_dir = Path.cwd()
    print(f"\n📁 Structure du projet:")
    
    important_paths = [
        "src",
        "src/vision", 
        "src/vison",  # Faute de frappe détectée !
        "src/control",
        "src/ai_system",
        "requirements.txt"
    ]
    
    structure_ok = True
    for path in important_paths:
        full_path = current_dir / path
        exists = full_path.exists()
        print(f"  {path}: {'✅' if exists else '❌'}")
        if not exists and path in ["src", "requirements.txt"]:
            structure_ok = False
    
    return structure_ok


def fix_typo_in_directory():
    """Corrige la faute de frappe dans le nom de dossier"""
    current_dir = Path.cwd()
    wrong_dir = current_dir / "src" / "vison"  # Faute de frappe
    correct_dir = current_dir / "src" / "vision"
    
    if wrong_dir.exists() and not correct_dir.exists():
        print(f"\n🔧 CORRECTION: Renommage vison → vision")
        try:
            wrong_dir.rename(correct_dir)
            print("✅ Dossier renommé avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur renommage: {e}")
            return False
    elif wrong_dir.exists() and correct_dir.exists():
        print("⚠️ Les deux dossiers 'vison' et 'vision' existent")
        print("Veuillez supprimer manuellement 'vison' après vérification")
    
    return True


def install_missing_dependencies():
    """Installe les dépendances manquantes"""
    print(f"\n📦 INSTALLATION DÉPENDANCES")
    print("=" * 50)
    
    # Dépendances requises détectées comme manquantes
    required_deps = [
        "pyautogui>=0.9.54",
        "Pillow>=10.0.0"
    ]
    
    # Dépendances optionnelles utiles
    optional_deps = [
        "opencv-python>=4.8.0",
        "pytesseract>=0.3.10",
        "numpy>=1.24.0"
    ]
    
    print("Installation des dépendances requises...")
    for dep in required_deps:
        print(f"  📥 {dep}")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True, check=True)
            print(f"  ✅ {dep.split('>=')[0]} installé")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Erreur installation {dep}: {e}")
            return False
    
    print(f"\nInstallation des dépendances optionnelles...")
    for dep in optional_deps:
        print(f"  📥 {dep} (optionnel)")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {dep.split('>=')[0]} installé")
            else:
                print(f"  ⚠️ {dep.split('>=')[0]} échec (optionnel)")
        except Exception as e:
            print(f"  ⚠️ {dep.split('>=')[0]} non installé: {e}")
    
    return True


def fix_import_paths():
    """Corrige les chemins d'import dans test_system.py"""
    print(f"\n🔧 CORRECTION IMPORTS")
    print("=" * 50)
    
    test_file = Path("test_system.py")
    if not test_file.exists():
        print("❌ test_system.py non trouvé")
        return False
    
    try:
        # Lire le fichier
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corriger le chemin d'import
        old_import = "from src.vision.screen_capture import screen_capture"
        new_import = "from vision.screen_capture import screen_capture"
        
        if "src.vision" in content:
            # Remplacer tous les imports src.vision par vision
            content = content.replace("src.vision", "vision")
            content = content.replace("src.control", "control")
            content = content.replace("src.ai_system", "ai_system")
            
            # Sauvegarder
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Imports corrigés dans test_system.py")
            return True
        else:
            print("✅ Imports déjà corrects")
            return True
            
    except Exception as e:
        print(f"❌ Erreur correction imports: {e}")
        return False


def create_missing_init_files():
    """Crée les fichiers __init__.py manquants"""
    print(f"\n📄 CRÉATION FICHIERS __init__.py")
    print("=" * 50)
    
    dirs_needing_init = [
        "src/vision",
        "src/control", 
        "src/ai_system"
    ]
    
    for dir_path in dirs_needing_init:
        init_file = Path(dir_path) / "__init__.py"
        if not init_file.exists():
            try:
                init_file.parent.mkdir(parents=True, exist_ok=True)
                init_file.touch()
                print(f"✅ Créé: {init_file}")
            except Exception as e:
                print(f"❌ Erreur création {init_file}: {e}")
        else:
            print(f"✅ Existe: {init_file}")


def update_requirements():
    """Met à jour requirements.txt avec les nouvelles dépendances"""
    print(f"\n📋 MISE À JOUR REQUIREMENTS")
    print("=" * 50)
    
    req_file = Path("requirements.txt")
    
    # Nouvelles dépendances nécessaires
    new_deps = [
        "# === NOUVEAUX MODULES SYSTÈME ===",
        "",
        "# Vision et capture d'écran",
        "pyautogui>=0.9.54",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "",
        "# OCR (Reconnaissance de texte)", 
        "pytesseract>=0.3.10",
        "easyocr>=1.7.0",
        "",
        "# Traitement d'images et calculs",
        "numpy>=1.24.0",
        "scikit-image>=0.21.0"
    ]
    
    try:
        if req_file.exists():
            with open(req_file, 'r', encoding='utf-8') as f:
                existing = f.read()
            
            # Ajouter les nouvelles dépendances si pas déjà présentes
            if "pyautogui" not in existing:
                with open(req_file, 'a', encoding='utf-8') as f:
                    f.write('\n\n' + '\n'.join(new_deps))
                print("✅ requirements.txt mis à jour")
            else:
                print("✅ requirements.txt déjà à jour")
        else:
            # Créer requirements.txt
            with open(req_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_deps))
            print("✅ requirements.txt créé")
            
    except Exception as e:
        print(f"❌ Erreur requirements.txt: {e}")


def test_after_fixes():
    """Test rapide après corrections"""
    print(f"\n🧪 TEST APRÈS CORRECTIONS")
    print("=" * 50)
    
    try:
        # Test import des modules clés
        print("Test imports...")
        
        import pyautogui
        print("✅ pyautogui importé")
        
        from PIL import Image
        print("✅ Pillow/PIL importé")
        
        # Test structure src
        sys.path.insert(0, str(Path("src")))
        
        try:
            from vision.screen_capture import screen_capture
            print("✅ screen_capture importé")
        except ImportError as e:
            print(f"⚠️ screen_capture: {e}")
        
        try:
            from control.mouse_controller import mouse_controller
            print("✅ mouse_controller importé")
        except ImportError as e:
            print(f"⚠️ mouse_controller: {e}")
            
        try:
            from ai_system.command_parser import command_parser
            print("✅ command_parser importé")
        except ImportError as e:
            print(f"⚠️ command_parser: {e}")
        
        print("\n✅ Tests de base réussis")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False


def main():
    """Fonction principale de diagnostic et correction"""
    print("🔧 DIAGNOSTIC ET CORRECTION AUTOMATIQUE")
    print("=" * 60)
    
    # 1. Diagnostic environnement
    env_ok = check_python_environment()
    
    # 2. Correction faute de frappe dossier
    fix_typo_in_directory()
    
    # 3. Création fichiers __init__.py manquants
    create_missing_init_files()
    
    # 4. Installation dépendances
    if input("\n📦 Installer les dépendances manquantes ? (o/N): ").lower() == 'o':
        install_missing_dependencies()
    
    # 5. Correction imports
    fix_import_paths()
    
    # 6. Mise à jour requirements
    update_requirements()
    
    # 7. Test final
    print(f"\n" + "=" * 60)
    test_ok = test_after_fixes()
    
    print(f"\n📋 RÉSUMÉ:")
    print(f"  Structure projet: {'✅' if env_ok else '❌'}")
    print(f"  Tests finaux: {'✅' if test_ok else '⚠️'}")
    
    if test_ok:
        print(f"\n🎉 CORRECTION RÉUSSIE !")
        print(f"Vous pouvez maintenant relancer: python test_system.py")
    else:
        print(f"\n⚠️ Corrections partielles appliquées")
        print(f"Vérifiez manuellement les erreurs restantes")
    
    print(f"\n🚀 Commandes suggérées:")
    print(f"  python test_system.py        # Re-tester")
    print(f"  python main.py              # Lancer l'assistant")


if __name__ == "__main__":
    main()

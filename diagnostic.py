# diagnostic.py - Lance ce script pour diagnostiquer le problème
import sys
import os

print("=== DIAGNOSTIC PYTHON ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print()

print("=== ENVIRONNEMENT VIRTUEL ===")
print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'Non défini')}")
print(f"PATH (première entrée): {os.environ.get('PATH', '').split(os.pathsep)[0]}")
print()

print("=== TEST D'IMPORT ===")
try:
    import psutil
    print(f"✅ psutil importé avec succès")
    print(f"   Version: {psutil.__version__}")
    print(f"   Fichier: {psutil.__file__}")
except ImportError as e:
    print(f"❌ Erreur import psutil: {e}")

try:
    import requests
    print(f"✅ requests importé avec succès")
    print(f"   Version: {requests.__version__}")
except ImportError as e:
    print(f"❌ Erreur import requests: {e}")

print()
print("=== VÉRIFICATION DOSSIER SRC ===")
src_path = os.path.join(os.getcwd(), "src")
print(f"Dossier src existe: {os.path.exists(src_path)}")
if os.path.exists(src_path):
    print(f"Contenu src: {os.listdir(src_path)}")

print()
print("=== RECOMMENDATION ===")
if os.environ.get('VIRTUAL_ENV'):
    print("Environnement virtuel détecté")
else:
    print("⚠️ Aucun environnement virtuel détecté")
    print("Réactiver avec: .venv\\Scripts\\activate")
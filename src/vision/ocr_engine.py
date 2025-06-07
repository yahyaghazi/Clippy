import os
"""
Moteur OCR pour reconnaissance de texte à l'écran
"""

from PIL import Image
import numpy as np
from typing import List, Dict, Tuple, Optional
import re

# Import conditionnel des moteurs OCR
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ pytesseract non disponible")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️ easyocr non disponible")


class OCREngine:
    """Moteur de reconnaissance de texte"""
    
    def __init__(self):
        self.tesseract_available = TESSERACT_AVAILABLE
        self.easyocr_available = EASYOCR_AVAILABLE
        self.easyocr_reader = None
        
        # Initialiser EasyOCR si disponible
        if EASYOCR_AVAILABLE:
            try:
                self.easyocr_reader = easyocr.Reader(['fr', 'en'], gpu=False)
                print("[OCR] EasyOCR initialisé (français, anglais)")
            except Exception as e:
                print(f"[OCR] Erreur init EasyOCR: {e}")
                self.easyocr_available = False
        
        # Configuration Tesseract
        if TESSERACT_AVAILABLE:
            # Chemin Tesseract sur Windows (ajuster si nécessaire)
            import platform
            if platform.system() == "Windows":
                # Chemins courants d'installation
                possible_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(
                        os.getenv('USERNAME', '')
                    )
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
        
        print(f"[OCR] Moteurs disponibles: Tesseract={self.tesseract_available}, EasyOCR={self.easyocr_available}")
    
    def extract_text_tesseract(self, image: Image.Image, lang='fra+eng') -> str:
        """Extraction de texte avec Tesseract"""
        if not self.tesseract_available:
            return ""
        
        try:
            # Configuration Tesseract
            config = '--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6
            
            text = pytesseract.image_to_string(image, lang=lang, config=config)
            return text.strip()
            
        except Exception as e:
            print(f"[OCR ERROR] Tesseract: {e}")
            return ""
    
    def extract_text_easyocr(self, image: Image.Image) -> str:
        """Extraction de texte avec EasyOCR"""
        if not self.easyocr_available or not self.easyocr_reader:
            return ""
        
        try:
            # Convertir PIL en numpy array
            image_array = np.array(image)
            
            # Extraire le texte
            results = self.easyocr_reader.readtext(image_array)
            
            # Combiner tous les textes trouvés
            texts = [result[1] for result in results if result[2] > 0.5]  # Confiance > 50%
            return ' '.join(texts)
            
        except Exception as e:
            print(f"[OCR ERROR] EasyOCR: {e}")
            return ""
    
    def extract_text_detailed_easyocr(self, image: Image.Image) -> List[Dict]:
        """Extraction détaillée avec positions (EasyOCR)"""
        if not self.easyocr_available or not self.easyocr_reader:
            return []
        
        try:
            image_array = np.array(image)
            results = self.easyocr_reader.readtext(image_array)
            
            detailed_results = []
            for result in results:
                bbox, text, confidence = result
                
                # Calculer position rectangle
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                detailed_results.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox,
                    'x': min(x_coords),
                    'y': min(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords)
                })
            
            return detailed_results
            
        except Exception as e:
            print(f"[OCR ERROR] EasyOCR détaillé: {e}")
            return []
    
    def extract_text_auto(self, image: Image.Image) -> str:
        """Extraction automatique avec le meilleur moteur disponible"""
        # Essayer EasyOCR en premier (généralement plus précis)
        if self.easyocr_available:
            text = self.extract_text_easyocr(image)
            if text.strip():
                return text
        
        # Fallback sur Tesseract
        if self.tesseract_available:
            text = self.extract_text_tesseract(image)
            if text.strip():
                return text
        
        return "Aucun texte détecté"
    
    def preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Prétraitement d'image pour améliorer l'OCR"""
        try:
            # Convertir en numpy pour traitement
            img_array = np.array(image)
            
            # Convertir en niveaux de gris si couleur
            if len(img_array.shape) == 3:
                # Méthode simple de conversion
                gray_array = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
                gray_array = gray_array.astype(np.uint8)
            else:
                gray_array = img_array
            
            # Augmenter le contraste (simple)
            # Méthode basique sans OpenCV
            contrast_enhanced = np.clip(gray_array * 1.2, 0, 255).astype(np.uint8)
            
            # Reconvertir en PIL
            processed_image = Image.fromarray(contrast_enhanced, mode='L')
            
            # Redimensionner si trop petit (améliore OCR)
            width, height = processed_image.size
            if width < 300 or height < 100:
                scale_factor = max(300/width, 100/height, 2.0)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                processed_image = processed_image.resize(new_size, Image.Resampling.LANCZOS)
            
            return processed_image
            
        except Exception as e:
            print(f"[OCR ERROR] Prétraitement: {e}")
            return image
    
    def find_text_in_image(self, image: Image.Image, search_text: str, case_sensitive=False) -> List[Dict]:
        """Trouve du texte spécifique dans une image"""
        try:
            # Extraire tout le texte avec positions
            detailed_results = self.extract_text_detailed_easyocr(image)
            
            if not detailed_results and self.tesseract_available:
                # Fallback Tesseract (sans positions précises)
                full_text = self.extract_text_tesseract(image)
                if search_text.lower() in full_text.lower():
                    return [{'text': full_text, 'found': True, 'x': 0, 'y': 0}]
                else:
                    return []
            
            # Rechercher dans les résultats détaillés
            matches = []
            for result in detailed_results:
                text = result['text']
                if not case_sensitive:
                    text = text.lower()
                    search_text = search_text.lower()
                
                if search_text in text:
                    result['found'] = True
                    matches.append(result)
            
            return matches
            
        except Exception as e:
            print(f"[OCR ERROR] Recherche texte: {e}")
            return []
    
    def extract_structured_data(self, image: Image.Image) -> Dict:
        """Extrait des données structurées (emails, URLs, numéros)"""
        text = self.extract_text_auto(image)
        
        if not text:
            return {}
        
        # Patterns de regex
        patterns = {
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'urls': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'phones': r'(?:\+33|0)[1-9](?:[0-9]{8})',
            'numbers': r'\b\d+(?:[.,]\d+)?\b'
        }
        
        structured_data = {}
        for data_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                structured_data[data_type] = matches
        
        # Ajouter le texte brut
        structured_data['raw_text'] = text
        
        return structured_data
    
    def get_ocr_info(self) -> Dict:
        """Informations sur les moteurs OCR disponibles"""
        info = {
            'tesseract_available': self.tesseract_available,
            'easyocr_available': self.easyocr_available,
            'recommended_engine': 'EasyOCR' if self.easyocr_available else 'Tesseract' if self.tesseract_available else 'Aucun'
        }
        
        if self.tesseract_available:
            try:
                info['tesseract_version'] = pytesseract.get_tesseract_version()
            except:
                pass
        
        return info


# Instance globale
ocr_engine = OCREngine()
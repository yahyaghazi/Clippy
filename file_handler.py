# file_handler.py
"""Gestionnaire pour l'extraction de contenu des fichiers"""

import PyPDF2
from docx import Document
import pandas as pd
from pptx import Presentation
import openpyxl
import base64
from PIL import Image
import re
import hashlib
from config import IMAGE_EXTENSIONS, IMAGE_MIME_TYPES

class FileHandler:
    """Classe pour gérer l'extraction de contenu des fichiers"""
    
    @staticmethod
    def extract_text(file):
        """Extrait le texte des fichiers uploadés avec support complet Office + Images"""
        try:
            file_type = file.type.lower()
            file_name = file.name.lower()
            
            # Images - retourner les métadonnées
            if FileHandler.is_image_file(file):
                return FileHandler._extract_image_metadata(file)
            
            # PDF
            elif file_type == "application/pdf":
                return FileHandler._extract_pdf_text(file)
            
            # Word Documents (.docx)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return FileHandler._extract_docx_text(file)
            
            # Word Documents anciens (.doc)
            elif file_name.endswith('.doc'):
                return FileHandler._extract_doc_text(file)
            
            # Excel Files (.xlsx)
            elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                return FileHandler._extract_xlsx_text(file)
            
            # Excel anciens (.xls)
            elif file_name.endswith('.xls'):
                return FileHandler._extract_xls_text(file)
            
            # PowerPoint (.pptx)
            elif file_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                return FileHandler._extract_pptx_text(file)
            
            # PowerPoint ancien (.ppt)
            elif file_name.endswith('.ppt'):
                return "Format .ppt non supporté. Veuillez convertir en .pptx"
            
            # CSV
            elif file_type == "text/csv" or file_name.endswith('.csv'):
                return FileHandler._extract_csv_text(file)
            
            # RTF
            elif file_name.endswith('.rtf'):
                return FileHandler._extract_rtf_text(file)
            
            # Texte plain
            elif file_type == "text/plain":
                return file.read().decode("utf-8")
            
            else:
                return f"Type de fichier non supporté: {file_type}"
                
        except Exception as e:
            return f"Erreur lors de l'extraction: {str(e)}"
    
    @staticmethod
    def _extract_image_metadata(file):
        """Extrait les métadonnées d'une image"""
        try:
            image = Image.open(file)
            info = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "filename": file.name
            }
            
            metadata_text = f"""Image: {info['filename']}
Format: {info['format']}
Dimensions: {info['size'][0]} x {info['size'][1]} pixels
Mode couleur: {info['mode']}
Taille fichier: {FileHandler.format_file_size(file.size)}
"""
            return metadata_text
        except Exception as e:
            return f"Erreur lecture image: {str(e)}"
    
    @staticmethod
    def _extract_pdf_text(file):
        """Extrait le texte d'un fichier PDF"""
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text() or ""
            except Exception as e:
                text += f"\n[Erreur lecture page {page_num + 1}: {str(e)}]\n"
        return text
    
    @staticmethod
    def _extract_docx_text(file):
        """Extrait le texte d'un fichier Word .docx"""
        doc = Document(file)
        text = ""
        
        # Extraire les paragraphes
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        
        # Extraire le texte des tableaux
        for table in doc.tables:
            text += "\n--- Tableau ---\n"
            for row in table.rows:
                row_text = " | ".join([cell.text for cell in row.cells])
                text += row_text + "\n"
        
        return text
    
    @staticmethod
    def _extract_doc_text(file):
        """Extraction basique pour les fichiers .doc (format binaire ancien)"""
        try:
            content = file.read()
            text = content.decode('utf-8', errors='ignore')
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
            words = [word for word in text.split() if len(word) > 1 and word.isascii()]
            return ' '.join(words[:1000])  # Limiter à 1000 mots
        except:
            return "Impossible d'extraire le texte du fichier .doc. Utilisez le format .docx."
    
    @staticmethod
    def _extract_xlsx_text(file):
        """Extrait le texte d'un fichier Excel .xlsx"""
        workbook = openpyxl.load_workbook(file, data_only=True)
        text = ""
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            text += f"\n--- Feuille: {sheet_name} ---\n"
            
            for row in sheet.iter_rows(values_only=True):
                if any(cell is not None for cell in row):
                    row_text = " | ".join([str(cell) if cell is not None else "" for cell in row])
                    text += row_text + "\n"
        
        workbook.close()
        return text
    
    @staticmethod
    def _extract_xls_text(file):
        """Extrait le texte d'un fichier Excel .xls"""
        try:
            excel_data = pd.read_excel(file, sheet_name=None, engine='xlrd')
            text = ""
            
            for sheet_name, df in excel_data.items():
                text += f"\n--- Feuille: {sheet_name} ---\n"
                text += df.to_string(index=False) + "\n"
            
            return text
        except Exception as e:
            return f"Erreur lecture fichier Excel .xls: {str(e)}"
    
    @staticmethod
    def _extract_pptx_text(file):
        """Extrait le texte d'un fichier PowerPoint .pptx"""
        prs = Presentation(file)
        text = ""
        
        for slide_num, slide in enumerate(prs.slides, 1):
            text += f"\n--- Diapositive {slide_num} ---\n"
            
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text += shape.text + "\n"
                
                # Extraire le texte des tableaux
                if hasattr(shape, 'has_table') and shape.has_table:
                    text += "\n[Tableau]\n"
                    for row in shape.table.rows:
                        row_text = " | ".join([cell.text for cell in row.cells])
                        text += row_text + "\n"
        
        return text
    
    @staticmethod
    def _extract_csv_text(file):
        """Extrait le contenu d'un fichier CSV"""
        df = pd.read_csv(file, encoding='utf-8')
        return f"Fichier CSV avec {len(df)} lignes et {len(df.columns)} colonnes:\n\n" + df.to_string()
    
    @staticmethod
    def _extract_rtf_text(file):
        """Extrait le texte d'un fichier RTF"""
        content = file.read().decode('utf-8', errors='ignore')
        # Extraction basique RTF (enlever les balises)
        text = re.sub(r'\\[a-z]+\d*\s?', '', content)
        text = re.sub(r'[{}]', '', text)
        return text.strip()
    
    @staticmethod
    def is_image_file(file):
        """Vérifie si le fichier est une image"""
        return any(ext in file.type.lower() for ext in IMAGE_MIME_TYPES) or \
               any(file.name.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)
    
    @staticmethod
    def encode_image_to_base64(file):
        """Encode une image en base64 pour l'API Ollama"""
        return base64.b64encode(file.getvalue()).decode('utf-8')
    
    @staticmethod
    def get_file_hash(file):
        """Génère un hash unique pour éviter les re-traitements"""
        return hashlib.md5(file.getvalue()).hexdigest()
    
    @staticmethod
    def format_file_size(size_bytes):
        """Formate la taille du fichier de manière lisible"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024**2):.1f} MB"
    
    @staticmethod
    def get_file_type_emoji(file_type, file_name):
        """Retourne l'emoji approprié selon le type de fichier"""
        if "image" in file_type or any(file_name.endswith(ext) for ext in IMAGE_EXTENSIONS):
            return "🖼️"
        elif "pdf" in file_type:
            return "📄"
        elif "word" in file_type or file_name.endswith(('.doc', '.docx')):
            return "📝"
        elif "excel" in file_type or "spreadsheet" in file_type or file_name.endswith(('.xls', '.xlsx')):
            return "📊"
        elif "powerpoint" in file_type or "presentation" in file_type or file_name.endswith(('.ppt', '.pptx')):
            return "📊"
        elif "csv" in file_type or file_name.endswith('.csv'):
            return "📋"
        elif file_name.endswith('.rtf'):
            return "📝"
        else:
            return "📄"
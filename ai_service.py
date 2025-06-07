# ai_service.py
"""Service pour gérer les interactions avec l'IA Ollama"""

import ollama
from file_handler import FileHandler

class AIService:
    """Classe pour gérer les interactions avec l'IA"""
    
    @staticmethod
    def generate_multi_file_analysis_prompt(files_content, user_question):
        """Génère le prompt pour l'analyse multi-fichiers"""
        prompt = f"""Tu es un assistant IA spécialisé dans l'analyse de documents multiples. 
        
Question de l'utilisateur: {user_question}

Je vais te fournir plusieurs documents à analyser. Pour chaque document, je t'indiquerai son nom et son contenu.

Documents à analyser:

"""
        
        for i, (filename, content, file_type) in enumerate(files_content, 1):
            prompt += f"""
=== DOCUMENT {i}: {filename} ===
Type: {file_type}
Contenu:
{content}

"""
        
        prompt += f"""
=== ANALYSE DEMANDÉE ===
Question: {user_question}

Instructions:
1. Analyse chaque document individuellement
2. Identifie les liens et corrélations entre les documents
3. Réponds à la question en utilisant les informations de TOUS les documents
4. Cite tes sources en mentionnant les noms des fichiers
5. Structure ta réponse de manière claire et logique

Réponds de manière complète et détaillée en utilisant toutes les informations pertinentes des documents fournis."""
        
        return prompt
    
    @staticmethod
    def generate_file_analysis_prompt(file_ext, is_image=False):
        """Génère le prompt approprié selon le type de fichier"""
        
        if is_image:
            return """Analyse cette image en détail et fournis:
            1. Description générale de l'image
            2. Éléments principaux visibles
            3. Couleurs dominantes et composition
            4. Contexte et ambiance
            5. Détails techniques si pertinents
            6. Suggestions d'utilisation ou d'amélioration"""
        
        elif file_ext in ['xlsx', 'xls', 'csv']:
            return """Analyse ce fichier de données et fournis:
            1. Structure et organisation des données
            2. Statistiques descriptives importantes
            3. Tendances ou patterns observés
            4. Résumé des informations clés
            5. Suggestions d'analyses complémentaires
            
            Contenu du fichier:
            {content}"""
        
        elif file_ext in ['pptx', 'ppt']:
            return """Analyse cette présentation et fournis:
            1. Structure et nombre de diapositives
            2. Thèmes et messages principaux
            3. Points clés de chaque section
            4. Résumé exécutif
            5. Suggestions d'amélioration
            
            Contenu de la présentation:
            {content}"""
        
        else:
            return """Analyse ce document et fournis un résumé détaillé incluant:
            1. Le type et la structure du document
            2. Les points clés et informations importantes
            3. Un résumé concis
            4. Des suggestions de questions pertinentes à poser
            
            Document:
            {content}"""
    
    @staticmethod
    def analyze_multiple_files(files_data, user_question, selected_model, temperature, max_tokens):
        """Analyse plusieurs fichiers avec une question globale"""
        try:
            # Préparer le contenu de tous les fichiers
            files_content = []
            has_image = False
            
            for file_data in files_data:
                filename = file_data['filename']
                content = file_data['content']
                is_image = file_data['is_image']
                file_type = file_data['file_type']
                
                if is_image:
                    has_image = True
                    # Pour les images, on utilise les métadonnées comme contenu textuel
                    files_content.append((filename, content, "Image"))
                else:
                    files_content.append((filename, content, file_type))
            
            # Générer le prompt global
            prompt = AIService.generate_multi_file_analysis_prompt(files_content, user_question)
            
            # Si il y a des images et que LlaVa n'est pas utilisé, on fait un avertissement
            if has_image and selected_model != "llava":
                warning_msg = "⚠️ Certains fichiers sont des images. Pour une analyse optimale, utilisez le modèle LlaVa."
                return f"{warning_msg}\n\n" + AIService._call_ollama(prompt, selected_model, temperature, max_tokens)
            
            return AIService._call_ollama(prompt, selected_model, temperature, max_tokens)
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'analyse multi-fichiers: {str(e)}")
    
    @staticmethod
    def analyze_file(uploaded_file, content, selected_model, temperature, max_tokens):
        """Analyse un fichier avec l'IA appropriée"""
        try:
            is_image = FileHandler.is_image_file(uploaded_file)
            file_ext = uploaded_file.name.split('.')[-1].lower()
            
            # Générer le prompt approprié
            prompt_template = AIService.generate_file_analysis_prompt(file_ext, is_image)
            
            if is_image:
                # Traitement spécial pour les images
                uploaded_file.seek(0)  # Reset file pointer
                image_base64 = FileHandler.encode_image_to_base64(uploaded_file)
                
                result = ollama.chat(
                    model=selected_model,
                    messages=[{
                        "role": "user", 
                        "content": prompt_template,
                        "images": [image_base64]
                    }],
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                )
            else:
                # Traitement pour les documents
                prompt = prompt_template.format(content=content)
                result = ollama.chat(
                    model=selected_model,
                    messages=[{"role": "user", "content": prompt}],
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                )
            
            return result["message"]["content"]
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'analyse: {str(e)}")
    
    @staticmethod
    def _call_ollama(prompt, selected_model, temperature, max_tokens):
        """Appel générique à Ollama"""
        result = ollama.chat(
            model=selected_model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )
        return result["message"]["content"]
    
    @staticmethod
    def chat_with_ai(messages, selected_model, temperature, max_tokens):
        """Gère la conversation avec l'IA"""
        try:
            # Nettoyer les messages pour l'API (enlever les métadonnées)
            context_messages = []
            for msg in messages[-10:]:  # Garder seulement les 10 derniers messages
                clean_msg = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                context_messages.append(clean_msg)
            
            result = ollama.chat(
                model=selected_model,
                messages=context_messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )
            
            return result["message"]["content"]
            
        except Exception as e:
            raise Exception(f"Erreur communication IA: {str(e)}")
    
    @staticmethod
    def validate_model_for_content(selected_model, has_images):
        """Valide si le modèle sélectionné est approprié pour le contenu"""
        warnings = []
        
        if has_images and selected_model != "llava":
            warnings.append("Pour une analyse optimale des images, utilisez le modèle LlaVa")
        
        return warnings
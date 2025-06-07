# ai_service.py
"""Service pour gérer les interactions avec l'IA Ollama"""

import ollama
from file_handler import FileHandler
import time

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
            # Limiter la taille du contenu pour éviter les prompts trop longs
            truncated_content = content[:5000] if len(content) > 5000 else content
            if len(content) > 5000:
                truncated_content += "\n[...contenu tronqué...]"
            
            prompt += f"""
=== DOCUMENT {i}: {filename} ===
Type: {file_type}
Contenu:
{truncated_content}

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
6. Si certains contenus sont tronqués, indique-le dans ta réponse

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
            6. Suggestions d'utilisation ou d'amélioration
            
            Sois précis et détaillé dans ta description."""
        
        elif file_ext in ['xlsx', 'xls', 'csv']:
            return """Analyse ce fichier de données et fournis:
            1. Structure et organisation des données
            2. Statistiques descriptives importantes
            3. Tendances ou patterns observés
            4. Résumé des informations clés
            5. Suggestions d'analyses complémentaires
            6. Points d'attention ou anomalies détectées
            
            Contenu du fichier:
            {content}"""
        
        elif file_ext in ['pptx', 'ppt']:
            return """Analyse cette présentation et fournis:
            1. Structure et nombre de diapositives
            2. Thèmes et messages principaux
            3. Points clés de chaque section
            4. Résumé exécutif
            5. Cohérence et flow de la présentation
            6. Suggestions d'amélioration
            
            Contenu de la présentation:
            {content}"""
        
        elif file_ext in ['docx', 'doc']:
            return """Analyse ce document Word et fournis:
            1. Type et structure du document
            2. Thèmes principaux abordés
            3. Points clés et arguments principaux
            4. Résumé concis
            5. Style et ton du document
            6. Suggestions de questions pertinentes à poser
            
            Document:
            {content}"""
        
        elif file_ext == 'pdf':
            return """Analyse ce document PDF et fournis:
            1. Nature et type du document
            2. Structure et organisation
            3. Points clés et informations importantes
            4. Résumé synthétique
            5. Éléments remarquables
            6. Suggestions de questions pertinentes
            
            Document:
            {content}"""
        
        else:
            return """Analyse ce document et fournis un résumé détaillé incluant:
            1. Le type et la structure du document
            2. Les points clés et informations importantes
            3. Un résumé concis
            4. Le contexte et l'objectif apparent
            5. Des suggestions de questions pertinentes à poser
            
            Document:
            {content}"""
    
    @staticmethod
    def analyze_multiple_files(files_data, user_question, selected_model, temperature, max_tokens):
        """Analyse plusieurs fichiers avec une question globale"""
        try:
            # Vérifier que Ollama est disponible
            if not AIService._check_ollama_connection():
                raise Exception("Impossible de se connecter à Ollama. Vérifiez que le service est démarré.")
            
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
                    files_content.append((filename, content, "Image"))
                else:
                    files_content.append((filename, content, file_type))
            
            # Générer le prompt global
            prompt = AIService.generate_multi_file_analysis_prompt(files_content, user_question)
            
            # Validation du modèle pour les images
            if has_image and selected_model.lower() != "llava":
                warning_msg = "⚠️ Certains fichiers sont des images. Pour une analyse optimale, utilisez le modèle LlaVa.\n\n"
            else:
                warning_msg = ""
            
            # Appel à l'IA
            response = AIService._call_ollama_with_retry(prompt, selected_model, temperature, max_tokens)
            return warning_msg + response
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'analyse multi-fichiers: {str(e)}")
    
    @staticmethod
    def analyze_file(uploaded_file, content, selected_model, temperature, max_tokens):
        """Analyse un fichier avec l'IA appropriée"""
        try:
            # Vérifier que Ollama est disponible
            if not AIService._check_ollama_connection():
                raise Exception("Impossible de se connecter à Ollama. Vérifiez que le service est démarré.")
            
            is_image = FileHandler.is_image_file(uploaded_file)
            file_ext = uploaded_file.name.split('.')[-1].lower() if uploaded_file.name else 'txt'
            
            # Générer le prompt approprié
            prompt_template = AIService.generate_file_analysis_prompt(file_ext, is_image)
            
            if is_image:
                # Traitement spécial pour les images avec LlaVa
                if selected_model.lower() != "llava":
                    return "⚠️ Pour analyser les images, veuillez utiliser le modèle LlaVa."
                
                uploaded_file.seek(0)
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
                # Limiter la taille du contenu
                truncated_content = content[:8000] if len(content) > 8000 else content
                if len(content) > 8000:
                    truncated_content += "\n[...contenu tronqué pour l'analyse...]"
                
                prompt = prompt_template.format(content=truncated_content)
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
            if "model" in str(e).lower() and "not found" in str(e).lower():
                raise Exception(f"Le modèle '{selected_model}' n'est pas disponible. Vérifiez qu'il est installé dans Ollama.")
            else:
                raise Exception(f"Erreur lors de l'analyse: {str(e)}")
    
    @staticmethod
    def _call_ollama_with_retry(prompt, selected_model, temperature, max_tokens, max_retries=3):
        """Appel à Ollama avec retry en cas d'erreur"""
        for attempt in range(max_retries):
            try:
                return AIService._call_ollama(prompt, selected_model, temperature, max_tokens)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1)  # Attendre 1 seconde avant de réessayer
    
    @staticmethod
    def _call_ollama(prompt, selected_model, temperature, max_tokens):
        """Appel générique à Ollama"""
        try:
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
            if "connection" in str(e).lower():
                raise Exception("Impossible de se connecter à Ollama. Vérifiez que le service est démarré.")
            elif "model" in str(e).lower():
                raise Exception(f"Erreur avec le modèle '{selected_model}': {str(e)}")
            else:
                raise e
    
    @staticmethod
    def _check_ollama_connection():
        """Vérifie si Ollama est accessible"""
        try:
            # Essayer de lister les modèles pour vérifier la connexion
            ollama.list()
            return True
        except Exception:
            return False
    
    @staticmethod
    def chat_with_ai(messages, selected_model, temperature, max_tokens):
        """Gère la conversation avec l'IA"""
        try:
            # Vérifier que Ollama est disponible
            if not AIService._check_ollama_connection():
                raise Exception("Impossible de se connecter à Ollama. Vérifiez que le service est démarré.")
            
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
            if "model" in str(e).lower() and "not found" in str(e).lower():
                raise Exception(f"Le modèle '{selected_model}' n'est pas disponible. Vérifiez qu'il est installé dans Ollama.")
            else:
                raise Exception(f"Erreur communication IA: {str(e)}")
    
    @staticmethod
    def validate_model_for_content(selected_model, has_images):
        """Valide si le modèle sélectionné est approprié pour le contenu"""
        warnings = []
        
        if has_images and selected_model.lower() != "llava":
            warnings.append("Pour une analyse optimale des images, utilisez le modèle LlaVa")
        
        return warnings
    
    @staticmethod
    def get_available_models():
        """Récupère la liste des modèles disponibles dans Ollama"""
        try:
            models = ollama.list()
            return [model['name'] for model in models['models']]
        except Exception:
            # Retourner les modèles par défaut si Ollama n'est pas accessible
            return ["llama3", "mistral", "codellama", "gemma", "llava"]
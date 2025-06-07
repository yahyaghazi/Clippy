# ui_components.py
"""Composants d'interface utilisateur pour Streamlit"""

import streamlit as st
import json
from datetime import datetime
from PIL import Image
import io
from config import MODEL_INFO, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS, DEFAULT_MODEL_INDEX, HELP_MESSAGES
from file_handler import FileHandler

class UIComponents:
    """Classe pour gérer les composants d'interface utilisateur"""
    
    @staticmethod
    def setup_sidebar():
        """Configure la barre latérale avec tous les contrôles"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Sélection du modèle
            selected_model = st.selectbox(
                "🧠 Choisis ton modèle IA :",
                options=list(MODEL_INFO.keys()),
                format_func=lambda x: MODEL_INFO[x],
                index=DEFAULT_MODEL_INDEX,
                help="Choisissez LlaVa pour analyser des images"
            )
            st.session_state["model"] = selected_model
            
            # Paramètres avancés
            with st.expander("🎛️ Paramètres avancés"):
                temperature = st.slider("Créativité", 0.0, 1.0, DEFAULT_TEMPERATURE, 0.1)
                max_tokens = st.slider("Longueur max réponse", 100, 3000, DEFAULT_MAX_TOKENS, 100)
            
            # Statistiques de session
            UIComponents._display_session_stats()
            
            # Boutons d'action
            UIComponents._display_action_buttons(selected_model)
            
            return selected_model, temperature, max_tokens
    
    @staticmethod
    def _display_session_stats():
        """Affiche les statistiques de la session"""
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.subheader("📊 Statistiques")
        
        if "messages" in st.session_state and st.session_state["messages"]:
            msg_count = len([m for m in st.session_state["messages"] if m["role"] == "user"])
            st.write(f"Messages envoyés: {msg_count}")
            if msg_count > 0:
                st.write(f"Dernier message: {datetime.now().strftime('%H:%M')}")
        else:
            st.write("Aucun message encore")
        
        # Statistiques des fichiers en attente
        if "pending_files" in st.session_state and st.session_state["pending_files"]:
            st.write(f"📁 Fichiers en attente: {len(st.session_state['pending_files'])}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _display_action_buttons(selected_model):
        """Affiche les boutons d'action"""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Vider", help="Vider l'historique"):
                st.session_state["messages"] = []
                if "pending_files" in st.session_state:
                    st.session_state["pending_files"] = []
                st.rerun()
        
        with col2:
            if st.button("💾 Sauver", help="Sauvegarder la conversation"):
                UIComponents._handle_save_conversation(selected_model)
    
    @staticmethod
    def _handle_save_conversation(selected_model):
        """Gère la sauvegarde de la conversation"""
        if "messages" in st.session_state and st.session_state["messages"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            
            # Préparer les données à sauvegarder (sans les données d'image)
            save_messages = []
            for msg in st.session_state["messages"]:
                clean_msg = {k: v for k, v in msg.items() if k not in ["image_data", "file_object"]}
                save_messages.append(clean_msg)
            
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "model": selected_model,
                "messages": save_messages
            }
            
            st.download_button(
                label="📥 Télécharger JSON",
                data=json.dumps(save_data, indent=2, ensure_ascii=False),
                file_name=filename,
                mime="application/json"
            )
        else:
            st.warning("Aucune conversation à sauvegarder")
    
    @staticmethod
    def display_multi_file_upload():
        """Affiche la zone d'upload multiple de fichiers"""
        from config import SUPPORTED_FILE_TYPES, HELP_MESSAGES
        
        st.markdown("### 📂 Upload de documents")
        st.info(HELP_MESSAGES["multi_upload"])
        
        uploaded_files = st.file_uploader(
            "📎 Sélectionnez vos fichiers",
            type=SUPPORTED_FILE_TYPES,
            help=HELP_MESSAGES["file_formats"],
            accept_multiple_files=True
        )
        
        return uploaded_files
    
    @staticmethod
    def display_pending_files():
        """Affiche les fichiers en attente d'analyse"""
        if "pending_files" not in st.session_state:
            st.session_state["pending_files"] = []
        
        if st.session_state["pending_files"]:
            st.markdown('<div class="pending-files">', unsafe_allow_html=True)
            st.markdown("### 📁 Fichiers en attente d'analyse")
            st.info(HELP_MESSAGES["pending_files"])
            
            # Afficher la liste des fichiers
            for i, file_data in enumerate(st.session_state["pending_files"]):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    emoji = FileHandler.get_file_type_emoji("", file_data['filename'])
                    st.write(f"{emoji} **{file_data['filename']}** ({file_data['size']})")
                
                with col2:
                    file_ext = file_data['filename'].split('.')[-1].upper()
                    st.write(f"📝 {file_ext}")
                
                with col3:
                    if st.button("🗑️", key=f"remove_{i}", help="Supprimer ce fichier"):
                        st.session_state["pending_files"].pop(i)
                        st.rerun()
            
            # Bouton pour vider tous les fichiers
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🗑️ Vider tous", type="secondary"):
                    st.session_state["pending_files"] = []
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            return True
        
        return False
    
    @staticmethod
    def display_file_upload():
        """Affiche la zone d'upload de fichier simple (conservée pour compatibilité)"""
        from config import SUPPORTED_FILE_TYPES, HELP_MESSAGES
        
        uploaded_file = st.file_uploader(
            "📎 Upload de document ou image",
            type=SUPPORTED_FILE_TYPES,
            help=HELP_MESSAGES["file_formats"]
        )
        
        if uploaded_file:
            UIComponents._display_file_info(uploaded_file)
            
            # Affichage spécial pour les images
            if FileHandler.is_image_file(uploaded_file):
                UIComponents._display_image_preview(uploaded_file)
        
        return uploaded_file
    
    @staticmethod
    def _display_file_info(uploaded_file):
        """Affiche les informations du fichier uploadé"""
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            emoji = FileHandler.get_file_type_emoji(uploaded_file.type, uploaded_file.name)
            st.write(f"{emoji} **{uploaded_file.name}**")
        
        with col2:
            file_size = getattr(uploaded_file, 'size', 0)
            st.write(f"📊 {FileHandler.format_file_size(file_size)}")
        
        with col3:
            file_ext = uploaded_file.name.split('.')[-1].upper() if uploaded_file.name else "???"
            st.write(f"📝 {file_ext}")
        
        with col4:
            UIComponents._display_file_size_indicator(file_size)
    
    @staticmethod
    def _display_file_size_indicator(file_size):
        """Affiche l'indicateur de taille de fichier"""
        if file_size > 5*1024*1024:  # > 5MB
            st.write("🔴 Gros")
        elif file_size > 1024*1024:  # > 1MB
            st.write("🟡 Moyen")
        else:
            st.write("🟢 Léger")
    
    @staticmethod
    def _display_image_preview(uploaded_file):
        """Affiche l'aperçu d'une image"""
        st.info(HELP_MESSAGES["image_model_suggestion"])
        try:
            uploaded_file.seek(0)
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Aperçu: {uploaded_file.name}", width=400)
        except Exception as e:
            st.error(f"Impossible d'afficher l'image: {e}")
    
    @staticmethod
    def display_chat_history():
        """Affiche l'historique des messages"""
        if "messages" not in st.session_state:
            st.session_state["messages"] = []
        
        chat_container = st.container()
        with chat_container:
            for i, msg in enumerate(st.session_state["messages"]):
                with st.chat_message(msg["role"]):
                    if msg["role"] == "user" and msg.get("file_info"):
                        UIComponents._display_file_message(msg, i)
                    elif msg["role"] == "user" and msg.get("multi_files"):
                        UIComponents._display_multi_file_message(msg, i)
                    else:
                        st.markdown(msg["content"])
    
    @staticmethod
    def _display_file_message(msg, index):
        """Affiche un message contenant un fichier"""
        file_info = msg["file_info"]
        emoji = FileHandler.get_file_type_emoji(
            file_info.get("type", ""), 
            file_info.get("name", "")
        )
        st.markdown(f"{emoji} **Fichier:** {file_info['name']} ({file_info['size']})")
        
        # Affichage spécial pour les images
        if msg.get("is_image") and msg.get("image_data"):
            try:
                st.image(msg["image_data"], caption=file_info['name'], width=300)
            except Exception as e:
                st.error(f"Erreur affichage image: {e}")
        
        # Bouton pour voir les détails
        with st.expander(f"Voir détails du fichier"):
            if msg.get("is_image"):
                st.text_area("Métadonnées de l'image:", msg["content"], height=150, key=f"details_{index}")
            else:
                preview_content = msg["content"][:500]
                if len(msg["content"]) > 500:
                    preview_content += "..."
                st.text_area("Extrait du fichier:", preview_content, height=100, key=f"details_{index}")
    
    @staticmethod
    def _display_multi_file_message(msg, index):
        """Affiche un message contenant plusieurs fichiers"""
        files_info = msg["multi_files"]
        user_question = msg.get("user_question", "Analyse globale")
        
        st.markdown(f"🔍 **Question:** {user_question}")
        st.markdown(f"📁 **Fichiers analysés:** {len(files_info)}")
        
        # Afficher la liste des fichiers
        with st.expander(f"Voir les {len(files_info)} fichiers"):
            for file_info in files_info:
                emoji = FileHandler.get_file_type_emoji("", file_info['filename'])
                st.write(f"{emoji} {file_info['filename']} ({file_info['size']})")
    
    @staticmethod
    def display_warnings(warnings):
        """Affiche les avertissements"""
        for warning in warnings:
            st.warning(f"⚠️ {warning}")
    
    @staticmethod
    def display_error(error_msg, has_images=False, selected_model=""):
        """Affiche les messages d'erreur avec suggestions"""
        st.error(f"❌ {error_msg}")
        
        if has_images and selected_model.lower() != "llava":
            st.info(HELP_MESSAGES["llava_suggestion"])
        elif "connection" in error_msg.lower() or "ollama" in error_msg.lower():
            st.info(HELP_MESSAGES["ollama_check"])
        elif "model" in error_msg.lower():
            st.info("💡 Vérifiez que le modèle sélectionné est installé dans Ollama")
    
    @staticmethod
    def create_user_message(uploaded_file, content, file_hash):
        """Crée un message utilisateur à partir d'un fichier"""
        is_image = FileHandler.is_image_file(uploaded_file)
        
        file_size = getattr(uploaded_file, 'size', 0)
        file_info = {
            "name": uploaded_file.name,
            "size": FileHandler.format_file_size(file_size),
            "type": getattr(uploaded_file, 'type', '')
        }
        
        user_msg = {
            "role": "user",
            "content": f"Analyse ce {'image' if is_image else 'document'}:\n\n{content}",
            "file_info": file_info,
            "file_hash": file_hash,
            "is_image": is_image
        }
        
        # Ajouter l'image pour l'affichage si c'est une image
        if is_image:
            try:
                uploaded_file.seek(0)
                image = Image.open(uploaded_file)
                user_msg["image_data"] = image
            except Exception as e:
                st.error(f"Erreur chargement image: {e}")
        
        return user_msg
    
    @staticmethod
    def create_multi_file_message(files_data, user_question):
        """Crée un message utilisateur pour l'analyse multi-fichiers"""
        files_info = []
        
        for file_data in files_data:
            files_info.append({
                "filename": file_data['filename'],
                "size": file_data['size'],
                "file_type": file_data['file_type']
            })
        
        user_msg = {
            "role": "user",
            "content": f"Analyse croisée de {len(files_data)} fichiers avec la question: {user_question}",
            "multi_files": files_info,
            "user_question": user_question
        }
        
        return user_msg
    
    @staticmethod
    def process_uploaded_files(uploaded_files):
        """Traite les fichiers uploadés et les ajoute à la liste d'attente"""
        if not uploaded_files:
            return
        
        if "pending_files" not in st.session_state:
            st.session_state["pending_files"] = []
        
        # Obtenir les noms des fichiers déjà en attente
        existing_files = {f['filename'] for f in st.session_state["pending_files"]}
        
        new_files_added = 0
        errors = []
        
        for uploaded_file in uploaded_files:
            try:
                # Éviter les doublons
                if uploaded_file.name not in existing_files:
                    file_hash = FileHandler.get_file_hash(uploaded_file)
                    is_image = FileHandler.is_image_file(uploaded_file)
                    
                    # Extraire le contenu
                    uploaded_file.seek(0)
                    content = FileHandler.extract_text(uploaded_file)
                    
                    file_size = getattr(uploaded_file, 'size', 0)
                    
                    file_data = {
                        "filename": uploaded_file.name,
                        "size": FileHandler.format_file_size(file_size),
                        "content": content,
                        "is_image": is_image,
                        "file_type": uploaded_file.name.split('.')[-1].upper() if uploaded_file.name else "???",
                        "file_hash": file_hash
                    }
                    
                    st.session_state["pending_files"].append(file_data)
                    existing_files.add(uploaded_file.name)
                    new_files_added += 1
                    
            except Exception as e:
                errors.append(f"Erreur avec {uploaded_file.name}: {str(e)}")
        
        # Afficher les résultats
        if new_files_added > 0:
            st.success(f"✅ {new_files_added} fichier(s) ajouté(s) à l'analyse")
        
        if errors:
            for error in errors:
                st.error(error)
        
        if new_files_added > 0:
            st.rerun()
    
    @staticmethod
    def display_analysis_input():
        """Affiche la zone de saisie pour l'analyse globale"""
        if "pending_files" in st.session_state and st.session_state["pending_files"]:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 🔍 Analyse globale")
            
            analysis_question = st.text_area(
                "Posez votre question sur l'ensemble des documents:",
                placeholder="Ex: Quels sont les points communs entre ces documents ? Résumez les informations principales...",
                height=100
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("🚀 Lancer l'analyse globale", type="primary"):
                    if analysis_question.strip():
                        return analysis_question.strip()
                    else:
                        st.warning("⚠️ Veuillez saisir une question pour l'analyse")
            
            with col2:
                if st.button("📋 Suggestions"):
                    suggestions = [
                        "Résumez les points clés de tous les documents",
                        "Quelles sont les corrélations entre ces documents ?",
                        "Identifiez les contradictions ou divergences",
                        "Créez une synthèse comparative",
                        "Quelles sont les recommandations principales ?"
                    ]
                    st.write("💡 **Questions suggérées:**")
                    for i, suggestion in enumerate(suggestions):
                        if st.button(f"• {suggestion}", key=f"sugg_{i}"):
                            return suggestion
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        return None
    
    @staticmethod
    def initialize_session_state():
        """Initialise les variables de session state"""
        if "messages" not in st.session_state:
            st.session_state["messages"] = []
        
        if "pending_files" not in st.session_state:
            st.session_state["pending_files"] = []
# main.py
"""Application principale Streamlit pour l'assistant IA avec support multi-fichiers"""

import streamlit as st
from file_handler import FileHandler
from ai_service import AIService
from ui_components import UIComponents
from config import PAGE_CONFIG, CUSTOM_CSS

def main():
    """Fonction principale de l'application"""
    
    # Configuration de la page
    st.set_page_config(**PAGE_CONFIG)
    
    # CSS personnalisé
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Initialisation du session state
    UIComponents.initialize_session_state()
    
    # En-tête principal
    st.markdown('<div class="main-header"><h1>🤖 Assistant IA Multi-Documents</h1><p>Analysez vos documents avec l\'intelligence artificielle</p></div>', unsafe_allow_html=True)
    
    # Configuration de la barre latérale
    selected_model, temperature, max_tokens = UIComponents.setup_sidebar()
    
    # Interface principale
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Zone d'upload multiple
        uploaded_files = UIComponents.display_multi_file_upload()
        
        # Traitement des fichiers uploadés
        if uploaded_files:
            UIComponents.process_uploaded_files(uploaded_files)
        
        # Affichage des fichiers en attente
        has_pending_files = UIComponents.display_pending_files()
        
        # Zone d'analyse globale
        if has_pending_files:
            analysis_question = UIComponents.display_analysis_input()
            
            if analysis_question:
                handle_multi_file_analysis(analysis_question, selected_model, temperature, max_tokens)
    
    with col2:
        # Upload de fichier simple (pour compatibilité)
        st.markdown("### 📄 Upload simple")
        uploaded_file = UIComponents.display_file_upload()
        
        if uploaded_file:
            handle_single_file_analysis(uploaded_file, selected_model, temperature, max_tokens)
    
    # Affichage de l'historique des conversations
    st.markdown("---")
    st.markdown("### 💬 Conversation")
    
    # Zone de chat
    UIComponents.display_chat_history()
    
    # Input pour le chat libre
    if prompt := st.chat_input("Posez une question..."):
        handle_chat_message(prompt, selected_model, temperature, max_tokens)

def handle_multi_file_analysis(question, selected_model, temperature, max_tokens):
    """Gère l'analyse de plusieurs fichiers"""
    try:
        # Créer le message utilisateur
        user_msg = UIComponents.create_multi_file_message(
            st.session_state["pending_files"], 
            question
        )
        st.session_state["messages"].append(user_msg)
        
        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.markdown(f"🔍 **Question:** {question}")
            st.markdown(f"📁 **Fichiers analysés:** {len(st.session_state['pending_files'])}")
        
        # Analyser avec l'IA
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analyse en cours..."):
                try:
                    # Vérifier les avertissements
                    has_images = any(f['is_image'] for f in st.session_state["pending_files"])
                    warnings = AIService.validate_model_for_content(selected_model, has_images)
                    
                    if warnings:
                        UIComponents.display_warnings(warnings)
                    
                    # Lancer l'analyse
                    response = AIService.analyze_multiple_files(
                        st.session_state["pending_files"],
                        question,
                        selected_model,
                        temperature,
                        max_tokens
                    )
                    
                    st.markdown(response)
                    
                    # Ajouter la réponse à l'historique
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    # Vider les fichiers en attente après analyse
                    st.session_state["pending_files"] = []
                    
                except Exception as e:
                    error_msg = str(e)
                    UIComponents.display_error(error_msg, has_images, selected_model)
                    
                    # Ajouter l'erreur à l'historique
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": f"❌ Erreur: {error_msg}"
                    })
        
        # Forcer le rafraîchissement
        st.rerun()
        
    except Exception as e:
        st.error(f"Erreur lors de l'analyse: {e}")

def handle_single_file_analysis(uploaded_file, selected_model, temperature, max_tokens):
    """Gère l'analyse d'un fichier unique"""
    try:
        # Vérifier si le fichier a déjà été traité
        file_hash = FileHandler.get_file_hash(uploaded_file)
        
        # Vérifier dans l'historique si le fichier a déjà été analysé
        already_processed = any(
            msg.get("file_hash") == file_hash 
            for msg in st.session_state["messages"] 
            if msg["role"] == "user"
        )
        
        if not already_processed:
            # Extraire le contenu
            with st.spinner("📖 Extraction du contenu..."):
                content = FileHandler.extract_text(uploaded_file)
            
            if content and not content.startswith("Erreur"):
                # Créer le message utilisateur
                user_msg = UIComponents.create_user_message(uploaded_file, content, file_hash)
                st.session_state["messages"].append(user_msg)
                
                # Analyser avec l'IA
                with st.spinner("🧠 Analyse en cours..."):
                    try:
                        response = AIService.analyze_file(
                            uploaded_file,
                            content,
                            selected_model,
                            temperature,
                            max_tokens
                        )
                        
                        # Ajouter la réponse à l'historique
                        st.session_state["messages"].append({
                            "role": "assistant",
                            "content": response
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        error_msg = str(e)
                        is_image = FileHandler.is_image_file(uploaded_file)
                        UIComponents.display_error(error_msg, is_image, selected_model)
                        
                        # Ajouter l'erreur à l'historique
                        st.session_state["messages"].append({
                            "role": "assistant",
                            "content": f"❌ Erreur: {error_msg}"
                        })
            else:
                st.error(f"Impossible d'extraire le contenu: {content}")
        else:
            st.info("📄 Ce fichier a déjà été analysé dans cette session")
            
    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier: {e}")

def handle_chat_message(prompt, selected_model, temperature, max_tokens):
    """Gère les messages de chat libre"""
    try:
        # Ajouter le message utilisateur
        st.session_state["messages"].append({
            "role": "user",
            "content": prompt
        })
        
        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Générer la réponse
        with st.chat_message("assistant"):
            with st.spinner("🤔 Réflexion..."):
                try:
                    response = AIService.chat_with_ai(
                        st.session_state["messages"],
                        selected_model,
                        temperature,
                        max_tokens
                    )
                    
                    st.markdown(response)
                    
                    # Ajouter la réponse à l'historique
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": response
                    })
                    
                except Exception as e:
                    error_msg = str(e)
                    UIComponents.display_error(error_msg, False, selected_model)
                    
                    # Ajouter l'erreur à l'historique
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": f"❌ Erreur: {error_msg}"
                    })
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Erreur lors du chat: {e}")

def display_help_section():
    """Affiche la section d'aide"""
    with st.expander("❓ Aide et informations"):
        st.markdown("""
        ### 🚀 Comment utiliser l'assistant
        
        **1. Upload multiple de fichiers:**
        - Sélectionnez plusieurs fichiers en une fois
        - Les fichiers sont mis en attente d'analyse
        - Posez une question globale pour analyser tous les fichiers
        
        **2. Upload simple:**
        - Upload d'un seul fichier pour une analyse immédiate
        - Compatible avec tous les formats supportés
        
        **3. Chat libre:**
        - Posez des questions sans fichier
        - L'IA utilise ses connaissances générales
        
        ### 📄 Formats supportés
        - **Documents:** PDF, Word (docx/doc), PowerPoint (pptx), RTF, TXT
        - **Données:** Excel (xlsx/xls), CSV
        - **Images:** PNG, JPG, JPEG, GIF, BMP, TIFF (utiliser LlaVa)
        
        ### 🤖 Modèles disponibles
        - **Llama 3:** Polyvalent et performant
        - **Mistral:** Rapide et efficace  
        - **CodeLlama:** Spécialisé en code
        - **Gemma:** Équilibré et précis
        - **LlaVa:** Analyse les images
        
        ### 💡 Conseils
        - Utilisez LlaVa pour analyser les images
        - Les gros fichiers peuvent prendre plus de temps
        - Vérifiez qu'Ollama est démarré avant d'utiliser l'application
        """)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erreur critique de l'application: {e}")
        st.info("💡 Vérifiez que toutes les dépendances sont installées et qu'Ollama est démarré")
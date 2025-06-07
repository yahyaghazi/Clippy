"""
Système d'apprentissage des habitudes utilisateur
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional


class UserLearningEngine:
    """Apprend des habitudes utilisateur pour améliorer les suggestions"""
    
    def __init__(self, data_file: str = "user_patterns.json"):
        self.data_file = Path(data_file)
        self.user_patterns: Dict[str, Any] = {}
        self.suggestion_feedback: Dict[str, int] = {}
        self.app_transitions: List[Dict] = []
        self.load_data()
    
    def load_data(self):
        """Charge les données d'apprentissage existantes"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_patterns = data.get('patterns', {})
                    self.suggestion_feedback = data.get('feedback', {})
                    self.app_transitions = data.get('transitions', [])
                print(f"[LEARNING] Données chargées: {len(self.app_transitions)} transitions")
            except Exception as e:
                print(f"[LEARNING] Erreur chargement données: {e}")
    
    def save_data(self):
        """Sauvegarde les données d'apprentissage"""
        try:
            data = {
                'patterns': self.user_patterns,
                'feedback': self.suggestion_feedback,
                'transitions': self.app_transitions[-1000:]  # Garder seulement les 1000 dernières
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[LEARNING] Erreur sauvegarde données: {e}")
    
    def record_user_action(self, app_name: str, action: str, timestamp: float):
        """Enregistre une action utilisateur"""
        # Enregistrer dans les patterns
        if app_name not in self.user_patterns:
            self.user_patterns[app_name] = []
        
        self.user_patterns[app_name].append({
            'action': action,
            'timestamp': timestamp,
            'hour': time.localtime(timestamp).tm_hour
        })
        
        # Garder seulement les 50 dernières actions par app
        if len(self.user_patterns[app_name]) > 50:
            self.user_patterns[app_name] = self.user_patterns[app_name][-50:]
    
    def record_app_transition(self, from_app: str, to_app: str):
        """Enregistre une transition entre applications"""
        transition = {
            'from': from_app,
            'to': to_app,
            'timestamp': time.time(),
            'hour': time.localtime().tm_hour
        }
        self.app_transitions.append(transition)
        
        # Sauvegarder périodiquement
        if len(self.app_transitions) % 10 == 0:
            self.save_data()
    
    def get_common_workflows(self) -> Dict[str, List[str]]:
        """Identifie les workflows communs de l'utilisateur"""
        workflows = {}
        
        # Analyser les transitions des 7 derniers jours
        week_ago = time.time() - (86400 * 7)
        recent_transitions = [t for t in self.app_transitions 
                            if t['timestamp'] > week_ago]
        
        for transition in recent_transitions:
            from_app = transition['from']
            to_app = transition['to']
            
            if from_app not in workflows:
                workflows[from_app] = []
            workflows[from_app].append(to_app)
        
        # Garder seulement les transitions fréquentes
        for app in list(workflows.keys()):
            app_counts = {}
            for target in workflows[app]:
                app_counts[target] = app_counts.get(target, 0) + 1
            
            # Garder seulement si >= 3 occurrences
            frequent_targets = [app for app, count in app_counts.items() if count >= 3]
            if frequent_targets:
                workflows[app] = frequent_targets
            else:
                del workflows[app]
        
        return workflows
    
    def get_contextual_suggestion(self, app_name: str, context: str) -> Optional[str]:
        """Génère une suggestion basée sur l'apprentissage utilisateur"""
        workflows = self.get_common_workflows()
        current_hour = time.localtime().tm_hour
        
        # Suggestion basée sur les workflows
        if app_name in workflows and workflows[app_name]:
            next_apps = workflows[app_name][:2]  # Top 2
            if len(next_apps) == 1:
                return f"Tu passes souvent à {next_apps[0]} après {app_name}"
            else:
                return f"Tu passes souvent à {' ou '.join(next_apps)} après {app_name}"
        
        # Suggestion basée sur l'heure
        if 9 <= current_hour <= 17:
            return "En journée de travail - pense à faire des pauses régulières !"
        elif current_hour >= 22:
            return "Il se fait tard - pense à sauvegarder ton travail !"
        elif 6 <= current_hour <= 8:
            return "Bon matin ! Prêt pour une journée productive ?"
        
        # Pas de suggestion personnalisée
        return None
    
    def get_personalized_suggestion(self, app_name: str, context: str) -> Optional[str]:
        """Génère une suggestion personnalisée (alias pour get_contextual_suggestion)"""
        return self.get_contextual_suggestion(app_name, context)
    
    def record_suggestion_feedback(self, suggestion_id: str, feedback: bool):
        """Enregistre le feedback sur une suggestion"""
        if suggestion_id not in self.suggestion_feedback:
            self.suggestion_feedback[suggestion_id] = 0
        
        # +1 pour positif, -1 pour négatif
        self.suggestion_feedback[suggestion_id] += 1 if feedback else -1
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques d'usage"""
        total_transitions = len(self.app_transitions)
        workflows = self.get_common_workflows()
        
        return {
            'total_transitions': total_transitions,
            'tracked_workflows': len(workflows),
            'most_common_workflow': max(workflows.items(), key=lambda x: len(x[1])) if workflows else None
        }
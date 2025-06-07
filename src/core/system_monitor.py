"""
Surveillance du système et détection d'activité
"""

import threading
import time
import psutil
from typing import Callable, Dict, List, Tuple, Optional
from ..config.settings import settings
from ..utils.app_mapper import app_mapper


class SystemMonitor:
    """Surveillance intelligente des processus système"""
    
    def __init__(self, callback: Callable[[str, str], None]):
        self.callback = callback
        self.current_app = ""
        self.current_context = ""
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Historique pour améliorer la détection
        self.process_history: Dict[int, Dict] = {}
        self.app_usage_time: Dict[str, float] = {}
        self.last_detection_time = time.time()
    
    def start(self):
        """Démarre la surveillance"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("🔍 Surveillance système démarrée")
    
    def stop(self):
        """Arrête la surveillance"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        print("⏹️ Surveillance système arrêtée")
    
    def _monitor_loop(self):
        """Boucle principale de surveillance"""
        while self.running:
            try:
                app_name, context = self._get_active_app_info()
                
                # Détecter seulement les vrais changements d'application
                if app_name != self.current_app:
                    self._log_app_change(self.current_app, app_name)
                    self.current_app = app_name
                    self.current_context = context
                    
                    # Callback vers l'UI
                    self.callback(app_name, context)
                
                time.sleep(settings.monitoring.check_interval)
                
            except Exception as e:
                print(f"Erreur dans la boucle de surveillance: {e}")
                time.sleep(5)
    
    def _get_active_app_info(self) -> Tuple[str, str]:
        """Analyse les processus pour déterminer l'application active"""
        try:
            current_time = time.time()
            scored_apps = []
            
            # Récupérer tous les processus intéressants
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'create_time', 'memory_info']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    # Ignorer les processus système
                    if proc_name in settings.monitoring.ignored_processes:
                        continue
                    
                    # Filtrer les applications intéressantes
                    if self._is_interesting_app(proc_name):
                        score = self._calculate_app_score(proc_info, current_time)
                        if score > 0:
                            scored_apps.append({
                                'name': proc_name,
                                'score': score,
                                'proc_info': proc_info
                            })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Trier par score et sélectionner le meilleur
            if scored_apps:
                scored_apps.sort(key=lambda x: x['score'], reverse=True)
                best_app = scored_apps[0]
                
                app_display_name = app_mapper.get_display_name(best_app['name'])
                context = app_mapper.get_context(app_display_name)
                
                if settings.debug_mode:
                    print(f"[DEBUG] App active: {app_display_name} (score: {best_app['score']:.1f})")
                
                return app_display_name, context
            
            return "Système", "Activité de base"
            
        except Exception as e:
            print(f"[ERROR] Analyse processus: {e}")
            return "Inconnu", "Erreur de détection"
    
    def _is_interesting_app(self, proc_name: str) -> bool:
        """Détermine si un processus est intéressant à surveiller"""
        interesting_patterns = [
            # Navigateurs
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 'brave.exe',
            
            # Éditeurs
            'notepad.exe', 'notepad++.exe', 'code.exe', 'sublime_text.exe',
            'atom.exe', 'vim.exe', 'emacs.exe',
            
            # Suite Office
            'winword.exe', 'excel.exe', 'powerpnt.exe', 'outlook.exe',
            
            # Développement
            'python.exe', 'node.exe', 'java.exe', 'javaw.exe',
            'pycharm64.exe', 'idea64.exe', 'devenv.exe',
            
            # Communication
            'discord.exe', 'slack.exe', 'teams.exe', 'zoom.exe',
            'telegram.exe', 'whatsapp.exe',
            
            # Multimédia
            'spotify.exe', 'vlc.exe', 'photoshop.exe', 'gimp.exe',
            
            # Gaming
            'steam.exe', 'origin.exe', 'epicgameslauncher.exe',
            
            # Système (si pas dans ignored)
            'cmd.exe', 'powershell.exe', 'explorer.exe'
        ]
        
        return proc_name in interesting_patterns
    
    def _calculate_app_score(self, proc_info: Dict, current_time: float) -> float:
        """Calcule un score d'activité pour un processus"""
        try:
            pid = proc_info['pid']
            create_time = proc_info['create_time']
            memory_info = proc_info['memory_info']
            
            # Score basé sur la récence (processus récents = plus probablement actifs)
            time_since_creation = current_time - create_time
            recency_score = max(0, 100 - (time_since_creation / 3600))  # Décroît sur 1h
            
            # Score basé sur la mémoire utilisée
            memory_mb = memory_info.rss / (1024 * 1024) if memory_info else 0
            memory_score = min(50, memory_mb / settings.monitoring.score_memory_threshold * 50)
            
            # Bonus pour les applications qu'on suit depuis longtemps
            history_bonus = 0
            if pid in self.process_history:
                history_bonus = min(20, len(self.process_history[pid]) * 2)
            
            # Score total
            total_score = recency_score + memory_score + history_bonus
            
            # Mettre à jour l'historique
            if pid not in self.process_history:
                self.process_history[pid] = []
            self.process_history[pid].append(current_time)
            
            # Nettoyer l'historique (garder seulement les 10 dernières entrées)
            if len(self.process_history[pid]) > 10:
                self.process_history[pid] = self.process_history[pid][-10:]
            
            return total_score
            
        except Exception as e:
            print(f"Erreur calcul score: {e}")
            return 0
    
    def _log_app_change(self, old_app: str, new_app: str):
        """Log les changements d'application pour les statistiques"""
        current_time = time.time()
        
        # Calculer le temps d'utilisation de l'ancienne app
        if old_app and old_app != "":
            usage_time = current_time - self.last_detection_time
            if old_app in self.app_usage_time:
                self.app_usage_time[old_app] += usage_time
            else:
                self.app_usage_time[old_app] = usage_time
        
        self.last_detection_time = current_time
        
        if settings.debug_mode and old_app and new_app != old_app:
            print(f"[CHANGEMENT] {old_app} → {new_app}")
    
    def get_usage_stats(self) -> Dict[str, float]:
        """Retourne les statistiques d'utilisation des applications"""
        # Ajouter le temps de l'app actuelle
        if self.current_app:
            current_time = time.time()
            additional_time = current_time - self.last_detection_time
            
            stats = self.app_usage_time.copy()
            if self.current_app in stats:
                stats[self.current_app] += additional_time
            else:
                stats[self.current_app] = additional_time
            
            return stats
        
        return self.app_usage_time.copy()
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.app_usage_time.clear()
        self.process_history.clear()
        self.last_detection_time = time.time()
        print("📊 Statistiques remises à zéro")
    
    def cleanup_old_processes(self):
        """Nettoie l'historique des processus morts"""
        current_pids = set(proc.info['pid'] for proc in psutil.process_iter(['pid']))
        old_pids = set(self.process_history.keys()) - current_pids
        
        for pid in old_pids:
            del self.process_history[pid]
        
        if old_pids and settings.debug_mode:
            print
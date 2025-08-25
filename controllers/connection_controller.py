#!/usr/bin/env python3
"""
controllers/connection_controller.py - Contrôleur des connexions et tuyaux
Logique métier pour le mode connexion, construction de tuyaux orthogonaux
"""

from typing import Optional, List, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, QPointF, Qt
from PyQt6.QtWidgets import QGraphicsScene

# Import des composants existants
from components.ports import Port
from components.pipe import InteractivePipeBuilder, OrthogonalPipe

class ConnectionController(QObject):
    """
    Contrôleur des connexions hydrauliques
    Responsabilité : Mode connexion, construction interactive de tuyaux
    """
    
    # === SIGNAUX ÉMIS ===
    
    # Mode connexion
    connection_mode_changed = pyqtSignal(bool)              # is_active
    
    # Construction de tuyaux
    pipe_construction_started = pyqtSignal(str, str)        # component_id, port_id
    pipe_construction_cancelled = pyqtSignal()
    pipe_created = pyqtSignal(str)                          # pipe_id
    
    # Interaction ports
    port_hovered = pyqtSignal(str, str, bool)               # component_id, port_id, is_entering
    port_clicked = pyqtSignal(str, str)                     # component_id, port_id
    
    # Waypoints
    waypoint_added = pyqtSignal(QPointF)                    # position
    waypoint_removed = pyqtSignal(int)                      # index
    
    # Erreurs
    connection_failed = pyqtSignal(str, str, str)           # start_port, end_port, reason
    
    def __init__(self, work_area):
        super().__init__()
        
        self.work_area = work_area
        self.scene = work_area.scene
        
        # État du mode connexion
        self.connection_mode = False
        
        # Construction de tuyau en cours
        self.pipe_builder: Optional[InteractivePipeBuilder] = None
        self.start_component = None
        self.start_port_id = None
        
        # État de survol
        self.hovering_port: Optional[Tuple[str, str]] = None  # (component_id, port_id)
        
        # Collection des tuyaux créés
        self.pipes = {}  # pipe_id -> OrthogonalPipe
        self.pipe_counter = 0
        
        # Connexion des signaux
        self.connect_signals()
        
        print("[CONNECTION_CONTROLLER] Contrôleur initialisé")
    
    def connect_signals(self):
        """Connexion des signaux UI et composants"""
        # Signaux de la zone de travail
        self.work_area.mouse_clicked.connect(self.handle_mouse_click)
        self.work_area.mouse_moved.connect(self.handle_mouse_move)
        
        # Signaux des ports (statiques)
        Port._signals.port_clicked.connect(self.on_port_clicked)
        Port._signals.port_hovered.connect(self.on_port_hovered)
        
        print("[CONNECTION_CONTROLLER] Signaux connectés")
    
    # === GESTION MODE CONNEXION ===
    
    def toggle_mode(self, active: Optional[bool] = None):
        """Active/désactive le mode connexion"""
        if active is None:
            active = not self.connection_mode
        
        if active == self.connection_mode:
            return  # Pas de changement
        
        self.connection_mode = active
        
        if active:
            self.enable_connection_mode()
        else:
            self.disable_connection_mode()
        
        # Signal de changement d'état
        self.connection_mode_changed.emit(self.connection_mode)
        
        print(f"[CONNECTION_CONTROLLER] Mode connexion: {'ACTIVÉ' if active else 'DÉSACTIVÉ'}")
    
    def enable_connection_mode(self):
        """Active le mode connexion"""
        # Mettre tous les ports en mode connexion
        self.set_all_ports_connection_mode(True)
        
        # Désactiver le déplacement des composants
        self.set_components_movable(False)
        
        print("[CONNECTION_CONTROLLER] Mode connexion activé")
    
    def disable_connection_mode(self):
        """Désactive le mode connexion"""
        # Annuler toute construction en cours
        if self.pipe_builder:
            self.cancel_pipe_construction()
        
        # Désactiver le mode connexion des ports
        self.set_all_ports_connection_mode(False)
        
        # Réactiver le déplacement des composants
        self.set_components_movable(True)
        
        print("[CONNECTION_CONTROLLER] Mode connexion désactivé")
    
    def set_all_ports_connection_mode(self, active: bool):
        """Active/désactive le mode connexion sur tous les ports"""
        for item in self.scene.items():
            if isinstance(item, Port):
                item.set_connection_mode(active)
    
    def set_components_movable(self, movable: bool):
        """Active/désactive le déplacement des composants"""
        for item in self.scene.items():
            if hasattr(item, 'component_id'):  # C'est un composant hydraulique
                item.setFlag(item.GraphicsItemFlag.ItemIsMovable, movable)
                item.setFlag(item.GraphicsItemFlag.ItemIsSelectable, movable)
                if not movable:
                    item.setSelected(False)
    
    # === GESTION DES CLICS SOURIS ===
    
    def handle_mouse_click(self, position: QPointF, button: Qt.MouseButton):
        """Gestion des clics souris dans la zone de travail"""
        if not self.connection_mode or button != Qt.MouseButton.LeftButton:
            return
        
        if not self.pipe_builder:
            return  # Pas de construction en cours
        
        # Logique basée sur le survol de port
        if self.hovering_port:
            # Clic sur un port → terminer la construction
            component_id, port_id = self.hovering_port
            self.finish_pipe_construction(component_id, port_id)
        else:
            # Clic dans le vide → ajouter waypoint
            self.add_waypoint(position)
    
    def handle_mouse_move(self, position: QPointF):
        """Gestion du mouvement de souris"""
        if self.pipe_builder:
            # Mettre à jour le preview du tuyau
            self.pipe_builder.update_preview(position)
    
    # === GESTION DES SIGNAUX PORTS ===
    
    def on_port_clicked(self, component, port_id: str):
        """Gestionnaire du clic sur un port"""
        if not self.connection_mode:
            return
        
        component_id = component.component_id
        port = component.get_port_by_id(port_id)
        
        if not port or port.is_connected:
            print(f"[CONNECTION_CONTROLLER] Port {component_id}.{port_id} non disponible")
            return
        
        # Émettre signal
        self.port_clicked.emit(component_id, port_id)
        
        if not self.pipe_builder:
            # Démarrer une nouvelle construction
            self.start_pipe_construction(component, port_id)
        else:
            # Vérifier si c'est le même port (annuler) ou différent (terminer)
            if (self.start_component.component_id == component_id and 
                self.start_port_id == port_id):
                # Même port → annuler
                self.cancel_pipe_construction()
            else:
                # Port différent → terminer
                self.finish_pipe_construction(component_id, port_id)
    
    def on_port_hovered(self, component, port_id: str, is_entering: bool):
        """Gestionnaire du survol de port"""
        if not self.connection_mode:
            return
        
        component_id = component.component_id
        
        if is_entering:
            self.hovering_port = (component_id, port_id)
        else:
            self.hovering_port = None
        
        # Émettre signal
        self.port_hovered.emit(component_id, port_id, is_entering)
    
    # === CONSTRUCTION DE TUYAUX ===
    
    def start_pipe_construction(self, start_component, start_port_id: str):
        """Démarre la construction interactive d'un tuyau"""
        if self.pipe_builder:
            # Annuler construction précédente
            self.cancel_pipe_construction()
        
        self.start_component = start_component
        self.start_port_id = start_port_id
        
        # Créer le constructeur interactif
        self.pipe_builder = InteractivePipeBuilder(
            self.scene, start_component, start_port_id
        )
        
        # Signaux
        self.pipe_construction_started.emit(start_component.component_id, start_port_id)
        
        print(f"[CONNECTION_CONTROLLER] Construction démarrée: {start_component.component_id}.{start_port_id}")
    
    def add_waypoint(self, position: QPointF):
        """Ajoute un point intermédiaire au tuyau en construction"""
        if not self.pipe_builder:
            return
        
        self.pipe_builder.add_waypoint(position)
        self.waypoint_added.emit(position)
        
        print(f"[CONNECTION_CONTROLLER] Waypoint ajouté: {position}")
    
    def finish_pipe_construction(self, end_component_id: str, end_port_id: str):
        """Termine la construction du tuyau"""
        if not self.pipe_builder:
            return
        
        # Récupérer le composant de fin
        end_component = self.find_component_by_id(end_component_id)
        if not end_component:
            print(f"[CONNECTION_CONTROLLER] Composant {end_component_id} non trouvé")
            return
        
        # Vérifier les règles de connexion
        start_port = self.start_component.get_port_by_id(self.start_port_id)
        end_port = end_component.get_port_by_id(end_port_id)
        
        if not self.can_connect_ports(start_port, end_port):
            reason = "Connexion non autorisée"
            self.connection_failed.emit(
                f"{self.start_component.component_id}.{self.start_port_id}",
                f"{end_component_id}.{end_port_id}",
                reason
            )
            return
        
        # Créer le tuyau final
        pipe = self.pipe_builder.finish_pipe(end_component, end_port_id)
        
        if pipe:
            # Enregistrer le tuyau
            pipe_id = self.register_pipe(pipe)
            
            # Connecter les ports
            start_port.connect_to_pipe(pipe)
            end_port.connect_to_pipe(pipe)
            
            # Signaux de succès
            self.pipe_created.emit(pipe_id)
            
            print(f"[CONNECTION_CONTROLLER] Tuyau créé: {pipe_id}")
        
        # Nettoyer
        self.cleanup_pipe_construction()
    
    def cancel_pipe_construction(self):
        """Annule la construction en cours"""
        if self.pipe_builder:
            self.pipe_builder.cancel()
            self.cleanup_pipe_construction()
            
            self.pipe_construction_cancelled.emit()
            print("[CONNECTION_CONTROLLER] Construction annulée")
    
    def cleanup_pipe_construction(self):
        """Nettoie l'état de construction"""
        self.pipe_builder = None
        self.start_component = None
        self.start_port_id = None
        self.hovering_port = None
    
    # === GESTION DES TUYAUX ===
    
    def register_pipe(self, pipe: OrthogonalPipe) -> str:
        """Enregistre un tuyau créé"""
        self.pipe_counter += 1
        pipe_id = f"pipe_{self.pipe_counter:03d}"
        
        # Assigner l'ID au tuyau
        pipe.pipe_id = pipe_id
        
        # Stocker dans la collection
        self.pipes[pipe_id] = pipe
        
        return pipe_id
    
    def remove_pipe(self, pipe_id: str) -> bool:
        """Supprime un tuyau"""
        if pipe_id not in self.pipes:
            return False
        
        try:
            pipe = self.pipes[pipe_id]
            
            # Déconnecter les ports
            if hasattr(pipe, 'start_component') and hasattr(pipe, 'start_port'):
                start_port = pipe.start_component.get_port_by_id(pipe.start_port)
                if start_port:
                    start_port.disconnect_from_pipe()
            
            if hasattr(pipe, 'end_component') and hasattr(pipe, 'end_port'):
                end_port = pipe.end_component.get_port_by_id(pipe.end_port)
                if end_port:
                    end_port.disconnect_from_pipe()
            
            # Supprimer de la scène
            if hasattr(pipe, 'delete_pipe'):
                pipe.delete_pipe()
            elif pipe.scene():
                self.scene.removeItem(pipe)
            
            # Supprimer de la collection
            del self.pipes[pipe_id]
            
            print(f"[CONNECTION_CONTROLLER] Tuyau supprimé: {pipe_id}")
            return True
            
        except Exception as e:
            print(f"[CONNECTION_CONTROLLER] Erreur suppression tuyau {pipe_id}: {e}")
            return False
    
    def get_pipe(self, pipe_id: str) -> Optional[OrthogonalPipe]:
        """Récupère un tuyau par son ID"""
        return self.pipes.get(pipe_id)
    
    def get_all_pipes(self) -> List[OrthogonalPipe]:
        """Retourne tous les tuyaux"""
        return list(self.pipes.values())
    
    def get_pipes_count(self) -> int:
        """Retourne le nombre de tuyaux"""
        return len(self.pipes)
    
    # === VALIDATION DES CONNEXIONS ===
    
    def can_connect_ports(self, start_port: Port, end_port: Port) -> bool:
        """Vérifie si deux ports peuvent être connectés"""
        if not start_port or not end_port:
            return False
        
        # Utiliser la méthode existante des ports
        return start_port.can_connect_to(end_port)
    
    def find_component_by_id(self, component_id: str):
        """Trouve un composant par son ID dans la scène"""
        for item in self.scene.items():
            if hasattr(item, 'component_id') and item.component_id == component_id:
                return item
        return None
    
    # === INFORMATION ET DEBUG ===
    
    def get_connection_info(self) -> dict:
        """Retourne des informations sur l'état des connexions"""
        return {
            "connection_mode": self.connection_mode,
            "construction_active": self.pipe_builder is not None,
            "pipes_count": len(self.pipes),
            "hovering_port": self.hovering_port,
            "start_component": self.start_component.component_id if self.start_component else None,
            "start_port": self.start_port_id
        }
    
    def get_pipes_summary(self) -> List[dict]:
        """Retourne un résumé de tous les tuyaux"""
        summary = []
        
        for pipe_id, pipe in self.pipes.items():
            pipe_info = {
                "pipe_id": pipe_id,
                "length": getattr(pipe, 'length', 0),
                "waypoints": len(getattr(pipe, 'waypoints', [])),
                "diameter": getattr(pipe, 'diameter', 0),
            }
            
            # Informations de connexion
            if hasattr(pipe, 'start_component'):
                pipe_info["start"] = f"{pipe.start_component.component_id}.{pipe.start_port}"
            if hasattr(pipe, 'end_component'):
                pipe_info["end"] = f"{pipe.end_component.component_id}.{pipe.end_port}"
            
            summary.append(pipe_info)
        
        return summary
    
    # === NETTOYAGE ===
    
    def clear_all(self):
        """Supprime tous les tuyaux et remet à zéro"""
        # Annuler construction en cours
        if self.pipe_builder:
            self.cancel_pipe_construction()
        
        # Supprimer tous les tuyaux
        pipe_ids = list(self.pipes.keys())
        for pipe_id in pipe_ids:
            self.remove_pipe(pipe_id)
        
        # Réinitialiser compteurs
        self.pipe_counter = 0
        
        # Désactiver mode connexion
        if self.connection_mode:
            self.toggle_mode(False)
        
        print("[CONNECTION_CONTROLLER] Tout nettoyé")
    
    def cleanup(self):
        """Nettoyage avant fermeture"""
        print("[CONNECTION_CONTROLLER] Nettoyage...")
        self.clear_all()

# === POINT D'ENTRÉE POUR TESTS ===

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QVBoxLayout, QWidget, QPushButton
    
    app = QApplication(sys.argv)
    
    # Créer une zone de travail de test
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    
    # Simuler work_area
    class MockWorkArea:
        def __init__(self, scene):
            self.scene = scene
            self.mouse_clicked = None
            self.mouse_moved = None
    
    work_area = MockWorkArea(scene)
    
    # Créer le contrôleur
    controller = ConnectionController(work_area)
    
    # Interface de test
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Boutons de test
    btn_toggle = QPushButton("Toggle Mode Connexion")
    btn_toggle.clicked.connect(controller.toggle_mode)
    layout.addWidget(btn_toggle)
    
    btn_info = QPushButton("Afficher Info")
    btn_info.clicked.connect(lambda: print(controller.get_connection_info()))
    layout.addWidget(btn_info)
    
    btn_clear = QPushButton("Clear All")
    btn_clear.clicked.connect(controller.clear_all)
    layout.addWidget(btn_clear)
    
    layout.addWidget(view)
    
    # Connexions de test
    controller.connection_mode_changed.connect(
        lambda active: print(f"Mode connexion: {'ON' if active else 'OFF'}")
    )
    controller.pipe_created.connect(
        lambda pipe_id: print(f"Tuyau créé: {pipe_id}")
    )
    controller.pipe_construction_started.connect(
        lambda comp_id, port_id: print(f"Construction démarrée: {comp_id}.{port_id}")
    )
    
    window.setCentralWidget(central_widget)
    window.show()
    
    print("=== TEST CONNECTION CONTROLLER ===")
    print("Utilisez les boutons pour tester le contrôleur")
    
    sys.exit(app.exec())
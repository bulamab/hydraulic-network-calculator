#!/usr/bin/env python3
"""
components/ports.py - Système de ports hydrauliques avec gestion du scale
Gestion des ports avec événements, états et scale synchronisé
"""

from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QObject
from PyQt6.QtGui import QPen, QBrush, QColor

class PortSignals(QObject):
    """Signaux pour les ports (Qt nécessite une classe héritant de QObject)"""
    port_clicked = pyqtSignal(object, str)  # (component, port_id)
    port_hovered = pyqtSignal(object, str, bool)  # (component, port_id, is_entering)

class Port(QGraphicsEllipseItem):
    """
    Port hydraulique avec gestion d'événements, d'états ET de scale
    VERSION AMÉLIORÉE avec synchronisation scale
    """
    
    # Signaux statiques partagés (un seul gestionnaire pour tous les ports)
    _signals = PortSignals()
    
    # Taille de base du port (sera multipliée par le scale)
    BASE_RADIUS = 3.0
    
    def __init__(self, port_id, port_type, position, parent_component):
        # Commencer par une taille de base
        super().__init__(-self.BASE_RADIUS, -self.BASE_RADIUS, 
                         self.BASE_RADIUS * 2, self.BASE_RADIUS * 2)
        
        # Propriétés du port
        self.port_id = port_id
        self.port_type = port_type  # "input", "output", "bidirectional"
        self.parent_component = parent_component
        
        # État de connexion
        self.is_connected = False
        self.connected_pipe = None
        
        # États visuels
        self.is_hovered = False
        self.connection_mode = False
        
        # Position initiale (sera ajustée depuis le composant parent)
        self.initial_position = position
        
        # GESTION SCALE
        self.current_scale = 1.0  # Scale actuel du port
        self.effective_radius = self.BASE_RADIUS  # Rayon effectif
        
        # Configuration graphique
        self.setZValue(10)  # Au-dessus des composants
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
        
        # Style initial
        self.update_visual_style()
        
        print(f"[PORT] Créé: {parent_component.component_id}.{port_id} ({port_type}) - position: {position}")
    
    def update_scale(self, scale: float):
        """
        Met à jour la taille du port selon le scale
        Args:
            scale: Nouveau scale à appliquer
        """
        if scale != self.current_scale:
            self.current_scale = scale
            self.effective_radius = self.BASE_RADIUS * scale
            
            # Mettre à jour la géométrie du cercle (centré)
            new_size = self.effective_radius * 2
            self.setRect(-self.effective_radius, -self.effective_radius, new_size, new_size)
            
            # Mettre à jour le style (épaisseur de trait selon scale)
            self.update_visual_style()
            
            print(f"[PORT] Scale mis à jour: {self.port_id} scale={scale}, rayon={self.effective_radius}")
    
    def get_current_scale(self) -> float:
        """Retourne le scale actuel du port"""
        return self.current_scale
    
    def get_effective_radius(self) -> float:
        """Retourne le rayon effectif actuel"""
        return self.effective_radius
    
    def update_visual_style(self):
        """Met à jour le style visuel selon l'état ET le scale"""
        # Épaisseur de trait adaptée au scale
        base_pen_width = 2
        scaled_pen_width = max(1, int(base_pen_width * self.current_scale))
        
        if self.is_connected:
            # Port connecté = rouge
            pen = QPen(QColor(200, 0, 0), scaled_pen_width)
            brush = QBrush(QColor(255, 100, 100))
        elif self.is_hovered and self.connection_mode:
            # Port survolé en mode connexion = jaune brillant
            pen = QPen(QColor(255, 215, 0), scaled_pen_width + 1)
            brush = QBrush(QColor(255, 255, 0))
        elif self.connection_mode and not self.is_connected:
            # Mode connexion + port libre = vert brillant
            pen = QPen(QColor(0, 200, 0), scaled_pen_width)
            brush = QBrush(QColor(100, 255, 100))
        elif self.is_hovered:
            # Hover normal = vert clair
            pen = QPen(QColor(0, 150, 0), scaled_pen_width)
            brush = QBrush(QColor(150, 255, 150))
        else:
            # Port libre normal = vert discret
            pen = QPen(QColor(0, 100, 0), scaled_pen_width)
            brush = QBrush(QColor(200, 255, 200, 180))
        
        self.setPen(pen)
        self.setBrush(brush)
    
    def set_connection_mode(self, active):
        """Active/désactive le mode connexion"""
        self.connection_mode = active
        self.update_visual_style()
    
    def connect_to_pipe(self, pipe):
        """Connecte ce port à un tuyau"""
        self.is_connected = True
        self.connected_pipe = pipe
        self.update_visual_style()
        print(f"[PORT] {self.parent_component.component_id}.{self.port_id} connecté")
    
    def disconnect_from_pipe(self):
        """Déconnecte ce port"""
        self.is_connected = False
        self.connected_pipe = None
        self.update_visual_style()
        print(f"[PORT] {self.parent_component.component_id}.{self.port_id} déconnecté")
    
    def get_global_position(self):
        """Position globale du port dans la scène"""
        return self.scenePos()
    
    def get_center_position(self):
        """Position du centre du port (pour connexions précises)"""
        # Le centre est à la position du port (car le rect est centré)
        return self.scenePos()
    
    def can_connect_to(self, other_port):
        """Vérifie si ce port peut se connecter à un autre"""
        # Vérifier que les ports ne sont pas déjà connectés
        if self.is_connected or other_port.is_connected:
            print(f"[PORT] Connexion impossible: port déjà connecté")
            return False
        
        # Empêcher la connexion d'un port avec lui-même
        if self == other_port:
            print(f"[PORT] Connexion impossible: même port")
            return False
        
        # Empêcher la connexion entre ports du même composant
        if self.parent_component == other_port.parent_component:
            print(f"[PORT] Connexion impossible: même composant ({self.parent_component.component_id})")
            return False
        
        # Règles métier futures (input→output, même type de fluide, etc.)
        print(f"[PORT] Connexion autorisée: {self.parent_component.component_id}.{self.port_id} → {other_port.parent_component.component_id}.{other_port.port_id}")
        return True
    
    # === ÉVÉNEMENTS SOURIS ===
    
    def mousePressEvent(self, event):
        """Clic sur le port - émet un signal"""
        print(f"[PORT DEBUG] mousePressEvent appelé sur {self.parent_component.component_id}.{self.port_id}")
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Émettre le signal pour que la fenêtre principale gère la connexion
            Port._signals.port_clicked.emit(self.parent_component, self.port_id)
            print(f"[PORT] Signal émis pour {self.parent_component.component_id}.{self.port_id}")
            
            # NE PAS appeler super() pour éviter la propagation
            event.accept()
        else:
            print(f"[PORT DEBUG] Bouton non-gauche cliqué")
            super().mousePressEvent(event)
    
    def hoverEnterEvent(self, event):
        """Souris entre dans le port"""
        print(f"[PORT DEBUG] Hover ENTER sur {self.parent_component.component_id}.{self.port_id}")
        self.is_hovered = True
        self.update_visual_style()
        Port._signals.port_hovered.emit(self.parent_component, self.port_id, True)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Souris sort du port"""
        print(f"[PORT DEBUG] Hover LEAVE sur {self.parent_component.component_id}.{self.port_id}")
        self.is_hovered = False
        self.update_visual_style()
        Port._signals.port_hovered.emit(self.parent_component, self.port_id, False)
        super().hoverLeaveEvent(event)
    
    # === INFORMATIONS DEBUG ===
    
    def get_info(self):
        """Informations du port pour debug"""
        return {
            "id": self.port_id,
            "type": self.port_type,
            "component": self.parent_component.component_id,
            "connected": self.is_connected,
            "position": self.get_global_position(),
            "scale_info": {
                "current_scale": self.current_scale,
                "base_radius": self.BASE_RADIUS,
                "effective_radius": self.effective_radius
            }
        }
    
    def show_debug_info(self):
        """Affiche les informations de debug"""
        info = self.get_info()
        print(f"\n=== PORT DEBUG: {info['id']} ===")
        print(f"Type: {info['type']}")
        print(f"Composant: {info['component']}")
        print(f"Connecté: {info['connected']}")
        print(f"Position: {info['position']}")
        print(f"Scale: {info['scale_info']['current_scale']}")
        print(f"Rayon base: {info['scale_info']['base_radius']}")
        print(f"Rayon effectif: {info['scale_info']['effective_radius']}")
        print("=" * 30 + "\n")


# === FONCTION UTILITAIRE ===

def create_scaled_port(port_id: str, port_type: str, position: QPointF, 
                      parent_component, initial_scale: float = 1.0) -> Port:
    """
    Crée un port avec scale initial
    
    Args:
        port_id: ID du port
        port_type: Type du port
        position: Position initiale
        parent_component: Composant parent
        initial_scale: Scale initial à appliquer
    
    Returns:
        Port configuré avec le scale
    """
    port = Port(port_id, port_type, position, parent_component)
    if initial_scale != 1.0:
        port.update_scale(initial_scale)
    return port


# === POINT D'ENTRÉE POUR TESTS ===

if __name__ == "__main__":
    # Test du système de ports avec scale
    from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider, QLabel
    import sys
    
    app = QApplication(sys.argv)
    
    # Interface de test
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Contrôle de scale
    scale_label = QLabel("Scale ports: 1.00")
    layout.addWidget(scale_label)
    
    scale_slider = QSlider(Qt.Orientation.Horizontal)
    scale_slider.setMinimum(25)   # 0.25x
    scale_slider.setMaximum(400)  # 4.0x
    scale_slider.setValue(100)    # 1.0x
    layout.addWidget(scale_slider)
    
    # Scène de test
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    layout.addWidget(view)
    
    # Créer des ports de test
    class MockComponent:
        def __init__(self, component_id):
            self.component_id = component_id
    
    mock_comp = MockComponent("test_component")
    
    # Créer plusieurs ports à différentes positions
    test_ports = []
    positions = [
        QPointF(100, 100),
        QPointF(200, 100), 
        QPointF(150, 150),
        QPointF(100, 200),
        QPointF(200, 200)
    ]
    
    port_types = ["input", "output", "bidirectional", "input", "output"]
    
    for i, (pos, port_type) in enumerate(zip(positions, port_types)):
        port = Port(f"port_{i}", port_type, pos, mock_comp)
        port.setPos(pos)
        scene.addItem(port)
        test_ports.append(port)
    
    # Simuler états différents
    test_ports[0].set_connection_mode(True)  # Mode connexion
    test_ports[1].connect_to_pipe(None)      # Connecté
    test_ports[2].is_hovered = True          # Survolé
    test_ports[2].update_visual_style()
    
    # Fonction de mise à jour du scale
    def update_ports_scale(value):
        new_scale = value / 100.0
        for port in test_ports:
            port.update_scale(new_scale)
        scale_label.setText(f"Scale ports: {new_scale:.2f}")
    
    scale_slider.valueChanged.connect(update_ports_scale)
    
    # Boutons de test
    btn_info = QPushButton("Debug Info")
    btn_info.clicked.connect(lambda: [port.show_debug_info() for port in test_ports])
    layout.addWidget(btn_info)
    
    btn_toggle_connection = QPushButton("Toggle Connection Mode")
    def toggle_connection():
        for port in test_ports:
            port.set_connection_mode(not port.connection_mode)
    btn_toggle_connection.clicked.connect(toggle_connection)
    layout.addWidget(btn_toggle_connection)
    
    window.setCentralWidget(central_widget)
    window.setWindowTitle("Test Ports avec Scale")
    window.show()
    
    print("=== TEST PORTS AVEC SCALE ===")
    print("• Utilisez le slider pour changer la taille des ports")
    print("• Cliquez sur les ports pour tester les événements")
    print("• 'Debug Info' pour voir les détails")
    
    sys.exit(app.exec())
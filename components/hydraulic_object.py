#!/usr/bin/env python3
"""
components/hydraulic_object.py - Classe hydraulique unifiée v3.0 CORRIGÉE
Gestion correcte du scale SVG et positions des ports
"""

from PyQt6.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QByteArray, QPointF, pyqtSignal, QObject
from PyQt6.QtGui import QPen, QBrush, QColor

from typing import Dict, List, Any, Optional

# Import configuration avec gestion des chemins
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from config.hydraulic_objects import get_object_config, get_port_configs
except ImportError:
    # Si import direct échoue, essayer chemin relatif
    import importlib.util
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'hydraulic_objects.py')
    spec = importlib.util.spec_from_file_location("hydraulic_objects", config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    get_object_config = config_module.get_object_config
    get_port_configs = config_module.get_port_configs

# Import du système de ports existant
try:
    from .ports import Port
except ImportError:
    from ports import Port

class HydraulicObjectSignals(QObject):
    """Signaux pour HydraulicObject (Qt nécessite QObject)"""
    properties_changed = pyqtSignal(str, dict)  # object_id, new_properties
    position_changed = pyqtSignal(str, QPointF)  # object_id, new_position
    selected = pyqtSignal(str)  # object_id
    scale_changed = pyqtSignal(str, float)  # object_id, new_scale

class HydraulicObject(QGraphicsItemGroup):
    """
    Classe hydraulique unifiée avec gestion scale correcte
    VERSION CORRIGÉE pour synchronisation SVG/ports
    """
    
    # Signaux partagés
    _signals = HydraulicObjectSignals()
    
    # Scale global par défaut (peut être modifié par la WorkArea)
    GLOBAL_SCALE = 1.0
    
    def __init__(self, component_id: str, object_type: str, properties: Dict[str, Any] = None):
        super().__init__()
        
        # Identité de l'objet
        self.component_id = component_id
        self.object_type = object_type
        
        # Configuration depuis HYDRAULIC_OBJECT_TYPES
        self.config = get_object_config(object_type)
        if not self.config:
            raise ValueError(f"Type d'objet inconnu: {object_type}")
        
        # Propriétés hydrauliques
        self.properties = self.config.get("default_properties", {}).copy()
        if properties:
            self.properties.update(properties)
        
        # GESTION SCALE AMÉLIORÉE
        self.base_svg_scale = self.config.get("svg_scale", 1.0)  # Scale SVG depuis config
        self.current_scale = self.base_svg_scale * self.GLOBAL_SCALE  # Scale effectif
        
        # Éléments graphiques
        self.main_shape = None
        self.ports: List[Port] = []
        
        # État de l'objet
        self.is_created = False
        
        # Construction de l'objet
        self.create_appearance()
        self.create_ports()
        self.setup_graphics()
        
        # APPLIQUER LE SCALE AU GROUPE ENTIER
        self.setScale(self.current_scale)
        
        # IMPORTANT: Mettre à jour les positions des ports APRÈS le scale du groupe
        self.update_ports_scale()
        
        self.is_created = True
        
        print(f"[HYDRAULIC_OBJECT] Créé: {component_id} ({object_type}) - Scale: {self.current_scale}")
    
    def create_appearance(self):
        """Crée l'apparence visuelle basée sur la configuration"""
        svg_content = self.config.get("svg_content")
        
        if svg_content:
            self.create_svg_shape(svg_content)
        else:
            self.create_fallback_shape()
    
    def create_svg_shape(self, svg_content: str):
        """Crée la forme SVG SANS scale (sera appliqué au groupe)"""
        try:
            svg_item = QGraphicsSvgItem()
            
            # Préparer le contenu SVG
            if isinstance(svg_content, str):
                svg_bytes = QByteArray(svg_content.encode('utf-8'))
            else:
                svg_bytes = svg_content
            
            # Créer le renderer SVG
            renderer = QSvgRenderer(svg_bytes)
            if renderer.isValid():
                svg_item.setSharedRenderer(renderer)
                
                # PAS de scale ici - le scale sera appliqué au groupe entier
                # svg_item.setScale(self.current_scale)  
                
                self.addToGroup(svg_item)
                self.main_shape = svg_item
                
                print(f"[HYDRAULIC_OBJECT] SVG chargé pour {self.component_id} (scale via groupe)")
            else:
                print(f"[HYDRAULIC_OBJECT] SVG invalide pour {self.component_id}, fallback utilisé")
                self.create_fallback_shape()
                
        except Exception as e:
            print(f"[HYDRAULIC_OBJECT] Erreur SVG pour {self.component_id}: {e}")
            self.create_fallback_shape()
    
    def create_fallback_shape(self):
        """Crée une forme de fallback SANS scale (sera appliqué au groupe)"""
        # Paramètres depuis la configuration - TAILLE DE BASE
        base_size = self.config.get("fallback_size", (60, 40))
        color_str = self.config.get("fallback_color", "#FFB6C1")
        
        # Taille de base, le scale sera appliqué au groupe
        width = base_size[0]
        height = base_size[1]
        
        # Conversion couleur string vers QColor
        if isinstance(color_str, str):
            color = QColor(color_str)
        else:
            color = color_str
        
        # Créer rectangle avec taille de base
        rect = QGraphicsRectItem(0, 0, width, height)
        rect.setPen(QPen(QColor(0, 100, 200), 2))
        rect.setBrush(QBrush(color))
        
        self.addToGroup(rect)
        self.main_shape = rect
        
        print(f"[HYDRAULIC_OBJECT] Fallback créé pour {self.component_id}: {width}x{height} (scale via groupe)")
    
    def create_ports(self):
        """Crée les ports avec positions BASE (le scale du groupe s'appliquera automatiquement)"""
        port_configs = get_port_configs(self.object_type)
        
        for port_config in port_configs:
            port_id = port_config["id"]
            port_type = port_config["type"]
            base_position = port_config["position"]
            
            # Convertir position SANS appliquer de scale
            # Le scale sera géré par le groupe ET par update_ports_scale()
            if isinstance(base_position, (list, tuple)):
                position = QPointF(float(base_position[0]), float(base_position[1]))
            else:
                position = base_position
            
            # Créer le port avec position de base
            port = Port(port_id, port_type, position, self)
            self.ports.append(port)
            
            print(f"[HYDRAULIC_OBJECT] Port créé: {port_id} à {position} (position de base)")
    
    def setup_graphics(self):
        """Configuration graphique de l'objet"""
        # Propriétés graphiques
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        # Z-index par défaut
        self.setZValue(10)
    
    # === GESTION SCALE GLOBALE ===
    
    @classmethod
    def set_global_scale(cls, scale: float):
        """Définit le scale global pour tous les objets hydrauliques"""
        cls.GLOBAL_SCALE = scale
        print(f"[HYDRAULIC_OBJECT] Scale global défini: {scale}")
    
    @classmethod
    def get_global_scale(cls) -> float:
        """Retourne le scale global actuel"""
        return cls.GLOBAL_SCALE
    
    def update_scale(self, new_global_scale: float = None):
        """Met à jour le scale de cet objet spécifique - VERSION SIMPLE avec setScale()"""
        if new_global_scale is not None:
            # Calculer nouveau scale effectif
            new_scale = self.base_svg_scale * new_global_scale
        else:
            # Utiliser le scale global actuel
            new_scale = self.base_svg_scale * self.GLOBAL_SCALE
        
        if new_scale != self.current_scale:
            old_scale = self.current_scale
            self.current_scale = new_scale
            
            # SOLUTION SIMPLE: Appliquer le scale au groupe entier !
            self.setScale(self.current_scale)
            
            # Mettre à jour positions des ports (qui sont HORS du groupe)
            self.update_ports_scale()
            
            # Émettre signal
            if self.is_created:
                self._signals.scale_changed.emit(self.component_id, self.current_scale)
            
            print(f"[HYDRAULIC_OBJECT] Scale groupe mis à jour: {self.component_id} {old_scale} → {self.current_scale}")
    
    def update_ports_scale(self):
        """Met à jour les positions ET tailles des ports selon le nouveau scale"""
        port_configs = get_port_configs(self.object_type)
        
        for i, port in enumerate(self.ports):
            if i < len(port_configs):
                base_position = port_configs[i]["position"]
                
                # Recalculer position avec nouveau scale
                if isinstance(base_position, (list, tuple)):
                    scaled_x = float(base_position[0]) * self.current_scale
                    scaled_y = float(base_position[1]) * self.current_scale
                    new_position = QPointF(scaled_x, scaled_y)
                    
                    # Mettre à jour position initiale du port
                    port.initial_position = new_position
                    
                    # Si le port est dans une scène, mettre à jour sa position globale
                    if port.scene():
                        global_pos = self.scenePos() + new_position
                        port.setPos(global_pos)
                    
                    # NOUVEAU: Mettre à jour la taille du port selon le scale
                    if hasattr(port, 'update_scale'):
                        port.update_scale(self.current_scale)
                    
                    print(f"[HYDRAULIC_OBJECT] Port {port.port_id} mis à jour: pos={new_position}, scale={self.current_scale}")
    
    def get_effective_scale(self) -> float:
        """Retourne le scale effectif actuel de l'objet"""
        return self.current_scale
    
    def get_base_svg_scale(self) -> float:
        """Retourne le scale SVG de base depuis la configuration"""
        return self.base_svg_scale
    
    # === GESTION DES PORTS (inchangé) ===
    
    def get_port_by_id(self, port_id: str) -> Optional[Port]:
        """Récupère un port par son ID"""
        for port in self.ports:
            if port.port_id == port_id:
                return port
        return None
    
    def get_available_ports(self) -> List[Port]:
        """Retourne les ports libres"""
        return [port for port in self.ports if not port.is_connected]
    
    def get_connected_ports(self) -> List[Port]:
        """Retourne les ports connectés"""
        return [port for port in self.ports if port.is_connected]
    
    def set_connection_mode(self, active: bool):
        """Active/désactive le mode connexion pour tous les ports"""
        for port in self.ports:
            port.set_connection_mode(active)
    
    # === GESTION DES PROPRIÉTÉS (inchangé) ===
    
    def get_property(self, key: str, default=None):
        """Récupère une propriété hydraulique"""
        return self.properties.get(key, default)
    
    def set_property(self, key: str, value: Any):
        """Modifie une propriété hydraulique"""
        old_value = self.properties.get(key)
        self.properties[key] = value
        
        # Émettre signal si changement et objet créé
        if old_value != value and self.is_created:
            self._signals.properties_changed.emit(self.component_id, {key: value})
            print(f"[HYDRAULIC_OBJECT] Propriété mise à jour: {self.component_id}.{key} = {value}")
    
    def update_properties(self, new_properties: Dict[str, Any]):
        """Met à jour plusieurs propriétés"""
        changes = {}
        
        for key, value in new_properties.items():
            old_value = self.properties.get(key)
            if old_value != value:
                self.properties[key] = value
                changes[key] = value
        
        # Émettre signal si changements
        if changes and self.is_created:
            self._signals.properties_changed.emit(self.component_id, changes)
            print(f"[HYDRAULIC_OBJECT] Propriétés mises à jour: {self.component_id} ({len(changes)} changements)")
    
    def get_all_properties(self) -> Dict[str, Any]:
        """Retourne toutes les propriétés"""
        return self.properties.copy()
    
    # === ÉVÉNEMENTS GRAPHIQUES ===
    
    def itemChange(self, change, value):
        """Notification de changement - synchronise ports et signaux"""
        if change == QGraphicsItemGroup.GraphicsItemChange.ItemPositionChange:
            # Mettre à jour les positions des ports
            self.update_ports_positions(value)
            
            # Mettre à jour tous les tuyaux connectés
            for port in self.get_connected_ports():
                if port.connected_pipe and hasattr(port.connected_pipe, 'update_path'):
                    port.connected_pipe.update_path()
        
        elif change == QGraphicsItemGroup.GraphicsItemChange.ItemPositionHasChanged:
            # Émettre signal de déplacement
            if self.is_created:
                self._signals.position_changed.emit(self.component_id, value)
        
        elif change == QGraphicsItemGroup.GraphicsItemChange.ItemSelectedHasChanged:
            # Émettre signal de sélection
            if value and self.is_created:  # Sélectionné
                self._signals.selected.emit(self.component_id)
        
        return super().itemChange(change, value)
    
    def update_ports_positions(self, new_component_position: QPointF):
        """Met à jour les positions des ports quand l'objet bouge"""
        for port in self.ports:
            # Calculer la nouvelle position globale du port (avec scale correct)
            global_port_pos = new_component_position + port.initial_position
            port.setPos(global_port_pos)
    
    def mousePressEvent(self, event):
        """Gestion des clics sur l'objet"""
        print(f"[HYDRAULIC_OBJECT] Clic sur {self.component_id}")
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Double-clic = propriétés de l'objet"""
        print(f"[HYDRAULIC_OBJECT] Propriétés de {self.component_id}:")
        self.show_properties_summary()
        super().mouseDoubleClickEvent(event)
    
    # === INFORMATIONS ET DEBUG ===
    
    def show_properties_summary(self):
        """Affiche un résumé des propriétés pour debug"""
        print(f"\n=== PROPRIÉTÉS {self.component_id} ===")
        print(f"Type: {self.object_type}")
        print(f"Nom d'affichage: {self.config.get('display_name', 'N/A')}")
        print(f"Description: {self.config.get('description', 'N/A')}")
        
        print(f"\nScale:")
        print(f"  Scale SVG base: {self.base_svg_scale}")
        print(f"  Scale global: {self.GLOBAL_SCALE}")
        print(f"  Scale effectif: {self.current_scale}")
        
        print(f"\nPropriétés hydrauliques:")
        for key, value in self.properties.items():
            unit = ""
            constraints = self.config.get("property_constraints", {}).get(key, {})
            if "unit" in constraints:
                unit = f" {constraints['unit']}"
            print(f"  {key}: {value}{unit}")
        
        print(f"\nPorts ({len(self.ports)}):")
        for port in self.ports:
            status = "CONNECTÉ" if port.is_connected else "LIBRE"
            pos = port.initial_position
            print(f"  {port.port_id} ({port.port_type}): {status} @ {pos}")
        
        print("=" * (len(self.component_id) + 15) + "\n")
    
    def get_object_info(self) -> Dict[str, Any]:
        """Informations complètes pour API"""
        return {
            "id": self.component_id,
            "type": self.object_type,
            "display_name": self.config.get("display_name", self.object_type),
            "properties": self.properties.copy(),
            "position": self.scenePos(),
            "scale_info": {
                "base_svg_scale": self.base_svg_scale,
                "global_scale": self.GLOBAL_SCALE,
                "effective_scale": self.current_scale
            },
            "ports": [
                {
                    "id": port.port_id,
                    "type": port.port_type,
                    "connected": port.is_connected,
                    "position": port.get_global_position(),
                    "initial_position": port.initial_position
                }
                for port in self.ports
            ],
            "epanet_type": self.config.get("epanet_type"),
            "configuration": {
                "has_svg": self.config.get("svg_content") is not None,
                "ports_count": len(self.ports),
                "available_ports": len(self.get_available_ports()),
                "connected_ports": len(self.get_connected_ports())
            }
        }
    
    # === SÉRIALISATION ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialise l'objet pour sauvegarde"""
        return {
            "component_id": self.component_id,
            "object_type": self.object_type,
            "properties": self.properties,
            "position": {
                "x": self.scenePos().x(),
                "y": self.scenePos().y()
            },
            "scale_info": {
                "base_svg_scale": self.base_svg_scale,
                "current_scale": self.current_scale
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HydraulicObject':
        """Recrée un objet depuis les données sérialisées"""
        obj = cls(
            data["component_id"],
            data["object_type"],
            data["properties"]
        )
        
        # Restaurer position
        pos_data = data.get("position", {"x": 0, "y": 0})
        obj.setPos(QPointF(pos_data["x"], pos_data["y"]))
        
        # Restaurer scale si disponible
        scale_info = data.get("scale_info", {})
        if "current_scale" in scale_info:
            obj.current_scale = scale_info["current_scale"]
            obj.update_scale()
        
        return obj
    
    # === INTÉGRATION EPANET (interface future) ===
    
    def get_epanet_type(self) -> Optional[str]:
        """Retourne le type EPANET correspondant"""
        return self.config.get("epanet_type")
    
    def get_epanet_properties(self) -> Dict[str, Any]:
        """Retourne les propriétés formatées pour EPANET"""
        epanet_props = {}
        
        # Filtrer et convertir les propriétés selon le type EPANET
        epanet_type = self.get_epanet_type()
        
        if epanet_type == "PUMP":
            epanet_props.update({
                "flow_rate": self.get_property("flow_rate", 100.0),
                "pressure_head": self.get_property("pressure_head", 50.0),
                "efficiency": self.get_property("efficiency", 0.85)
            })
        elif epanet_type == "VALVE":
            epanet_props.update({
                "diameter": self.get_property("diameter", 100.0),
                "valve_type": self.get_property("valve_type", "PRV"),
                "setting": self.get_property("setting", 30.0)
            })
        elif epanet_type == "RESERVOIR":
            epanet_props.update({
                "head": self.get_property("head", 100.0)
            })
        elif epanet_type == "TANK":
            epanet_props.update({
                "elevation": self.get_property("elevation", 50.0),
                "init_level": self.get_property("init_level", 10.0),
                "min_level": self.get_property("min_level", 0.0),
                "max_level": self.get_property("max_level", 20.0),
                "diameter": self.get_property("diameter", 10.0)
            })
        
        return epanet_props


# === FONCTION DE CRÉATION AVEC SCALE ===

def create_hydraulic_object(component_id: str, object_type: str, 
                           properties: Dict[str, Any] = None,
                           position: QPointF = None,
                           custom_scale: float = None) -> HydraulicObject:
    """
    Fonction utilitaire pour créer facilement un objet hydraulique
    VERSION AMÉLIORÉE avec gestion scale
    
    Args:
        component_id: Identifiant unique de l'objet
        object_type: Type d'objet (PUMP, VALVE, RESERVOIR, TANK)
        properties: Propriétés personnalisées (optionnel)
        position: Position graphique (optionnel)
        custom_scale: Scale personnalisé pour cet objet (optionnel)
    
    Returns:
        HydraulicObject configuré et prêt à utiliser
    """
    # Créer l'objet
    obj = HydraulicObject(component_id, object_type, properties)
    
    # Appliquer scale personnalisé si spécifié
    if custom_scale is not None:
        obj.update_scale(custom_scale)
    
    # Positionner si spécifié
    if position:
        obj.setPos(position)
    
    return obj

def rotate_ports_around_center(self, angle_degrees: float):
    """
    Fait tourner les ports autour du centre de l'objet
    À appeler lors des rotations via TransformController
    
    Args:
        angle_degrees: Angle de rotation en degrés (positif = sens horaire)
    """
    if not self.ports:
        return
    
    import math
    
    # Convertir angle en radians
    angle_rad = math.radians(angle_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    print(f"[HYDRAULIC_OBJECT] Rotation ports de {self.component_id}: {angle_degrees}°")
    
    for port in self.ports:
        # Position initiale relative à l'objet
        old_rel_pos = port.initial_position
        
        # Calculer nouvelle position relative après rotation
        old_x = old_rel_pos.x()
        old_y = old_rel_pos.y()
        
        new_x = old_x * cos_a - old_y * sin_a
        new_y = old_x * sin_a + old_y * cos_a
        
        # Mettre à jour la position initiale du port
        port.initial_position = QPointF(new_x, new_y)
        
        # Calculer et appliquer nouvelle position globale
        global_pos = self.scenePos() + QPointF(new_x, new_y)
        port.setPos(global_pos)
        
        print(f"[HYDRAULIC_OBJECT]   Port {port.port_id}: ({old_x:.1f}, {old_y:.1f}) → ({new_x:.1f}, {new_y:.1f})")

def get_ports_relative_positions(self) -> dict:
    """
    Retourne les positions relatives de tous les ports
    Utile pour debug et vérification
    """
    positions = {}
    for port in self.ports:
        positions[port.port_id] = {
            "initial_position": port.initial_position,
            "global_position": port.scenePos(),
            "relative_to_object": port.scenePos() - self.scenePos()
        }
    return positions

def reset_ports_to_config_positions(self):
    """
    Remet les ports à leurs positions de configuration d'origine
    Utile en cas de problème avec les rotations
    """
    from config.hydraulic_objects import get_port_configs
    
    port_configs = get_port_configs(self.object_type)
    
    for i, port in enumerate(self.ports):
        if i < len(port_configs):
            base_position = port_configs[i]["position"]
            
            # Recalculer position avec scale actuel
            if isinstance(base_position, (list, tuple)):
                scaled_x = float(base_position[0]) * self.current_scale
                scaled_y = float(base_position[1]) * self.current_scale
                new_position = QPointF(scaled_x, scaled_y)
                
                # Remettre position initiale
                port.initial_position = new_position
                
                # Recalculer position globale
                global_pos = self.scenePos() + new_position
                port.setPos(global_pos)
                
                print(f"[HYDRAULIC_OBJECT] Port {port.port_id} remis à la position d'origine: {new_position}")

# === EXEMPLE D'INTÉGRATION DANS LE TRANSFORM CONTROLLER ===
"""
Remplacer la méthode _rotate_object_ports dans TransformController par :

def _rotate_object_ports(self, obj, angle_degrees: float, object_center: QPointF):
    '''Fait tourner les ports en utilisant la méthode de l'objet'''
    try:
        if hasattr(obj, 'rotate_ports_around_center'):
            obj.rotate_ports_around_center(angle_degrees)
        else:
            print(f"[TRANSFORM] Objet {getattr(obj, 'component_id', 'unknown')} ne supporte pas la rotation des ports")
    except Exception as e:
        print(f"[TRANSFORM] Erreur rotation ports: {e}")
"""


# === EXEMPLES D'UTILISATION ===

if __name__ == "__main__":
    # Test du système de scale
    from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider, QLabel
    import sys
    
    app = QApplication(sys.argv)
    
    # Créer interface de test
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Contrôles de scale
    scale_label = QLabel(f"Scale global: {HydraulicObject.get_global_scale():.2f}")
    layout.addWidget(scale_label)
    
    scale_slider = QSlider(Qt.Orientation.Horizontal)
    scale_slider.setMinimum(50)  # 0.5x
    scale_slider.setMaximum(300)  # 3.0x
    scale_slider.setValue(100)  # 1.0x
    layout.addWidget(scale_slider)
    
    # Créer la scène
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    layout.addWidget(view)
    
    # Créer objets de test
    pump = create_hydraulic_object("pump_test", "PUMP", position=QPointF(100, 100))
    valve = create_hydraulic_object("valve_test", "VALVE", position=QPointF(300, 100))
    reservoir = create_hydraulic_object("reservoir_test", "RESERVOIR", position=QPointF(100, 300))
    tank = create_hydraulic_object("tank_test", "TANK", position=QPointF(300, 300))
    
    # Ajouter à la scène
    objects = [pump, valve, reservoir, tank]
    for obj in objects:
        scene.addItem(obj)
        # Ajouter ports
        for port in obj.ports:
            port.setPos(obj.scenePos() + port.initial_position)
            scene.addItem(port)
    
    # Fonction de mise à jour du scale
    def update_scale(value):
        new_scale = value / 100.0  # Conversion slider → scale
        HydraulicObject.set_global_scale(new_scale)
        
        # Mettre à jour tous les objets
        for obj in objects:
            obj.update_scale()
        
        scale_label.setText(f"Scale global: {new_scale:.2f}")
    
    scale_slider.valueChanged.connect(update_scale)
    
    # Bouton reset
    reset_btn = QPushButton("Reset Scale (1.0)")
    reset_btn.clicked.connect(lambda: scale_slider.setValue(100))
    layout.addWidget(reset_btn)
    
    # Bouton info
    info_btn = QPushButton("Afficher info scale")
    def show_info():
        for obj in objects:
            print(f"\n{obj.component_id}:")
            print(f"  Scale base SVG: {obj.get_base_svg_scale()}")
            print(f"  Scale effectif: {obj.get_effective_scale()}")
            print(f"  Positions ports:")
            for port in obj.ports:
                print(f"    {port.port_id}: {port.initial_position}")
    
    info_btn.clicked.connect(show_info)
    layout.addWidget(info_btn)
    
    window.setCentralWidget(central_widget)
    window.setWindowTitle("Test HydraulicObject Scale Corrigé")
    window.show()
    
    print("=== TEST SCALE HYDRAULIC OBJECT ===")
    print("• Utilisez le slider pour changer le scale global")
    print("• Vérifiez que les ports suivent le SVG")
    print("• Cliquez 'Afficher info scale' pour debug")
    
    sys.exit(app.exec())
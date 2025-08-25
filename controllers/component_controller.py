#!/usr/bin/env python3
"""
controllers/component_controller.py - Contrôleur unifié v3.0 INTÉGRÉ
Logique métier pure avec intégration HydraulicObject unifié
"""

from typing import Dict, List, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QPointF
from PyQt6.QtWidgets import QGraphicsScene

# Import de la configuration
from config.hydraulic_objects import (
    HYDRAULIC_OBJECT_TYPES, get_object_config, get_default_properties,
    validate_property, get_port_configs
)

# Import de la classe unifiée
from components.hydraulic_object import HydraulicObject, create_hydraulic_object

class ComponentController(QObject):
    """
    Contrôleur unifié pour tous les composants hydrauliques v3.0
    Responsabilité : Logique de création, gestion et manipulation avec HydraulicObject
    """
    
    # === SIGNAUX ÉMIS ===
    
    # Événements d'objets
    object_added = pyqtSignal(str, str)                    # object_id, object_type
    object_removed = pyqtSignal(str)                       # object_id
    object_selected = pyqtSignal(str)                      # object_id
    object_moved = pyqtSignal(str, QPointF)                # object_id, new_position
    object_properties_changed = pyqtSignal(str, dict)      # object_id, properties
    
    # Événements de collection
    objects_count_changed = pyqtSignal(int)                # new_count
    objects_cleared = pyqtSignal()
    
    # Événements d'erreur
    object_creation_failed = pyqtSignal(str, str)          # object_type, error_message
    property_validation_failed = pyqtSignal(str, str, str) # object_id, property, error
    
    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        
        self.scene = scene
        
        # Collections des objets unifiés
        self.objects: Dict[str, HydraulicObject] = {}  # object_id -> HydraulicObject
        self.objects_by_type: Dict[str, List[str]] = {}  # object_type -> [object_ids]
        
        # Compteurs pour génération d'IDs
        self.type_counters: Dict[str, int] = {}
        
        # Configuration de positionnement automatique
        self.next_position = QPointF(100, 100)
        self.position_offset = QPointF(150, 120)
        self.max_objects_per_row = 6
        self.current_row_count = 0
        
        print("[COMPONENT_CONTROLLER] Contrôleur v3.0 initialisé avec HydraulicObject unifié")
    
    # === CRÉATION D'OBJETS UNIFIÉE ===
    
    def add_object(self, object_type: str, custom_properties: Dict[str, Any] = None,
                   position: QPointF = None) -> Optional[str]:
        """
        Méthode unique pour créer tout type d'objet hydraulique
        NOUVELLE VERSION INTÉGRÉE avec HydraulicObject
        
        Args:
            object_type: Type d'objet (PUMP, VALVE, RESERVOIR, TANK)
            custom_properties: Propriétés personnalisées (override des défauts)
            position: Position spécifique (sinon auto-calculée)
            
        Returns:
            object_id si succès, None si échec
        """
        print(f"[COMPONENT_CONTROLLER] Création objet unifié: {object_type}")
        
        try:
            # Vérifier que le type existe dans la configuration
            if object_type not in HYDRAULIC_OBJECT_TYPES:
                error_msg = f"Type d'objet inconnu: {object_type}"
                self.object_creation_failed.emit(object_type, error_msg)
                return None
            
            # Générer ID unique
            object_id = self.generate_object_id(object_type)
            
            # Calculer position
            if position is None:
                position = self.calculate_next_position()
            
            # Préparer propriétés validées
            properties = self.prepare_object_properties(object_type, custom_properties)
            
            # CRÉER L'OBJET HYDRAULIQUE UNIFIÉ
            hydraulic_obj = create_hydraulic_object(object_id, object_type, properties, position)
            
            # Ajouter à la scène
            self.scene.addItem(hydraulic_obj)
            
            # Ajouter les ports à la scène avec positions correctes
            self.add_object_ports_to_scene(hydraulic_obj, position)
            
            # Enregistrer l'objet dans les collections
            self.register_object(hydraulic_obj, object_type)
            
            # Connecter les signaux de l'objet unifié
            self.connect_object_signals(hydraulic_obj)
            
            # Émettre signaux de succès
            self.object_added.emit(object_id, object_type)
            self.objects_count_changed.emit(len(self.objects))
            
            print(f"[COMPONENT_CONTROLLER] Objet unifié créé avec succès: {object_id} ({object_type})")
            return object_id
            
        except Exception as e:
            error_msg = f"Erreur création {object_type}: {str(e)}"
            print(f"[COMPONENT_CONTROLLER] {error_msg}")
            import traceback
            traceback.print_exc()
            self.object_creation_failed.emit(object_type, error_msg)
            return None
    
    def generate_object_id(self, object_type: str) -> str:
        """Génère un ID unique pour un type d'objet"""
        if object_type not in self.type_counters:
            self.type_counters[object_type] = 0
        
        self.type_counters[object_type] += 1
        counter = self.type_counters[object_type]
        
        # Format: pump_001, valve_002, etc.
        prefix = object_type.lower()
        return f"{prefix}_{counter:03d}"
    
    def calculate_next_position(self) -> QPointF:
        """Calcule la prochaine position pour un objet (disposition automatique)"""
        position = QPointF(self.next_position)
        
        # Avancer à la position suivante
        self.current_row_count += 1
        
        if self.current_row_count >= self.max_objects_per_row:
            # Nouvelle ligne
            self.next_position.setX(100)
            self.next_position += QPointF(0, self.position_offset.y())
            self.current_row_count = 0
        else:
            # Même ligne
            self.next_position += QPointF(self.position_offset.x(), 0)
        
        return position
    
    def prepare_object_properties(self, object_type: str, 
                                 custom_properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prépare les propriétés finales d'un objet avec validation"""
        # Propriétés par défaut du type
        properties = get_default_properties(object_type)
        
        # Override avec propriétés personnalisées validées
        if custom_properties:
            for key, value in custom_properties.items():
                if validate_property(object_type, key, value):
                    properties[key] = value
                else:
                    self.property_validation_failed.emit("new_object", key, 
                                                       f"Valeur invalide: {value}")
        
        return properties
    
    def add_object_ports_to_scene(self, hydraulic_obj: HydraulicObject, position: QPointF):
        """Ajoute les ports de l'objet à la scène avec positions correctes"""
        for port in hydraulic_obj.ports:
            # Les positions sont déjà correctes grâce à update_ports_scale() dans HydraulicObject
            # Calculer position globale du port (position composant + position relative du port)
            global_port_pos = position + port.initial_position
            port.setPos(global_port_pos)
            
            # Ajouter le port à la scène
            self.scene.addItem(port)
        
        print(f"[COMPONENT_CONTROLLER] {len(hydraulic_obj.ports)} ports ajoutés à la scène avec positions correctes")
    
    def register_object(self, hydraulic_obj: HydraulicObject, object_type: str):
        """Enregistre l'objet dans les collections"""
        object_id = hydraulic_obj.component_id
        
        # Collection principale
        self.objects[object_id] = hydraulic_obj
        
        # Collection par type
        if object_type not in self.objects_by_type:
            self.objects_by_type[object_type] = []
        self.objects_by_type[object_type].append(object_id)
        
        print(f"[COMPONENT_CONTROLLER] Objet enregistré: {object_id}")
    
    def connect_object_signals(self, hydraulic_obj: HydraulicObject):
        """Connecte les signaux de l'objet unifié aux handlers du contrôleur"""
        # Connexion des signaux HydraulicObject
        hydraulic_obj._signals.position_changed.connect(self.on_object_moved)
        hydraulic_obj._signals.properties_changed.connect(self.on_object_properties_changed)
        hydraulic_obj._signals.selected.connect(self.on_object_selected)
        
        print(f"[COMPONENT_CONTROLLER] Signaux connectés pour {hydraulic_obj.component_id}")
    
    # === GESTION DES OBJETS ===
    
    def get_object(self, object_id: str) -> Optional[HydraulicObject]:
        """Récupère un objet par son ID"""
        return self.objects.get(object_id)
    
    def get_objects_by_type(self, object_type: str) -> List[HydraulicObject]:
        """Récupère tous les objets d'un type donné"""
        object_ids = self.objects_by_type.get(object_type, [])
        return [self.objects[obj_id] for obj_id in object_ids if obj_id in self.objects]
    
    def get_all_objects(self) -> List[HydraulicObject]:
        """Retourne tous les objets"""
        return list(self.objects.values())
    
    def remove_object(self, object_id: str) -> bool:
        """Supprime un objet et ses ports"""
        if object_id not in self.objects:
            return False
        
        try:
            hydraulic_obj = self.objects[object_id]
            
            # Déconnecter les signaux
            try:
                hydraulic_obj._signals.position_changed.disconnect()
                hydraulic_obj._signals.properties_changed.disconnect()
                hydraulic_obj._signals.selected.disconnect()
            except:
                pass  # Signaux déjà déconnectés
            
            # Supprimer les ports de la scène
            for port in hydraulic_obj.ports:
                # Déconnecter le port si connecté
                if port.is_connected and port.connected_pipe:
                    # TODO: Gérer suppression des tuyaux connectés
                    port.disconnect_from_pipe()
                
                # Supprimer de la scène
                if port.scene():
                    self.scene.removeItem(port)
            
            # Supprimer l'objet principal de la scène
            if hydraulic_obj.scene():
                self.scene.removeItem(hydraulic_obj)
            
            # Supprimer des collections
            del self.objects[object_id]
            
            # Supprimer de la collection par type
            for object_type, object_ids in self.objects_by_type.items():
                if object_id in object_ids:
                    object_ids.remove(object_id)
                    break
            
            # Signaux
            self.object_removed.emit(object_id)
            self.objects_count_changed.emit(len(self.objects))
            
            print(f"[COMPONENT_CONTROLLER] Objet supprimé: {object_id}")
            return True
            
        except Exception as e:
            print(f"[COMPONENT_CONTROLLER] Erreur suppression {object_id}: {e}")
            return False
    
    def update_object_properties(self, object_id: str, properties: Dict[str, Any]) -> bool:
        """Met à jour les propriétés d'un objet"""
        if object_id not in self.objects:
            return False
        
        hydraulic_obj = self.objects[object_id]
        object_type = hydraulic_obj.object_type
        
        # Valider et appliquer les propriétés
        validated_properties = {}
        for key, value in properties.items():
            if validate_property(object_type, key, value):
                validated_properties[key] = value
            else:
                self.property_validation_failed.emit(object_id, key, f"Valeur invalide: {value}")
        
        if validated_properties:
            # Utiliser la méthode unifiée de HydraulicObject
            hydraulic_obj.update_properties(validated_properties)
            print(f"[COMPONENT_CONTROLLER] Propriétés mises à jour: {object_id}")
            return True
        
        return False
    
    def select_object(self, object_id: str):
        """Sélectionne un objet"""
        if object_id in self.objects:
            hydraulic_obj = self.objects[object_id]
            hydraulic_obj.setSelected(True)
    
    def clear_selection(self):
        """Désélectionne tous les objets"""
        self.scene.clearSelection()
    
    def set_connection_mode(self, active: bool):
        """Active/désactive le mode connexion pour tous les objets"""
        for hydraulic_obj in self.objects.values():
            hydraulic_obj.set_connection_mode(active)
        
        print(f"[COMPONENT_CONTROLLER] Mode connexion: {'ACTIVÉ' if active else 'DÉSACTIVÉ'} pour {len(self.objects)} objets")
    
    # === GESTION GLOBALE ===
    
    def clear_all(self):
        """Supprime tous les objets"""
        object_ids = list(self.objects.keys())
        
        for object_id in object_ids:
            self.remove_object(object_id)
        
        # Réinitialiser les compteurs
        self.type_counters.clear()
        self.objects_by_type.clear()
        
        # Réinitialiser positionnement
        self.next_position = QPointF(100, 100)
        self.current_row_count = 0
        
        self.objects_cleared.emit()
        print("[COMPONENT_CONTROLLER] Tous les objets supprimés")
    
    def get_all_components_info(self) -> Dict[str, Any]:
        """Retourne des informations complètes sur tous les composants"""
        components_info = []
        
        for object_id, hydraulic_obj in self.objects.items():
            # Utiliser la méthode unifiée get_object_info
            info = hydraulic_obj.get_object_info()
            components_info.append(info)
        
        # Statistiques par type
        type_stats = {}
        for object_type, object_ids in self.objects_by_type.items():
            type_stats[object_type] = len(object_ids)
        
        return {
            "components": components_info,
            "total_components": len(self.objects),
            "by_type": type_stats,
            "next_position": self.next_position,
            "available_types": list(HYDRAULIC_OBJECT_TYPES.keys()),
            "architecture_version": "3.0_unified"
        }
    
    def get_objects_summary(self) -> Dict[str, Any]:
        """Résumé rapide pour affichage"""
        summary = {
            "total": len(self.objects),
            "by_type": {},
            "with_connections": 0
        }
        
        for hydraulic_obj in self.objects.values():
            obj_type = hydraulic_obj.object_type
            summary["by_type"][obj_type] = summary["by_type"].get(obj_type, 0) + 1
            
            # Compter objets avec connexions
            if hydraulic_obj.get_connected_ports():
                summary["with_connections"] += 1
        
        return summary
    
    # === SLOTS POUR ÉVÉNEMENTS OBJETS ===
    
    def on_object_moved(self, object_id: str, new_position: QPointF):
        """Réaction au déplacement d'un objet"""
        self.object_moved.emit(object_id, new_position)
        print(f"[COMPONENT_CONTROLLER] Objet déplacé: {object_id} -> {new_position}")
    
    def on_object_selected(self, object_id: str):
        """Réaction à la sélection d'un objet"""
        self.object_selected.emit(object_id)
        print(f"[COMPONENT_CONTROLLER] Objet sélectionné: {object_id}")
    
    def on_object_properties_changed(self, object_id: str, properties: Dict[str, Any]):
        """Réaction au changement de propriétés"""
        self.object_properties_changed.emit(object_id, properties)
        print(f"[COMPONENT_CONTROLLER] Propriétés changées: {object_id} -> {list(properties.keys())}")
    
    # === EXPORT ET SÉRIALISATION ===
    
    def export_objects_data(self) -> List[Dict[str, Any]]:
        """Exporte tous les objets pour sauvegarde"""
        return [obj.to_dict() for obj in self.objects.values()]
    
    def import_objects_data(self, objects_data: List[Dict[str, Any]]):
        """Importe des objets depuis des données sauvegardées"""
        self.clear_all()
        
        for obj_data in objects_data:
            try:
                # Recréer l'objet
                hydraulic_obj = HydraulicObject.from_dict(obj_data)
                
                # Ajouter à la scène
                self.scene.addItem(hydraulic_obj)
                self.add_object_ports_to_scene(hydraulic_obj, hydraulic_obj.scenePos())
                
                # Enregistrer
                self.register_object(hydraulic_obj, hydraulic_obj.object_type)
                self.connect_object_signals(hydraulic_obj)
                
                print(f"[COMPONENT_CONTROLLER] Objet importé: {hydraulic_obj.component_id}")
                
            except Exception as e:
                print(f"[COMPONENT_CONTROLLER] Erreur import objet: {e}")
        
        # Signaux finaux
        self.objects_count_changed.emit(len(self.objects))
    
    # === NETTOYAGE ===
    
    def cleanup(self):
        """Nettoyage avant fermeture"""
        print("[COMPONENT_CONTROLLER] Nettoyage...")
        self.clear_all()


# === FONCTION UTILITAIRE POUR TESTS ===

def test_unified_controller():
    """Test du contrôleur unifié avec HydraulicObject"""
    from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow
    import sys
    
    app = QApplication(sys.argv)
    
    # Test du contrôleur unifié
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    controller = ComponentController(scene)
    
    # Connexions de test
    controller.object_added.connect(lambda oid, otype: print(f"✅ Objet ajouté: {otype} ({oid})"))
    controller.objects_count_changed.connect(lambda count: print(f"📊 Nombre d'objets: {count}"))
    controller.object_creation_failed.connect(lambda otype, error: print(f"❌ Erreur {otype}: {error}"))
    controller.object_moved.connect(lambda oid, pos: print(f"🔄 Déplacé: {oid} -> {pos}"))
    controller.object_properties_changed.connect(lambda oid, props: print(f"⚙️ Propriétés: {oid} -> {props}"))
    
    # Test création objets de tous types
    print("=== TEST CONTRÔLEUR UNIFIÉ v3.0 ===")
    
    # Test PUMP
    pump_id = controller.add_object("PUMP", {
        "flow_rate": 200.0,
        "pressure_head": 60.0
    })
    print(f"Pompe créée: {pump_id}")
    
    # Test VALVE  
    valve_id = controller.add_object("VALVE", {
        "diameter": 150.0,
        "valve_type": "PRV"
    })
    print(f"Vanne créée: {valve_id}")
    
    # Test RESERVOIR
    reservoir_id = controller.add_object("RESERVOIR", {
        "head": 120.0
    })
    print(f"Réservoir créé: {reservoir_id}")
    
    # Test TANK
    tank_id = controller.add_object("TANK", {
        "diameter": 15.0,
        "init_level": 12.0
    })
    print(f"Tank créé: {tank_id}")
    
    # Test avec type invalide
    invalid_id = controller.add_object("INVALID_TYPE")
    print(f"Type invalide: {invalid_id}")
    
    # Afficher informations
    info = controller.get_all_components_info()
    print(f"\n📋 RÉSUMÉ: {info['total_components']} objets créés")
    print(f"🏗️ Architecture: {info['architecture_version']}")
    print(f"📦 Types disponibles: {info['available_types']}")
    
    summary = controller.get_objects_summary()
    print(f"📊 Répartition par type: {summary['by_type']}")
    
    # Test modification propriétés
    if pump_id:
        controller.update_object_properties(pump_id, {
            "flow_rate": 250.0,
            "efficiency": 0.90
        })
    
    # Afficher vue
    window = QMainWindow()
    window.setCentralWidget(view)
    window.setWindowTitle("Test ComponentController v3.0 Unifié")
    window.show()
    
    print("\n=== Interface affichée - Testez les interactions ===")
    print("• Cliquez sur les objets")
    print("• Double-cliquez pour voir les propriétés")
    print("• Déplacez les objets")
    
    return app.exec()


# === POINT D'ENTRÉE POUR TESTS ===

if __name__ == "__main__":
    import sys
    sys.exit(test_unified_controller())
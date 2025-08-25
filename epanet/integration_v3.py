#!/usr/bin/env python3
"""
epanet/integration_v3.py - Intégration EPANET pour architecture v3.0
Pont entre HydraulicObject unifié et modèle EPANET
"""

from typing import Optional, Dict, List, Any
from PyQt6.QtCore import QPointF

# Import des classes EPANET
from .structure import (
    EPANETNetwork, EPANETJunction, EPANETPump, EPANETPipe,
    EPANETCurve, PipeStatus, EPANETReservoir, EPANETTank, EPANETValve
)

# Import de l'objet unifié
from components.hydraulic_object import HydraulicObject

class EPANETIntegrationMixin:
    """
    Mixin pour ajouter les capacités EPANET aux HydraulicObject
    VERSION v3.0 - Compatible avec l'architecture unifiée
    """
    
    def __init__(self, *args, **kwargs):
        # Initialiser les objets EPANET
        self.epanet_objects = {}
        self._network_manager = None
        
        # Appeler le constructeur parent
        super().__init__(*args, **kwargs)
        
        # Créer automatiquement les objets EPANET après initialisation
        self.create_epanet_objects()
    
    def set_network_manager(self, manager):
        """Associe ce composant à un gestionnaire réseau"""
        self._network_manager = manager
        self.update_epanet_coordinates()
    
    def create_epanet_objects(self):
        """Crée les objets EPANET basés sur le type d'objet unifié"""
        object_type = getattr(self, 'object_type', None)
        
        if object_type == "PUMP":
            self._create_pump_epanet_objects()
        elif object_type == "VALVE":
            self._create_valve_epanet_objects()
        elif object_type == "RESERVOIR":
            self._create_reservoir_epanet_objects()
        elif object_type == "TANK":
            self._create_tank_epanet_objects()
        else:
            print(f"[EPANET] Type {object_type} non supporté pour l'intégration EPANET")
    
    def _create_pump_epanet_objects(self):
        """Crée les objets EPANET pour une pompe"""
        # Nœud d'aspiration
        aspiration_node = EPANETJunction(
            node_id=f"{self.component_id}_asp",
            elevation=0.0,
            demand=0.0
        )
        
        # Nœud de refoulement
        refoulement_node = EPANETJunction(
            node_id=f"{self.component_id}_ref",
            elevation=0.0,
            demand=0.0
        )
        
        # Lien pompe EPANET
        epanet_pump = EPANETPump(
            link_id=self.component_id,
            node1_id=aspiration_node.node_id,
            node2_id=refoulement_node.node_id,
            parameters=f"HEAD {self.component_id}_curve"
        )
        
        # Courbe de pompe basée sur les propriétés
        pump_curve = self._generate_pump_curve()
        
        # Stocker les objets EPANET
        self.epanet_objects = {
            'aspiration_node': aspiration_node,
            'refoulement_node': refoulement_node,
            'pump_link': epanet_pump,
            'pump_curve': pump_curve
        }
        
        print(f"[EPANET] Objets pompe créés pour {self.component_id}")
    
    def _create_valve_epanet_objects(self):
        """Crée les objets EPANET pour une vanne"""
        # Nœud d'entrée
        inlet_node = EPANETJunction(
            node_id=f"{self.component_id}_in",
            elevation=0.0,
            demand=0.0
        )
        
        # Nœud de sortie
        outlet_node = EPANETJunction(
            node_id=f"{self.component_id}_out",
            elevation=0.0,
            demand=0.0
        )
        
        # Vanne EPANET
        from .structure import ValveType
        valve_type_str = self.get_property("valve_type") or "PRV"
        valve_type = ValveType(valve_type_str)
        
        epanet_valve = EPANETValve(
            link_id=self.component_id,
            node1_id=inlet_node.node_id,
            node2_id=outlet_node.node_id,
            diameter=self.get_property("diameter") or 100.0,
            valve_type=valve_type,
            setting=self.get_property("setting") or 0.0,
            minor_loss=self.get_property("minor_loss") or 0.0
        )
        
        self.epanet_objects = {
            'inlet_node': inlet_node,
            'outlet_node': outlet_node,
            'valve_link': epanet_valve
        }
        
        print(f"[EPANET] Objets vanne créés pour {self.component_id}")
    
    def _create_reservoir_epanet_objects(self):
        """Crée les objets EPANET pour un réservoir"""
        epanet_reservoir = EPANETReservoir(
            node_id=self.component_id,
            head=self.get_property("head") or 100.0,
            pattern=self.get_property("pattern") or ""
        )
        
        self.epanet_objects = {
            'reservoir_node': epanet_reservoir
        }
        
        print(f"[EPANET] Objets réservoir créés pour {self.component_id}")
    
    def _create_tank_epanet_objects(self):
        """Crée les objets EPANET pour un tank"""
        epanet_tank = EPANETTank(
            node_id=self.component_id,
            elevation=self.get_property("elevation") or 50.0,
            init_level=self.get_property("init_level") or 10.0,
            min_level=self.get_property("min_level") or 0.0,
            max_level=self.get_property("max_level") or 20.0,
            diameter=self.get_property("diameter") or 10.0,
            min_vol=self.get_property("min_vol") or 0.0
        )
        
        self.epanet_objects = {
            'tank_node': epanet_tank
        }
        
        print(f"[EPANET] Objets tank créés pour {self.component_id}")
    
    def _generate_pump_curve(self):
        """Génère une courbe de pompe basée sur les propriétés"""
        flow_nominal = self.get_property("flow_rate") or 100.0  # L/min
        head_nominal = self.get_property("pressure_head") or 50.0  # m
        
        # Générer courbe caractéristique réaliste
        points = [
            (0.0, head_nominal * 1.2),                    # Point d'arrêt
            (flow_nominal * 0.5, head_nominal * 1.1),     # 50% débit nominal
            (flow_nominal, head_nominal),                  # Point nominal
            (flow_nominal * 1.2, head_nominal * 0.85),     # 120% débit nominal
            (flow_nominal * 1.5, head_nominal * 0.6),      # Débit élevé
            (flow_nominal * 2.0, 0.0)                      # Débit maximum
        ]
        
        return EPANETCurve(
            curve_id=f"{self.component_id}_curve",
            points=points,
            description=f"Pump curve for {self.component_id}"
        )
    
    def update_epanet_coordinates(self):
        """Met à jour les coordonnées EPANET depuis la position graphique"""
        if not self._network_manager:
            return
        
        pos = self.scenePos()
        scale_factor = self._network_manager.coordinate_scale
        
        for epanet_obj in self.epanet_objects.values():
            if hasattr(epanet_obj, 'x_coord'):
                epanet_obj.x_coord = pos.x() / scale_factor
                epanet_obj.y_coord = pos.y() / scale_factor
    
    def update_epanet_properties(self):
        """Met à jour les propriétés EPANET depuis les propriétés unifiées"""
        object_type = getattr(self, 'object_type', None)
        
        if object_type == "PUMP":
            self._update_pump_epanet_properties()
        elif object_type == "VALVE":
            self._update_valve_epanet_properties()
        elif object_type == "RESERVOIR":
            self._update_reservoir_epanet_properties()
        elif object_type == "TANK":
            self._update_tank_epanet_properties()
    
    def _update_pump_epanet_properties(self):
        """Met à jour les propriétés EPANET de la pompe"""
        if 'pump_curve' in self.epanet_objects:
            # Régénérer la courbe avec les nouvelles propriétés
            new_curve = self._generate_pump_curve()
            self.epanet_objects['pump_curve'] = new_curve
            
            # Mettre à jour la référence dans la pompe
            if 'pump_link' in self.epanet_objects:
                self.epanet_objects['pump_link'].parameters = f"HEAD {new_curve.curve_id}"
    
    def _update_valve_epanet_properties(self):
        """Met à jour les propriétés EPANET de la vanne"""
        if 'valve_link' in self.epanet_objects:
            valve = self.epanet_objects['valve_link']
            valve.diameter = self.get_property("diameter") or valve.diameter
            valve.setting = self.get_property("setting") or valve.setting
            valve.minor_loss = self.get_property("minor_loss") or valve.minor_loss
    
    def _update_reservoir_epanet_properties(self):
        """Met à jour les propriétés EPANET du réservoir"""
        if 'reservoir_node' in self.epanet_objects:
            reservoir = self.epanet_objects['reservoir_node']
            reservoir.head = self.get_property("head") or reservoir.head
            reservoir.pattern = self.get_property("pattern") or reservoir.pattern
    
    def _update_tank_epanet_properties(self):
        """Met à jour les propriétés EPANET du tank"""
        if 'tank_node' in self.epanet_objects:
            tank = self.epanet_objects['tank_node']
            tank.elevation = self.get_property("elevation") or tank.elevation
            tank.init_level = self.get_property("init_level") or tank.init_level
            tank.min_level = self.get_property("min_level") or tank.min_level
            tank.max_level = self.get_property("max_level") or tank.max_level
            tank.diameter = self.get_property("diameter") or tank.diameter
            tank.min_vol = self.get_property("min_vol") or tank.min_vol
    
    def get_epanet_node_id(self, port_id: str) -> str:
        """Détermine l'ID du nœud EPANET pour un port donné"""
        # Mapping port_id -> nœud EPANET selon le type d'objet
        object_type = getattr(self, 'object_type', None)
        
        if object_type == "PUMP":
            if port_id == "aspiration" and 'aspiration_node' in self.epanet_objects:
                return self.epanet_objects['aspiration_node'].node_id
            elif port_id == "refoulement" and 'refoulement_node' in self.epanet_objects:
                return self.epanet_objects['refoulement_node'].node_id
        
        elif object_type == "VALVE":
            if port_id == "inlet" and 'inlet_node' in self.epanet_objects:
                return self.epanet_objects['inlet_node'].node_id
            elif port_id == "outlet" and 'outlet_node' in self.epanet_objects:
                return self.epanet_objects['outlet_node'].node_id
        
        elif object_type in ["RESERVOIR", "TANK"]:
            # Un seul nœud
            for obj_name, epanet_obj in self.epanet_objects.items():
                if hasattr(epanet_obj, 'node_id'):
                    return epanet_obj.node_id
        
        # Fallback: générer ID basé sur composant + port
        return f"{self.component_id}_{port_id}"
    
    def get_epanet_summary(self) -> Dict[str, Any]:
        """Résumé des objets EPANET de ce composant"""
        object_type = getattr(self, 'object_type', None)
        
        summary = {
            "component_id": self.component_id,
            "object_type": object_type,
            "epanet_objects_count": len(self.epanet_objects),
            "objects": {}
        }
        
        for obj_name, epanet_obj in self.epanet_objects.items():
            if hasattr(epanet_obj, 'node_id'):
                summary["objects"][obj_name] = {
                    "type": "node",
                    "id": epanet_obj.node_id,
                    "epanet_type": epanet_obj.get_node_type().value
                }
            elif hasattr(epanet_obj, 'link_id'):
                summary["objects"][obj_name] = {
                    "type": "link",
                    "id": epanet_obj.link_id,
                    "epanet_type": epanet_obj.get_link_type().value
                }
            elif hasattr(epanet_obj, 'curve_id'):
                summary["objects"][obj_name] = {
                    "type": "curve",
                    "id": epanet_obj.curve_id,
                    "points_count": len(epanet_obj.points)
                }
        
        return summary

class EPANETIntegratedHydraulicObject(EPANETIntegrationMixin, HydraulicObject):
    """
    HydraulicObject avec intégration EPANET automatique
    Combine l'objet unifié avec les capacités EPANET
    """
    
    def __init__(self, component_id: str, object_type: str, properties: Dict[str, Any] = None):
        # Appeler les constructeurs dans le bon ordre
        super().__init__(component_id, object_type, properties)
        
        print(f"[EPANET] HydraulicObject intégré créé: {component_id} ({object_type})")
    
    def itemChange(self, change, value):
        """Override pour synchroniser automatiquement EPANET"""
        result = super().itemChange(change, value)
        
        # Synchroniser les coordonnées quand le composant bouge
        if (change == self.GraphicsItemChange.ItemPositionHasChanged and 
            hasattr(self, 'epanet_objects') and self.epanet_objects):
            self.update_epanet_coordinates()
        
        return result
    
    def set_property(self, property_name: str, value: Any) -> bool:
        """Override pour synchroniser les propriétés EPANET"""
        result = super().set_property(property_name, value)
        
        if result:
            # Synchroniser avec EPANET
            self.update_epanet_properties()
        
        return result

class NetworkManagerV3:
    """
    Gestionnaire réseau version 3.0 pour HydraulicObject unifiés
    Évolution du NetworkManager pour l'architecture v3.0
    """
    
    def __init__(self, scene, title="Hydraulic Network Calculator v3.0"):
        self.scene = scene
        self.epanet_network = EPANETNetwork(title)
        
        # Configuration des coordonnées
        self.coordinate_scale = 10.0  # 1 unité EPANET = 10 pixels
        
        # Collections des composants unifiés
        self.integrated_objects: Dict[str, EPANETIntegratedHydraulicObject] = {}
        self.integrated_pipes: Dict[str, Any] = {}  # TODO: Pipes intégrés
        
        print(f"[NETWORK v3.0] Gestionnaire réseau créé: {title}")
    
    def register_component(self, component: EPANETIntegratedHydraulicObject):
        """Enregistre un composant unifié dans le réseau EPANET"""
        if not isinstance(component, EPANETIntegrationMixin):
            print(f"[WARNING] Composant {component.component_id} n'a pas d'intégration EPANET")
            return
        
        # Associer le gestionnaire au composant
        component.set_network_manager(self)
        
        # Ajouter les objets EPANET au réseau
        for obj_name, epanet_obj in component.epanet_objects.items():
            self._add_epanet_object_to_network(epanet_obj)
        
        # Stocker la référence
        self.integrated_objects[component.component_id] = component
        
        print(f"[NETWORK v3.0] Composant enregistré: {component.component_id}")
    
    def _add_epanet_object_to_network(self, epanet_obj):
        """Ajoute un objet EPANET au réseau selon son type"""
        if hasattr(epanet_obj, 'node_id'):
            # C'est un nœud
            node_type = epanet_obj.get_node_type().value
            if node_type == "JUNCTION":
                self.epanet_network.junctions[epanet_obj.node_id] = epanet_obj
            elif node_type == "RESERVOIR":
                self.epanet_network.reservoirs[epanet_obj.node_id] = epanet_obj
            elif node_type == "TANK":
                self.epanet_network.tanks[epanet_obj.node_id] = epanet_obj
        
        elif hasattr(epanet_obj, 'link_id'):
            # C'est un lien
            link_type = epanet_obj.get_link_type().value
            if link_type == "PUMP":
                self.epanet_network.pumps[epanet_obj.link_id] = epanet_obj
            elif link_type == "VALVE":
                self.epanet_network.valves[epanet_obj.link_id] = epanet_obj
            elif link_type == "PIPE":
                self.epanet_network.pipes[epanet_obj.link_id] = epanet_obj
        
        elif hasattr(epanet_obj, 'curve_id'):
            # C'est une courbe
            self.epanet_network.curves[epanet_obj.curve_id] = epanet_obj
    
    def unregister_component(self, component: EPANETIntegratedHydraulicObject):
        """Supprime un composant du réseau"""
        if component.component_id not in self.integrated_objects:
            return
        
        # Supprimer les objets EPANET associés
        for obj_name, epanet_obj in component.epanet_objects.items():
            self._remove_epanet_object_from_network(epanet_obj)
        
        # Supprimer la référence
        del self.integrated_objects[component.component_id]
        
        print(f"[NETWORK v3.0] Composant supprimé: {component.component_id}")
    
    def _remove_epanet_object_from_network(self, epanet_obj):
        """Supprime un objet EPANET du réseau"""
        if hasattr(epanet_obj, 'node_id'):
            self.epanet_network.junctions.pop(epanet_obj.node_id, None)
            self.epanet_network.reservoirs.pop(epanet_obj.node_id, None)
            self.epanet_network.tanks.pop(epanet_obj.node_id, None)
        elif hasattr(epanet_obj, 'link_id'):
            self.epanet_network.pumps.pop(epanet_obj.link_id, None)
            self.epanet_network.valves.pop(epanet_obj.link_id, None)
            self.epanet_network.pipes.pop(epanet_obj.link_id, None)
        elif hasattr(epanet_obj, 'curve_id'):
            self.epanet_network.curves.pop(epanet_obj.curve_id, None)
    
    def sync_all_coordinates(self):
        """Synchronise toutes les coordonnées graphiques → EPANET"""
        for component in self.integrated_objects.values():
            component.update_epanet_coordinates()
        
        print(f"[NETWORK v3.0] Coordonnées synchronisées pour {len(self.integrated_objects)} composants")
    
    def validate_network(self) -> List[str]:
        """Valide le réseau EPANET complet"""
        return self.epanet_network.validate_network()
    
    def export_to_file(self, filename: str) -> str:
        """Exporte le réseau vers un fichier EPANET"""
        # Synchronisation préalable
        self.sync_all_coordinates()
        
        # Validation
        errors = self.validate_network()
        if errors:
            error_msg = f"Erreurs de validation réseau:\n" + "\n".join(f"  - {err}" for err in errors)
            raise ValueError(error_msg)
        
        # Génération du contenu
        epanet_content = self.epanet_network.to_epanet_file()
        
        # Sauvegarde
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(epanet_content)
        
        stats = self.epanet_network.get_statistics()
        print(f"[EXPORT v3.0] Réseau exporté vers {filename}")
        print(f"[EXPORT v3.0] Statistiques: {stats['total_nodes']} nœuds, {stats['total_links']} liens")
        
        return filename
    
    def get_network_summary(self) -> Dict[str, Any]:
        """Résumé complet du réseau v3.0"""
        epanet_stats = self.epanet_network.get_statistics()
        
        return {
            "title": self.epanet_network.title,
            "version": "3.0 - HydraulicObject Unifié",
            "integrated_objects": len(self.integrated_objects),
            "integrated_pipes": len(self.integrated_pipes),
            "epanet_statistics": epanet_stats,
            "coordinate_scale": self.coordinate_scale,
            "validation_errors": len(self.validate_network()),
            "objects_by_type": self._get_objects_by_type_stats()
        }
    
    def _get_objects_by_type_stats(self) -> Dict[str, int]:
        """Statistiques par type d'objet"""
        stats = {}
        for component in self.integrated_objects.values():
            object_type = getattr(component, 'object_type', 'UNKNOWN')
            stats[object_type] = stats.get(object_type, 0) + 1
        return stats

# === EXEMPLE D'UTILISATION ===

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QGraphicsScene
    import sys
    
    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    
    # Créer le gestionnaire réseau v3.0
    manager = NetworkManagerV3(scene, "Test Architecture v3.0")
    
    # Créer des objets intégrés
    pump = EPANETIntegratedHydraulicObject("pump_test", "PUMP", {
        "flow_rate": 150.0,
        "pressure_head": 60.0
    })
    pump.setPos(100, 200)
    
    valve = EPANETIntegratedHydraulicObject("valve_test", "VALVE", {
        "diameter": 125.0,
        "valve_type": "PRV"
    })
    valve.setPos(300, 200)
    
    # Enregistrer dans le réseau
    manager.register_component(pump)
    manager.register_component(valve)
    
    # Afficher le résumé
    summary = manager.get_network_summary()
    print("\n=== RÉSUMÉ RÉSEAU v3.0 ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Test export
    try:
        filename = manager.export_to_file("test_v3_integration.inp")
        print(f"\n✅ Export réussi: {filename}")
    except Exception as e:
        print(f"\n❌ Erreur export: {e}")
    
    print("\n=== TEST TERMINÉ ===")
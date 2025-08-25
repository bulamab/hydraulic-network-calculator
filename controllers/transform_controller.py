#!/usr/bin/env python3
"""
controllers/transform_controller.py - Contrôleur des transformations d'objets
Rotation, alignement, miroirs et autres transformations géométriques
"""

from typing import List, Dict, Tuple, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QPointF
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsItem
import math

# Import pour les objets hydrauliques
try:
    from components.hydraulic_object import HydraulicObject
except ImportError:
    HydraulicObject = None

class TransformController(QObject):
    """
    Contrôleur des transformations géométriques des objets hydrauliques
    Responsabilité : Rotation, alignement, miroirs, mise à l'échelle
    """
    
    # === SIGNAUX ÉMIS ===
    
    # Transformations appliquées
    objects_rotated = pyqtSignal(list, float)              # objects, angle_degrees
    objects_aligned = pyqtSignal(list, str)                # objects, alignment_type
    objects_flipped = pyqtSignal(list, str)                # objects, flip_type
    
    # Erreurs de transformation
    transformation_failed = pyqtSignal(str, str)           # operation, error_message
    
    def __init__(self):
        super().__init__()
        
        # Historique des transformations pour undo/redo (futur)
        self.transformation_history: List[Dict] = []
        self.max_history = 50
        
        print("[TRANSFORM_CONTROLLER] Contrôleur transformations initialisé")
    
    # === ROTATION D'OBJETS ===
    
    def rotate_objects(self, objects: List, angle_degrees: float) -> bool:
        """
        Applique une rotation aux objets sélectionnés
        
        Args:
            objects: Liste d'objets hydrauliques à transformer
            angle_degrees: Angle de rotation en degrés (positif = sens horaire)
            
        Returns:
            bool: Succès de l'opération
        """
        if not objects:
            self.transformation_failed.emit("rotation", "Aucun objet sélectionné")
            return False
        
        try:
            print(f"[TRANSFORM] Rotation {angle_degrees}° sur {len(objects)} objet(s)")
            
            # Filtrer les objets hydrauliques valides
            hydraulic_objects = self._filter_hydraulic_objects(objects)
            
            if not hydraulic_objects:
                self.transformation_failed.emit("rotation", "Aucun objet hydraulique valide")
                return False
            
            # Calculer le centre de rotation (centre du groupe sélectionné)
            rotation_center = self._calculate_objects_center(hydraulic_objects)
            
            # Appliquer la rotation à chaque objet
            rotated_objects = []
            for obj in hydraulic_objects:
                if self._rotate_single_object(obj, angle_degrees, rotation_center):
                    rotated_objects.append(obj)
            
            # Enregistrer dans l'historique
            self._record_transformation("rotation", rotated_objects, {
                "angle": angle_degrees,
                "center": rotation_center
            })
            
            # Émettre signal de succès
            self.objects_rotated.emit(rotated_objects, angle_degrees)
            
            print(f"[TRANSFORM] Rotation réussie sur {len(rotated_objects)} objet(s)")
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors de la rotation: {str(e)}"
            print(f"[TRANSFORM] {error_msg}")
            self.transformation_failed.emit("rotation", error_msg)
            return False
    
    def rotate_left_90(self, objects: List) -> bool:
        """Rotation 90° sens anti-horaire"""
        return self.rotate_objects(objects, -90.0)
    
    def rotate_right_90(self, objects: List) -> bool:
        """Rotation 90° sens horaire"""
        return self.rotate_objects(objects, 90.0)
    
    def _rotate_single_object(self, obj, angle_degrees: float, center: QPointF) -> bool:
        """
        Applique une rotation à un objet autour d'un centre donné
        AVEC rotation correcte des ports
        
        Args:
            obj: Objet hydraulique à faire tourner
            angle_degrees: Angle en degrés
            center: Centre de rotation
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Position actuelle de l'objet
            current_pos = obj.scenePos()
            
            # Calculer vecteur depuis le centre
            dx = current_pos.x() - center.x()
            dy = current_pos.y() - center.y()
            
            # Convertir angle en radians
            angle_rad = math.radians(angle_degrees)
            
            # Calculer nouvelle position après rotation
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            
            new_x = center.x() + (dx * cos_a - dy * sin_a)
            new_y = center.y() + (dx * sin_a + dy * cos_a)
            
            # Appliquer la nouvelle position
            obj.setPos(new_x, new_y)
            
            # Appliquer rotation à l'objet lui-même
            current_rotation = obj.rotation()
            obj.setRotation(current_rotation + angle_degrees)
            
            # NOUVEAU: Rotation correcte des ports
            self._rotate_object_ports(obj, angle_degrees, current_pos)
            
            # Mettre à jour les positions des ports après rotation
            if hasattr(obj, 'update_ports_positions'):
                obj.update_ports_positions(QPointF(new_x, new_y))
            
            return True
            
        except Exception as e:
            print(f"[TRANSFORM] Erreur rotation objet {getattr(obj, 'component_id', 'unknown')}: {e}")
            return False
    
    def _rotate_object_ports(self, obj, angle_degrees: float, object_center: QPointF):
        """
        Fait tourner les ports d'un objet en utilisant la méthode de l'objet
        VERSION SIMPLIFIÉE qui utilise la méthode intégrée de HydraulicObject
        
        Args:
            obj: Objet hydraulique
            angle_degrees: Angle de rotation en degrés
            object_center: Centre de l'objet (position avant rotation)
        """
        try:
            # Utiliser la méthode intégrée de l'objet si disponible
            if hasattr(obj, 'rotate_ports_around_center'):
                obj.rotate_ports_around_center(angle_degrees)
                return
            
            # Sinon, méthode de fallback pour compatibilité
            if not hasattr(obj, 'ports') or not obj.ports:
                return
            
            # Convertir angle en radians
            angle_rad = math.radians(angle_degrees)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            
            print(f"[TRANSFORM] Rotation ports (fallback) de {getattr(obj, 'component_id', 'unknown')}: {angle_degrees}°")
            
            for port in obj.ports:
                if hasattr(port, 'initial_position'):
                    # Position initiale du port relative à l'objet
                    initial_relative_pos = port.initial_position
                    
                    # Calculer nouvelle position relative après rotation
                    old_rel_x = initial_relative_pos.x()
                    old_rel_y = initial_relative_pos.y()
                    
                    new_rel_x = old_rel_x * cos_a - old_rel_y * sin_a
                    new_rel_y = old_rel_x * sin_a + old_rel_y * cos_a
                    
                    # Mettre à jour la position initiale du port
                    port.initial_position = QPointF(new_rel_x, new_rel_y)
                    
                    # Calculer nouvelle position globale du port
                    new_object_pos = obj.scenePos()
                    new_global_pos = new_object_pos + QPointF(new_rel_x, new_rel_y)
                    
                    # Appliquer la nouvelle position globale
                    port.setPos(new_global_pos)
                    
                    print(f"[TRANSFORM]   Port {port.port_id}: ({old_rel_x:.1f}, {old_rel_y:.1f}) → ({new_rel_x:.1f}, {new_rel_y:.1f})")
            
        except Exception as e:
            print(f"[TRANSFORM] Erreur rotation ports: {e}")
            import traceback
            traceback.print_exc()
    
    # === ALIGNEMENT D'OBJETS ===
    
    def align_objects_horizontal(self, objects: List) -> bool:
        """
        Aligne les objets horizontalement (même Y)
        
        Args:
            objects: Liste d'objets à aligner
            
        Returns:
            bool: Succès de l'opération
        """
        return self._align_objects(objects, "horizontal")
    
    def align_objects_vertical(self, objects: List) -> bool:
        """
        Aligne les objets verticalement (même X)
        
        Args:
            objects: Liste d'objets à aligner
            
        Returns:
            bool: Succès de l'opération
        """
        return self._align_objects(objects, "vertical")
    
    def _align_objects(self, objects: List, alignment_type: str) -> bool:
        """
        Implémentation générale de l'alignement
        
        Args:
            objects: Liste d'objets à aligner
            alignment_type: "horizontal" ou "vertical"
            
        Returns:
            bool: Succès de l'opération
        """
        if len(objects) < 2:
            self.transformation_failed.emit("alignment", "Au moins 2 objets requis pour l'alignement")
            return False
        
        try:
            print(f"[TRANSFORM] Alignement {alignment_type} sur {len(objects)} objet(s)")
            
            # Filtrer les objets hydrauliques valides
            hydraulic_objects = self._filter_hydraulic_objects(objects)
            
            if len(hydraulic_objects) < 2:
                self.transformation_failed.emit("alignment", "Au moins 2 objets hydrauliques valides requis")
                return False
            
            # Calculer la ligne de référence d'alignement
            reference_line = self._calculate_alignment_reference(hydraulic_objects, alignment_type)
            
            # Appliquer l'alignement
            aligned_objects = []
            for obj in hydraulic_objects:
                if self._align_single_object(obj, reference_line, alignment_type):
                    aligned_objects.append(obj)
            
            # Enregistrer dans l'historique
            self._record_transformation("alignment", aligned_objects, {
                "type": alignment_type,
                "reference": reference_line
            })
            
            # Émettre signal de succès
            self.objects_aligned.emit(aligned_objects, alignment_type)
            
            print(f"[TRANSFORM] Alignement {alignment_type} réussi sur {len(aligned_objects)} objet(s)")
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors de l'alignement {alignment_type}: {str(e)}"
            print(f"[TRANSFORM] {error_msg}")
            self.transformation_failed.emit("alignment", error_msg)
            return False
    
    def _calculate_alignment_reference(self, objects: List, alignment_type: str) -> float:
        """
        Calcule la ligne de référence pour l'alignement
        NOUVELLE LOGIQUE: Utilise la position du DERNIER OBJET SÉLECTIONNÉ
        
        Args:
            objects: Liste d'objets (le dernier est la référence)
            alignment_type: Type d'alignement
            
        Returns:
            float: Coordonnée de référence (X pour vertical, Y pour horizontal)
        """
        if not objects:
            raise ValueError("Aucun objet pour calculer la référence d'alignement")
        
        # Utiliser le DERNIER objet sélectionné comme référence
        reference_object = objects[-1]
        reference_pos = reference_object.scenePos()
        
        if alignment_type == "horizontal":
            # Aligner sur le Y du dernier objet sélectionné
            reference_coord = reference_pos.y()
            print(f"[TRANSFORM] Référence alignement horizontal: Y={reference_coord} (objet {getattr(reference_object, 'component_id', 'unknown')})")
            return reference_coord
        
        elif alignment_type == "vertical":
            # Aligner sur le X du dernier objet sélectionné
            reference_coord = reference_pos.x()
            print(f"[TRANSFORM] Référence alignement vertical: X={reference_coord} (objet {getattr(reference_object, 'component_id', 'unknown')})")
            return reference_coord
        
        else:
            raise ValueError(f"Type d'alignement non supporté: {alignment_type}")
    
    def _align_single_object(self, obj, reference_line: float, alignment_type: str) -> bool:
        """
        Aligne un objet sur une ligne de référence
        MISE À JOUR: Déplace aussi les ports
        
        Args:
            obj: Objet à aligner
            reference_line: Coordonnée de référence
            alignment_type: Type d'alignement
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            current_pos = obj.scenePos()
            
            if alignment_type == "horizontal":
                # Garder X, changer Y
                new_pos = QPointF(current_pos.x(), reference_line)
            elif alignment_type == "vertical":
                # Garder Y, changer X
                new_pos = QPointF(reference_line, current_pos.y())
            else:
                return False
            
            # Appliquer la nouvelle position
            obj.setPos(new_pos)
            
            # IMPORTANT: Mettre à jour les positions des ports
            self._update_object_ports_after_move(obj, current_pos, new_pos)
            
            print(f"[TRANSFORM] Objet {getattr(obj, 'component_id', 'unknown')} aligné: {current_pos} → {new_pos}")
            return True
            
        except Exception as e:
            print(f"[TRANSFORM] Erreur alignement objet {getattr(obj, 'component_id', 'unknown')}: {e}")
            return False
    
    def _update_object_ports_after_move(self, obj, old_pos: QPointF, new_pos: QPointF):
        """
        Met à jour les positions des ports après déplacement d'un objet
        
        Args:
            obj: Objet hydraulique
            old_pos: Ancienne position
            new_pos: Nouvelle position
        """
        try:
            # Utiliser la méthode standard de mise à jour des ports
            if hasattr(obj, 'update_ports_positions'):
                obj.update_ports_positions(new_pos)
                print(f"[TRANSFORM] Ports mis à jour pour {getattr(obj, 'component_id', 'unknown')}")
                return
            
            # Méthode de fallback si l'objet a des ports
            if hasattr(obj, 'ports') and obj.ports:
                # Calculer le déplacement
                delta = new_pos - old_pos
                
                for port in obj.ports:
                    if hasattr(port, 'setPos'):
                        # Déplacer chaque port du même delta
                        current_port_pos = port.scenePos()
                        new_port_pos = current_port_pos + delta
                        port.setPos(new_port_pos)
                
                print(f"[TRANSFORM] Ports déplacés (fallback) de {delta} pour {getattr(obj, 'component_id', 'unknown')}")
            
        except Exception as e:
            print(f"[TRANSFORM] Erreur mise à jour ports: {e}")
    
    # === MIROIR (FLIP) D'OBJETS ===
    
    def flip_objects_horizontal(self, objects: List) -> bool:
        """
        Applique un miroir horizontal aux objets (par rapport à leur propre centre)
        LOGIQUE CORRIGÉE: Chaque objet fait un miroir par rapport à SON centre
        
        Args:
            objects: Liste d'objets à transformer (chacun miroir par rapport à son centre)
            
        Returns:
            bool: Succès de l'opération
        """
        if not objects:
            self.transformation_failed.emit("flip", "Aucun objet sélectionné")
            return False
        
        try:
            print(f"[TRANSFORM] Miroir horizontal sur {len(objects)} objet(s) (chacun par rapport à son centre)")
            
            # Filtrer les objets hydrauliques valides
            hydraulic_objects = self._filter_hydraulic_objects(objects)
            
            if not hydraulic_objects:
                self.transformation_failed.emit("flip", "Aucun objet hydraulique valide")
                return False
            
            # Appliquer le miroir à chaque objet individuellement
            flipped_objects = []
            for obj in hydraulic_objects:
                if self._flip_single_object_around_center(obj, "horizontal"):
                    flipped_objects.append(obj)
            
            # Enregistrer dans l'historique
            self._record_transformation("flip_horizontal", flipped_objects, {
                "type": "horizontal",
                "mode": "individual_center"
            })
            
            # Émettre signal de succès
            self.objects_flipped.emit(flipped_objects, "horizontal")
            
            print(f"[TRANSFORM] Miroir horizontal réussi sur {len(flipped_objects)} objet(s)")
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors du miroir horizontal: {str(e)}"
            print(f"[TRANSFORM] {error_msg}")
            self.transformation_failed.emit("flip_horizontal", error_msg)
            return False
    
    def flip_objects_vertical(self, objects: List) -> bool:
        """
        Applique un miroir vertical aux objets (par rapport à leur propre centre)
        LOGIQUE CORRIGÉE: Chaque objet fait un miroir par rapport à SON centre
        
        Args:
            objects: Liste d'objets à transformer (chacun miroir par rapport à son centre)
            
        Returns:
            bool: Succès de l'opération
        """
        if not objects:
            self.transformation_failed.emit("flip", "Aucun objet sélectionné")
            return False
        
        try:
            print(f"[TRANSFORM] Miroir vertical sur {len(objects)} objet(s) (chacun par rapport à son centre)")
            
            # Filtrer les objets hydrauliques valides
            hydraulic_objects = self._filter_hydraulic_objects(objects)
            
            if not hydraulic_objects:
                self.transformation_failed.emit("flip", "Aucun objet hydraulique valide")
                return False
            
            # Appliquer le miroir à chaque objet individuellement
            flipped_objects = []
            for obj in hydraulic_objects:
                if self._flip_single_object_around_center(obj, "vertical"):
                    flipped_objects.append(obj)
            
            # Enregistrer dans l'historique
            self._record_transformation("flip_vertical", flipped_objects, {
                "type": "vertical",
                "mode": "individual_center"
            })
            
            # Émettre signal de succès
            self.objects_flipped.emit(flipped_objects, "vertical")
            
            print(f"[TRANSFORM] Miroir vertical réussi sur {len(flipped_objects)} objet(s)")
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors du miroir vertical: {str(e)}"
            print(f"[TRANSFORM] {error_msg}")
            self.transformation_failed.emit("flip_vertical", error_msg)
            return False
    
    def _flip_single_object_around_center(self, obj, flip_type: str) -> bool:
        """
        Applique un miroir à un objet autour de SON PROPRE CENTRE
        NOUVELLE MÉTHODE: Miroir par rapport au centre de l'objet
        
        Args:
            obj: Objet à transformer
            flip_type: "horizontal" ou "vertical"
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # L'objet reste à la même position, seuls les ports sont inversés
            current_pos = obj.scenePos()
            
            print(f"[TRANSFORM] Miroir {flip_type} de {getattr(obj, 'component_id', 'unknown')} autour de son centre")
            
            # Appliquer le miroir aux ports seulement (l'objet ne bouge pas)
            self._flip_object_ports(obj, flip_type)
            
            # Optionnel: Appliquer transformation visuelle à l'objet principal
            if hasattr(obj, 'setTransform'):
                current_transform = obj.transform()
                
                if flip_type == "horizontal":
                    # Miroir horizontal: inverser X
                    flip_transform = QTransform()
                    flip_transform.scale(-1, 1)
                elif flip_type == "vertical":
                    # Miroir vertical: inverser Y  
                    flip_transform = QTransform()
                    flip_transform.scale(1, -1)
                else:
                    return False
                
                # Appliquer la transformation
                obj.setTransform(current_transform * flip_transform)
            
            print(f"[TRANSFORM] Miroir {flip_type} appliqué à {getattr(obj, 'component_id', 'unknown')}")
            return True
            
        except Exception as e:
            print(f"[TRANSFORM] Erreur miroir objet {getattr(obj, 'component_id', 'unknown')}: {e}")
            return False
    
    def _flip_objects(self, objects: List, flip_type: str) -> bool:
        """
        Implémentation générale du miroir
        
        Args:
            objects: Liste d'objets à transformer
            flip_type: "horizontal" ou "vertical"
            
        Returns:
            bool: Succès de l'opération
        """
        if not objects:
            self.transformation_failed.emit("flip", "Aucun objet sélectionné")
            return False
        
        try:
            print(f"[TRANSFORM] Miroir {flip_type} sur {len(objects)} objet(s)")
            
            # Filtrer les objets hydrauliques valides
            hydraulic_objects = self._filter_hydraulic_objects(objects)
            
            if not hydraulic_objects:
                self.transformation_failed.emit("flip", "Aucun objet hydraulique valide")
                return False
            
            # Calculer l'axe de réflexion
            reflection_axis = self._calculate_reflection_axis(hydraulic_objects, flip_type)
            
            # Appliquer le miroir
            flipped_objects = []
            for obj in hydraulic_objects:
                if self._flip_single_object(obj, reflection_axis, flip_type):
                    flipped_objects.append(obj)
            
            # Enregistrer dans l'historique
            self._record_transformation("flip", flipped_objects, {
                "type": flip_type,
                "axis": reflection_axis
            })
            
            # Émettre signal de succès
            self.objects_flipped.emit(flipped_objects, flip_type)
            
            print(f"[TRANSFORM] Miroir {flip_type} réussi sur {len(flipped_objects)} objet(s)")
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors du miroir {flip_type}: {str(e)}"
            print(f"[TRANSFORM] {error_msg}")
            self.transformation_failed.emit("flip", error_msg)
            return False
    
    def _calculate_reflection_axis(self, objects: List, flip_type: str) -> float:
        """
        Calcule l'axe de réflexion pour le miroir
        NOUVELLE LOGIQUE: Utilise la position du DERNIER OBJET SÉLECTIONNÉ comme axe
        
        Args:
            objects: Liste d'objets (le dernier définit l'axe)
            flip_type: Type de miroir
            
        Returns:
            float: Coordonnée de l'axe de réflexion
        """
        if not objects:
            raise ValueError("Aucun objet pour calculer l'axe de réflexion")
        
        # Utiliser le DERNIER objet sélectionné pour définir l'axe
        reference_object = objects[-1]
        reference_pos = reference_object.scenePos()
        
        if flip_type == "horizontal":
            # Axe vertical passant par le dernier objet (même X pour miroir horizontal)
            axis_coord = reference_pos.x()
            print(f"[TRANSFORM] Axe miroir horizontal: X={axis_coord} (objet {getattr(reference_object, 'component_id', 'unknown')})")
            return axis_coord
        
        elif flip_type == "vertical":
            # Axe horizontal passant par le dernier objet (même Y pour miroir vertical)
            axis_coord = reference_pos.y()
            print(f"[TRANSFORM] Axe miroir vertical: Y={axis_coord} (objet {getattr(reference_object, 'component_id', 'unknown')})")
            return axis_coord
        
        else:
            raise ValueError(f"Type de miroir non supporté: {flip_type}")
    
    def _flip_single_object(self, obj, axis: float, flip_type: str) -> bool:
        """
        Applique un miroir à un objet autour d'un axe
        MISE À JOUR: Déplace aussi les ports
        
        Args:
            obj: Objet à transformer
            axis: Coordonnée de l'axe de réflexion
            flip_type: Type de miroir
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            current_pos = obj.scenePos()
            
            if flip_type == "horizontal":
                # Réflexion autour d'un axe vertical (X fixe)
                distance_to_axis = current_pos.x() - axis
                new_x = axis - distance_to_axis  # Miroir
                new_pos = QPointF(new_x, current_pos.y())
                
                print(f"[TRANSFORM] Miroir horizontal: {getattr(obj, 'component_id', 'unknown')} X:{current_pos.x()} → {new_x} (axe X={axis})")
                
            elif flip_type == "vertical":
                # Réflexion autour d'un axe horizontal (Y fixe)
                distance_to_axis = current_pos.y() - axis
                new_y = axis - distance_to_axis  # Miroir
                new_pos = QPointF(current_pos.x(), new_y)
                
                print(f"[TRANSFORM] Miroir vertical: {getattr(obj, 'component_id', 'unknown')} Y:{current_pos.y()} → {new_y} (axe Y={axis})")
                
            else:
                return False
            
            # Appliquer la nouvelle position
            obj.setPos(new_pos)
            
            # IMPORTANT: Mettre à jour les positions des ports
            self._update_object_ports_after_move(obj, current_pos, new_pos)
            
            # NOUVEAU: Appliquer aussi le miroir aux ports eux-mêmes
            self._flip_object_ports(obj, flip_type)
            
            # Note: On n'applique PAS de transformation de scale négative car cela 
            # déforme l'objet. On fait juste un déplacement en miroir.
            
            return True
            
        except Exception as e:
            print(f"[TRANSFORM] Erreur miroir objet {getattr(obj, 'component_id', 'unknown')}: {e}")
            return False
    
    def _flip_object_ports(self, obj, flip_type: str):
        """
        Applique un miroir aux ports d'un objet (positions relatives)
        
        Args:
            obj: Objet hydraulique
            flip_type: Type de miroir ("horizontal" ou "vertical")
        """
        try:
            if not hasattr(obj, 'ports') or not obj.ports:
                return
            
            print(f"[TRANSFORM] Miroir des ports de {getattr(obj, 'component_id', 'unknown')}: {flip_type}")
            
            for port in obj.ports:
                if hasattr(port, 'initial_position'):
                    # Position relative actuelle
                    current_rel_pos = port.initial_position
                    
                    if flip_type == "horizontal":
                        # Inverser la position X relative
                        new_rel_pos = QPointF(-current_rel_pos.x(), current_rel_pos.y())
                    elif flip_type == "vertical":
                        # Inverser la position Y relative
                        new_rel_pos = QPointF(current_rel_pos.x(), -current_rel_pos.y())
                    else:
                        continue
                    
                    # Mettre à jour la position initiale relative
                    port.initial_position = new_rel_pos
                    
                    # Recalculer position globale
                    global_pos = obj.scenePos() + new_rel_pos
                    port.setPos(global_pos)
                    
                    print(f"[TRANSFORM]   Port {port.port_id}: {current_rel_pos} → {new_rel_pos}")
            
        except Exception as e:
            print(f"[TRANSFORM] Erreur miroir ports: {e}")
    
    # === UTILITAIRES ===
    
    def _filter_hydraulic_objects(self, objects: List) -> List:
        """
        Filtre les objets pour ne garder que les objets hydrauliques valides
        
        Args:
            objects: Liste d'objets mixtes
            
        Returns:
            List: Objets hydrauliques valides seulement
        """
        hydraulic_objects = []
        
        for obj in objects:
            # Vérifier si c'est un objet hydraulique
            if hasattr(obj, 'component_id') and hasattr(obj, 'object_type'):
                hydraulic_objects.append(obj)
            elif HydraulicObject and isinstance(obj, HydraulicObject):
                hydraulic_objects.append(obj)
        
        return hydraulic_objects
    
    def _calculate_objects_center(self, objects: List) -> QPointF:
        """
        Calcule le centre géométrique d'un groupe d'objets
        
        Args:
            objects: Liste d'objets
            
        Returns:
            QPointF: Point central
        """
        if not objects:
            return QPointF(0, 0)
        
        total_x = sum(obj.scenePos().x() for obj in objects)
        total_y = sum(obj.scenePos().y() for obj in objects)
        
        center_x = total_x / len(objects)
        center_y = total_y / len(objects)
        
        return QPointF(center_x, center_y)
    
    def _record_transformation(self, operation: str, objects: List, parameters: Dict):
        """
        Enregistre une transformation dans l'historique (pour undo/redo futur)
        
        Args:
            operation: Type d'opération
            objects: Objets transformés
            parameters: Paramètres de la transformation
        """
        record = {
            "operation": operation,
            "timestamp": __import__('time').time(),
            "objects": [getattr(obj, 'component_id', str(id(obj))) for obj in objects],
            "parameters": parameters
        }
        
        # Ajouter à l'historique
        self.transformation_history.append(record)
        
        # Limiter la taille de l'historique
        if len(self.transformation_history) > self.max_history:
            self.transformation_history.pop(0)
        
        print(f"[TRANSFORM] Transformation enregistrée: {operation} sur {len(objects)} objet(s)")
    
    # === INFORMATIONS ET DEBUG ===
    
    def get_transformation_history(self) -> List[Dict]:
        """Retourne l'historique des transformations"""
        return self.transformation_history.copy()
    
    def clear_history(self):
        """Vide l'historique des transformations"""
        self.transformation_history.clear()
        print("[TRANSFORM] Historique des transformations vidé")
    
    def get_controller_info(self) -> Dict:
        """Retourne des informations sur le contrôleur"""
        return {
            "transformations_count": len(self.transformation_history),
            "max_history": self.max_history,
            "supported_operations": ["rotation", "alignment", "flip"],
            "rotation_angles": [90, -90, 180, -180],
            "alignment_types": ["horizontal", "vertical"],
            "flip_types": ["horizontal", "vertical"]
        }


# === POINT D'ENTRÉE POUR TESTS ===

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
    from PyQt6.QtCore import QPointF
    
    app = QApplication(sys.argv)
    
    # Simuler des objets hydrauliques pour test
    class MockHydraulicObject:
        def __init__(self, component_id, x, y):
            self.component_id = component_id
            self.object_type = "PUMP"
            self._pos = QPointF(x, y)
            self._rotation = 0.0
            self._transform = QTransform()
        
        def scenePos(self):
            return self._pos
        
        def setPos(self, pos):
            self._pos = pos
            print(f"  {self.component_id} déplacé à {pos}")
        
        def rotation(self):
            return self._rotation
        
        def setRotation(self, angle):
            self._rotation = angle
            print(f"  {self.component_id} tourné à {angle}°")
        
        def transform(self):
            return self._transform
        
        def setTransform(self, transform):
            self._transform = transform
            print(f"  {self.component_id} transform appliquée")
        
        def update_ports_positions(self, pos):
            print(f"  {self.component_id} ports mis à jour")
    
    # Interface de test
    window = QWidget()
    layout = QVBoxLayout(window)
    
    # Contrôleur
    controller = TransformController()
    
    # Log des événements
    log = QTextEdit()
    log.setMaximumHeight(300)
    layout.addWidget(log)
    
    def log_event(message):
        log.append(f"• {message}")
    
    # Connexions de test
    controller.objects_rotated.connect(
        lambda objs, angle: log_event(f"🔄 {len(objs)} objet(s) tourné(s) de {angle}°")
    )
    controller.objects_aligned.connect(
        lambda objs, align_type: log_event(f"⫷ {len(objs)} objet(s) aligné(s) {align_type}")
    )
    controller.objects_flipped.connect(
        lambda objs, flip_type: log_event(f"🪞 {len(objs)} objet(s) miroir {flip_type}")
    )
    controller.transformation_failed.connect(
        lambda op, error: log_event(f"❌ Erreur {op}: {error}")
    )
    
    # Créer objets de test
    test_objects = [
        MockHydraulicObject("pump_001", 100, 100),
        MockHydraulicObject("valve_002", 200, 150),
        MockHydraulicObject("tank_003", 150, 200)
    ]
    
    # Boutons de test
    buttons_layout = QVBoxLayout()
    
    # Test rotations
    btn_rotate_left = QPushButton("🔄 Rotation 90° Gauche")
    btn_rotate_left.clicked.connect(lambda: controller.rotate_left_90(test_objects))
    buttons_layout.addWidget(btn_rotate_left)
    
    btn_rotate_right = QPushButton("🔄 Rotation 90° Droite")
    btn_rotate_right.clicked.connect(lambda: controller.rotate_right_90(test_objects))
    buttons_layout.addWidget(btn_rotate_right)
    
    # Test alignements
    btn_align_h = QPushButton("⫷ Alignement Horizontal")
    btn_align_h.clicked.connect(lambda: controller.align_objects_horizontal(test_objects))
    buttons_layout.addWidget(btn_align_h)
    
    btn_align_v = QPushButton("⫸ Alignement Vertical")
    btn_align_v.clicked.connect(lambda: controller.align_objects_vertical(test_objects))
    buttons_layout.addWidget(btn_align_v)
    
    # Test miroirs
    btn_flip_h = QPushButton("🪞 Miroir Horizontal")
    btn_flip_h.clicked.connect(lambda: controller.flip_objects_horizontal(test_objects))
    buttons_layout.addWidget(btn_flip_h)
    
    btn_flip_v = QPushButton("🪞 Miroir Vertical")
    btn_flip_v.clicked.connect(lambda: controller.flip_objects_vertical(test_objects))
    buttons_layout.addWidget(btn_flip_v)
    
    # Test erreurs
    btn_test_empty = QPushButton("❌ Test Liste Vide")
    btn_test_empty.clicked.connect(lambda: controller.rotate_left_90([]))
    buttons_layout.addWidget(btn_test_empty)
    
    btn_test_single = QPushButton("⚠️ Test Alignement 1 Objet")
    btn_test_single.clicked.connect(lambda: controller.align_objects_horizontal([test_objects[0]]))
    buttons_layout.addWidget(btn_test_single)
    
    # Informations
    btn_info = QPushButton("ℹ️ Informations Contrôleur")
    btn_info.clicked.connect(lambda: log_event(f"📋 Info: {controller.get_controller_info()}"))
    buttons_layout.addWidget(btn_info)
    
    btn_history = QPushButton("📜 Historique")
    btn_history.clicked.connect(lambda: log_event(f"📜 Historique: {len(controller.get_transformation_history())} opération(s)"))
    buttons_layout.addWidget(btn_history)
    
    layout.addLayout(buttons_layout)
    
    window.setWindowTitle("Test Transform Controller")
    window.show()
    
    log_event("🚀 Transform Controller chargé")
    log_event("📝 Testez les transformations avec les boutons")
    log_event(f"🔧 {len(test_objects)} objets de test créés")
    
    print("=== TEST TRANSFORM CONTROLLER ===")
    print("• Objets de test avec positions simulées")
    print("• Rotations: 90° gauche/droite")
    print("• Alignements: horizontal/vertical")
    print("• Miroirs: horizontal/vertical") 
    print("• Gestion d'erreurs et historique")
    
    sys.exit(app.exec())
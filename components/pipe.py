#!/usr/bin/env python3
"""
HydraulicPipe - Connexions orthogonales avec points intermédiaires
Version avancée avec tracé professionnel
"""

from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsLineItem, QGraphicsEllipseItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath
import math

class OrthogonalPipe(QGraphicsPathItem):
    """
    Tuyau hydraulique avec tracé orthogonal et points intermédiaires
    """
    
    def __init__(self, start_component, start_port, end_component, end_port, waypoints=None):
        super().__init__()
        
        # Composants connectés
        self.start_component = start_component
        self.start_port = start_port
        self.end_component = end_component
        self.end_port = end_port
        
        # Points intermédiaires
        self.waypoints = waypoints or []
        
        # Propriétés hydrauliques
        self.diameter = 50  # mm
        self.material = "steel"
        self.length = 0  # calculé automatiquement
        
        # ID unique
        self.pipe_id = f"pipe_{id(self):x}"
        
        # Éléments visuels pour les points intermédiaires
        self.waypoint_indicators = []
        
        # Configuration
        self.setup_pipe()
        self.register_with_components()
        
        print(f"[ORTHOPIPE] Créé: {start_component.component_id}[{start_port}] → {end_component.component_id}[{end_port}] avec {len(self.waypoints)} points")
    
    def setup_pipe(self):
        """Configuration visuelle du tuyau"""
        # Style moderne
        pen = QPen(QColor(41, 128, 185), 4)  # Bleu
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.setPen(pen)
        
        # Créer le tracé orthogonal
        self.update_orthogonal_path()
        
        # Propriétés graphiques
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setZValue(1)
        
        print(f"[ORTHOPIPE] Configuration appliquée: {self.pipe_id}")
    
    def register_with_components(self):
        """S'enregistre auprès des composants"""
        try:
            if not hasattr(self.start_component, 'connected_pipes'):
                self.start_component.connected_pipes = []
            if not hasattr(self.end_component, 'connected_pipes'):
                self.end_component.connected_pipes = []
            
            self.start_component.connected_pipes.append(self)
            self.end_component.connected_pipes.append(self)
            
            print(f"[ORTHOPIPE] Enregistré avec les composants")
        except Exception as e:
            print(f"[ORTHOPIPE] Erreur enregistrement: {e}")
    
    def update_orthogonal_path(self):
        """Met à jour le tracé orthogonal du tuyau"""
        try:
            # Récupérer les positions des ports
            start_port_obj = self.start_component.get_port_by_id(self.start_port)
            end_port_obj = self.end_component.get_port_by_id(self.end_port)
            
            if not start_port_obj or not end_port_obj:
                print(f"[ORTHOPIPE] Erreur: ports non trouvés")
                return
            
            start_pos = start_port_obj.scenePos()
            end_pos = end_port_obj.scenePos()
            
            # Créer le chemin orthogonal
            path = QPainterPath()
            points = self.calculate_orthogonal_path(start_pos, end_pos, self.waypoints)
            
            if points:
                path.moveTo(points[0])
                for point in points[1:]:
                    path.lineTo(point)
                
                self.setPath(path)
                
                # Calculer la longueur totale
                self.length = self.calculate_total_length(points)
                
                # Mettre à jour les indicateurs de points intermédiaires
                self.update_waypoint_indicators()
                
                print(f"[ORTHOPIPE] Tracé mis à jour: {len(points)} points, longueur: {self.length:.1f}mm")
            
        except Exception as e:
            print(f"[ORTHOPIPE] Erreur mise à jour: {e}")
            import traceback
            traceback.print_exc()
    
    def calculate_orthogonal_path(self, start_pos, end_pos, waypoints):
        """Calcule un tracé orthogonal entre deux points avec waypoints"""
        points = [start_pos]
        
        # Ajouter les points intermédiaires
        current_pos = start_pos
        
        for waypoint in waypoints:
            # Créer des segments orthogonaux vers chaque waypoint
            ortho_points = self.create_orthogonal_segments(current_pos, waypoint)
            points.extend(ortho_points[1:])  # Exclure le premier point (déjà ajouté)
            current_pos = waypoint
        
        # Segments finaux vers le port de destination
        final_points = self.create_orthogonal_segments(current_pos, end_pos)
        points.extend(final_points[1:])
        
        return points
    
    def create_orthogonal_segments(self, start, end):
        """Crée des segments orthogonaux entre deux points"""
        # Stratégie simple : d'abord horizontal, puis vertical
        # (ou vertical puis horizontal selon la distance)
        
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        # Si la distance horizontale est plus grande, commencer par horizontal
        if abs(dx) >= abs(dy):
            intermediate = QPointF(end.x(), start.y())
            return [start, intermediate, end]
        else:
            intermediate = QPointF(start.x(), end.y())
            return [start, intermediate, end]
    
    def calculate_total_length(self, points):
        """Calcule la longueur totale du tracé"""
        total_length = 0
        for i in range(len(points) - 1):
            dx = points[i+1].x() - points[i].x()
            dy = points[i+1].y() - points[i].y()
            total_length += math.sqrt(dx*dx + dy*dy)
        
        return round(total_length * 0.5, 1)  # Conversion pixels → mm
    
    def update_waypoint_indicators(self):
        """Met à jour les indicateurs visuels des points intermédiaires"""
        # Supprimer les anciens indicateurs
        for indicator in self.waypoint_indicators:
            if indicator.scene():
                indicator.scene().removeItem(indicator)
        
        self.waypoint_indicators.clear()
        
        # Créer de nouveaux indicateurs
        for waypoint in self.waypoints:
            indicator = QGraphicsEllipseItem(-4, -4, 8, 8)
            indicator.setPen(QPen(QColor(255, 140, 0), 2))  # Orange
            indicator.setBrush(QBrush(QColor(255, 165, 0)))
            indicator.setPos(waypoint)
            indicator.setZValue(5)
            
            # Ajouter à la scène
            if self.scene():
                self.scene().addItem(indicator)
            
            self.waypoint_indicators.append(indicator)
    
    def update_path(self):
        """Alias pour la compatibilité"""
        self.update_orthogonal_path()
    
    def mousePressEvent(self, event):
        """Clic sur le tuyau"""
        print(f"[ORTHOPIPE] Sélectionné: {self.pipe_id} (longueur: {self.length}mm)")
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Double-clic = propriétés"""
        print(f"\n[ORTHOPIPE] Propriétés de {self.pipe_id}:")
        print(f"  Connexion: {self.start_component.component_id}[{self.start_port}] → {self.end_component.component_id}[{self.end_port}]")
        print(f"  Points intermédiaires: {len(self.waypoints)}")
        print(f"  Longueur totale: {self.length} mm")
        print(f"  Diamètre: {self.diameter} mm")
        print(f"  Matériau: {self.material}")
        
        super().mouseDoubleClickEvent(event)
    
    def delete_pipe(self):
        """Supprime le tuyau et ses indicateurs"""
        try:
            # Supprimer les indicateurs
            for indicator in self.waypoint_indicators:
                if indicator.scene():
                    indicator.scene().removeItem(indicator)
            
            # Déconnecter les ports
            start_port_obj = self.start_component.get_port_by_id(self.start_port)
            end_port_obj = self.end_component.get_port_by_id(self.end_port)
            
            if start_port_obj:
                start_port_obj.disconnect_from_pipe()
            if end_port_obj:
                end_port_obj.disconnect_from_pipe()
            
            # Retirer des listes
            if hasattr(self.start_component, 'connected_pipes'):
                if self in self.start_component.connected_pipes:
                    self.start_component.connected_pipes.remove(self)
            
            if hasattr(self.end_component, 'connected_pipes'):
                if self in self.end_component.connected_pipes:
                    self.end_component.connected_pipes.remove(self)
            
            # Retirer de la scène
            if self.scene():
                self.scene().removeItem(self)
            
            print(f"[ORTHOPIPE] Supprimé: {self.pipe_id}")
            
        except Exception as e:
            print(f"[ORTHOPIPE] Erreur suppression: {e}")

# Classe pour le tracé interactif pendant la création
class InteractivePipeBuilder:
    """
    Constructeur interactif de tuyaux orthogonaux
    Gère le tracé en temps réel pendant la création
    """
    
    def __init__(self, scene, start_component, start_port):
        self.scene = scene
        self.start_component = start_component
        self.start_port = start_port
        self.waypoints = []
        
        # Ligne de preview en temps réel
        self.preview_path = QGraphicsPathItem()
        pen = QPen(QColor(255, 165, 0), 3)  # Orange
        pen.setStyle(Qt.PenStyle.DashLine)
        self.preview_path.setPen(pen)
        self.preview_path.setZValue(10)
        scene.addItem(self.preview_path)
        
        print(f"[BUILDER] Construction interactive démarrée depuis {start_component.component_id}.{start_port}")
    
    def add_waypoint(self, position):
        """Ajoute un point intermédiaire"""
        self.waypoints.append(position)
        print(f"[BUILDER] Point intermédiaire ajouté: {position}")
        
        # Mettre à jour le preview
        self.update_preview(position)
    
    def update_preview(self, current_mouse_pos):
        """Met à jour le preview en temps réel"""
        try:
            start_port_obj = self.start_component.get_port_by_id(self.start_port)
            if not start_port_obj:
                return
            
            start_pos = start_port_obj.scenePos()
            
            # Créer le chemin de preview
            path = QPainterPath()
            points = self.calculate_preview_path(start_pos, current_mouse_pos)
            
            if points:
                path.moveTo(points[0])
                for point in points[1:]:
                    path.lineTo(point)
                
                self.preview_path.setPath(path)
            
        except Exception as e:
            print(f"[BUILDER] Erreur preview: {e}")
    
    def calculate_preview_path(self, start_pos, end_pos):
        """Calcule le tracé de preview orthogonal"""
        points = [start_pos]
        current_pos = start_pos
        
        # Ajouter les waypoints existants
        for waypoint in self.waypoints:
            ortho_points = self.create_orthogonal_segments(current_pos, waypoint)
            points.extend(ortho_points[1:])
            current_pos = waypoint
        
        # Segment final vers la position actuelle
        final_points = self.create_orthogonal_segments(current_pos, end_pos)
        points.extend(final_points[1:])
        
        return points
    
    def create_orthogonal_segments(self, start, end):
        """Crée des segments orthogonaux (même logique que OrthogonalPipe)"""
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        if abs(dx) >= abs(dy):
            intermediate = QPointF(end.x(), start.y())
            return [start, intermediate, end]
        else:
            intermediate = QPointF(start.x(), end.y())
            return [start, intermediate, end]
    
    def finish_pipe(self, end_component, end_port):
        """Termine la construction du tuyau"""
        try:
            # Supprimer le preview
            if self.preview_path.scene():
                self.scene.removeItem(self.preview_path)
            
            # Créer le tuyau final
            pipe = OrthogonalPipe(
                self.start_component, self.start_port,
                end_component, end_port,
                self.waypoints
            )
            
            self.scene.addItem(pipe)
            
            print(f"[BUILDER] Tuyau terminé avec {len(self.waypoints)} points intermédiaires")
            return pipe
            
        except Exception as e:
            print(f"[BUILDER] Erreur finalisation: {e}")
            return None
    
    def cancel(self):
        """Annule la construction"""
        if self.preview_path.scene():
            self.scene.removeItem(self.preview_path)
        print(f"[BUILDER] Construction annulée")

# Alias pour compatibilité avec l'ancien système
HydraulicPipe = OrthogonalPipe
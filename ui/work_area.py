#!/usr/bin/env python3
"""
ui/work_area.py - Zone de travail avec système de zoom unifié
Interface pure avec gestion scale globale des objets hydrauliques
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtCore import QPointF

# Import pour contrôle des objets hydrauliques
try:
    from components.hydraulic_object import HydraulicObject
except ImportError:
    # Fallback si module pas disponible
    HydraulicObject = None

class HydraulicWorkArea(QGraphicsView):
    """
    Zone de travail graphique avec système de zoom unifié
    Responsabilité : Affichage, événements souris ET contrôle scale objets
    """
    
    # === SIGNAUX ÉMIS ===
    
    # Événements souris
    mouse_clicked = pyqtSignal(QPointF, Qt.MouseButton)    # position, bouton
    mouse_moved = pyqtSignal(QPointF)                      # position
    mouse_double_clicked = pyqtSignal(QPointF)             # position
    
    # Événements de sélection
    selection_changed = pyqtSignal(list)                   # liste des items sélectionnés
    
    # Événements de zoom NOUVEAUX
    objects_scale_changed = pyqtSignal(float)              # nouveau scale objets
    view_zoom_changed = pyqtSignal(float)                  # nouveau zoom vue
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Création de la scène
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # SYSTÈME DE ZOOM UNIFIÉ
        self.objects_scale = 1.0  # Scale des objets hydrauliques
        self.view_zoom = 1.0      # Zoom de la vue (transform)
        self.zoom_factor = 1.15   # Facteur d'augmentation par cran molette
        
        # Limites de zoom
        self.min_objects_scale = 0.1
        self.max_objects_scale = 5.0
        self.min_view_zoom = 0.1
        self.max_view_zoom = 10.0
        
        # Mode de zoom (objets vs vue)
        self.zoom_mode = "objects"  # "objects" ou "view"
        
        # Configuration
        self.setup_view()
        self.setup_scene()
        
        print("[WORK_AREA] Zone de travail avec zoom unifié créée")
    
    def setup_view(self):
        """Configuration de la vue graphique"""
        # Taille et position
        self.setMinimumSize(800, 600)
        
        # Qualité de rendu
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        # Interaction
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)  # Sélection multiple
        self.setInteractive(True)
        
        # Ancrage zoom
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Barres de défilement
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        print("[WORK_AREA] Vue configurée avec zoom unifié")
    
    def setup_scene(self):
        """Configuration de la scène graphique"""
        # Taille de la scène (plus grande que la vue)
        self.scene.setSceneRect(0, 0, 2000, 1500)
        
        # Couleur de fond
        self.scene.setBackgroundBrush(QColor(248, 248, 248))  # Gris très clair
        
        # Connexion des signaux de la scène
        self.scene.selectionChanged.connect(self.on_selection_changed)
        
        # Grille optionnelle
        self.grid_enabled = False
        self.grid_size = 20
        
        print("[WORK_AREA] Scène configurée")
    
    # === SYSTÈME DE ZOOM UNIFIÉ ===
    
    def set_zoom_mode(self, mode: str):
        """
        Définit le mode de zoom
        Args:
            mode: "objects" (zoom objets hydrauliques) ou "view" (zoom vue)
        """
        if mode in ["objects", "view"]:
            self.zoom_mode = mode
            print(f"[WORK_AREA] Mode zoom: {mode}")
        else:
            print(f"[WORK_AREA] Mode zoom invalide: {mode}")
    
    def get_zoom_mode(self) -> str:
        """Retourne le mode de zoom actuel"""
        return self.zoom_mode
    
    def set_objects_scale(self, scale: float):
        """
        Change le scale de tous les objets hydrauliques
        Args:
            scale: Nouveau scale (1.0 = normal)
        """
        # Limiter le scale
        scale = max(self.min_objects_scale, min(self.max_objects_scale, scale))
        
        if HydraulicObject and scale != self.objects_scale:
            self.objects_scale = scale
            
            # Appliquer à tous les objets hydrauliques
            HydraulicObject.set_global_scale(scale)
            for obj in self.get_all_hydraulic_objects():
                if hasattr(obj, 'update_scale'):
                    obj.update_scale()
            
            # Émettre signal
            self.objects_scale_changed.emit(scale)
            
            print(f"[WORK_AREA] Scale objets mis à jour: {scale}")
    
    def get_objects_scale(self) -> float:
        """Retourne le scale actuel des objets"""
        return self.objects_scale
    
    def set_view_zoom(self, zoom: float):
        """
        Change le zoom de la vue (transform)
        Args:
            zoom: Nouveau zoom (1.0 = normal)
        """
        # Limiter le zoom
        zoom = max(self.min_view_zoom, min(self.max_view_zoom, zoom))
        
        if zoom != self.view_zoom:
            # Calculer facteur de transformation
            current_transform = self.transform()
            current_scale = current_transform.m11()  # Facteur de scale actuel
            
            # Réinitialiser transform et appliquer nouveau zoom
            self.resetTransform()
            self.scale(zoom, zoom)
            
            self.view_zoom = zoom
            
            # Émettre signal
            self.view_zoom_changed.emit(zoom)
            
            print(f"[WORK_AREA] Zoom vue mis à jour: {zoom}")
    
    def get_view_zoom(self) -> float:
        """Retourne le zoom actuel de la vue"""
        return self.view_zoom
    
    def zoom_objects_in(self, factor: float = None):
        """Zoom avant sur les objets hydrauliques"""
        if factor is None:
            factor = self.zoom_factor
        
        new_scale = self.objects_scale * factor
        self.set_objects_scale(new_scale)
    
    def zoom_objects_out(self, factor: float = None):
        """Zoom arrière sur les objets hydrauliques"""
        if factor is None:
            factor = self.zoom_factor
        
        new_scale = self.objects_scale / factor
        self.set_objects_scale(new_scale)
    
    def zoom_view_in(self, factor: float = None):
        """Zoom avant sur la vue"""
        if factor is None:
            factor = self.zoom_factor
        
        new_zoom = self.view_zoom * factor
        self.set_view_zoom(new_zoom)
    
    def zoom_view_out(self, factor: float = None):
        """Zoom arrière sur la vue"""
        if factor is None:
            factor = self.zoom_factor
        
        new_zoom = self.view_zoom / factor
        self.set_view_zoom(new_zoom)
    
    def reset_objects_scale(self):
        """Remet le scale des objets à 1.0"""
        self.set_objects_scale(1.0)
    
    def reset_view_zoom(self):
        """Remet le zoom de la vue à 1.0"""
        self.set_view_zoom(1.0)
    
    def reset_all_zoom(self):
        """Remet tous les zooms à 1.0"""
        self.reset_objects_scale()
        self.reset_view_zoom()
    
    # === GESTION ÉVÉNEMENTS SOURIS AMÉLIORÉE ===
    
    def wheelEvent(self, event):
        """
        Gestion de la molette - Zoom selon le mode actuel
        """
        # Déterminer direction
        zoom_in = event.angleDelta().y() > 0
        
        if self.zoom_mode == "objects":
            # Zoom objets hydrauliques
            if zoom_in:
                self.zoom_objects_in()
            else:
                self.zoom_objects_out()
        
        elif self.zoom_mode == "view":
            # Zoom vue classique
            if zoom_in:
                self.zoom_view_in()
            else:
                self.zoom_view_out()
        
        event.accept()
    
    def mousePressEvent(self, event):
        """Gestion des clics souris"""
        scene_pos = self.mapToScene(event.pos())
        
        # Émettre signal avec position et bouton
        self.mouse_clicked.emit(scene_pos, event.button())
        
        # Comportement par défaut (sélection, etc.)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Gestion du mouvement de la souris"""
        scene_pos = self.mapToScene(event.pos())
        
        # Émettre signal de mouvement
        self.mouse_moved.emit(scene_pos)
        
        # Comportement par défaut
        super().mouseMoveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Gestion du double-clic"""
        scene_pos = self.mapToScene(event.pos())
        
        # Émettre signal de double-clic
        self.mouse_double_clicked.emit(scene_pos)
        
        # Comportement par défaut
        super().mouseDoubleClickEvent(event)
    
    def keyPressEvent(self, event):
        """
        Gestion clavier pour zoom
        """
        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            # + : Zoom avant
            if self.zoom_mode == "objects":
                self.zoom_objects_in()
            else:
                self.zoom_view_in()
            event.accept()
            
        elif event.key() == Qt.Key.Key_Minus:
            # - : Zoom arrière
            if self.zoom_mode == "objects":
                self.zoom_objects_out()
            else:
                self.zoom_view_out()
            event.accept()
            
        elif event.key() == Qt.Key.Key_0:
            # 0 : Reset zoom
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.reset_all_zoom()
            elif self.zoom_mode == "objects":
                self.reset_objects_scale()
            else:
                self.reset_view_zoom()
            event.accept()
            
        elif event.key() == Qt.Key.Key_O:
            # O : Mode objets
            self.set_zoom_mode("objects")
            event.accept()
            
        elif event.key() == Qt.Key.Key_V:
            # V : Mode vue
            self.set_zoom_mode("view")
            event.accept()
            
        else:
            super().keyPressEvent(event)
    
    # === GRILLE (inchangé) ===
    
    def enable_grid(self, enabled: bool = True, size: int = 20):
        """Active/désactive l'affichage d'une grille"""
        self.grid_enabled = enabled
        self.grid_size = size
        
        if enabled:
            self.draw_grid()
        else:
            # Supprimer la grille existante
            for item in self.scene.items():
                if hasattr(item, 'is_grid_line') and item.is_grid_line:
                    self.scene.removeItem(item)
        
        self.scene.update()
    
    def draw_grid(self):
        """Dessine une grille sur la scène"""
        if not self.grid_enabled:
            return
        
        rect = self.scene.sceneRect()
        pen = QPen(QColor(220, 220, 220), 1, Qt.PenStyle.DotLine)
        
        # Lignes verticales
        x = rect.left()
        while x <= rect.right():
            line = self.scene.addLine(x, rect.top(), x, rect.bottom(), pen)
            line.is_grid_line = True
            line.setZValue(-1000)  # Arrière-plan
            x += self.grid_size
        
        # Lignes horizontales
        y = rect.top()
        while y <= rect.bottom():
            line = self.scene.addLine(rect.left(), y, rect.right(), y, pen)
            line.is_grid_line = True
            line.setZValue(-1000)  # Arrière-plan
            y += self.grid_size
    
    # === GESTION SÉLECTION (inchangé) ===
    
    def on_selection_changed(self):
        """Réaction aux changements de sélection"""
        selected_items = self.scene.selectedItems()
        
        # Filtrer pour ne garder que les objets hydrauliques
        hydraulic_objects = []
        for item in selected_items:
            if hasattr(item, 'component_id'):  # C'est un objet hydraulique
                hydraulic_objects.append(item)
        
        # Émettre signal
        self.selection_changed.emit(hydraulic_objects)
    
    def select_all_objects(self):
        """Sélectionne tous les objets hydrauliques"""
        for item in self.scene.items():
            if hasattr(item, 'component_id'):
                item.setSelected(True)
    
    def clear_selection(self):
        """Désélectionne tous les objets"""
        self.scene.clearSelection()
    
    # === GESTION SCÈNE (inchangé) ===
    
    def clear_scene(self):
        """Vide complètement la scène"""
        self.scene.clear()
        
        # Reconfigurer la scène
        self.setup_scene()
        
        # Redessiner la grille si nécessaire
        if self.grid_enabled:
            self.draw_grid()
        
        # Reset des zooms
        self.reset_all_zoom()
        
        print("[WORK_AREA] Scène vidée et zoom reseté")
    
    def add_item(self, item):
        """Ajoute un item à la scène"""
        self.scene.addItem(item)
    
    def remove_item(self, item):
        """Supprime un item de la scène"""
        if item in self.scene.items():
            self.scene.removeItem(item)
    
    def get_items_at_position(self, position: QPointF):
        """Retourne les items à une position donnée"""
        return self.scene.items(position)
    
    def get_all_hydraulic_objects(self):
        """Retourne tous les objets hydrauliques de la scène"""
        hydraulic_objects = []
        for item in self.scene.items():
            if hasattr(item, 'component_id'):
                hydraulic_objects.append(item)
        return hydraulic_objects
    
    # === UTILITAIRES AFFICHAGE ===
    
    def center_on_objects(self):
        """Centre la vue sur tous les objets"""
        objects = self.get_all_hydraulic_objects()
        
        if objects:
            # Calculer le rectangle englobant
            bounding_rect = objects[0].sceneBoundingRect()
            for obj in objects[1:]:
                bounding_rect = bounding_rect.united(obj.sceneBoundingRect())
            
            # Centrer sur ce rectangle avec marge
            margin = 50
            bounding_rect.adjust(-margin, -margin, margin, margin)
            self.fitInView(bounding_rect, Qt.AspectRatioMode.KeepAspectRatio)
            
            # Mettre à jour view_zoom
            self.view_zoom = self.transform().m11()
    
    def zoom_to_fit(self):
        """Zoom pour afficher tous les objets"""
        if self.get_all_hydraulic_objects():
            self.center_on_objects()
        else:
            # Si pas d'objets, afficher toute la scène
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.view_zoom = self.transform().m11()
    
    # === INFORMATIONS DEBUG ===
    
    def get_view_info(self) -> dict:
        """Retourne des informations sur la vue pour debug"""
        return {
            "scene_rect": self.scene.sceneRect(),
            "view_rect": self.viewport().rect(),
            "total_items": len(self.scene.items()),
            "hydraulic_objects": len(self.get_all_hydraulic_objects()),
            "selected_items": len(self.scene.selectedItems()),
            "zoom_info": {
                "mode": self.zoom_mode,
                "objects_scale": self.objects_scale,
                "view_zoom": self.view_zoom,
                "view_transform": self.transform()
            },
            "grid_enabled": self.grid_enabled
        }
    
    def print_zoom_info(self):
        """Affiche les informations de zoom"""
        print(f"\n=== ZOOM INFO ===")
        print(f"Mode: {self.zoom_mode}")
        print(f"Scale objets: {self.objects_scale:.2f}")
        print(f"Zoom vue: {self.view_zoom:.2f}")
        print(f"Transform vue: {self.transform()}")
        print(f"Objets hydrauliques: {len(self.get_all_hydraulic_objects())}")
        print("==================\n")


# === POINT D'ENTRÉE POUR TESTS ===

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QSlider
    
    app = QApplication(sys.argv)
    
    # Test de la zone de travail avec zoom
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Contrôles de zoom
    controls_widget = QWidget()
    controls_layout = QHBoxLayout(controls_widget)
    
    # Mode zoom
    mode_label = QLabel("Mode: objects")
    controls_layout.addWidget(mode_label)
    
    btn_mode_objects = QPushButton("Mode Objets")
    btn_mode_view = QPushButton("Mode Vue")
    controls_layout.addWidget(btn_mode_objects)
    controls_layout.addWidget(btn_mode_view)
    
    # Scale objets
    objects_scale_label = QLabel("Scale objets: 1.00")
    controls_layout.addWidget(objects_scale_label)
    
    objects_scale_slider = QSlider(Qt.Orientation.Horizontal)
    objects_scale_slider.setMinimum(10)   # 0.1x
    objects_scale_slider.setMaximum(500)  # 5.0x
    objects_scale_slider.setValue(100)    # 1.0x
    controls_layout.addWidget(objects_scale_slider)
    
    # Boutons zoom
    btn_zoom_in = QPushButton("Zoom +")
    btn_zoom_out = QPushButton("Zoom -")
    btn_reset = QPushButton("Reset")
    controls_layout.addWidget(btn_zoom_in)
    controls_layout.addWidget(btn_zoom_out)
    controls_layout.addWidget(btn_reset)
    
    layout.addWidget(controls_widget)
    
    # Zone de travail
    work_area = HydraulicWorkArea()
    layout.addWidget(work_area)
    
    # Fonctions de contrôle
    def set_mode_objects():
        work_area.set_zoom_mode("objects")
        mode_label.setText("Mode: objects")
    
    def set_mode_view():
        work_area.set_zoom_mode("view")
        mode_label.setText("Mode: view")
    
    def update_objects_scale(value):
        scale = value / 100.0
        work_area.set_objects_scale(scale)
        objects_scale_label.setText(f"Scale objets: {scale:.2f}")
    
    def zoom_in():
        if work_area.get_zoom_mode() == "objects":
            work_area.zoom_objects_in()
        else:
            work_area.zoom_view_in()
    
    def zoom_out():
        if work_area.get_zoom_mode() == "objects":
            work_area.zoom_objects_out()
        else:
            work_area.zoom_view_out()
    
    def reset_zoom():
        work_area.reset_all_zoom()
        objects_scale_slider.setValue(100)
        objects_scale_label.setText("Scale objets: 1.00")
    
    # Connexions
    btn_mode_objects.clicked.connect(set_mode_objects)
    btn_mode_view.clicked.connect(set_mode_view)
    objects_scale_slider.valueChanged.connect(update_objects_scale)
    btn_zoom_in.clicked.connect(zoom_in)
    btn_zoom_out.clicked.connect(zoom_out)
    btn_reset.clicked.connect(reset_zoom)
    
    # Connexions signaux work_area
    work_area.objects_scale_changed.connect(
        lambda scale: objects_scale_label.setText(f"Scale objets: {scale:.2f}")
    )
    work_area.mouse_clicked.connect(lambda pos, btn: print(f"Clic: {pos} ({btn})"))
    work_area.selection_changed.connect(lambda items: print(f"Sélection: {len(items)} objets"))
    
    # Boutons de test
    test_buttons = QWidget()
    test_layout = QHBoxLayout(test_buttons)
    
    btn_grid = QPushButton("Toggle Grid")
    btn_grid.clicked.connect(lambda: work_area.enable_grid(not work_area.grid_enabled))
    test_layout.addWidget(btn_grid)
    
    btn_info = QPushButton("Zoom Info")
    btn_info.clicked.connect(work_area.print_zoom_info)
    test_layout.addWidget(btn_info)
    
    layout.addWidget(test_buttons)
    
    window.setCentralWidget(central_widget)
    window.setWindowTitle("Test WorkArea Zoom Unifié")
    window.show()
    
    print("=== TEST WORK AREA ZOOM UNIFIÉ ===")
    print("CONTRÔLES:")
    print("• Molette souris: zoom selon mode actuel")
    print("• +/- : zoom clavier")
    print("• 0 : reset zoom")
    print("• O/V : changer mode objets/vue")
    print("• Ctrl+0 : reset tout")
    
    sys.exit(app.exec())
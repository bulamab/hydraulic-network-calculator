#!/usr/bin/env python3
"""
ui/toolbar.py - Barre d'outils pour manipulation des objets hydrauliques
Rotation, alignement et autres transformations
"""

from PyQt6.QtWidgets import QToolBar, QWidget, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QBrush, QColor, QPolygon

class HydraulicToolbar(QToolBar):
    """
    Barre d'outils pour manipulation des objets hydrauliques
    Rotation, alignement et transformations
    """
    
    # === SIGNAUX ÉMIS ===
    
    # Rotation
    rotate_left_requested = pyqtSignal()       # Rotation 90° gauche
    rotate_right_requested = pyqtSignal()      # Rotation 90° droite
    
    # Alignement (futur)
    align_horizontal_requested = pyqtSignal()   # Alignement horizontal
    align_vertical_requested = pyqtSignal()     # Alignement vertical
    align_grid_requested = pyqtSignal()         # Alignement sur grille
    
    # Transformations (futur)
    flip_horizontal_requested = pyqtSignal()    # Miroir horizontal
    flip_vertical_requested = pyqtSignal()      # Miroir vertical
    
    # État
    selection_changed = pyqtSignal(int)         # Nombre d'objets sélectionnés
    
    def __init__(self, parent=None):
        super().__init__("Outils Hydrauliques", parent)
        
        # État interne
        self.selected_objects_count = 0
        
        # Configuration toolbar
        self.setMovable(True)
        self.setFloatable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setObjectName("hydraulicToolbar")
        
        # Construction interface
        self.create_toolbar_widgets()
        self.update_buttons_state()
        
        print("[TOOLBAR] Barre d'outils hydrauliques créée")
    
    def create_toolbar_widgets(self):
        """Construction des widgets de la barre d'outils"""
        
        # === LABEL INFORMATION ===
        self.info_label = QLabel("Aucun objet sélectionné")
        self.info_label.setObjectName("toolbarInfo")
        self.addWidget(self.info_label)
        
        # Séparateur
        self.addSeparator()
        
        # === SECTION ROTATION ===
        self.create_rotation_section()
        
        # Séparateur
        self.addSeparator()
        
        # === SECTION ALIGNEMENT (préparé pour futur) ===
        self.create_alignment_section()
        
        # Séparateur
        self.addSeparator()
        
        # === SECTION TRANSFORMATIONS (préparé pour futur) ===
        self.create_transform_section()
        
        # Stretch pour pousser les éléments à droite
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)
    
    def create_rotation_section(self):
        """Création des boutons de rotation"""
        
        # Label section
        rotation_label = QLabel("Rotation:")
        rotation_label.setObjectName("toolbarSectionLabel")
        self.addWidget(rotation_label)
        
        # Bouton rotation gauche (90° sens anti-horaire)
        self.rotate_left_btn = QPushButton()
        self.rotate_left_btn.setIcon(self.create_rotate_left_icon())
        self.rotate_left_btn.setText("90° ↺")
        self.rotate_left_btn.setToolTip("Rotation 90° sens anti-horaire\nRaccourci: Ctrl+L")
        self.rotate_left_btn.setObjectName("rotateLeftButton")
        self.rotate_left_btn.clicked.connect(self.on_rotate_left)
        self.addWidget(self.rotate_left_btn)
        
        # Bouton rotation droite (90° sens horaire)
        self.rotate_right_btn = QPushButton()
        self.rotate_right_btn.setIcon(self.create_rotate_right_icon())
        self.rotate_right_btn.setText("90° ↻")
        self.rotate_right_btn.setToolTip("Rotation 90° sens horaire\nRaccourci: Ctrl+R")
        self.rotate_right_btn.setObjectName("rotateRightButton")
        self.rotate_right_btn.clicked.connect(self.on_rotate_right)
        self.addWidget(self.rotate_right_btn)
    
    def create_alignment_section(self):
        """Création des boutons d'alignement (préparé pour futur)"""
        
        # Label section
        align_label = QLabel("Alignement:")
        align_label.setObjectName("toolbarSectionLabel")
        self.addWidget(align_label)
        
        # Bouton alignement horizontal
        self.align_h_btn = QPushButton()
        self.align_h_btn.setIcon(self.create_align_horizontal_icon())
        self.align_h_btn.setText("⫷ Horizontal")
        self.align_h_btn.setToolTip("Aligner horizontalement sur le dernier objet sélectionné")
        self.align_h_btn.setObjectName("alignHorizontalButton")
        self.align_h_btn.clicked.connect(self.on_align_horizontal)
        # ACTIVÉ MAINTENANT !
        self.addWidget(self.align_h_btn)
        
        # Bouton alignement vertical
        self.align_v_btn = QPushButton()
        self.align_v_btn.setIcon(self.create_align_vertical_icon())
        self.align_v_btn.setText("⫸ Vertical")
        self.align_v_btn.setToolTip("Aligner verticalement sur le dernier objet sélectionné")
        self.align_v_btn.setObjectName("alignVerticalButton")
        self.align_v_btn.clicked.connect(self.on_align_vertical)
        # ACTIVÉ MAINTENANT !
        self.addWidget(self.align_v_btn)
    
    def create_transform_section(self):
        """Création des boutons de transformation (préparé pour futur)"""
        
        # Label section
        transform_label = QLabel("Transformation:")
        transform_label.setObjectName("toolbarSectionLabel")
        self.addWidget(transform_label)
        
        # Bouton miroir horizontal
        self.flip_h_btn = QPushButton()
        self.flip_h_btn.setIcon(self.create_flip_horizontal_icon())
        self.flip_h_btn.setText("⟷ Miroir H")
        self.flip_h_btn.setToolTip("Miroir horizontal de chaque objet par rapport à son centre")
        self.flip_h_btn.setObjectName("flipHorizontalButton")
        self.flip_h_btn.clicked.connect(self.on_flip_horizontal)
        self.addWidget(self.flip_h_btn)
        
        # Bouton miroir vertical
        self.flip_v_btn = QPushButton()
        self.flip_v_btn.setIcon(self.create_flip_vertical_icon())
        self.flip_v_btn.setText("⟷ Miroir V")
        self.flip_v_btn.setToolTip("Miroir vertical de chaque objet par rapport à son centre")
        self.flip_v_btn.setObjectName("flipVerticalButton")
        self.flip_v_btn.clicked.connect(self.on_flip_vertical)
        self.addWidget(self.flip_v_btn)
    
    # === CRÉATION D'ICÔNES ===
    
    def create_rotate_left_icon(self) -> QIcon:
        """Crée icône rotation gauche"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dessiner flèche circulaire gauche
        pen = QPen(QColor(52, 152, 219), 3)
        painter.setPen(pen)
        
        # Arc de cercle
        painter.drawArc(4, 4, 16, 16, 45 * 16, 270 * 16)  # 270° arc
        
        # Pointe de flèche
        painter.drawLine(4, 10, 8, 6)
        painter.drawLine(4, 10, 8, 14)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_rotate_right_icon(self) -> QIcon:
        """Crée icône rotation droite"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dessiner flèche circulaire droite
        pen = QPen(QColor(52, 152, 219), 3)
        painter.setPen(pen)
        
        # Arc de cercle
        painter.drawArc(4, 4, 16, 16, 45 * 16, -270 * 16)  # -270° arc
        
        # Pointe de flèche
        painter.drawLine(20, 10, 16, 6)
        painter.drawLine(20, 10, 16, 14)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_align_horizontal_icon(self) -> QIcon:
        """Crée icône alignement horizontal"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Ligne de référence horizontale
        pen = QPen(QColor(231, 76, 60), 2)
        painter.setPen(pen)
        painter.drawLine(2, 12, 22, 12)
        
        # Rectangles à aligner
        brush = QBrush(QColor(52, 152, 219, 100))
        painter.setBrush(brush)
        painter.setPen(QPen(QColor(52, 152, 219), 2))
        
        painter.drawRect(4, 8, 4, 8)   # Rectangle gauche
        painter.drawRect(10, 6, 4, 12)  # Rectangle centre  
        painter.drawRect(16, 9, 4, 6)   # Rectangle droite
        
        painter.end()
        return QIcon(pixmap)
    
    def create_align_vertical_icon(self) -> QIcon:
        """Crée icône alignement vertical"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Ligne de référence verticale
        pen = QPen(QColor(231, 76, 60), 2)
        painter.setPen(pen)
        painter.drawLine(12, 2, 12, 22)
        
        # Rectangles à aligner
        brush = QBrush(QColor(52, 152, 219, 100))
        painter.setBrush(brush)
        painter.setPen(QPen(QColor(52, 152, 219), 2))
        
        painter.drawRect(8, 4, 8, 4)   # Rectangle haut
        painter.drawRect(6, 10, 12, 4)  # Rectangle centre
        painter.drawRect(9, 16, 6, 4)   # Rectangle bas
        
        painter.end()
        return QIcon(pixmap)
    
    def create_flip_horizontal_icon(self) -> QIcon:
        """Crée icône miroir horizontal"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Ligne de réflexion verticale
        pen = QPen(QColor(231, 76, 60), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(12, 4, 12, 20)
        
        # Formes originale et miroir
        brush = QBrush(QColor(52, 152, 219, 100))
        painter.setBrush(brush)
        painter.setPen(QPen(QColor(52, 152, 219), 2))
        
        # Triangle gauche
        left_triangle = QPolygon([QPoint(4, 8), QPoint(10, 12), QPoint(4, 16)])
        painter.drawPolygon(left_triangle)
        
        # Triangle droite (miroir)
        right_triangle = QPolygon([QPoint(20, 8), QPoint(14, 12), QPoint(20, 16)])
        painter.drawPolygon(right_triangle)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_flip_vertical_icon(self) -> QIcon:
        """Crée icône miroir vertical"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Ligne de réflexion horizontale
        pen = QPen(QColor(231, 76, 60), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(4, 12, 20, 12)
        
        # Formes originale et miroir
        brush = QBrush(QColor(52, 152, 219, 100))
        painter.setBrush(brush)
        painter.setPen(QPen(QColor(52, 152, 219), 2))
        
        # Triangle haut
        top_triangle = QPolygon([QPoint(8, 4), QPoint(12, 10), QPoint(16, 4)])
        painter.drawPolygon(top_triangle)
        
        # Triangle bas (miroir)
        bottom_triangle = QPolygon([QPoint(8, 20), QPoint(12, 14), QPoint(16, 20)])
        painter.drawPolygon(bottom_triangle)
        
        painter.end()
        return QIcon(pixmap)
    
    # === GESTIONNAIRES D'ÉVÉNEMENTS ===
    
    def on_rotate_left(self):
        """Rotation 90° sens anti-horaire"""
        print("[TOOLBAR] Rotation 90° gauche demandée")
        self.rotate_left_requested.emit()
    
    def on_rotate_right(self):
        """Rotation 90° sens horaire"""
        print("[TOOLBAR] Rotation 90° droite demandée")
        self.rotate_right_requested.emit()
    
    def on_align_horizontal(self):
        """Alignement horizontal"""
        print("[TOOLBAR] Alignement horizontal demandé")
        self.align_horizontal_requested.emit()
    
    def on_align_vertical(self):
        """Alignement vertical"""
        print("[TOOLBAR] Alignement vertical demandé")
        self.align_vertical_requested.emit()
    
    def on_flip_horizontal(self):
        """Miroir horizontal"""
        print("[TOOLBAR] Miroir horizontal demandé")
        self.flip_horizontal_requested.emit()
    
    def on_flip_vertical(self):
        """Miroir vertical"""
        print("[TOOLBAR] Miroir vertical demandé")
        self.flip_vertical_requested.emit()
    
    # === GESTION DE LA SÉLECTION ===
    
    @pyqtSlot(list)
    def on_selection_changed(self, selected_objects):
        """Réaction aux changements de sélection"""
        count = len(selected_objects)
        self.selected_objects_count = count
        
        # Mettre à jour l'état des boutons
        self.update_buttons_state()
        
        # Mettre à jour le label d'information
        if count == 0:
            self.info_label.setText("Aucun objet sélectionné")
        elif count == 1:
            obj = selected_objects[0]
            obj_type = getattr(obj, 'object_type', 'Objet')
            obj_id = getattr(obj, 'component_id', 'unknown')
            self.info_label.setText(f"1 {obj_type} sélectionné ({obj_id})")
        else:
            self.info_label.setText(f"{count} objets sélectionnés")
        
        # Émettre signal
        self.selection_changed.emit(count)
        
        print(f"[TOOLBAR] Sélection mise à jour: {count} objet(s)")
    
    def update_buttons_state(self):
        """Met à jour l'état d'activation des boutons selon la sélection"""
        has_selection = self.selected_objects_count > 0
        has_multiple_selection = self.selected_objects_count > 1
        
        # Boutons de rotation : nécessitent au moins 1 objet
        self.rotate_left_btn.setEnabled(has_selection)
        self.rotate_right_btn.setEnabled(has_selection)
        
        # Boutons d'alignement : nécessitent au moins 2 objets
        self.align_h_btn.setEnabled(has_multiple_selection)
        self.align_v_btn.setEnabled(has_multiple_selection)
        
        # Boutons de miroir : nécessitent au moins 1 objet (miroir individuel)
        self.flip_h_btn.setEnabled(has_selection)
        self.flip_v_btn.setEnabled(has_selection)
    
    # === RACCOURCIS CLAVIER ===
    
    def setup_shortcuts(self, parent_widget):
        """Configure les raccourcis clavier (à appeler depuis la fenêtre principale)"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # Raccourci rotation gauche: Ctrl+L
        shortcut_left = QShortcut(QKeySequence("Ctrl+L"), parent_widget)
        shortcut_left.activated.connect(self.on_rotate_left)
        
        # Raccourci rotation droite: Ctrl+R  
        shortcut_right = QShortcut(QKeySequence("Ctrl+R"), parent_widget)
        shortcut_right.activated.connect(self.on_rotate_right)
        
        print("[TOOLBAR] Raccourcis clavier configurés: Ctrl+L, Ctrl+R")
    
    # === MÉTHODES UTILITAIRES ===
    
    def get_selected_count(self) -> int:
        """Retourne le nombre d'objets sélectionnés"""
        return self.selected_objects_count
    
    def reset_selection(self):
        """Remet à zéro la sélection"""
        self.on_selection_changed([])
    
    def enable_alignment_tools(self, enabled: bool = True):
        """Active/désactive les outils d'alignement - OBSOLÈTE, alignement toujours actif"""
        print(f"[TOOLBAR] enable_alignment_tools obsolète - alignement toujours actif selon sélection")
    
    def enable_transform_tools(self, enabled: bool = True):
        """Active/désactive les outils de transformation (miroirs pas encore activés)"""
        print(f"[TOOLBAR] Outils miroir pas encore activés - utilisez rotation et alignement")


# === STYLES CSS POUR LA TOOLBAR ===

def get_toolbar_stylesheet() -> str:
    """Retourne les styles CSS pour la barre d'outils"""
    return """
    /* === TOOLBAR HYDRAULIQUE === */
    
    QToolBar#hydraulicToolbar {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                   stop: 0 #ffffff, stop: 1 #f8f9fa);
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 4px;
        margin: 2px;
        spacing: 8px;
    }
    
    QToolBar#hydraulicToolbar::separator {
        background-color: #d0d0d0;
        width: 2px;
        margin: 4px;
    }
    
    /* === BOUTONS ROTATION === */
    
    #rotateLeftButton, #rotateRightButton {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
        min-width: 80px;
        min-height: 28px;
    }
    
    #rotateLeftButton:hover, #rotateRightButton:hover {
        background-color: #2980b9;
        transform: translateY(-1px);
    }
    
    #rotateLeftButton:pressed, #rotateRightButton:pressed {
        background-color: #21618c;
        transform: translateY(0px);
    }
    
    #rotateLeftButton:disabled, #rotateRightButton:disabled {
        background-color: #bdc3c7;
        color: #7f8c8d;
    }
    
    /* === BOUTONS ALIGNEMENT === */
    
    #alignHorizontalButton, #alignVerticalButton {
        background-color: #27ae60;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
        min-width: 90px;
        min-height: 28px;
    }
    
    #alignHorizontalButton:hover, #alignVerticalButton:hover {
        background-color: #229954;
        transform: translateY(-1px);
    }
    
    #alignHorizontalButton:disabled, #alignVerticalButton:disabled {
        background-color: #bdc3c7;
        color: #7f8c8d;
    }
    
    /* === BOUTONS TRANSFORMATION === */
    
    #flipHorizontalButton, #flipVerticalButton {
        background-color: #9b59b6;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
        min-width: 80px;
        min-height: 28px;
    }
    
    #flipHorizontalButton:hover, #flipVerticalButton:hover {
        background-color: #8e44ad;
        transform: translateY(-1px);
    }
    
    #flipHorizontalButton:disabled, #flipVerticalButton:disabled {
        background-color: #bdc3c7;
        color: #7f8c8d;
    }
    
    /* === LABELS === */
    
    #toolbarInfo {
        font-weight: bold;
        color: #2c3e50;
        padding: 6px 12px;
        background-color: #ecf0f1;
        border-radius: 4px;
        min-width: 150px;
    }
    
    #toolbarSectionLabel {
        font-weight: bold;
        color: #34495e;
        font-size: 11px;
        padding: 4px 8px;
    }
    """


# === POINT D'ENTRÉE POUR TESTS ===

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout
    
    app = QApplication(sys.argv)
    
    # Interface de test
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Créer la toolbar
    toolbar = HydraulicToolbar()
    
    # Ajouter stylesheet
    window.setStyleSheet(get_toolbar_stylesheet())
    
    # Log des événements
    log = QTextEdit()
    log.setMaximumHeight(200)
    layout.addWidget(log)
    
    def log_event(message):
        log.append(f"• {message}")
    
    # Connexions de test
    toolbar.rotate_left_requested.connect(lambda: log_event("🔄 Rotation 90° GAUCHE"))
    toolbar.rotate_right_requested.connect(lambda: log_event("🔄 Rotation 90° DROITE"))
    toolbar.align_horizontal_requested.connect(lambda: log_event("⫷ Alignement HORIZONTAL"))
    toolbar.align_vertical_requested.connect(lambda: log_event("⫸ Alignement VERTICAL"))
    toolbar.selection_changed.connect(lambda count: log_event(f"📋 Sélection: {count} objet(s)"))
    
    # Ajouter la toolbar à la fenêtre
    window.addToolBar(toolbar)
    
    # Raccourcis clavier
    toolbar.setup_shortcuts(window)
    
    # Boutons de test de sélection
    test_widget = QWidget()
    test_layout = QHBoxLayout(test_widget)
    
    btn_select_1 = QPushButton("Simuler 1 objet sélectionné")
    btn_select_1.clicked.connect(lambda: toolbar.on_selection_changed([{"id": "pump_001", "type": "PUMP"}]))
    test_layout.addWidget(btn_select_1)
    
    btn_select_3 = QPushButton("Simuler 3 objets sélectionnés")
    btn_select_3.clicked.connect(lambda: toolbar.on_selection_changed([
        {"id": "pump_001"}, {"id": "valve_002"}, {"id": "tank_003"}
    ]))
    test_layout.addWidget(btn_select_3)
    
    btn_select_0 = QPushButton("Aucune sélection")
    btn_select_0.clicked.connect(lambda: toolbar.on_selection_changed([]))
    test_layout.addWidget(btn_select_0)
    
    # Boutons d'activation des fonctionnalités futures
    btn_enable_align = QPushButton("Activer Alignement")
    btn_enable_align.clicked.connect(lambda: toolbar.enable_alignment_tools(True))
    test_layout.addWidget(btn_enable_align)
    
    btn_enable_transform = QPushButton("Activer Transformation")
    btn_enable_transform.clicked.connect(lambda: toolbar.enable_transform_tools(True))
    test_layout.addWidget(btn_enable_transform)
    
    layout.addWidget(test_widget)
    
    window.setCentralWidget(central_widget)
    window.setWindowTitle("Test Barre d'Outils Hydraulique")
    window.show()
    
    log_event("🚀 Barre d'outils chargée")
    log_event("📝 Testez les boutons et raccourcis Ctrl+L / Ctrl+R")
    log_event("🔧 Simulez des sélections avec les boutons de test")
    
    print("=== TEST HYDRAULIC TOOLBAR ===")
    print("• Boutons rotation: toujours disponibles")
    print("• Boutons alignement: activés si 2+ objets sélectionnés")
    print("• Raccourcis: Ctrl+L (gauche), Ctrl+R (droite)")
    print("• Icônes: créées dynamiquement")
    
    sys.exit(app.exec())
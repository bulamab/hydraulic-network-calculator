#!/usr/bin/env python3
"""
ui/styles.py - Styles CSS centralisés pour l'application
Thème moderne et cohérent pour toute l'interface
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

# === COULEURS DU THÈME ===

COLORS = {
    # Couleurs principales
    "primary": "#3498db",      # Bleu principal
    "primary_dark": "#2980b9", # Bleu foncé
    "secondary": "#2c3e50",    # Gris-bleu foncé
    "accent": "#e74c3c",       # Rouge accent
    
    # Couleurs fonctionnelles
    "success": "#27ae60",      # Vert succès
    "warning": "#f39c12",      # Orange avertissement
    "error": "#e74c3c",        # Rouge erreur
    "info": "#3498db",         # Bleu information
    
    # Couleurs spécialisées
    "epanet": "#9b59b6",       # Violet EPANET
    "connection": "#27ae60",   # Vert connexion
    "connection_active": "#e74c3c",  # Rouge connexion active
    
    # Couleurs de fond
    "background": "#f8f9fa",   # Fond principal
    "sidebar": "#ffffff",      # Fond sidebar
    "work_area": "#f8f8f8",    # Fond zone de travail
    
    # Couleurs de texte
    "text_primary": "#2c3e50", # Texte principal
    "text_secondary": "#7f8c8d", # Texte secondaire
    "text_muted": "#bdc3c7",   # Texte discret
    
    # Couleurs de bordure
    "border": "#e0e0e0",       # Bordure standard
    "border_active": "#3498db", # Bordure active
    "border_hover": "#bdc3c7", # Bordure survol
}

# === POLICES ===

FONTS = {
    "main": "Segoe UI, Arial, sans-serif",
    "title": "Segoe UI, Arial, sans-serif",
    "mono": "Consolas, Monaco, monospace"
}

# === STYLES CSS PRINCIPAUX ===

def get_main_stylesheet() -> str:
    """Retourne la feuille de style principale"""
    return f"""
    /* === STYLES GLOBAUX === */
    
    QMainWindow {{
        background-color: {COLORS['background']};
        font-family: {FONTS['main']};
        font-size: 12px;
    }}
    
    /* === SIDEBAR === */
    
    #sidebar {{
        background-color: {COLORS['sidebar']};
        border-right: 2px solid {COLORS['border']};
        border-radius: 0px;
    }}
    
    /* === TITRES ET LABELS === */
    
    #mainTitle {{
        font-size: 18px;
        font-weight: bold;
        color: {COLORS['text_primary']};
        padding: 10px 0;
        border-bottom: 3px solid {COLORS['primary']};
        margin-bottom: 15px;
    }}
    
    #versionLabel {{
        font-size: 11px;
        color: {COLORS['text_secondary']};
        font-style: italic;
        margin-bottom: 10px;
    }}
    
    #epanetLabel {{
        font-size: 12px;
        font-weight: bold;
        color: {COLORS['epanet']};
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 5px;
        border: 1px solid {COLORS['border']};
        margin-bottom: 15px;
    }}
    
    #sectionTitle {{
        font-size: 14px;
        font-weight: bold;
        color: {COLORS['text_primary']};
        margin: 20px 0 8px 0;
        padding-bottom: 5px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    #counterLabel {{
        font-size: 11px;
        color: {COLORS['text_secondary']};
        padding: 2px 0;
    }}
    
    /* === BOUTONS OBJETS HYDRAULIQUES === */
    
    #objectButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        padding: 12px 15px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 13px;
        margin: 3px 0;
        text-align: left;
        min-height: 20px;
    }}
    
    #objectButton:hover {{
        background-color: {COLORS['primary_dark']};
        transform: translateY(-1px);
    }}
    
    #objectButton:pressed {{
        background-color: {COLORS['primary_dark']};
        transform: translateY(0px);
    }}
    
    /* === BOUTON CONNEXION === */
    
    #connectionButton {{
        background-color: {COLORS['connection']};
        color: white;
        border: none;
        padding: 12px 15px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 13px;
        margin: 3px 0;
        min-height: 20px;
    }}
    
    #connectionButton:hover {{
        background-color: #229954;
    }}
    
    #connectionButton:checked {{
        background-color: {COLORS['connection_active']};
        color: white;
    }}
    
    #connectionButton:checked:hover {{
        background-color: #c0392b;
    }}
    
    /* === BOUTONS EPANET === */
    
    #epanetButton {{
        background-color: {COLORS['epanet']};
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
        margin: 3px 0;
        text-align: left;
        min-height: 18px;
    }}
    
    #epanetButton:hover {{
        background-color: #8e44ad;
        transform: translateY(-1px);
    }}
    
    #epanetButton:pressed {{
        background-color: #8e44ad;
        transform: translateY(0px);
    }}
    
    /* === BOUTONS ACTIONS === */
    
    #actionButton {{
        background-color: #95a5a6;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
        margin: 3px 0;
        text-align: left;
        min-height: 18px;
    }}
    
    #actionButton:hover {{
        background-color: #7f8c8d;
        transform: translateY(-1px);
    }}
    
    #actionButton:pressed {{
        background-color: #7f8c8d;
        transform: translateY(0px);
    }}
    
    /* === DIALOGS ET MESSAGES === */
    
    QDialog {{
        background-color: {COLORS['sidebar']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
    }}
    
    QMessageBox {{
        background-color: {COLORS['sidebar']};
        font-family: {FONTS['main']};
        font-size: 12px;
    }}
    
    /* === CHAMPS DE SAISIE === */
    
    QLineEdit {{
        border: 2px solid {COLORS['border']};
        border-radius: 5px;
        padding: 8px;
        font-size: 12px;
        background-color: white;
    }}
    
    QLineEdit:focus {{
        border-color: {COLORS['primary']};
        outline: none;
    }}
    
    QLineEdit:disabled {{
        background-color: #f5f5f5;
        color: {COLORS['text_secondary']};
    }}
    
    /* === LABELS DE FORMULAIRE === */
    
    QLabel {{
        color: {COLORS['text_primary']};
        font-size: 12px;
    }}
    
    /* === BARRES DE DÉFILEMENT === */
    
    QScrollBar:vertical {{
        background-color: #f0f0f0;
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['text_muted']};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['text_secondary']};
    }}
    
    QScrollBar:horizontal {{
        background-color: #f0f0f0;
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['text_muted']};
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['text_secondary']};
    }}
    
    /* === TOOLTIPS === */
    
    QToolTip {{
        background-color: {COLORS['secondary']};
        color: white;
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 5px;
        font-size: 11px;
    }}
    
    /* === ANIMATIONS === */
    
    QPushButton {{
        transition: all 0.2s ease;
    }}
    
    QPushButton:hover {{
        transition: all 0.2s ease;
    }}
    """

def get_work_area_stylesheet() -> str:
    """Styles spécifiques à la zone de travail"""
    return f"""
    QGraphicsView {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        background-color: {COLORS['work_area']};
    }}
    
    QGraphicsView:focus {{
        border-color: {COLORS['border_active']};
        outline: none;
    }}
    """

def get_dialog_stylesheet() -> str:
    """Styles pour les dialogues"""
    return f"""
    /* === DIALOGUES PROPRIÉTÉS === */
    
    QDialog {{
        background-color: {COLORS['sidebar']};
        border: 2px solid {COLORS['border']};
        border-radius: 10px;
    }}
    
    QDialog QLabel {{
        font-weight: bold;
        margin-bottom: 5px;
        color: {COLORS['text_primary']};
    }}
    
    QDialog QLineEdit {{
        margin-bottom: 10px;
        padding: 10px;
        font-size: 13px;
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
    }}
    
    QDialog QLineEdit:focus {{
        border-color: {COLORS['primary']};
    }}
    
    QDialog QPushButton {{
        padding: 10px 20px;
        margin: 5px;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
        min-width: 80px;
    }}
    
    QDialog QPushButton#okButton {{
        background-color: {COLORS['success']};
        color: white;
    }}
    
    QDialog QPushButton#okButton:hover {{
        background-color: #229954;
    }}
    
    QDialog QPushButton#cancelButton {{
        background-color: {COLORS['text_secondary']};
        color: white;
    }}
    
    QDialog QPushButton#cancelButton:hover {{
        background-color: #6c7b7d;
    }}
    """

# === FONCTIONS D'APPLICATION DES STYLES ===

def apply_application_styles(app_or_widget):
    """Applique les styles principaux à l'application ou widget"""
    main_style = get_main_stylesheet()
    work_area_style = get_work_area_stylesheet()
    dialog_style = get_dialog_stylesheet()
    
    # Combiner tous les styles
    complete_stylesheet = main_style + work_area_style + dialog_style
    
    app_or_widget.setStyleSheet(complete_stylesheet)

def apply_dark_theme(app_or_widget):
    """Applique un thème sombre (version future)"""
    # TODO: Implémenter thème sombre
    dark_colors = {
        "background": "#2b2b2b",
        "sidebar": "#3c3c3c", 
        "text_primary": "#ffffff",
        "text_secondary": "#cccccc",
        "border": "#555555",
        # etc.
    }
    # Pour l'instant, utiliser le thème clair
    apply_application_styles(app_or_widget)

def setup_application_font(app: QApplication):
    """Configure la police par défaut de l'application"""
    # Police principale
    font = QFont(FONTS['main'].split(',')[0])  # Prendre la première police
    font.setPointSize(10)
    font.setWeight(QFont.Weight.Normal)
    
    app.setFont(font)

# === STYLES POUR COMPOSANTS SPÉCIALISÉS ===

def get_port_styles() -> dict:
    """Retourne les styles pour les ports hydrauliques"""
    return {
        "free": {
            "pen_color": "#2d8e2d",      # Vert foncé
            "pen_width": 2,
            "brush_color": "#90EE90",    # Vert clair
            "brush_alpha": 180
        },
        "connected": {
            "pen_color": "#c82333",      # Rouge foncé  
            "pen_width": 3,
            "brush_color": "#FF6B6B",    # Rouge clair
            "brush_alpha": 255
        },
        "hovered": {
            "pen_color": "#1a7c1a",      # Vert très foncé
            "pen_width": 3,
            "brush_color": "#98FB98",    # Vert très clair
            "brush_alpha": 255
        },
        "connection_mode": {
            "pen_color": "#0f5f0f",      # Vert profond
            "pen_width": 3,
            "brush_color": "#00FF00",    # Vert vif
            "brush_alpha": 200
        },
        "connection_mode_hovered": {
            "pen_color": "#FFD700",      # Or
            "pen_width": 4,
            "brush_color": "#FFFF00",    # Jaune vif
            "brush_alpha": 255
        }
    }

def get_pipe_styles() -> dict:
    """Retourne les styles pour les tuyaux"""
    return {
        "normal": {
            "pen_color": "#2980b9",      # Bleu
            "pen_width": 4,
            "pen_style": "solid"
        },
        "selected": {
            "pen_color": "#e74c3c",      # Rouge
            "pen_width": 5,
            "pen_style": "solid"
        },
        "preview": {
            "pen_color": "#f39c12",      # Orange
            "pen_width": 3,
            "pen_style": "dashed"
        },
        "waypoint": {
            "pen_color": "#e67e22",      # Orange foncé
            "pen_width": 2,
            "brush_color": "#f39c12",    # Orange
            "size": 8
        }
    }

def get_component_styles() -> dict:
    """Retourne les styles pour les composants hydrauliques"""
    return {
        "normal": {
            "border_color": "#34495e",
            "border_width": 2,
            "shadow_enabled": True,
            "shadow_blur": 5,
            "shadow_offset": (2, 2)
        },
        "selected": {
            "border_color": "#e74c3c",
            "border_width": 3,
            "shadow_enabled": True,
            "shadow_blur": 8,
            "shadow_offset": (3, 3)
        },
        "hovered": {
            "border_color": "#3498db",
            "border_width": 2,
            "shadow_enabled": True,
            "shadow_blur": 6,
            "shadow_offset": (2, 2)
        }
    }

# === CONSTANTES UTILES ===

# Tailles standard
SIZES = {
    "port_radius": 8,
    "component_min_size": (30, 30),
    "pipe_min_width": 2,
    "pipe_max_width": 8,
    "sidebar_width": 280,
    "toolbar_height": 40
}

# Z-Index pour layering
Z_INDEX = {
    "background": -1000,
    "grid": -500,
    "pipes": 1,
    "components": 10,
    "ports": 20,
    "selection": 50,
    "preview": 100,
    "dialogs": 1000
}

# === FONCTIONS UTILITAIRES ===

def lighten_color(color: str, factor: float = 0.2) -> str:
    """Éclaircit une couleur hexadécimale"""
    # Conversion hex vers RGB
    color = color.lstrip('#')
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # Éclaircissement
    rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
    
    # Conversion RGB vers hex
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def darken_color(color: str, factor: float = 0.2) -> str:
    """Assombrit une couleur hexadécimale"""
    color = color.lstrip('#')
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # Assombrissement
    rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
    
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def get_color_with_alpha(color: str, alpha: int) -> str:
    """Retourne une couleur avec transparence pour CSS"""
    color = color.lstrip('#')
    r = int(color[0:2], 16)
    g = int(color[2:4], 16) 
    b = int(color[4:6], 16)
    
    return f"rgba({r}, {g}, {b}, {alpha/255.0})"

# === POINT D'ENTRÉE POUR TESTS ===

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
    
    app = QApplication(sys.argv)
    
    # Test des styles
    window = QWidget()
    window.setWindowTitle("Test des styles")
    layout = QVBoxLayout(window)
    
    # Titre
    title = QLabel("Test des styles CSS")
    title.setObjectName("mainTitle")
    layout.addWidget(title)
    
    # Boutons de test
    btn_object = QPushButton("+ Test Objet")
    btn_object.setObjectName("objectButton")
    layout.addWidget(btn_object)
    
    btn_connection = QPushButton("Mode Connexion")
    btn_connection.setObjectName("connectionButton")
    btn_connection.setCheckable(True)
    layout.addWidget(btn_connection)
    
    btn_epanet = QPushButton("✓ Test EPANET")
    btn_epanet.setObjectName("epanetButton")
    layout.addWidget(btn_epanet)
    
    btn_action = QPushButton("Action Test")
    btn_action.setObjectName("actionButton")
    layout.addWidget(btn_action)
    
    # Appliquer les styles
    apply_application_styles(window)
    setup_application_font(app)
    
    # Afficher
    window.show()
    
    print("=== TEST STYLES ===")
    print(f"Couleurs disponibles: {list(COLORS.keys())}")
    print(f"Polices: {FONTS}")
    print(f"Tailles: {SIZES}")
    
    sys.exit(app.exec())
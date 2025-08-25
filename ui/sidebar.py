#!/usr/bin/env python3
"""
ui/sidebar.py - Interface sidebar modulaire et auto-générée
Interface pure sans logique métier, génération depuis configuration
"""

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QMessageBox, QWidget)
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont

# Configuration des objets
from config.hydraulic_objects import (
    HYDRAULIC_OBJECT_TYPES, get_object_types, get_display_name, get_object_config
)

class HydraulicSidebar(QFrame):
    """
    Sidebar hydraulique - Interface pure auto-générée
    Responsabilité : Interface utilisateur seulement, émission de signaux
    """
    
    # === SIGNAUX ÉMIS ===
    
    # Création d'objets
    object_requested = pyqtSignal(str, dict)        # object_type, custom_properties
    
    # Mode connexion
    connection_mode_toggled = pyqtSignal(bool)       # is_active
    
    # Actions EPANET
    validation_requested = pyqtSignal()
    export_requested = pyqtSignal()
    summary_requested = pyqtSignal()
    
    # Actions générales
    clear_requested = pyqtSignal()
    info_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # État interne
        self.object_counter = 0
        self.pipe_counter = 0
        self.connection_mode_active = False
        
        # Configuration
        self.setFixedWidth(280)  # Élargie pour nouveaux boutons
        self.setObjectName("sidebar")
        
        # Construction interface
        self.setup_ui()
        
        print("[SIDEBAR] Interface créée")
    
    def setup_ui(self):
        """Construction de l'interface complète"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titre principal
        self.create_title_section(layout)
        
        # Section objets hydrauliques (auto-générée)
        self.create_objects_section(layout)
        
        # Section connexions
        self.create_connections_section(layout)
        
        # Section EPANET
        self.create_epanet_section(layout)
        
        # Section actions
        self.create_actions_section(layout)
        
        # Espacement et informations
        layout.addStretch()
        self.create_info_section(layout)
    
    def create_title_section(self, layout):
        """Titre et indicateurs de statut"""
        # Titre principal
        title = QLabel("Hydraulic Network Calculator")
        title.setObjectName("mainTitle")
        layout.addWidget(title)
        
        # Version et mode
        version_label = QLabel("v3.0 - Architecture Unifiée")
        version_label.setObjectName("versionLabel")
        layout.addWidget(version_label)
        
        # Indicateur EPANET
        epanet_label = QLabel("🔧 Mode EPANET Intégré")
        epanet_label.setObjectName("epanetLabel")
        layout.addWidget(epanet_label)
    
    def create_objects_section(self, layout):
        """Section objets hydrauliques - AUTO-GÉNÉRÉE depuis configuration"""
        section_title = QLabel("Objets Hydrauliques")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)
        
        # Conteneur pour boutons d'objets
        objects_widget = QWidget()
        objects_layout = QVBoxLayout(objects_widget)
        objects_layout.setContentsMargins(0, 0, 0, 0)
        objects_layout.setSpacing(5)
        
        # GÉNÉRATION AUTOMATIQUE des boutons depuis configuration
        for object_type in get_object_types():
            config = get_object_config(object_type)
            display_name = config.get("display_name", object_type)
            description = config.get("description", "")
            
            # Créer bouton pour ce type d'objet
            btn = QPushButton(f"+ {display_name}")
            btn.setObjectName("objectButton")
            btn.setToolTip(description)
            
            # Connecter au signal avec le type d'objet
            btn.clicked.connect(lambda checked, ot=object_type: self.object_requested.emit(ot, {}))
            
            objects_layout.addWidget(btn)
            
            print(f"[SIDEBAR] Bouton créé: {display_name} ({object_type})")
        
        layout.addWidget(objects_widget)
    
    def create_connections_section(self, layout):
        """Section gestion des connexions"""
        section_title = QLabel("Connexions")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)
        
        # Bouton mode connexion
        self.connection_button = QPushButton("Mode Connexion")
        self.connection_button.setObjectName("connectionButton")
        self.connection_button.setCheckable(True)
        self.connection_button.clicked.connect(self.on_connection_button_clicked)
        layout.addWidget(self.connection_button)
    
    def create_epanet_section(self, layout):
        """Section fonctions EPANET"""
        section_title = QLabel("Calculs EPANET")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)
        
        # Bouton validation
        btn_validate = QPushButton("✓ Valider réseau")
        btn_validate.setObjectName("epanetButton")
        btn_validate.clicked.connect(self.validation_requested.emit)
        layout.addWidget(btn_validate)
        
        # Bouton export
        btn_export = QPushButton("📁 Exporter EPANET")
        btn_export.setObjectName("epanetButton")
        btn_export.clicked.connect(self.export_requested.emit)
        layout.addWidget(btn_export)
        
        # Bouton résumé
        btn_summary = QPushButton("📊 Résumé réseau")
        btn_summary.setObjectName("epanetButton")
        btn_summary.clicked.connect(self.summary_requested.emit)
        layout.addWidget(btn_summary)
    
    def create_actions_section(self, layout):
        """Section actions générales"""
        section_title = QLabel("Actions")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)
        
        # Bouton info composants
        btn_info = QPushButton("ℹ️ Info composants")
        btn_info.setObjectName("actionButton")
        btn_info.clicked.connect(self.info_requested.emit)
        layout.addWidget(btn_info)
        
        # Bouton vider
        btn_clear = QPushButton("🗑️ Vider la scène")
        btn_clear.setObjectName("actionButton")
        btn_clear.clicked.connect(self.clear_requested.emit)
        layout.addWidget(btn_clear)
    
    def create_info_section(self, layout):
        """Section informations et compteurs"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Compteurs
        self.objects_counter_label = QLabel("Objets: 0")
        self.objects_counter_label.setObjectName("counterLabel")
        info_layout.addWidget(self.objects_counter_label)
        
        self.pipes_counter_label = QLabel("Tuyaux: 0")
        self.pipes_counter_label.setObjectName("counterLabel")
        info_layout.addWidget(self.pipes_counter_label)
        
        layout.addWidget(info_widget)
    
    # === GESTION ÉVÉNEMENTS BOUTONS ===
    
    def on_connection_button_clicked(self):
        """Gestion clic bouton mode connexion"""
        self.connection_mode_active = self.connection_button.isChecked()
        self.connection_mode_toggled.emit(self.connection_mode_active)
    
    # === SLOTS POUR RETOUR DES CONTROLLERS ===
    
    @pyqtSlot(str, str)
    def on_object_added(self, object_id: str, object_type: str):
        """Réaction à l'ajout d'un objet"""
        self.object_counter += 1
        print(f"[SIDEBAR] Objet ajouté: {object_type} ({object_id})")
    
    @pyqtSlot(str)
    def on_pipe_created(self, pipe_id: str):
        """Réaction à la création d'un tuyau"""
        self.pipe_counter += 1
        print(f"[SIDEBAR] Tuyau créé: {pipe_id}")
    
    @pyqtSlot(int)
    def update_object_counter(self, count: int):
        """Mise à jour compteur objets"""
        self.object_counter = count
        self.objects_counter_label.setText(f"Objets: {count}")
    
    @pyqtSlot(int)
    def update_pipe_counter(self, count: int):
        """Mise à jour compteur tuyaux"""
        self.pipe_counter = count
        self.pipes_counter_label.setText(f"Tuyaux: {count}")
    
    @pyqtSlot(bool)
    def update_connection_button(self, is_active: bool):
        """Mise à jour état bouton connexion"""
        self.connection_mode_active = is_active
        self.connection_button.setChecked(is_active)
        
        if is_active:
            self.connection_button.setText("❌ Annuler Connexion")
        else:
            self.connection_button.setText("🔗 Mode Connexion")
    
    # === MESSAGES UTILISATEUR ===
    
    def show_success_message(self, message: str):
        """Affiche un message de succès"""
        QMessageBox.information(self, "Succès", message)
    
    def show_error_message(self, message: str):
        """Affiche un message d'erreur"""
        QMessageBox.warning(self, "Erreur", message)
    
    def show_info_message(self, title: str, message: str):
        """Affiche un message d'information"""
        QMessageBox.information(self, title, message)
    
    # === RÉINITIALISATION ===
    
    def reset_counters(self):
        """Remet à zéro tous les compteurs"""
        self.object_counter = 0
        self.pipe_counter = 0
        self.update_object_counter(0)
        self.update_pipe_counter(0)
        
        # Désactiver mode connexion
        self.connection_mode_active = False
        self.connection_button.setChecked(False)
        self.update_connection_button(False)
        
        print("[SIDEBAR] Compteurs remis à zéro")

# === POINT D'ENTRÉE POUR TESTS ===

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # Test de la sidebar
    window = QMainWindow()
    sidebar = HydraulicSidebar()
    window.setCentralWidget(sidebar)
    
    # Connexions de test
    sidebar.object_requested.connect(lambda ot, props: print(f"Objet demandé: {ot}"))
    sidebar.connection_mode_toggled.connect(lambda active: print(f"Mode connexion: {active}"))
    sidebar.validation_requested.connect(lambda: print("Validation demandée"))
    
    window.show()
    sys.exit(app.exec())
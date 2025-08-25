#!/usr/bin/env python3
"""
ui/main_window.py - Fenêtre principale MISE À JOUR avec barre d'outils
Intégration de la barre d'outils de transformation des objets hydrauliques
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QFont

# Imports UI
from .sidebar import HydraulicSidebar
from .work_area import HydraulicWorkArea
from .toolbar import HydraulicToolbar, get_toolbar_stylesheet
from .styles import apply_application_styles

# Imports Controllers
from controllers import ComponentController, ConnectionController, EPANETController
from controllers.transform_controller import TransformController

# Configuration
from config.hydraulic_objects import get_config_summary

class HydraulicMainWindow(QMainWindow):
    """
    Fenêtre principale MISE À JOUR avec barre d'outils
    ResponsabilitÃ© : Orchestrateur UI ↔ Controllers + Transformations
    """
    
    def __init__(self):
        super().__init__()
        
        # Configuration fenêtre
        self.setWindowTitle("Hydraulic Network Calculator v3.0 - Architecture Unifiée + Outils")
        self.setGeometry(100, 100, 1600, 1000)  # Agrandie pour la toolbar
        
        # Initialisation composants
        self.init_ui_components()
        self.init_controllers()
        self.setup_layout()
        self.connect_signals()
        self.apply_styles()
        
        # Informations de démarrage
        self.log_startup_info()
        
        print("[MAIN_WINDOW] Initialisation avec barre d'outils terminée")
    
    def init_ui_components(self):
        """Initialisation des composants UI (MISE À JOUR)"""
        print("[MAIN_WINDOW] Création composants UI avec toolbar...")
        
        # Zone de travail graphique
        self.work_area = HydraulicWorkArea(self)
        
        # Barre latérale
        self.sidebar = HydraulicSidebar(self)
        
        # NOUVEAU: Barre d'outils hydraulique
        self.toolbar = HydraulicToolbar(self)
        
        print("[MAIN_WINDOW] Composants UI créés avec toolbar")
    
    def init_controllers(self):
        """Initialisation des contrôleurs métier (MISE À JOUR)"""
        print("[MAIN_WINDOW] Création contrôleurs avec transformations...")
        
        # Contrôleur des composants hydrauliques
        self.component_controller = ComponentController(self.work_area.scene)
        
        # Contrôleur des connexions (mode connexion, tuyaux)
        self.connection_controller = ConnectionController(self.work_area)
        
        # Contrôleur EPANET (calculs, export, validation)
        self.epanet_controller = EPANETController()
        
        # NOUVEAU: Contrôleur des transformations (rotation, alignement)
        self.transform_controller = TransformController()
        
        print("[MAIN_WINDOW] Contrôleurs créés avec transformations")
    
    def setup_layout(self):
        """Configuration du layout principal (INCHANGÉ)"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout horizontal principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Ajouter composants
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.work_area)
        
        # NOUVEAU: Ajouter la barre d'outils à la fenêtre
        self.addToolBar(self.toolbar)
        
        print("[MAIN_WINDOW] Layout configuré avec toolbar")
    
    def connect_signals(self):
        """Connexion des signaux entre UI et Controllers (MISE À JOUR)"""
        print("[MAIN_WINDOW] Connexion signaux avec toolbar...")
        
        # === SIGNAUX EXISTANTS (inchangés) ===
        
        # SIDEBAR → CONTROLLERS
        self.sidebar.object_requested.connect(self.component_controller.add_object)
        self.sidebar.connection_mode_toggled.connect(self.connection_controller.toggle_mode)
        self.sidebar.validation_requested.connect(self.epanet_controller.validate_network)
        self.sidebar.export_requested.connect(self.epanet_controller.export_network)
        self.sidebar.summary_requested.connect(self.epanet_controller.show_summary)
        self.sidebar.clear_requested.connect(self.clear_all)
        self.sidebar.info_requested.connect(self.show_component_info)
        
        # CONTROLLERS → UI FEEDBACK
        self.component_controller.object_added.connect(self.sidebar.on_object_added)
        self.component_controller.objects_count_changed.connect(self.sidebar.update_object_counter)
        self.connection_controller.connection_mode_changed.connect(self.sidebar.update_connection_button)
        self.connection_controller.pipe_created.connect(self.sidebar.on_pipe_created)
        self.epanet_controller.validation_completed.connect(self.on_validation_result)
        self.epanet_controller.export_completed.connect(self.on_export_result)
        self.epanet_controller.calculation_completed.connect(self.on_calculation_result)
        
        # === NOUVEAUX SIGNAUX TOOLBAR ===
        
        # TOOLBAR → TRANSFORM CONTROLLER
        self.toolbar.rotate_left_requested.connect(self.on_rotate_left_requested)
        self.toolbar.rotate_right_requested.connect(self.on_rotate_right_requested)
        self.toolbar.align_horizontal_requested.connect(self.on_align_horizontal_requested)
        self.toolbar.align_vertical_requested.connect(self.on_align_vertical_requested)
        # NOUVEAUX: Signaux miroirs
        self.toolbar.flip_horizontal_requested.connect(self.on_flip_horizontal_requested)
        self.toolbar.flip_vertical_requested.connect(self.on_flip_vertical_requested)
        
        # WORK AREA → TOOLBAR (sélection)
        self.work_area.selection_changed.connect(self.toolbar.on_selection_changed)
        
        # TRANSFORM CONTROLLER → UI FEEDBACK
        self.transform_controller.objects_rotated.connect(self.on_objects_rotated)
        self.transform_controller.objects_aligned.connect(self.on_objects_aligned)
        self.transform_controller.objects_flipped.connect(self.on_objects_flipped)
        self.transform_controller.transformation_failed.connect(self.on_transformation_failed)
        
        # RACCOURCIS CLAVIER TOOLBAR
        self.toolbar.setup_shortcuts(self)
        
        print("[MAIN_WINDOW] Signaux connectés avec toolbar")
    
    def apply_styles(self):
        """Application des styles CSS (MISE À JOUR)"""
        # Styles application généraux
        apply_application_styles(self)
        
        # Styles spécifiques toolbar
        toolbar_styles = get_toolbar_stylesheet()
        current_stylesheet = self.styleSheet()
        self.setStyleSheet(current_stylesheet + "\n" + toolbar_styles)
        
        print("[MAIN_WINDOW] Styles appliqués avec toolbar")
    
    # === NOUVEAUX SLOTS POUR TOOLBAR ===
    
    @pyqtSlot()
    def on_rotate_left_requested(self):
        """Demande de rotation 90° gauche"""
        selected_objects = self.work_area.scene.selectedItems()
        
        if not selected_objects:
            self.sidebar.show_error_message("Aucun objet sélectionné pour la rotation")
            return
        
        print(f"[MAIN_WINDOW] Rotation gauche demandée pour {len(selected_objects)} objet(s)")
        
        # Appliquer la transformation
        success = self.transform_controller.rotate_left_90(selected_objects)
        
        if not success:
            self.sidebar.show_error_message("Erreur lors de la rotation gauche")
    
    @pyqtSlot()
    def on_rotate_right_requested(self):
        """Demande de rotation 90° droite"""
        selected_objects = self.work_area.scene.selectedItems()
        
        if not selected_objects:
            self.sidebar.show_error_message("Aucun objet sélectionné pour la rotation")
            return
        
        print(f"[MAIN_WINDOW] Rotation droite demandée pour {len(selected_objects)} objet(s)")
        
        # Appliquer la transformation
        success = self.transform_controller.rotate_right_90(selected_objects)
        
        if not success:
            self.sidebar.show_error_message("Erreur lors de la rotation droite")
    
    @pyqtSlot()
    def on_align_horizontal_requested(self):
        """Demande d'alignement horizontal"""
        selected_objects = self.work_area.scene.selectedItems()
        
        if len(selected_objects) < 2:
            self.sidebar.show_error_message("Au moins 2 objets requis pour l'alignement")
            return
        
        print(f"[MAIN_WINDOW] Alignement horizontal demandé pour {len(selected_objects)} objet(s)")
        
        # Appliquer la transformation
        success = self.transform_controller.align_objects_horizontal(selected_objects)
        
        if not success:
            self.sidebar.show_error_message("Erreur lors de l'alignement horizontal")
    
    @pyqtSlot()
    def on_align_vertical_requested(self):
        """Demande d'alignement vertical"""
        selected_objects = self.work_area.scene.selectedItems()
        
        if len(selected_objects) < 2:
            self.sidebar.show_error_message("Au moins 2 objets requis pour l'alignement")
            return
        
        print(f"[MAIN_WINDOW] Alignement vertical demandé pour {len(selected_objects)} objet(s)")
        
        # Appliquer la transformation
        success = self.transform_controller.align_objects_vertical(selected_objects)
        
        if not success:
            self.sidebar.show_error_message("Erreur lors de l'alignement vertical")
    
    @pyqtSlot()
    def on_flip_horizontal_requested(self):
        """Demande de miroir horizontal"""
        selected_objects = self.work_area.scene.selectedItems()
        
        if not selected_objects:
            self.sidebar.show_error_message("Aucun objet sélectionné pour le miroir")
            return
        
        print(f"[MAIN_WINDOW] Miroir horizontal demandé pour {len(selected_objects)} objet(s)")
        
        # Appliquer la transformation
        success = self.transform_controller.flip_objects_horizontal(selected_objects)
        
        if not success:
            self.sidebar.show_error_message("Erreur lors du miroir horizontal")
    
    @pyqtSlot()
    def on_flip_vertical_requested(self):
        """Demande de miroir vertical"""
        selected_objects = self.work_area.scene.selectedItems()
        
        if not selected_objects:
            self.sidebar.show_error_message("Aucun objet sélectionné pour le miroir")
            return
        
        print(f"[MAIN_WINDOW] Miroir vertical demandé pour {len(selected_objects)} objet(s)")
        
        # Appliquer la transformation
        success = self.transform_controller.flip_objects_vertical(selected_objects)
        
        if not success:
            self.sidebar.show_error_message("Erreur lors du miroir vertical")
    
    # === SLOTS POUR RETOUR TRANSFORMATIONS ===
    
    @pyqtSlot(list, float)
    def on_objects_rotated(self, objects, angle_degrees):
        """Retour de rotation d'objets"""
        message = f"✅ {len(objects)} objet(s) tourné(s) de {angle_degrees}°"
        self.sidebar.show_success_message(message)
        print(f"[ROTATION] {message}")
    
    @pyqtSlot(list, str)
    def on_objects_aligned(self, objects, alignment_type):
        """Retour d'alignement d'objets"""
        alignment_name = "horizontalement" if alignment_type == "horizontal" else "verticalement"
        message = f"✅ {len(objects)} objet(s) aligné(s) {alignment_name}"
        self.sidebar.show_success_message(message)
        print(f"[ALIGNMENT] {message}")
    
    @pyqtSlot(list, str)
    def on_objects_flipped(self, objects, flip_type):
        """Retour de miroir d'objets"""
        flip_name = "horizontalement" if flip_type == "horizontal" else "verticalement"
        message = f"✅ {len(objects)} objet(s) mis en miroir {flip_name}"
        self.sidebar.show_success_message(message)
        print(f"[FLIP] {message}")
    
    @pyqtSlot(str, str)
    def on_transformation_failed(self, operation, error_message):
        """Retour d'erreur de transformation"""
        full_message = f"❌ Erreur {operation}: {error_message}"
        self.sidebar.show_error_message(full_message)
        print(f"[TRANSFORM_ERROR] {full_message}")
    
    # === SLOTS EXISTANTS (inchangés) ===
    
    @pyqtSlot(bool, list)
    def on_validation_result(self, success: bool, errors: list):
        """Retour de validation EPANET"""
        if success:
            self.sidebar.show_success_message("✅ Réseau valide")
            print("[VALIDATION] Réseau valide")
        else:
            error_msg = f"❌ {len(errors)} erreur(s) détectée(s)"
            self.sidebar.show_error_message(error_msg)
            print(f"[VALIDATION] Erreurs: {errors}")
    
    @pyqtSlot(str, dict)
    def on_export_result(self, filename: str, stats: dict):
        """Retour d'export EPANET"""
        message = f"✅ Export réussi: {filename}"
        self.sidebar.show_success_message(message)
        print(f"[EXPORT] Fichier créé: {filename}")
        print(f"[EXPORT] Statistiques: {stats}")
    
    @pyqtSlot(dict)
    def on_calculation_result(self, results: dict):
        """Retour de calculs hydrauliques"""
        print(f"[CALCUL] Résultats reçus: {len(results)} éléments")
        # TODO: Affichage résultats sur interface graphique
    
    # === ACTIONS GÉNÉRALES (inchangées) ===
    
    @pyqtSlot()
    def clear_all(self):
        """Vide complètement l'interface et les données"""
        print("[MAIN_WINDOW] Nettoyage complet...")
        
        # Vider les contrôleurs
        self.component_controller.clear_all()
        self.connection_controller.clear_all()
        self.epanet_controller.clear_all()
        
        # NOUVEAU: Vider l'historique des transformations
        self.transform_controller.clear_history()
        
        # Vider l'interface
        self.work_area.clear_scene()
        self.sidebar.reset_counters()
        self.toolbar.reset_selection()
        
        print("[MAIN_WINDOW] Nettoyage terminé")
    
    @pyqtSlot()
    def show_component_info(self):
        """Affiche les informations des composants (MISE À JOUR)"""
        info = self.component_controller.get_all_components_info()
        transform_info = self.transform_controller.get_controller_info()
        
        print("\n" + "="*70)
        print("INFORMATIONS COMPOSANTS + TRANSFORMATIONS")
        print("="*70)
        
        if not info["components"]:
            print("Aucun composant dans le réseau")
        else:
            for comp_info in info["components"]:
                print(f"\n{comp_info['id']} ({comp_info['type']}):")
                print(f"  Position: {comp_info['position']}")
                print(f"  Ports: {comp_info['configuration']['ports_count']} ({comp_info['configuration']['connected_ports']} connectés)")
                print(f"  Propriétés: {len(comp_info['properties'])}")
                
                # NOUVEAU: Informations de scale
                scale_info = comp_info.get('scale_info', {})
                if scale_info:
                    print(f"  Scale: base={scale_info.get('base_svg_scale', 'N/A')}, effectif={scale_info.get('effective_scale', 'N/A')}")
        
        print(f"\nTOTAL: {info['total_components']} composants")
        
        # NOUVEAU: Informations transformations
        print(f"\nTRANSFORMATIONS:")
        print(f"  Historique: {transform_info['transformations_count']} opération(s)")
        print(f"  Opérations supportées: {', '.join(transform_info['supported_operations'])}")
        print(f"  Types alignement: {', '.join(transform_info['alignment_types'])}")
        
        print("="*70 + "\n")
    
    def log_startup_info(self):
        """Affiche les informations de démarrage (MISE À JOUR)"""
        config_summary = get_config_summary()
        
        print("\n[STARTUP] === HYDRAULIC NETWORK CALCULATOR v3.0 + OUTILS ===")
        print(f"[STARTUP] Types d'objets disponibles: {config_summary['total_object_types']}")
        print(f"[STARTUP] Types EPANET supportés: {config_summary['epanet_types']}")
        print(f"[STARTUP] Total ports configurés: {config_summary['total_ports']}")
        print("[STARTUP] NOUVEAUTÉS:")
        print("[STARTUP] • Barre d'outils de transformation")
        print("[STARTUP] • Rotation 90° gauche/droite (Ctrl+L/Ctrl+R)")
        print("[STARTUP] • Alignement horizontal/vertical (à activer)")
        print("[STARTUP] • Miroirs horizontal/vertical (à activer)")
        print("[STARTUP] Interface prête\n")
    
    # === GESTION FERMETURE (MISE À JOUR) ===
    
    def closeEvent(self, event):
        """Gestion de la fermeture de l'application (MISE À JOUR)"""
        print("[MAIN_WINDOW] Fermeture application...")
        
        # Nettoyage des contrôleurs
        self.component_controller.cleanup()
        self.connection_controller.cleanup() 
        self.epanet_controller.cleanup()
        
        # NOUVEAU: Nettoyage contrôleur transformations
        self.transform_controller.clear_history()
        
        print("[MAIN_WINDOW] Nettoyage terminé")
        event.accept()


# === POINT D'ENTRÉE POUR TESTS ===

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = HydraulicMainWindow()
    window.show()
    
    print("=== TEST MAIN WINDOW AVEC TOOLBAR ===")
    print("NOUVELLES FONCTIONNALITÉS:")
    print("• Barre d'outils en haut de la fenêtre")
    print("• Rotation 90° avec boutons ou Ctrl+L/Ctrl+R")
    print("• Informations sélection en temps réel")
    print("• Alignement horizontal/vertical (préparé)")
    print("• Messages de succès/erreur pour transformations")
    print("")
    print("WORKFLOW TEST:")
    print("1. Créez quelques objets hydrauliques")
    print("2. Sélectionnez-en un ou plusieurs")
    print("3. Utilisez les boutons de rotation")
    print("4. Testez les raccourcis clavier")
    print("5. Vérifiez les messages de retour")
    
    sys.exit(app.exec())
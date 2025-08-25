#!/usr/bin/env python3
"""
Hydraulic Network Calculator v3.0 - Architecture unifiée + Outils de Transformation
Point d'entrée avec barre d'outils intégrée
"""

import sys
from PyQt6.QtWidgets import QApplication

# Import de l'interface principale mise à jour
from ui.main_window import HydraulicMainWindow

def main():
    """Point d'entrée principal - Configuration avec barre d'outils"""
    
    # Création application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Hydraulic Network Calculator")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("Hydraulic Engineering Tools")
    
    # Création et affichage fenêtre principale avec toolbar
    window = HydraulicMainWindow()
    window.show()
    
    # Instructions de démarrage mises à jour
    print("\n" + "="*80)
    print("HYDRAULIC NETWORK CALCULATOR v3.0 - ARCHITECTURE UNIFIÉE + OUTILS")
    print("="*80)
    print("✨ NOUVELLES FONCTIONNALITÉS:")
    print("• Architecture UI/Controllers séparée")
    print("• Objets hydrauliques unifiés et configurables")
    print("• Extension triviale de nouveaux composants")
    print("• Intégration EPANET native")
    print("• 🔧 BARRE D'OUTILS DE TRANSFORMATION:")
    print("  - Rotation 90° gauche/droite")
    print("  - Raccourcis clavier: Ctrl+L / Ctrl+R")
    print("  - Alignement horizontal/vertical (à activer)")
    print("  - Informations sélection en temps réel")
    print("")
    print("🚀 UTILISATION:")
    print("1. Sélectionnez un type d'objet hydraulique dans la sidebar")
    print("2. Cliquez dans la zone de travail pour créer l'objet")
    print("3. Sélectionnez un ou plusieurs objets")
    print("4. Utilisez la barre d'outils pour les transformer:")
    print("   • Boutons de rotation dans la toolbar")
    print("   • Ou raccourcis Ctrl+L (gauche) / Ctrl+R (droite)")
    print("5. Activez le mode connexion pour relier les objets")
    print("6. Exportez vers EPANET pour calculs hydrauliques")
    print("")
    print("🎮 CONTRÔLES:")
    print("• Zoom objets: Molette souris (mode par défaut)")
    print("• Zoom vue: Touche V puis molette")
    print("• Sélection: Clic ou glisser pour sélection multiple")
    print("• Rotation: Ctrl+L/Ctrl+R ou boutons toolbar")
    print("• Reset zoom: Touche 0")
    print("="*80 + "\n")
    
    # Lancement boucle événements
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
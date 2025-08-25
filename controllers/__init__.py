#!/usr/bin/env python3
"""
controllers/__init__.py - Imports centralisés des contrôleurs MISE À JOUR
Ajout du contrôleur de transformations
"""

# Import des contrôleurs principaux
from .component_controller import ComponentController
from .connection_controller import ConnectionController
from .epanet_controller import EPANETController
from .transform_controller import TransformController

# Exports pour faciliter l'import
__all__ = [
    'ComponentController',
    'ConnectionController', 
    'EPANETController',
    'TransformController'
]

# Version des contrôleurs
__version__ = "3.1.0"

def get_controllers_info():
    """Retourne des informations sur les contrôleurs disponibles"""
    return {
        "version": __version__,
        "controllers": __all__,
        "description": "Contrôleurs pour architecture UI/Logique séparée + Transformations",
        "new_features": [
            "TransformController pour rotation/alignement/miroirs",
            "Intégration toolbar hydraulique",
            "Historique des transformations",
            "Raccourcis clavier pour rotations"
        ]
    }
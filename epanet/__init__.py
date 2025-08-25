#!/usr/bin/env python3
"""
Module EPANET pour Hydraulic Network Calculator
Version simplifiée pour éviter les erreurs d'import
"""

__version__ = "1.0.0"

try:
    # Import des classes principales
    from .structure import *
    from .integration import *
    
    EPANET_MODULE_AVAILABLE = True
    print("✅ Module EPANET chargé avec succès")
    
except ImportError as e:
    print(f"❌ Erreur chargement EPANET: {e}")
    EPANET_MODULE_AVAILABLE = False
    
    # Classes vides pour éviter les erreurs
    class NetworkManager:
        def __init__(self, *args, **kwargs):
            raise ImportError("Module EPANET non disponible")
    
    class EPANETIntegratedPump:
        def __init__(self, *args, **kwargs):
            raise ImportError("Module EPANET non disponible")
    
    class EPANETIntegratedPipe:
        def __init__(self, *args, **kwargs):
            raise ImportError("Module EPANET non disponible")
    
    class PumpPropertiesDialog:
        def __init__(self, *args, **kwargs):
            raise ImportError("Module EPANET non disponible")
    
    class InteractivePipeBuilder:
        def __init__(self, *args, **kwargs):
            raise ImportError("Module EPANET non disponible")

def is_available():
    return EPANET_MODULE_AVAILABLE
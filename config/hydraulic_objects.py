#!/usr/bin/env python3
"""
config/hydraulic_objects.py - Configuration unifiée avec parsing SVG automatique
Définition déclarative avec extraction automatique des ports depuis SVG
"""

from typing import Dict, List, Any

# Import du parser SVG avec gestion des imports relatifs/absolus
try:
    # Import relatif (quand utilisé comme module)
    from .svg_port_parser import parse_svg_ports
except ImportError:
    # Import absolu (quand exécuté directement)
    from svg_port_parser import parse_svg_ports

# === SVG AVEC PORTS INTÉGRÉS ===

# SVG Pompe avec ports définis
DEFAULT_PUMP_SVG = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="30" height="30" viewBox="0 0 7.9374998 7.9375" version="1.1">
  <g id="layer1">
    <!-- Port d'aspiration (entrée) -->
    <circle style="fill:#e6e6e6;stroke:none;" id="Port1" cx="3.96875" cy="7.4083333" r="0.52916664" 
            data-type="input" data-description="Port d'aspiration"/>
    <!-- Port de refoulement (sortie) -->
    <circle style="fill:#e6e6e6;stroke:none;" id="Port2" cx="3.96875" cy="0.52916664" r="0.52916664" 
            data-type="output" data-description="Port de refoulement"/>
    <g id="Pump">
      <circle style="fill:#ffffff;stroke:#000000;stroke-width:0.321473;" id="path1" 
              cx="3.96875" cy="-3.96875" r="3.5434301" transform="rotate(90)" />
      <path style="fill:#000000;stroke:#000000;stroke-width:1;" id="path2"
            d="m 74.169556,133.26312 -7.446397,-4.29918 7.446397,-4.29918 z"
            transform="matrix(0,0.40122979,-0.67417618,0,90.913169,-25.790285)" />
    </g>
  </g>
</svg>'''

# SVG Vanne avec ports définis
DEFAULT_VALVE_SVG = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   width="30"
   height="30"
   viewBox="0 0 7.9374998 7.9375"
   version="1.1"
   id="svg1"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <defs
     id="defs1" />
  <circle
     style="fill:#e6e6e6;stroke:none;stroke-width:1.70053;stroke-dasharray:none"
     id="Port2"
     cx="3.96875"
     cy="0.52916664"
     r="0.52916664" />
  <circle
     style="fill:#e6e6e6;stroke:none;stroke-width:1.70053;stroke-dasharray:none"
     id="Port1"
     cx="3.96875"
     cy="7.4083333"
     r="0.52916664" />
  <g
     id="Vanne">
    <path
       style="fill:#ffffff;stroke:#000000;stroke-width:0.366936;stroke-dasharray:none;stroke-opacity:1"
       id="path3-4"
       d="m 66.948057,168.83345 0,-3.60178 3.119232,1.80089 z"
       transform="matrix(0,1.008771,-1.1104448,0,189.44919,-66.820234)" />
    <path
       style="fill:#ffffff;stroke:#000000;stroke-width:0.366936;stroke-dasharray:none;stroke-opacity:1"
       id="path3-4-2"
       d="m 66.948057,168.83345 0,-3.60178 3.119232,1.80089 z"
       transform="matrix(0,-1.008771,-1.1104448,0,189.44919,74.650599)" />
    <ellipse
       style="fill:#ffffff;stroke:#000000;stroke-width:0.3;stroke-dasharray:none;stroke-opacity:1"
       id="path4-5"
       cx="3.96875"
       cy="-3.96875"
       rx="0.67178625"
       ry="0.67752796"
       transform="rotate(90)" />
  </g>
</svg>
'''

# SVG Réservoir avec port défini
DEFAULT_RESERVOIR_SVG = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="30" height="30" viewBox="0 0 30 30" version="1.1">
  <g id="reservoir">
    <rect x="5" y="8" width="20" height="15" fill="#87CEEB" stroke="#000" stroke-width="2"/>
    <!-- Port de sortie -->
    <circle id="Port1" cx="15" cy="23" r="3" fill="#e6e6e6" stroke="none"
            data-type="output" data-description="Sortie réservoir"/>
    <text x="15" y="17" text-anchor="middle" font-size="8" fill="#000">R</text>
  </g>
</svg>'''

# === TYPES D'OBJETS HYDRAULIQUES ===

HYDRAULIC_OBJECT_TYPES: Dict[str, Dict[str, Any]] = {
    
    # === POMPE ===
    "PUMP": {
        "display_name": "Pompe",
        "description": "Pompe centrifuge pour élévation de pression",
        "svg_content": DEFAULT_PUMP_SVG,
        "svg_scale": 2.0,
        "fallback_size": (30, 30),
        "fallback_color": "#FFB6C1",  # Rose clair
        
        # Configuration des ports - GÉNÉRÉE AUTOMATIQUEMENT depuis SVG
        "ports": "auto_from_svg",  # Sera remplacé par parse_svg_ports()
        
        # Configuration EPANET
        "epanet_type": "PUMP",
        "epanet_node_prefix": "PU",
        
        # Propriétés par défaut
        "default_properties": {
            "flow_rate": 100.0,        # L/min
            "pressure_head": 50.0,     # m
            "efficiency": 0.85,        # 85%
            "power_rating": 5.5,       # kW
            "speed": 2900,             # rpm
            "impeller_diameter": 200   # mm
        },
        
        # Validation des propriétés
        "property_constraints": {
            "flow_rate": {"min": 1.0, "max": 10000.0, "unit": "L/min"},
            "pressure_head": {"min": 1.0, "max": 500.0, "unit": "m"},
            "efficiency": {"min": 0.1, "max": 1.0, "unit": "%"}
        }
    },
    
    # === VANNE ===
    "VALVE": {
        "display_name": "Vanne",
        "description": "Vanne de régulation de débit/pression",
        "svg_content": DEFAULT_VALVE_SVG,
        "svg_scale": 2.0,
        "fallback_size": (30, 20),
        "fallback_color": "#D3D3D3",  # Gris clair
        
        # Ports générés automatiquement depuis SVG
        "ports": "auto_from_svg",
        
        # Configuration EPANET
        "epanet_type": "VALVE",
        "epanet_node_prefix": "VL",
        
        # Propriétés par défaut
        "default_properties": {
            "diameter": 100.0,         # mm
            "valve_type": "PRV",       # Pressure Reducing Valve
            "setting": 30.0,           # Consigne (bar ou L/s selon type)
            "minor_loss": 0.0,         # Coefficient perte de charge
            "status": "OPEN"           # OPEN, CLOSED, CV
        },
        
        # Types de vannes EPANET
        "valve_types": ["PRV", "PSV", "PBV", "FCV", "TCV", "GPV"],
        
        "property_constraints": {
            "diameter": {"min": 10.0, "max": 1000.0, "unit": "mm"},
            "setting": {"min": 0.0, "max": 1000.0, "unit": "variable"}
        }
    },
    
    # === RÉSERVOIR ===
    "RESERVOIR": {
        "display_name": "Réservoir",
        "description": "Source d'eau à hauteur constante",
        "svg_content": DEFAULT_RESERVOIR_SVG,
        "svg_scale": 1.0,
        "fallback_size": (30, 25),
        "fallback_color": "#87CEEB",  # Bleu ciel
        
        # Port généré automatiquement depuis SVG
        "ports": "auto_from_svg",
        
        # Configuration EPANET
        "epanet_type": "RESERVOIR",
        "epanet_node_prefix": "R",
        
        # Propriétés par défaut
        "default_properties": {
            "head": 100.0,             # m (hauteur hydraulique)
            "pattern": "",             # Pattern de variation (optionnel)
        },
        
        "property_constraints": {
            "head": {"min": 0.0, "max": 1000.0, "unit": "m"}
        }
    },
    
    # === RÉSERVOIR DE STOCKAGE (TANK) ===
    "TANK": {
        "display_name": "Tank",
        "description": "Réservoir de stockage avec niveau variable",
        "svg_content": DEFAULT_RESERVOIR_SVG,  # Même SVG pour l'instant
        "svg_scale": 1.0,
        "fallback_size": (30, 25),
        "fallback_color": "#98FB98",  # Vert clair
        
        # Port généré automatiquement depuis SVG
        "ports": "auto_from_svg",
        
        # Configuration EPANET
        "epanet_type": "TANK",
        "epanet_node_prefix": "T",
        
        # Propriétés par défaut
        "default_properties": {
            "elevation": 50.0,         # m (élévation du fond)
            "init_level": 10.0,        # m (niveau initial)
            "min_level": 0.0,          # m (niveau minimum)
            "max_level": 20.0,         # m (niveau maximum)
            "diameter": 10.0,          # m (diamètre)
            "min_vol": 0.0,            # m³ (volume minimum)
        },
        
        "property_constraints": {
            "elevation": {"min": 0.0, "max": 1000.0, "unit": "m"},
            "init_level": {"min": 0.0, "max": 100.0, "unit": "m"},
            "diameter": {"min": 1.0, "max": 100.0, "unit": "m"}
        }
    }
}

# === CONFIGURATION TUYAUX ===

PIPE_DEFAULT_PROPERTIES = {
    "diameter": 100.0,             # mm
    "roughness": 100.0,            # Coefficient Hazen-Williams
    "minor_loss": 0.0,             # Coefficient pertes mineures
    "status": "OPEN",              # OPEN, CLOSED, CV
    "material": "STEEL"            # Matériau (informatif)
}

PIPE_CONSTRAINTS = {
    "diameter": {"min": 10.0, "max": 2000.0, "unit": "mm"},
    "roughness": {"min": 50.0, "max": 150.0, "unit": "Hazen-Williams"},
    "minor_loss": {"min": 0.0, "max": 10.0, "unit": "coefficient"}
}

# === FONCTIONS UTILITAIRES ===

def get_object_types() -> List[str]:
    """Retourne la liste des types d'objets disponibles"""
    return list(HYDRAULIC_OBJECT_TYPES.keys())

def get_object_config(object_type: str) -> Dict[str, Any]:
    """Retourne la configuration d'un type d'objet"""
    return HYDRAULIC_OBJECT_TYPES.get(object_type, {})

def get_display_name(object_type: str) -> str:
    """Retourne le nom d'affichage d'un type d'objet"""
    config = get_object_config(object_type)
    return config.get("display_name", object_type)

def get_default_properties(object_type: str) -> Dict[str, Any]:
    """Retourne les propriétés par défaut d'un type d'objet"""
    config = get_object_config(object_type)
    return config.get("default_properties", {}).copy()

def validate_property(object_type: str, property_name: str, value: Any) -> bool:
    """Valide une propriété selon les contraintes définies"""
    config = get_object_config(object_type)
    constraints = config.get("property_constraints", {})
    
    if property_name not in constraints:
        return True  # Pas de contrainte définie
    
    constraint = constraints[property_name]
    
    # Validation numérique
    if isinstance(value, (int, float)):
        min_val = constraint.get("min")
        max_val = constraint.get("max")
        
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
    
    return True

def get_port_configs(object_type: str) -> List[Dict[str, Any]]:
    """
    Retourne la configuration des ports pour un type d'objet
    VERSION AMÉLIORÉE avec parsing SVG automatique
    """
    config = get_object_config(object_type)
    ports_config = config.get("ports", [])
    
    # Si ports définis comme "auto_from_svg", parser le SVG
    if ports_config == "auto_from_svg":
        svg_content = config.get("svg_content", "")
        if svg_content:
            print(f"[CONFIG] Parsing automatique des ports pour {object_type}")
            return parse_svg_ports(svg_content)
        else:
            print(f"[CONFIG] Aucun SVG trouvé pour {object_type}, ports vides")
            return []
    
    # Sinon retourner la configuration manuelle existante
    return ports_config

# === INFORMATIONS POUR DEBUG ===

def get_config_summary() -> Dict[str, Any]:
    """Retourne un résumé de la configuration pour debug"""
    return {
        "total_object_types": len(HYDRAULIC_OBJECT_TYPES),
        "object_types": get_object_types(),
        "total_ports": sum(len(config.get("ports", [])) for config in HYDRAULIC_OBJECT_TYPES.values()),
        "epanet_types": list(set(config.get("epanet_type") for config in HYDRAULIC_OBJECT_TYPES.values()))
    }

if __name__ == "__main__":
    # Test de la configuration avec parsing SVG automatique
    summary = get_config_summary()
    print("=== CONFIGURATION OBJETS HYDRAULIQUES AVEC SVG PARSING ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\n=== DÉTAIL PAR TYPE AVEC PORTS AUTOMATIQUES ===")
    for obj_type in get_object_types():
        config = get_object_config(obj_type)
        ports = get_port_configs(obj_type)  # Parsing automatique !
        
        print(f"\n{obj_type}:")
        print(f"  Nom: {config.get('display_name')}")
        print(f"  Ports détectés: {len(ports)}")
        for port in ports:
            print(f"    - {port['id']} ({port['type']}) à {port['position']}")
        print(f"  EPANET: {config.get('epanet_type')}")
        print(f"  Propriétés: {len(config.get('default_properties', {}))}")
    
    print("\n=== TEST PARSING SVG VANNE ===")
    valve_ports = get_port_configs("VALVE")
    print(f"Ports vanne: {valve_ports}")

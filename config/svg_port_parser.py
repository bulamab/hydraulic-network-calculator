#!/usr/bin/env python3
"""
config/svg_port_parser.py - Parser SVG pour extraction automatique des ports
Analyse les SVG pour extraire positions et types de ports automatiquement
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Tuple
import re

class SVGPortParser:
    """
    Parser pour extraire automatiquement les ports depuis les SVG
    """
    
    def __init__(self):
        # Expressions régulières pour identifier les ports
        self.port_id_patterns = [
            r"^[Pp]ort\d+$",           # Port1, Port2, port1, port2
            r"^[Pp]ort_\d+$",          # Port_1, port_1
            r"^[Pp]ort[-_]?\w+$"       # Port-inlet, port_outlet
        ]
        
        # Mapping des noms vers types de ports
        self.port_type_mapping = {
            # Mots-clés pour input
            "inlet": "input",
            "in": "input", 
            "aspiration": "input",
            "suction": "input",
            "entry": "input",
            "entree": "input",
            
            # Mots-clés pour output
            "outlet": "output",
            "out": "output",
            "discharge": "output", 
            "refoulement": "output",
            "exit": "output",
            "sortie": "output",
            
            # Mots-clés pour bidirectionnel
            "connection": "bidirectional",
            "conn": "bidirectional",
            "both": "bidirectional",
            "bidirect": "bidirectional"
        }
        
        print("[SVG_PARSER] Parser SVG initialisé")
    
    def parse_svg_ports(self, svg_content: str) -> List[Dict[str, Any]]:
        """
        Parse un SVG et extrait automatiquement les ports
        AVEC conversion coordonnées viewBox → pixels Qt
        
        Args:
            svg_content: Contenu SVG en string
            
        Returns:
            Liste des ports trouvés avec positions converties en pixels Qt
        """
        try:
            # Parser le XML
            root = ET.fromstring(svg_content)
            
            # Obtenir les dimensions SVG et viewBox pour conversion
            viewbox = self._get_svg_viewbox(svg_content)
            target_size = self._get_target_size_from_svg(root)
            
            print(f"[SVG_PARSER] ViewBox: {viewbox}, Taille cible: {target_size}")
            
            # Trouver tous les cercles qui pourraient être des ports
            ports = []
            circles = self._find_all_circles(root)
            
            for circle in circles:
                port_info = self._analyze_circle_as_port(circle, viewbox, target_size)
                if port_info:
                    ports.append(port_info)
            
            # Trier par ID pour avoir un ordre cohérent
            ports.sort(key=lambda p: self._extract_port_number(p['svg_element_id']))
            
            print(f"[SVG_PARSER] {len(ports)} ports extraits et convertis du SVG")
            return ports
            
        except ET.ParseError as e:
            print(f"[SVG_PARSER] Erreur parsing XML: {e}")
            return []
        except Exception as e:
            print(f"[SVG_PARSER] Erreur générale: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _find_all_circles(self, root) -> List[ET.Element]:
        """Trouve tous les éléments cercle dans le SVG"""
        circles = []
        
        # Chercher dans tout l'arbre XML
        for elem in root.iter():
            # Gérer les namespaces SVG
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag == 'circle':
                circles.append(elem)
        
        print(f"[SVG_PARSER] {len(circles)} cercles trouvés dans le SVG")
        return circles
    
    def _get_svg_viewbox(self, svg_content: str) -> Tuple[float, float, float, float]:
        """
        Extrait les dimensions du viewBox SVG pour conversion coordonnées
        
        Returns:
            (x, y, width, height) ou (0, 0, 100, 100) par défaut
        """
        try:
            root = ET.fromstring(svg_content)
            
            # Chercher viewBox
            viewbox = root.get('viewBox', '')
            if viewbox:
                values = [float(x) for x in viewbox.split()]
                if len(values) == 4:
                    return tuple(values)
            
            # Fallback: width/height attributes
            width = float(root.get('width', '100').replace('px', '').replace('pt', ''))
            height = float(root.get('height', '100').replace('px', '').replace('pt', ''))
            return (0, 0, width, height)
            
        except:
            return (0, 0, 100, 100)
    
    def _get_target_size_from_svg(self, root: ET.Element) -> Tuple[float, float]:
        """
        Extrait la taille cible depuis les attributs width/height du SVG
        
        Args:
            root: Élément racine du SVG
            
        Returns:
            (width, height) en pixels
        """
        try:
            # Extraire width et height, en enlevant les unités
            width_str = root.get('width', '30').replace('px', '').replace('pt', '').replace('mm', '')
            height_str = root.get('height', '30').replace('px', '').replace('pt', '').replace('mm', '')
            
            width = float(width_str)
            height = float(height_str)
            
            return (width, height)
            
        except (ValueError, TypeError):
            # Fallback vers taille standard
            return (30.0, 30.0)
    
    def _analyze_circle_as_port(self, circle: ET.Element, viewbox: Tuple[float, float, float, float], 
                               target_size: Tuple[float, float]) -> Dict[str, Any]:
        """
        Analyse un cercle pour déterminer si c'est un port
        AVEC conversion de coordonnées viewBox → Qt
        
        Args:
            circle: Élément XML du cercle
            viewbox: ViewBox du SVG (x, y, width, height)
            target_size: Taille cible en pixels (width, height)
            
        Returns:
            Dict avec infos du port ou None si pas un port
        """
        # Récupérer l'ID du cercle
        circle_id = circle.get('id', '')
        
        # Vérifier si l'ID correspond à un pattern de port
        if not self._is_port_id(circle_id):
            return None
        
        # Extraire position SVG (coordonnées viewBox)
        svg_position = self._extract_circle_position(circle)
        if not svg_position:
            return None
        
        # CONVERSION CRUCIALE: viewBox → pixels Qt
        qt_position = self._convert_svg_to_qt_coordinates(svg_position, viewbox, target_size)
        
        # Déterminer le type de port
        port_type = self._determine_port_type(circle_id, circle)
        
        # Extraire description/tooltip optionnel
        description = self._extract_description(circle)
        
        port_info = {
            "id": self._clean_port_id(circle_id),
            "type": port_type,
            "position": qt_position,  # Position convertie en pixels Qt
            "description": description,
            "svg_element_id": circle_id,
            "original_circle": {
                "cx": circle.get('cx', '0'),
                "cy": circle.get('cy', '0'),
                "r": circle.get('r', '8')
            },
            "conversion_info": {
                "svg_position": svg_position,
                "qt_position": qt_position,
                "viewbox": viewbox,
                "target_size": target_size
            }
        }
        
        print(f"[SVG_PARSER] Port détecté: {port_info['id']} ({port_type})")
        print(f"  SVG: {svg_position} → Qt: {qt_position}")
        return port_info
    
    def _is_port_id(self, element_id: str) -> bool:
        """Vérifie si un ID correspond à un pattern de port"""
        for pattern in self.port_id_patterns:
            if re.match(pattern, element_id, re.IGNORECASE):
                return True
        return False
    
    def _extract_circle_position(self, circle: ET.Element) -> Tuple[float, float]:
        """Extrait la position (cx, cy) d'un cercle"""
        try:
            cx = float(circle.get('cx', 0))
            cy = float(circle.get('cy', 0))
            return (cx, cy)
        except (ValueError, TypeError):
            print(f"[SVG_PARSER] Position invalide pour cercle {circle.get('id', 'unknown')}")
            return None
    
    def _convert_svg_to_qt_coordinates(self, svg_pos: Tuple[float, float], 
                                     svg_viewbox: Tuple[float, float, float, float],
                                     target_size: Tuple[float, float]) -> Tuple[float, float]:
        """
        Convertit les coordonnées SVG vers les coordonnées Qt
        FORMULE EXACTE: qt_coord = (svg_coord - viewbox_offset) / viewbox_size * target_size
        
        Args:
            svg_pos: Position (x, y) dans le viewBox SVG
            svg_viewbox: ViewBox du SVG (x, y, width, height)  
            target_size: Taille cible en pixels Qt (width, height)
            
        Returns:
            Position convertie pour Qt en pixels
        """
        svg_x, svg_y = svg_pos
        vb_x, vb_y, vb_width, vb_height = svg_viewbox
        target_width, target_height = target_size
        
        # Conversion proportionnelle exacte
        # Exemple: 3.96875 dans viewBox [0,0,7.9375,7.9375] vers 30px
        # qt_x = (3.96875 - 0) / 7.9375 * 30 = 0.5 * 30 = 15.0
        qt_x = ((svg_x - vb_x) / vb_width) * target_width
        qt_y = ((svg_y - vb_y) / vb_height) * target_height
        
        # Arrondir pour avoir des positions nettes
        qt_x = round(qt_x, 2)
        qt_y = round(qt_y, 2)
        
        return (qt_x, qt_y)
    
    def _determine_port_type(self, circle_id: str, circle: ET.Element) -> str:
        """Détermine le type de port basé sur l'ID et les attributs"""
        # Vérifier d'abord les attributs data-type ou class
        data_type = circle.get('data-type', '').lower()
        if data_type in ['input', 'output', 'bidirectional']:
            return data_type
        
        class_attr = circle.get('class', '').lower()
        for port_type in ['input', 'output', 'bidirectional']:
            if port_type in class_attr:
                return port_type
        
        # Analyser l'ID pour des mots-clés
        id_lower = circle_id.lower()
        for keyword, port_type in self.port_type_mapping.items():
            if keyword in id_lower:
                return port_type
        
        # Fallback: analyser le numéro de port
        # Convention: Port1, Port3, Port5... = input, Port2, Port4, Port6... = output
        port_num_match = re.search(r'(\d+)', circle_id)
        if port_num_match:
            port_num = int(port_num_match.group(1))
            return "input" if port_num % 2 == 1 else "output"
        
        # Fallback final
        return "bidirectional"
    
    def _clean_port_id(self, svg_id: str) -> str:
        """Nettoie l'ID SVG pour créer un ID de port utilisable"""
        # Convertir Port1 -> 1, Port_Inlet -> inlet, etc.
        cleaned = re.sub(r'^[Pp]ort[-_]?', '', svg_id)
        return cleaned.lower() if cleaned else svg_id.lower()
    
    def _extract_port_number(self, svg_id: str) -> int:
        """Extrait le numéro de port pour le tri"""
        port_num_match = re.search(r'(\d+)', svg_id)
        return int(port_num_match.group(1)) if port_num_match else 999
    
    def _extract_description(self, circle: ET.Element) -> str:
        """Extrait une description depuis les attributs du cercle"""
        # Chercher dans title, desc, data-description
        desc_sources = [
            circle.get('data-description', ''),
            circle.get('title', ''),
            circle.get('desc', '')
        ]
        
        # Chercher aussi dans les éléments enfants <title> ou <desc>
        for child in circle:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag in ['title', 'desc'] and child.text:
                desc_sources.append(child.text.strip())
        
        # Retourner la première description non-vide
        for desc in desc_sources:
            if desc and desc.strip():
                return desc.strip()
        
        return f"Port {circle.get('id', 'unknown')}"
    
    def validate_svg_ports(self, svg_content: str) -> Tuple[bool, List[str]]:
        """
        Valide que le SVG contient des ports correctement définis
        
        Returns:
            (is_valid, list_of_warnings)
        """
        warnings = []
        ports = self.parse_svg_ports(svg_content)
        
        if not ports:
            warnings.append("Aucun port détecté dans le SVG")
            return False, warnings
        
        # Vérifier qu'il y a au moins un input et un output
        types = [port['type'] for port in ports]
        if 'input' not in types and 'bidirectional' not in types:
            warnings.append("Aucun port d'entrée détecté")
        
        if 'output' not in types and 'bidirectional' not in types:
            warnings.append("Aucun port de sortie détecté")
        
        # Vérifier les IDs dupliqués
        ids = [port['id'] for port in ports]
        if len(ids) != len(set(ids)):
            warnings.append("IDs de ports dupliqués détectés")
        
        # Vérifier les positions valides
        for port in ports:
            x, y = port['position']
            if x < 0 or y < 0:
                warnings.append(f"Position négative pour port {port['id']}: {port['position']}")
        
        is_valid = len(warnings) == 0
        return is_valid, warnings

# === FONCTIONS UTILITAIRES ===

def parse_svg_ports(svg_content: str) -> List[Dict[str, Any]]:
    """Function utilitaire pour parser les ports depuis SVG"""
    parser = SVGPortParser()
    return parser.parse_svg_ports(svg_content)

def validate_svg_component(svg_content: str) -> Tuple[bool, List[str]]:
    """Function utilitaire pour valider un SVG de composant"""
    parser = SVGPortParser()
    return parser.validate_svg_ports(svg_content)

# === EXEMPLE D'UTILISATION ===

if __name__ == "__main__":
    # Test avec un SVG d'exemple
    test_svg = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="30" height="30" viewBox="0 0 30 30" version="1.1">
      <g id="valve">
        <rect x="5" y="10" width="20" height="10" fill="#d0d0d0" stroke="#000" stroke-width="2"/>
        
        <!-- Port d'entrée -->
        <circle id="Port1" cx="5" cy="15" r="3" fill="#e6e6e6" 
                data-type="input" data-description="Entrée vanne"/>
                
        <!-- Port de sortie -->
        <circle id="Port2" cx="25" cy="15" r="3" fill="#e6e6e6" 
                data-type="output" data-description="Sortie vanne"/>
        
        <!-- Port optionnel -->
        <circle id="port_drain" cx="15" cy="25" r="2" fill="#e6e6e6"
                data-type="output" data-description="Vidange"/>
        
        <text x="15" y="17" text-anchor="middle" font-size="8" fill="#000">V</text>
      </g>
    </svg>'''
    
    print("=== TEST SVG PORT PARSER AVEC CONVERSION ===")
    
    # Test du parser
    parser = SVGPortParser()
    ports = parser.parse_svg_ports(test_svg)
    
    print(f"\n=== {len(ports)} PORTS DÉTECTÉS ET CONVERTIS ===")
    for port in ports:
        print(f"Port: {port['id']}")
        print(f"  Type: {port['type']}")
        print(f"  Position SVG: {port['conversion_info']['svg_position']}")
        print(f"  Position Qt: {port['position']}")
        print(f"  Description: {port['description']}")
        print(f"  Conversion: ViewBox{port['conversion_info']['viewbox']} → Taille{port['conversion_info']['target_size']}")
        print()
    
    # Test avec votre SVG spécifique
    your_svg = '''<svg
       width="30"
       height="30"
       viewBox="0 0 7.9374998 7.9375"
       version="1.1"
       xmlns="http://www.w3.org/2000/svg">
      <circle id="Port2" cx="3.96875" cy="0.52916664" r="0.52916664" />
      <circle id="Port1" cx="3.96875" cy="7.4083333" r="0.52916664" />
    </svg>'''
    
    print("=== TEST AVEC VOTRE SVG ===")
    your_ports = parser.parse_svg_ports(your_svg)
    
    for port in your_ports:
        svg_pos = port['conversion_info']['svg_position'] 
        qt_pos = port['position']
        print(f"Port{port['id']}: SVG{svg_pos} → Qt{qt_pos}")
        
        # Vérification du calcul
        # Port1: 3.96875/7.9375*30 = 15.0, 7.4083333/7.9375*30 = 28.0  
        # Port2: 3.96875/7.9375*30 = 15.0, 0.52916664/7.9375*30 = 2.0
        expected_x = round((svg_pos[0] / 7.9375) * 30, 2)
        expected_y = round((svg_pos[1] / 7.9375) * 30, 2)
        print(f"  Vérification: attendu ({expected_x}, {expected_y})")
        print(f"  Correct: {qt_pos == (expected_x, expected_y)}")
        print()
    
    # Test conversion coordonnées avec votre exemple
    viewbox = parser._get_svg_viewbox(test_svg)
    print(f"\n=== CONVERSION COORDONNÉES ===")
    print(f"ViewBox: {viewbox}")
    
    for port in ports:
        if 'conversion_info' in port:
            svg_pos = port['conversion_info']['svg_position']
            qt_pos = port['position']
            print(f"Port {port['id']}: SVG{svg_pos} → Qt{qt_pos}")
    
    # Test validation
    is_valid, warnings = parser.validate_svg_ports(test_svg)
    print(f"\n=== VALIDATION ===")
    print(f"Valide: {is_valid}")
    if warnings:
        print("Avertissements:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("\n=== TEST TERMINÉ ===")
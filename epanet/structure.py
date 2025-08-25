#!/usr/bin/env python3
"""
epanet/structure.py - Classes EPANET pures
Structure de données compatibles avec le format EPANET
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

# === ÉNUMÉRATIONS EPANET ===

class NodeType(Enum):
    JUNCTION = "JUNCTION"
    RESERVOIR = "RESERVOIR" 
    TANK = "TANK"

class LinkType(Enum):
    PIPE = "PIPE"
    PUMP = "PUMP"
    VALVE = "VALVE"

class PipeStatus(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    CV = "CV"  # Check Valve

class ValveType(Enum):
    PRV = "PRV"  # Pressure Reducing Valve
    PSV = "PSV"  # Pressure Sustaining Valve
    PBV = "PBV"  # Pressure Breaker Valve
    FCV = "FCV"  # Flow Control Valve
    TCV = "TCV"  # Throttle Control Valve
    GPV = "GPV"  # General Purpose Valve

# === CLASSES DE BASE ===

@dataclass
class EPANETNode(ABC):
    """Classe de base pour tous les nœuds EPANET"""
    node_id: str
    elevation: float = 0.0
    x_coord: float = 0.0
    y_coord: float = 0.0
    
    @abstractmethod
    def get_node_type(self) -> NodeType:
        pass
    
    @abstractmethod
    def to_epanet_section(self) -> str:
        """Génère la ligne pour le fichier EPANET"""
        pass

@dataclass
class EPANETLink(ABC):
    """Classe de base pour tous les liens EPANET"""
    link_id: str
    node1_id: str
    node2_id: str
    
    @abstractmethod
    def get_link_type(self) -> LinkType:
        pass
    
    @abstractmethod
    def to_epanet_section(self) -> str:
        """Génère la ligne pour le fichier EPANET"""
        pass

# === NŒUDS SPÉCIALISÉS ===

@dataclass
class EPANETJunction(EPANETNode):
    """Nœud de jonction EPANET"""
    demand: float = 0.0
    pattern: str = ""
    
    def get_node_type(self) -> NodeType:
        return NodeType.JUNCTION
    
    def to_epanet_section(self) -> str:
        return f" {self.node_id:<15}\t{self.elevation:<11}\t{self.demand:<11}\t{self.pattern:<15}\t;"

@dataclass
class EPANETReservoir(EPANETNode):
    """Réservoir EPANET (source infinie)"""
    head: float = 0.0
    pattern: str = ""
    
    def get_node_type(self) -> NodeType:
        return NodeType.RESERVOIR
    
    def to_epanet_section(self) -> str:
        return f" {self.node_id:<15}\t{self.head:<11}\t{self.pattern:<15}\t;"

@dataclass
class EPANETTank(EPANETNode):
    """Réservoir de stockage EPANET"""
    init_level: float = 0.0
    min_level: float = 0.0
    max_level: float = 10.0
    diameter: float = 10.0
    min_vol: float = 0.0
    vol_curve: str = ""
    overflow: str = ""
    
    def get_node_type(self) -> NodeType:
        return NodeType.TANK
    
    def to_epanet_section(self) -> str:
        return (f" {self.node_id:<15}\t{self.elevation:<11}\t{self.init_level:<11}\t"
                f"{self.min_level:<11}\t{self.max_level:<11}\t{self.diameter:<11}\t"
                f"{self.min_vol:<11}\t{self.vol_curve:<15}\t{self.overflow}")

# === LIENS SPÉCIALISÉS ===

@dataclass
class EPANETPipe(EPANETLink):
    """Tuyau EPANET"""
    length: float = 1000.0
    diameter: float = 100.0  # mm
    roughness: float = 100.0  # Coefficient Hazen-Williams
    minor_loss: float = 0.0
    status: PipeStatus = PipeStatus.OPEN
    
    def get_link_type(self) -> LinkType:
        return LinkType.PIPE
    
    def to_epanet_section(self) -> str:
        return (f" {self.link_id:<15}\t{self.node1_id:<15}\t{self.node2_id:<15}\t"
                f"{self.length:<11}\t{self.diameter:<11}\t{self.roughness:<11}\t"
                f"{self.minor_loss:<11}\t{self.status.value:<5}\t;")

@dataclass
class EPANETPump(EPANETLink):
    """Pompe EPANET"""
    parameters: str = "HEAD 1"  # Référence à une courbe
    
    def get_link_type(self) -> LinkType:
        return LinkType.PUMP
    
    def to_epanet_section(self) -> str:
        return f" {self.link_id:<15}\t{self.node1_id:<15}\t{self.node2_id:<15}\t{self.parameters}\t;"

@dataclass
class EPANETValve(EPANETLink):
    """Vanne EPANET"""
    diameter: float = 100.0
    valve_type: ValveType = ValveType.PRV
    setting: float = 0.0
    minor_loss: float = 0.0
    
    def get_link_type(self) -> LinkType:
        return LinkType.VALVE
    
    def to_epanet_section(self) -> str:
        return (f" {self.link_id:<15}\t{self.node1_id:<15}\t{self.node2_id:<15}\t"
                f"{self.diameter:<11}\t{self.valve_type.value}\t{self.setting:<11}\t"
                f"{self.minor_loss:<11}\t;")

# === COURBES ET PATTERNS ===

@dataclass
class EPANETCurve:
    """Courbe EPANET (pompe, efficacité, etc.)"""
    curve_id: str
    points: List[Tuple[float, float]] = field(default_factory=list)
    description: str = ""
    
    def add_point(self, x: float, y: float):
        """Ajoute un point à la courbe"""
        self.points.append((x, y))
    
    def to_epanet_section(self) -> str:
        """Génère les lignes pour la section [CURVES]"""
        lines = []
        if self.description:
            lines.append(f";{self.description}")
        
        for x, y in self.points:
            lines.append(f" {self.curve_id:<15}\t{x:<11}\t{y:<11}")
        
        return "\n".join(lines)

@dataclass
class EPANETPattern:
    """Pattern EPANET (demande, etc.)"""
    pattern_id: str
    multipliers: List[float] = field(default_factory=list)
    description: str = ""
    
    def to_epanet_section(self) -> str:
        """Génère les lignes pour la section [PATTERNS]"""
        lines = []
        if self.description:
            lines.append(f";{self.description}")
        
        # EPANET limite à 6 valeurs par ligne
        chunks = [self.multipliers[i:i+6] for i in range(0, len(self.multipliers), 6)]
        for chunk in chunks:
            values = "\t".join(f"{val:<11}" for val in chunk)
            lines.append(f" {self.pattern_id:<15}\t{values}")
        
        return "\n".join(lines)

# === RÉSEAU EPANET COMPLET ===

class EPANETNetwork:
    """Modèle complet du réseau EPANET"""
    
    def __init__(self, title: str = "Hydraulic Network"):
        self.title = title
        
        # Collections d'objets
        self.junctions: Dict[str, EPANETJunction] = {}
        self.reservoirs: Dict[str, EPANETReservoir] = {}
        self.tanks: Dict[str, EPANETTank] = {}
        self.pipes: Dict[str, EPANETPipe] = {}
        self.pumps: Dict[str, EPANETPump] = {}
        self.valves: Dict[str, EPANETValve] = {}
        self.curves: Dict[str, EPANETCurve] = {}
        self.patterns: Dict[str, EPANETPattern] = {}
        
        # Options globales par défaut
        self.options = {
            "Units": "LPS",  # L/s
            "Headloss": "H-W",  # Hazen-Williams
            "Specific Gravity": "1.0",
            "Viscosity": "1.0",
            "Trials": "40",
            "Accuracy": "0.001",
            "Unbalanced": "Continue 10",
            "Pattern": "1",
            "Demand Multiplier": "1.0",
            "Emitter Exponent": "0.5",
            "Quality": "None",
            "Diffusivity": "1.0",
            "Tolerance": "0.01"
        }
        
        # Paramètres temporels par défaut
        self.times = {
            "Duration": "24:00",
            "Hydraulic Timestep": "1:00",
            "Quality Timestep": "0:05",
            "Pattern Timestep": "2:00",
            "Pattern Start": "0:00",
            "Report Timestep": "1:00",
            "Report Start": "0:00",
            "Start ClockTime": "12 am",
            "Statistic": "None"
        }
    
    # === MÉTHODES D'AJOUT ===
    
    def add_junction(self, node_id: str, elevation: float = 0.0, 
                    demand: float = 0.0, x: float = 0.0, y: float = 0.0) -> EPANETJunction:
        """Ajoute une jonction au réseau"""
        junction = EPANETJunction(node_id, elevation, x, y, demand)
        self.junctions[node_id] = junction
        return junction
    
    def add_reservoir(self, node_id: str, head: float = 100.0, 
                     x: float = 0.0, y: float = 0.0) -> EPANETReservoir:
        """Ajoute un réservoir au réseau"""
        reservoir = EPANETReservoir(node_id, head, x, y, head)
        self.reservoirs[node_id] = reservoir
        return reservoir
    
    def add_tank(self, node_id: str, elevation: float = 0.0, init_level: float = 10.0,
                min_level: float = 0.0, max_level: float = 20.0, diameter: float = 10.0,
                x: float = 0.0, y: float = 0.0) -> EPANETTank:
        """Ajoute un tank au réseau"""
        tank = EPANETTank(node_id, elevation, x, y, init_level, min_level, 
                         max_level, diameter)
        self.tanks[node_id] = tank
        return tank
    
    def add_pipe(self, link_id: str, node1_id: str, node2_id: str,
                length: float = 1000.0, diameter: float = 100.0,
                roughness: float = 100.0) -> EPANETPipe:
        """Ajoute un tuyau au réseau"""
        pipe = EPANETPipe(link_id, node1_id, node2_id, length, diameter, roughness)
        self.pipes[link_id] = pipe
        return pipe
    
    def add_pump(self, link_id: str, node1_id: str, node2_id: str,
                curve_id: str = "1") -> EPANETPump:
        """Ajoute une pompe au réseau"""
        pump = EPANETPump(link_id, node1_id, node2_id, f"HEAD {curve_id}")
        self.pumps[link_id] = pump
        return pump
    
    def add_pump_curve(self, curve_id: str, points: List[Tuple[float, float]],
                      description: str = "") -> EPANETCurve:
        """Ajoute une courbe de pompe"""
        curve = EPANETCurve(curve_id, points, description)
        self.curves[curve_id] = curve
        return curve
    
    # === VALIDATION ===
    
    def validate_network(self) -> List[str]:
        """Valide la cohérence du réseau"""
        errors = []
        
        # Vérifier les références de nœuds
        all_nodes = set(self.junctions.keys()) | set(self.reservoirs.keys()) | set(self.tanks.keys())
        
        # Vérifier les liens
        all_links = list(self.pipes.values()) + list(self.pumps.values()) + list(self.valves.values())
        for link in all_links:
            if link.node1_id not in all_nodes:
                errors.append(f"{link.get_link_type().value} {link.link_id}: nœud {link.node1_id} introuvable")
            if link.node2_id not in all_nodes:
                errors.append(f"{link.get_link_type().value} {link.link_id}: nœud {link.node2_id} introuvable")
        
        # Vérifier les références de courbes
        for pump in self.pumps.values():
            curve_id = pump.parameters.split()[-1] if "HEAD" in pump.parameters else None
            if curve_id and curve_id not in self.curves:
                errors.append(f"Pump {pump.link_id}: courbe {curve_id} introuvable")
        
        # Vérifier qu'il y a au moins une source
        if not self.reservoirs and not self.tanks:
            errors.append("Aucune source d'eau (réservoir ou tank) dans le réseau")
        
        return errors
    
    # === EXPORT EPANET ===
    
    def to_epanet_file(self) -> str:
        """Génère le fichier EPANET complet"""
        sections = []
        
        # Titre
        sections.append(f"[TITLE]\n {self.title}\n")
        
        # Junctions
        if self.junctions:
            sections.append("[JUNCTIONS]")
            sections.append(";ID              \tElev        \tDemand      \tPattern         ")
            for junction in self.junctions.values():
                sections.append(junction.to_epanet_section())
            sections.append("")
        
        # Reservoirs
        if self.reservoirs:
            sections.append("[RESERVOIRS]")
            sections.append(";ID              \tHead        \tPattern         ")
            for reservoir in self.reservoirs.values():
                sections.append(reservoir.to_epanet_section())
            sections.append("")
        
        # Tanks
        if self.tanks:
            sections.append("[TANKS]")
            sections.append(";ID              \tElevation   \tInitLevel   \tMinLevel    \tMaxLevel    \tDiameter    \tMinVol      \tVolCurve        \tOverflow")
            for tank in self.tanks.values():
                sections.append(tank.to_epanet_section())
            sections.append("")
        
        # Pipes
        if self.pipes:
            sections.append("[PIPES]")
            sections.append(";ID              \tNode1           \tNode2           \tLength      \tDiameter    \tRoughness   \tMinorLoss   \tStatus")
            for pipe in self.pipes.values():
                sections.append(pipe.to_epanet_section())
            sections.append("")
        
        # Pumps
        if self.pumps:
            sections.append("[PUMPS]")
            sections.append(";ID              \tNode1           \tNode2           \tParameters")
            for pump in self.pumps.values():
                sections.append(pump.to_epanet_section())
            sections.append("")
        
        # Valves
        if self.valves:
            sections.append("[VALVES]")
            sections.append(";ID              \tNode1           \tNode2           \tDiameter    \tType\tSetting     \tMinorLoss   ")
            for valve in self.valves.values():
                sections.append(valve.to_epanet_section())
            sections.append("")
        
        # Curves
        if self.curves:
            sections.append("[CURVES]")
            sections.append(";ID              \tX-Value     \tY-Value")
            for curve in self.curves.values():
                sections.append(curve.to_epanet_section())
            sections.append("")
        
        # Patterns
        if self.patterns:
            sections.append("[PATTERNS]")
            sections.append(";ID              \tMultipliers")
            for pattern in self.patterns.values():
                sections.append(pattern.to_epanet_section())
            sections.append("")
        
        # Coordinates
        sections.append("[COORDINATES]")
        sections.append(";Node            \tX-Coord           \tY-Coord")
        all_nodes = list(self.junctions.values()) + list(self.reservoirs.values()) + list(self.tanks.values())
        for node in all_nodes:
            sections.append(f"{node.node_id:<15}\t{node.x_coord:<17}\t{node.y_coord:<17}")
        sections.append("")
        
        # Options
        sections.append("[OPTIONS]")
        for key, value in self.options.items():
            sections.append(f" {key:<17}\t{value}")
        sections.append("")
        
        # Times
        sections.append("[TIMES]")
        for key, value in self.times.items():
            sections.append(f" {key:<17}\t{value}")
        sections.append("")
        
        # Sections vides mais requises par EPANET
        empty_sections = ["TAGS", "DEMANDS", "STATUS", "CONTROLS", "RULES", 
                         "ENERGY", "EMITTERS", "QUALITY", "SOURCES", "REACTIONS", 
                         "MIXING", "REPORT", "VERTICES", "LABELS", "BACKDROP"]
        
        for section in empty_sections:
            sections.append(f"[{section}]\n")
        
        sections.append("[END]")
        
        return "\n".join(sections)
    
    # === STATISTIQUES ===
    
    def get_statistics(self) -> Dict[str, int]:
        """Retourne les statistiques du réseau"""
        return {
            "junctions": len(self.junctions),
            "reservoirs": len(self.reservoirs),
            "tanks": len(self.tanks),
            "pipes": len(self.pipes),
            "pumps": len(self.pumps),
            "valves": len(self.valves),
            "curves": len(self.curves),
            "patterns": len(self.patterns),
            "total_nodes": len(self.junctions) + len(self.reservoirs) + len(self.tanks),
            "total_links": len(self.pipes) + len(self.pumps) + len(self.valves)
        }
    
    # === UTILITÉS ===
    
    def to_json(self) -> str:
        """Sérialise le réseau en JSON"""
        data = {
            "title": self.title,
            "nodes": {
                "junctions": {k: v.__dict__ for k, v in self.junctions.items()},
                "reservoirs": {k: v.__dict__ for k, v in self.reservoirs.items()},
                "tanks": {k: v.__dict__ for k, v in self.tanks.items()}
            },
            "links": {
                "pipes": {k: {**v.__dict__, "status": v.status.value} for k, v in self.pipes.items()},
                "pumps": {k: v.__dict__ for k, v in self.pumps.items()},
                "valves": {k: {**v.__dict__, "valve_type": v.valve_type.value} for k, v in self.valves.items()}
            },
            "curves": {k: v.__dict__ for k, v in self.curves.items()},
            "patterns": {k: v.__dict__ for k, v in self.patterns.items()},
            "options": self.options,
            "times": self.times
        }
        return json.dumps(data, indent=2)

# === EXEMPLE ET TEST ===

if __name__ == "__main__":
    # Test de création d'un réseau simple
    network = EPANETNetwork("Réseau de test")
    
    # Ajouter un réservoir (source)
    reservoir = network.add_reservoir("R1", head=100.0, x=0, y=50)
    
    # Ajouter des jonctions
    j1 = network.add_junction("J1", elevation=90, x=20, y=50)
    j2 = network.add_junction("J2", elevation=85, demand=50, x=40, y=50)
    
    # Ajouter un tuyau
    pipe1 = network.add_pipe("P1", "R1", "J1", length=1000, diameter=200)
    pipe2 = network.add_pipe("P2", "J1", "J2", length=800, diameter=150)
    
    # Ajouter une pompe avec courbe
    pump = network.add_pump("PU1", "R1", "J1", curve_id="CURVE1")
    curve_points = [(0, 120), (50, 100), (100, 75), (150, 45), (200, 0)]
    curve = network.add_pump_curve("CURVE1", curve_points, "Courbe pompe principale")
    
    # Validation
    print("=== VALIDATION ===")
    errors = network.validate_network()
    if errors:
        for error in errors:
            print(f"❌ {error}")
    else:
        print("✅ Réseau valide")
    
    # Statistiques
    print("\n=== STATISTIQUES ===")
    stats = network.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Test export
    print("\n=== EXPORT EPANET ===")
    epanet_content = network.to_epanet_file()
    
    # Sauvegarder le fichier test
    with open("test_network.inp", "w") as f:
        f.write(epanet_content)
    
    print("✅ Fichier EPANET généré: test_network.inp")
    print(f"📏 Taille: {len(epanet_content)} caractères")
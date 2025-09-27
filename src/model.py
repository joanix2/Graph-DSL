"""
Modèle interne pour représenter les graphes, états et règles
"""

import networkx as nx
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class GraphConfig:
    """Configuration du graphe pour la simulation"""
    iterations: int = 100
    step_delay: float = 0.1
    auto_stop: bool = True
    verbose: bool = True

@dataclass
class AttrDef:
    """Définition d'un attribut dans un type"""
    name: str
    attr_type: Any  # Type de l'attribut (string, int, enum, etc.)

@dataclass
class TypeDef:
    """Définition d'un type (entity ou relation)"""
    name: str
    kind: str  # "entity" ou "relation"  
    attributes: List[AttrDef]

@dataclass
class Node:
    """Représente un nœud du graphe"""
    id: str
    properties: Dict[str, Any]
    state: Optional[str] = None
    type_name: Optional[str] = None

@dataclass
class Edge:
    """Représente une arête du graphe"""
    source: str
    target: str
    properties: Dict[str, Any]
    relation_name: Optional[str] = None
    type_name: Optional[str] = None
    
@dataclass
class Rule:
    """Représente une règle d'évolution"""
    name: str
    condition: Any  # Dictionnaire représentant la condition
    action: Any     # Dictionnaire représentant l'action

class GraphModel:
    """Modèle principal du graphe avec ses règles"""
    
    def __init__(self, name: str):
        self.name = name
        self.graph = nx.Graph()
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.rules: List[Rule] = []
        self.types: Dict[str, TypeDef] = {}
        self.config: GraphConfig = GraphConfig()
    
    def add_type(self, type_def: TypeDef):
        """Ajoute une définition de type"""
        self.types[type_def.name] = type_def
    
    def add_node(self, node: Node):
        """Ajoute un nœud au graphe"""
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.properties)
    
    def add_edge(self, edge: Edge):
        """Ajoute une arête au graphe"""
        self.edges.append(edge)
        self.graph.add_edge(edge.source, edge.target, **edge.properties)
    
    def add_rule(self, rule: Rule):
        """Ajoute une règle d'évolution"""
        self.rules.append(rule)
    
    def set_config(self, config: GraphConfig):
        """Définit la configuration du graphe"""
        self.config = config
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Retourne les voisins d'un nœud"""
        return list(self.graph.neighbors(node_id))
    
    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """Récupère un nœud par son ID"""
        return self.nodes.get(node_id)
    
    def count_neighbors_with_state(self, node_id: str, state: str) -> int:
        """Compte les voisins d'un nœud ayant un état donné"""
        count = 0
        neighbors = self.get_neighbors(node_id)
        for neighbor_id in neighbors:
            neighbor = self.get_node_by_id(neighbor_id)
            if neighbor and neighbor.properties.get('state') == state:
                count += 1
        return count
    
    def update_node_property(self, node_id: str, property_name: str, value: Any):
        """Met à jour une propriété d'un nœud"""
        if node_id in self.nodes:
            self.nodes[node_id].properties[property_name] = value
            # Mettre à jour aussi dans le graphe NetworkX
            self.graph.nodes[node_id][property_name] = value
    
    def __repr__(self):
        return f"GraphModel(name={self.name}, nodes={len(self.nodes)}, edges={len(self.edges)}, rules={len(self.rules)}, types={len(self.types)}, config={self.config})"


"""
Tests pour le modèle de données Graph DSL
"""

import pytest
from src.model import (
    GraphModel, Node, Edge, Rule, TypeDef, AttrDef, GraphConfig
)

class TestGraphModel:
    
    def test_graph_model_creation(self):
        """Test création d'un modèle de graphe"""
        model = GraphModel("TestGraph")
        
        assert model.name == "TestGraph"
        assert isinstance(model.nodes, dict)
        assert isinstance(model.edges, list)
        assert isinstance(model.rules, list)
        assert isinstance(model.types, dict)
        assert isinstance(model.config, GraphConfig)
    
    def test_add_node(self):
        """Test ajout de nœuds"""
        model = GraphModel("TestGraph")
        node = Node("node1", {"state": "active", "value": 42})
        
        model.add_node(node)
        
        assert "node1" in model.nodes
        assert model.nodes["node1"] == node
        assert model.nodes["node1"].properties["state"] == "active"
        assert model.nodes["node1"].properties["value"] == 42
        # Vérifier que le nœud est ajouté au graph NetworkX
        assert "node1" in model.graph.nodes
    
    def test_add_edge(self):
        """Test ajout d'arêtes"""
        model = GraphModel("TestGraph")
        
        # D'abord ajouter des nœuds
        node1 = Node("node1", {})
        node2 = Node("node2", {})
        model.add_node(node1)
        model.add_node(node2)
        
        # Puis ajouter une arête
        edge = Edge("node1", "node2", {"weight": 1.5})
        model.add_edge(edge)
        
        assert len(model.edges) == 1
        assert model.edges[0] == edge
        assert model.edges[0].source == "node1"
        assert model.edges[0].target == "node2"
        assert model.edges[0].properties["weight"] == 1.5
        # Vérifier que l'arête est ajoutée au graph NetworkX
        assert model.graph.has_edge("node1", "node2")

class TestNode:
    
    def test_node_creation(self):
        """Test création d'un nœud"""
        properties = {"state": "alive", "energy": 10, "x": 5.5}
        node = Node("cell1", properties)
        
        assert node.id == "cell1"
        assert node.properties == properties
        assert node.properties["state"] == "alive"
        assert node.properties["energy"] == 10
        assert node.properties["x"] == 5.5
    
    def test_node_empty_properties(self):
        """Test nœud avec propriétés vides"""
        node = Node("empty_node", {})
        
        assert node.id == "empty_node"
        assert node.properties == {}
    
    def test_node_update_property(self):
        """Test mise à jour d'une propriété de nœud"""
        node = Node("test", {"state": "dead"})
        node.properties["state"] = "alive"
        
        assert node.properties["state"] == "alive"

class TestEdge:
    
    def test_edge_creation(self):
        """Test création d'une arête"""
        properties = {"weight": 2.0, "type": "connection"}
        edge = Edge("from_node", "to_node", properties)
        
        assert edge.source == "from_node"
        assert edge.target == "to_node"
        assert edge.properties == properties
    
    def test_edge_no_properties(self):
        """Test arête avec propriétés vides"""
        edge = Edge("a", "b", {})
        
        assert edge.source == "a"
        assert edge.target == "b"
        assert edge.properties == {}
    
    def test_edge_with_type_info(self):
        """Test arête avec informations de type"""
        properties = {"weight": 1.0}
        edge = Edge("node1", "node2", properties, "connection", "LinkType")
        
        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.relation_name == "connection"
        assert edge.type_name == "LinkType"

class TestTypeDef:
    
    def test_typedef_creation(self):
        """Test création d'une définition de type"""
        attrs = [
            AttrDef("state", "string"),
            AttrDef("energy", "int")
        ]
        typedef = TypeDef("CellType", "entity", attrs)
        
        assert typedef.name == "CellType"
        assert typedef.kind == "entity"
        assert len(typedef.attributes) == 2
        assert typedef.attributes[0].name == "state"
        assert typedef.attributes[1].name == "energy"

class TestAttrDef:
    
    def test_attrdef_creation(self):
        """Test création d'une définition d'attribut"""
        attr = AttrDef("temperature", "float")
        
        assert attr.name == "temperature"
        assert attr.attr_type == "float"
    
    def test_attrdef_with_type_info(self):
        """Test attribut avec information de type"""
        attr = AttrDef("status", {"type": "enum", "values": ["active", "inactive"]})
        
        assert attr.name == "status"
        assert attr.attr_type["type"] == "enum"
        assert "active" in attr.attr_type["values"]

class TestRule:
    
    def test_rule_creation(self):
        """Test création d'une règle"""
        condition = {"type": "comparison", "left": "energy", "operator": ">", "right": 5}
        action = {"type": "set_property", "property": "state", "value": "alive"}
        rule = Rule("activation", condition, action)
        
        assert rule.name == "activation"
        assert rule.condition == condition
        assert rule.action == action
    
    def test_rule_with_dict_structures(self):
        """Test règle avec structures dict"""
        condition = {"type": "neighbor_count", "target": "node", "state_filter": "alive", "comparator": ">=", "value": 2}
        action = {"type": "set_attribute", "target": "node", "attribute": "state", "value": "alive"}
        rule = Rule("activation_rule", condition, action)
        
        assert rule.name == "activation_rule"
        assert rule.condition["type"] == "neighbor_count"
        assert rule.action["type"] == "set_attribute"

class TestGraphConfig:
    
    def test_config_creation(self):
        """Test création d'une configuration"""
        config = GraphConfig()
        
        # Valeurs par défaut
        assert config.iterations == 100
        assert config.step_delay == 0.1
        assert config.auto_stop == True
        assert config.verbose == True
    
    def test_config_custom_values(self):
        """Test configuration avec valeurs personnalisées"""
        config = GraphConfig(
            iterations=50,
            step_delay=0.5,
            auto_stop=False,
            verbose=False
        )
        
        assert config.iterations == 50
        assert config.step_delay == 0.5
        assert config.auto_stop == False
        assert config.verbose == False

class TestModelIntegration:
    
    def test_complete_model(self):
        """Test d'un modèle complet"""
        model = GraphModel("CompleteTest")
        
        # Ajouter un type
        attrs = [AttrDef("state", "string"), AttrDef("energy", "int")]
        cell_type = TypeDef("Cell", "entity", attrs)
        model.add_type(cell_type)
        
        # Ajouter des nœuds
        node1 = Node("cell1", {"state": "alive", "energy": 10}, type_name="Cell")
        node2 = Node("cell2", {"state": "dead", "energy": 0}, type_name="Cell")
        model.add_node(node1)
        model.add_node(node2)
        
        # Ajouter une arête
        edge = Edge("cell1", "cell2", {})
        model.add_edge(edge)
        
        # Ajouter une règle
        condition = {"type": "comparison", "property": "energy", "operator": ">", "value": 5}
        action = {"type": "set_property", "property": "state", "value": "alive"}
        rule = Rule("activation", condition, action)
        model.add_rule(rule)
        
        # Vérifier le modèle complet
        assert len(model.types) == 1
        assert len(model.nodes) == 2
        assert len(model.edges) == 1
        assert len(model.rules) == 1
        
        # Vérifier les fonctions utilitaires
        neighbors = model.get_neighbors("cell1")
        assert "cell2" in neighbors
        
        node = model.get_node_by_id("cell1")
        assert node is not None
        assert node.properties["state"] == "alive"
        
        # Test comptage voisins
        count = model.count_neighbors_with_state("cell1", "dead")
        assert count == 1
        
        # Test mise à jour propriété
        model.update_node_property("cell1", "energy", 15)
        assert model.nodes["cell1"].properties["energy"] == 15

"""
Tests pour le parser Graph DSL
"""

import pytest
from src.parser import GraphDSLParser
from src.model import GraphModel, Node, TypeDef

class TestGraphDSLParser:
    
    def setup_method(self):
        self.parser = GraphDSLParser()
    
    def test_parse_simple_graph(self, simple_graph_dsl):
        """Test parsing d'un graphe simple"""
        model = self.parser.parse_to_model(simple_graph_dsl)
        
        assert isinstance(model, GraphModel)
        assert model.name == "SimpleTest"
        assert len(model.nodes) == 2
        assert len(model.edges) == 1
        assert len(model.types) == 1
        assert len(model.rules) == 1
    
    def test_parse_config_block(self, sample_dsl_content):
        """Test parsing du bloc de configuration"""
        model = self.parser.parse_to_model(sample_dsl_content)
        
        assert model.config is not None
        assert model.config.iterations == 5
        assert model.config.step_delay == 0.1
        assert model.config.auto_stop == False
        assert model.config.verbose == True
    
    def test_parse_type_definitions(self, sample_dsl_content):
        """Test parsing des définitions de types"""
        model = self.parser.parse_to_model(sample_dsl_content)
        
        assert "Node" in model.types
        node_type = model.types["Node"]
        assert isinstance(node_type, TypeDef)
        assert len(node_type.attributes) == 2
        
        # Vérifier les attributs
        state_attr = next((attr for attr in node_type.attributes if attr.name == "state"), None)
        assert state_attr is not None
        assert state_attr.type == "string"
        assert state_attr.default_value == "dead"
        
        energy_attr = next((attr for attr in node_type.attributes if attr.name == "energy"), None)
        assert energy_attr is not None
        assert energy_attr.type == "int"
        assert energy_attr.default_value == 0
    
    def test_parse_entities(self, sample_dsl_content):
        """Test parsing des entités"""
        model = self.parser.parse_to_model(sample_dsl_content)
        
        assert len(model.nodes) == 3
        assert "cell1" in model.nodes
        assert "cell2" in model.nodes
        assert "cell3" in model.nodes
        
        # Vérifier les propriétés
        cell1 = model.nodes["cell1"]
        assert cell1.properties["state"] == "alive"
        assert cell1.properties["energy"] == 10
        
        cell2 = model.nodes["cell2"]
        assert cell2.properties["state"] == "dead"
        assert cell2.properties["energy"] == 0
    
    def test_parse_relations(self, sample_dsl_content):
        """Test parsing des relations"""
        model = self.parser.parse_to_model(sample_dsl_content)
        
        assert len(model.edges) == 3
        
        # Vérifier les connexions
        edge_pairs = [(edge.from_node, edge.to_node) for edge in model.edges]
        assert ("cell1", "cell2") in edge_pairs
        assert ("cell2", "cell3") in edge_pairs
        assert ("cell3", "cell1") in edge_pairs
    
    def test_parse_rules(self, sample_dsl_content):
        """Test parsing des règles"""
        model = self.parser.parse_to_model(sample_dsl_content)
        
        assert len(model.rules) == 2
        
        rule_names = [rule.name for rule in model.rules]
        assert "birth" in rule_names
        assert "death" in rule_names
        
        # Vérifier une règle spécifique
        birth_rule = next((rule for rule in model.rules if rule.name == "birth"), None)
        assert birth_rule is not None
        assert "energy > 5" in str(birth_rule.condition)
        assert "state = \"alive\"" in str(birth_rule.action)
    
    def test_parse_invalid_syntax(self):
        """Test handling des erreurs de syntaxe"""
        invalid_dsl = """
        graph InvalidGraph {
            entity missing_type_def
        }
        """
        
        with pytest.raises(Exception):
            self.parser.parse_to_model(invalid_dsl)
    
    def test_parse_empty_graph(self):
        """Test parsing d'un graphe vide"""
        empty_dsl = """
        graph EmptyGraph {
            config {
                iterations 1
            }
        }
        """
        
        model = self.parser.parse_to_model(empty_dsl)
        assert model.name == "EmptyGraph"
        assert len(model.nodes) == 0
        assert len(model.edges) == 0
        assert len(model.types) == 0
        assert len(model.rules) == 0
        assert model.config.iterations == 1
    
    def test_ast_generation(self, simple_graph_dsl):
        """Test génération de l'AST"""
        ast = self.parser.parse(simple_graph_dsl)
        
        assert ast is not None
        assert hasattr(ast, 'data')
        assert ast.data == 'start'
        
        # Vérifier que l'AST contient les éléments attendus
        assert len(ast.children) > 0
    
    def test_multiple_config_blocks(self):
        """Test gestion de plusieurs blocs de configuration"""
        multi_config_dsl = """
        graph MultiConfig {
            config {
                iterations 5
            }
            
            config {
                verbose true
            }
        }
        """
        
        model = self.parser.parse_to_model(multi_config_dsl)
        # Le dernier bloc de config devrait prévaloir
        assert model.config.verbose == True
        # Les valeurs précédentes devraient être conservées si pas redéfinies
        assert model.config.iterations == 5

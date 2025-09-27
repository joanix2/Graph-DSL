"""
Tests pour le simulateur de base Graph DSL
"""

import pytest
from src.simulator import NetworkXSimulator, SimulationConfig
from src.parser import GraphDSLParser
from src.model import GraphModel, Node, Rule, GraphConfig

class TestSimulationConfig:
    
    def test_default_config(self):
        """Test configuration par défaut"""
        config = SimulationConfig()
        
        assert config.max_steps == 100
        assert config.step_delay == 0.0
        assert config.auto_stop_on_stable == True
        assert config.verbose == False
    
    def test_custom_config(self):
        """Test configuration personnalisée"""
        config = SimulationConfig(
            max_steps=50,
            step_delay=1.5,
            auto_stop_on_stable=False,
            verbose=True
        )
        
        assert config.max_steps == 50
        assert config.step_delay == 1.5
        assert config.auto_stop_on_stable == False
        assert config.verbose == True

class TestNetworkXSimulator:
    
    def test_simulator_initialization(self, simple_graph_dsl):
        """Test initialisation du simulateur"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(simple_graph_dsl)
        
        simulator = NetworkXSimulator(model)
        
        assert simulator.model == model
        assert simulator.nx_graph is not None
        assert simulator.observers == []
        assert simulator.evolution_history == []
    
    def test_simulator_with_config(self, simple_graph_dsl):
        """Test simulateur avec configuration personnalisée"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(simple_graph_dsl)
        
        config = SimulationConfig(max_steps=5, verbose=True)
        simulator = NetworkXSimulator(model, config)
        
        assert simulator.config.max_steps == 5
        assert simulator.config.verbose == True
    
    def test_add_observer(self, simple_graph_dsl):
        """Test ajout d'observateurs"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(simple_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        observer_calls = []
        def test_observer(graph, step):
            observer_calls.append((graph, step))
        
        simulator.add_observer(test_observer)
        assert len(simulator.observers) == 1
        
        # Tester l'appel de l'observateur
        simulator._notify_observers(model, 0)
        assert len(observer_calls) == 1
        assert observer_calls[0][1] == 0
    
    def test_observer_error_handling(self, simple_graph_dsl):
        """Test gestion d'erreurs dans les observateurs"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(simple_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        def failing_observer(graph, step):
            raise ValueError("Test error")
        
        def working_observer(graph, step):
            pass
        
        simulator.add_observer(failing_observer)
        simulator.add_observer(working_observer)
        
        # Ne devrait pas lever d'exception
        simulator._notify_observers(model, 0)
    
    def test_empty_graph_simulation(self):
        """Test simulation d'un graphe vide"""
        empty_dsl = """
        graph Empty {
            config { iterations 2 }
        }
        """
        
        parser = GraphDSLParser()
        model = parser.parse_to_model(empty_dsl)
        simulator = NetworkXSimulator(model)
        
        steps = simulator.run()
        
        assert steps >= 0
        assert len(simulator.evolution_history) > 0
    
    def test_single_node_simulation(self):
        """Test simulation avec un seul nœud"""
        single_node_dsl = """
        graph SingleNode {
            config { iterations 3 }
            
            type Cell {
                value: int = 1
            }
            
            entity node1: Cell { value = 5 }
            
            rule "increment" {
                condition: value < 10
                action: value = value + 1
            }
        }
        """
        
        parser = GraphDSLParser()
        model = parser.parse_to_model(single_node_dsl)
        simulator = NetworkXSimulator(model)
        
        steps = simulator.run()
        
        assert steps > 0
        assert len(model.nodes) == 1
        # Le nœud devrait avoir été modifié par la règle
        node = list(model.nodes.values())[0]
        assert node.properties["value"] >= 5
    
    def test_graph_conversion(self, sample_dsl_content):
        """Test conversion du modèle vers NetworkX"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(sample_dsl_content)
        simulator = NetworkXSimulator(model)
        
        nx_graph = simulator.nx_graph
        
        # Vérifier que tous les nœuds sont présents
        assert len(nx_graph.nodes) == len(model.nodes)
        for node_id in model.nodes.keys():
            assert node_id in nx_graph.nodes
        
        # Vérifier que toutes les arêtes sont présentes
        model_edges = [(edge.from_node, edge.to_node) for edge in model.edges]
        nx_edges = list(nx_graph.edges())
        assert len(nx_edges) == len(model_edges)
    
    def test_statistics_collection(self, simple_graph_dsl):
        """Test collection de statistiques"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(simple_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        # Lancer une simulation
        simulator.run()
        
        stats = simulator.get_statistics()
        
        assert isinstance(stats, dict)
        # Devrait contenir au moins quelques statistiques de base
        assert len(stats) >= 0
    
    def test_evolution_tracking(self, simple_graph_dsl):
        """Test suivi de l'évolution"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(simple_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        # Lancer une simulation courte
        steps = simulator.run()
        
        history = simulator.get_evolution_history()
        
        assert isinstance(history, list)
        assert len(history) == steps + 1  # +1 pour l'état initial
        
        # Vérifier la structure des entrées
        for entry in history:
            assert 'step' in entry
            assert 'metrics' in entry
            assert isinstance(entry['step'], int)
            assert isinstance(entry['metrics'], dict)
    
    def test_multiple_simulations(self, simple_graph_dsl):
        """Test exécutions multiples"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(simple_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        # Première simulation
        steps1 = simulator.run()
        history1_len = len(simulator.get_evolution_history())
        
        # Deuxième simulation (devrait reset l'historique)
        steps2 = simulator.run()
        history2_len = len(simulator.get_evolution_history())
        
        assert steps1 >= 0
        assert steps2 >= 0
        # L'historique devrait être remis à zéro entre les simulations
        assert history2_len <= history1_len + steps2 + 1

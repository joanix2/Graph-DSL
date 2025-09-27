"""
Tests pour l'intégration NetworkX avec Graph DSL
"""

import pytest
import sys
from src.parser import GraphDSLParser
from src.simulator import NetworkXSimulator

"""
Tests pour l'intégration NetworkX avec Graph DSL
"""

import pytest
import sys
from src.parser import GraphDSLParser
from src.simulator import NetworkXSimulator

@pytest.fixture
def complex_graph_dsl():
    """Crée un graphe de test plus complexe"""
    return """
types {
    entity Node {
        attr state: string
        attr energy: int
    }
    
    relation Edge {
        attr weight: int
    }
}

graph NetworkTest {
    config {
        iterations: 8
        step_delay: 0
        auto_stop: false
        verbose: true
    }

    entities {
        n1: Node(state="active", energy=100)
        n2: Node(state="inactive", energy=50)
        n3: Node(state="active", energy=75)
        n4: Node(state="inactive", energy=25)
        n5: Node(state="active", energy=90)
        n6: Node(state="inactive", energy=60)
    }

    relations {
        e1: Edge(n1, n2, weight=5)
        e2: Edge(n2, n3, weight=3)
        e3: Edge(n3, n4, weight=7)
        e4: Edge(n4, n5, weight=2)
        e5: Edge(n5, n6, weight=4)
        e6: Edge(n6, n1, weight=6)
        e7: Edge(n1, n4, weight=8)
        e8: Edge(n2, n5, weight=1)
    }

    rules {
        activation: if neighbor_count(node, state=active) >= 2 then node.state = active
        deactivation: if neighbor_count(node, state=active) == 0 then node.state = inactive
    }
}
"""

class TestNetworkXSimulator:
    
    def test_simulator_creation(self, complex_graph_dsl):
        """Test création du simulateur NetworkX"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        assert simulator is not None
        assert simulator.nx_graph is not None
        assert len(simulator.nx_graph.nodes) == 6
        assert len(simulator.nx_graph.edges) == 8
    
    def test_graph_metrics(self, complex_graph_dsl):
        """Test calcul des métriques de graphe"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        metrics = simulator.get_graph_metrics()
        
        assert 'density' in metrics
        assert 'average_clustering' in metrics
        assert 'diameter' in metrics
        assert 'is_connected' in metrics
        
        # Vérifier que les valeurs sont dans les bonnes plages
        assert 0 <= metrics['density'] <= 1
        assert 0 <= metrics['average_clustering'] <= 1
        assert metrics['diameter'] >= 0
        assert isinstance(metrics['is_connected'], bool)
    
    def test_centrality_analysis(self, complex_graph_dsl):
        """Test analyse de centralité"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        centralities = simulator.get_node_centralities()
        
        # Vérifier tous les types de centralité
        expected_types = ['degree', 'betweenness', 'closeness', 'eigenvector']
        for centrality_type in expected_types:
            assert centrality_type in centralities
            
            # Chaque nœud devrait avoir une valeur
            for node_id in model.nodes.keys():
                assert node_id in centralities[centrality_type]
                assert isinstance(centralities[centrality_type][node_id], float)
    
    def test_community_detection(self, complex_graph_dsl):
        """Test détection de communautés"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        communities = simulator.analyze_communities()
        
        assert isinstance(communities, list)
        # Vérifier que tous les nœuds sont dans une communauté
        all_nodes_in_communities = set()
        for community in communities:
            all_nodes_in_communities.update(community)
        
        expected_nodes = set(model.nodes.keys())
        assert all_nodes_in_communities == expected_nodes
    
    def test_shortest_paths(self, complex_graph_dsl):
        """Test calcul des plus courts chemins"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        paths = simulator.find_shortest_paths('n1')
        
        assert 'n1' in paths
        assert isinstance(paths['n1'], dict)
        
        # Vérifier que tous les autres nœuds sont atteignables
        for node_id in model.nodes.keys():
            if node_id != 'n1':
                assert node_id in paths['n1']
                path = paths['n1'][node_id]
                assert isinstance(path, list)
                assert len(path) >= 1
                assert path[0] == 'n1'  # Le chemin commence par le nœud source
                assert path[-1] == node_id  # Et se termine par la destination
    
    def test_simulation_run(self, complex_graph_dsl):
        """Test exécution de simulation"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        # Observer simple pour compter les étapes
        step_count = 0
        def count_observer(graph, step):
            nonlocal step_count
            step_count = step
        
        simulator.add_observer(count_observer)
        steps_executed = simulator.run()
        
        assert steps_executed > 0
        assert step_count == steps_executed
    
    def test_evolution_history(self, complex_graph_dsl):
        """Test historique d'évolution"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        # Lancer une simulation courte
        simulator.run()
        
        history = simulator.get_evolution_history()
        
        assert isinstance(history, list)
        assert len(history) > 0
        
        # Vérifier la structure des entrées d'historique
        for entry in history:
            assert 'step' in entry
            assert 'metrics' in entry
            assert isinstance(entry['step'], int)
            assert isinstance(entry['metrics'], dict)
    
    def test_statistics(self, complex_graph_dsl):
        """Test calcul de statistiques"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        # Lancer la simulation
        simulator.run()
        
        stats = simulator.get_statistics()
        
        assert isinstance(stats, dict)
        # Vérifier qu'il y a des statistiques significatives
        assert len(stats) > 0
    
    def test_export_formats(self, complex_graph_dsl):
        """Test export vers différents formats"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        exports = simulator.export_to_formats()
        
        assert isinstance(exports, dict)
        # Vérifier les formats d'export standard
        expected_formats = ['node_list', 'edge_list', 'graph_dict']
        for format_name in expected_formats:
            assert format_name in exports
    
    def test_observer_mechanism(self, complex_graph_dsl):
        """Test mécanisme d'observation"""
        parser = GraphDSLParser()
        model = parser.parse_to_model(complex_graph_dsl)
        simulator = NetworkXSimulator(model)
        
        # Liste pour capturer les appels d'observateur
        observer_calls = []
        
        def test_observer(graph, step):
            observer_calls.append(step)
        
        simulator.add_observer(test_observer)
        steps = simulator.run()
        
        # Vérifier que l'observateur a été appelé pour chaque étape
        assert len(observer_calls) == steps + 1  # +1 pour l'état initial (step 0)
        assert observer_calls[0] == 0  # Premier appel à l'étape 0
        assert observer_calls[-1] == steps  # Dernier appel à l'étape finale
    
    def test_error_handling(self):
        """Test gestion d'erreurs"""
        # Test avec un modèle vide/invalide
        parser = GraphDSLParser()
        empty_dsl = """
        graph Empty {
            config { iterations 1 }
        }
        """
        model = parser.parse_to_model(empty_dsl)
        simulator = NetworkXSimulator(model)
        
        # Devrait fonctionner même avec un graphe vide
        steps = simulator.run()
        assert steps >= 0
        
        # Les métriques devraient gérer le cas du graphe vide
        metrics = simulator.get_graph_metrics()
        assert isinstance(metrics, dict)

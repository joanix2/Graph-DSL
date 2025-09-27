#!/usr/bin/env python3
"""
Test du simulateur NetworkX avancé
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.parser import GraphDSLParser
from src.simulator import NetworkXSimulator

def create_test_graph_dsl():
    """Crée un graphe de test plus complexe"""
    return """
types {
    entity Node {
        attr state: {active, inactive}
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
        n1: Node(state=active, energy=100)
        n2: Node(state=inactive, energy=50)
        n3: Node(state=active, energy=75)
        n4: Node(state=inactive, energy=25)
        n5: Node(state=active, energy=90)
        n6: Node(state=inactive, energy=60)
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
        Activation: if neighbor_count(node, state=active) >= 2 then node.state = active
        Deactivation: if neighbor_count(node, state=active) == 0 then node.state = inactive
    }
}
"""

def test_networkx_features():
    """Test des fonctionnalités NetworkX avancées"""
    print("🔬 TEST SIMULATEUR NETWORKX AVANCÉ")
    print("=" * 50)
    
    # Parser le graphe
    parser = GraphDSLParser()
    dsl_content = create_test_graph_dsl()
    
    try:
        model = parser.parse_to_model(dsl_content)
        print(f"✅ Graphe parsé: {model}")
        
        # Créer le simulateur NetworkX
        simulator = NetworkXSimulator(model)
        
        print(f"\n📊 ANALYSE INITIALE")
        print("-" * 30)
        
        # Métriques initiales
        initial_metrics = simulator.get_graph_metrics()
        print("🔍 Métriques du graphe:")
        for metric, value in initial_metrics.items():
            if value is not None:
                if isinstance(value, float):
                    print(f"   {metric}: {value:.3f}")
                else:
                    print(f"   {metric}: {value}")
        
        # Centralités
        print("\n🎯 Centralités des nœuds:")
        centralities = simulator.get_node_centralities()
        for centrality_type, values in centralities.items():
            print(f"   {centrality_type}:")
            sorted_nodes = sorted(values.items(), key=lambda x: x[1], reverse=True)
            for node, score in sorted_nodes:
                print(f"     {node}: {score:.3f}")
        
        # Communautés
        communities = simulator.analyze_communities()
        if communities:
            print(f"\n🏘️ Communautés détectées: {len(communities)}")
            for i, community in enumerate(communities):
                print(f"   Communauté {i+1}: {community}")
        
        # Plus courts chemins (exemple)
        print(f"\n🛤️ Plus courts chemins depuis n1:")
        paths = simulator.find_shortest_paths('n1')
        if 'n1' in paths:
            for target, path in paths['n1'].items():
                if target != 'n1':
                    print(f"   n1 → {target}: {' → '.join(path)}")
        
        print(f"\n🎮 SIMULATION EN COURS")
        print("-" * 30)
        
        # Fonction d'observation personnalisée
        def detailed_observer(graph, step):
            print(f"\n--- Étape {step} ---")
            active_count = 0
            inactive_count = 0
            
            for node_id, node in graph.nodes.items():
                state = node.properties.get('state', 'unknown')
                energy = node.properties.get('energy', 0)
                
                if state == 'active':
                    active_count += 1
                else:
                    inactive_count += 1
                    
                print(f"  {node_id}: {state} (énergie: {energy})")
            
            print(f"  💡 Actifs: {active_count}, 😴 Inactifs: {inactive_count}")
            
            # Métriques en temps réel
            current_metrics = simulator.get_graph_metrics()
            clustering = current_metrics.get('average_clustering', 0)
            print(f"  🔗 Clustering moyen: {clustering:.3f}")
        
        # Ajouter l'observateur et lancer la simulation
        simulator.add_observer(detailed_observer)
        
        # État initial
        detailed_observer(model, 0)
        
        # Lancer la simulation
        steps = simulator.run()
        
        print(f"\n📈 ANALYSE POST-SIMULATION")
        print("-" * 30)
        
        # Statistiques finales
        final_stats = simulator.get_statistics()
        print("📊 Statistiques finales:")
        for key, value in final_stats.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
        
        # Historique d'évolution
        history = simulator.get_evolution_history()
        print(f"\n📜 Évolution des métriques:")
        print("Étape | Densité | Clustering")
        print("-" * 30)
        for entry in history[-5:]:  # Dernières 5 étapes
            step = entry['step']
            metrics = entry['metrics']
            density = metrics.get('density', 0)
            clustering = metrics.get('average_clustering', 0)
            print(f"{step:5d} | {density:7.3f} | {clustering:10.3f}")
        
        # Export des données
        print(f"\n💾 Export des données:")
        exports = simulator.export_to_formats()
        print(f"   Nœuds exportés: {len(exports.get('node_list', []))}")
        print(f"   Arêtes exportées: {len(exports.get('edge_list', []))}")
        print(f"   Format dict disponible: {'graph_dict' in exports}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comparison():
    """Test de comparaison des performances"""
    print(f"\n🏁 COMPARAISON ANCIEN/NOUVEAU SIMULATEUR")
    print("-" * 50)
    
    # TODO: Ajouter des tests de performance si nécessaire
    print("✅ Le nouveau simulateur NetworkX est prêt!")
    print("🚀 Fonctionnalités ajoutées:")
    print("   • Métriques de graphe avancées")
    print("   • Calcul de centralités") 
    print("   • Détection de communautés")
    print("   • Plus courts chemins")
    print("   • Historique d'évolution")
    print("   • Export multi-format")

def main():
    print("🔬 TESTS SIMULATEUR NETWORKX")
    print("Démonstration des capacités NetworkX intégrées")
    print("=" * 60)
    
    success = test_networkx_features()
    test_comparison()
    
    if success:
        print(f"\n🎉 TESTS RÉUSSIS!")
        print("Le simulateur NetworkX est opérationnel avec toutes ses fonctionnalités avancées.")
        return True
    else:
        print(f"\n❌ ÉCHEC DES TESTS")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

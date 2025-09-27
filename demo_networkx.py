#!/usr/bin/env python3
"""
Démonstration complète du simulateur NetworkX
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.parser import GraphDSLParser
from src.simulator import NetworkXSimulator

def demo_networkx_simulator():
    """Démonstration complète des capacités NetworkX"""
    
    print("🚀 DÉMONSTRATION SIMULATEUR NETWORKX")
    print("=" * 55)
    
    # Créer un graphe plus intéressant
    advanced_dsl = """
types {
    entity Cell {
        attr state: {alive, dead}
        attr age: int
        attr connections: int
    }
    relation Link {
        attr strength: int
        attr type: {strong, weak}
    }
}

graph CellularNetwork {
    config {
        iterations: 5
        step_delay: 0.2
        auto_stop: false
        verbose: true
    }

    entities {
        c1: Cell(state=alive, age=0, connections=3)
        c2: Cell(state=dead, age=1, connections=2)
        c3: Cell(state=alive, age=2, connections=4)
        c4: Cell(state=alive, age=0, connections=2)
        c5: Cell(state=dead, age=3, connections=1)
        c6: Cell(state=alive, age=1, connections=3)
        c7: Cell(state=dead, age=0, connections=2)
        c8: Cell(state=alive, age=2, connections=3)
    }

    relations {
        l1: Link(c1, c2, strength=8, type=strong)
        l2: Link(c1, c3, strength=5, type=weak)
        l3: Link(c2, c4, strength=7, type=strong)
        l4: Link(c3, c4, strength=3, type=weak)
        l5: Link(c3, c5, strength=9, type=strong)
        l6: Link(c4, c6, strength=4, type=weak)
        l7: Link(c5, c6, strength=6, type=strong)
        l8: Link(c5, c7, strength=2, type=weak)
        l9: Link(c6, c7, strength=8, type=strong)
        l10: Link(c6, c8, strength=5, type=weak)
        l11: Link(c7, c8, strength=7, type=strong)
        l12: Link(c1, c8, strength=3, type=weak)
    }

    rules {
        Birth: if neighbor_count(node, state=alive) >= 3 then node.state = alive
        Death: if neighbor_count(node, state=alive) <= 1 then node.state = dead
        Aging: if neighbor_count(node, state=alive) >= 2 then node.age = alive
    }
}
"""
    
    # Parser et créer le simulateur
    parser = GraphDSLParser()
    
    try:
        model = parser.parse_to_model(advanced_dsl)
        simulator = NetworkXSimulator(model)
        
        print("✅ Graphe complexe créé avec 8 nœuds et 12 arêtes")
        
        # Analyse NetworkX pré-simulation
        print(f"\n📊 ANALYSE PRÉ-SIMULATION")
        print("-" * 40)
        
        metrics = simulator.get_graph_metrics()
        print(f"🔢 Nœuds: {metrics['nodes_count']}, Arêtes: {metrics['edges_count']}")
        print(f"🔗 Densité: {metrics['density']:.3f}")
        print(f"📏 Diamètre: {metrics.get('diameter', 'N/A')}")
        print(f"🎯 Clustering moyen: {metrics['average_clustering']:.3f}")
        
        # Top 3 centralités
        centralities = simulator.get_node_centralities()
        if centralities.get('degree'):
            degree_top3 = sorted(centralities['degree'].items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"🏆 Top 3 centralités degré: {degree_top3}")
            
        if centralities.get('betweenness'):
            between_top3 = sorted(centralities['betweenness'].items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"🌉 Top 3 centralités intermédiarité: {between_top3}")
        
        # Communautés
        communities = simulator.analyze_communities()
        if communities:
            print(f"🏘️ {len(communities)} communautés détectées:")
            for i, community in enumerate(communities):
                print(f"   Communauté {i+1}: {community}")
        
        # Paths intéressants
        paths = simulator.find_shortest_paths('c1')
        if 'c1' in paths:
            longest_path = max(paths['c1'].items(), key=lambda x: len(x[1]))
            print(f"🛤️ Plus long chemin depuis c1: c1 → {longest_path[0]} via {longest_path[1]}")
        
        print(f"\n🎮 SIMULATION INTERACTIVE")
        print("-" * 40)
        
        def advanced_observer(graph, step):
            print(f"\n🔄 Étape {step}:")
            
            # Compter les états
            alive_count = sum(1 for node in graph.nodes.values() 
                            if node.properties.get('state') == 'alive')
            dead_count = len(graph.nodes) - alive_count
            
            # Âge moyen (avec conversion sécurisée)
            ages = []
            for node in graph.nodes.values():
                age_val = node.properties.get('age', 0)
                try:
                    ages.append(int(age_val))
                except (ValueError, TypeError):
                    ages.append(0)
            avg_age = sum(ages) / len(ages) if ages else 0
            
            # Connexions moyennes (avec conversion sécurisée)
            connections = []
            for node in graph.nodes.values():
                conn_val = node.properties.get('connections', 0)
                try:
                    connections.append(int(conn_val))
                except (ValueError, TypeError):
                    connections.append(0)
            avg_connections = sum(connections) / len(connections) if connections else 0
            
            print(f"   💚 Vivantes: {alive_count} | 💀 Mortes: {dead_count}")
            print(f"   📅 Âge moyen: {avg_age:.1f} | 🔗 Connexions moy: {avg_connections:.1f}")
            
            # Métriques réseau en temps réel
            current_metrics = simulator.get_graph_metrics()
            print(f"   🌐 Densité: {current_metrics.get('density', 0):.3f} | "
                  f"Clustering: {current_metrics.get('average_clustering', 0):.3f}")
        
        # Ajout de l'observateur avancé
        simulator.add_observer(advanced_observer)
        
        # État initial
        advanced_observer(model, 0)
        
        # Lancement de la simulation
        print(f"\n▶️ Démarrage de la simulation...")
        steps_executed = simulator.run()
        
        print(f"\n📊 RÉSULTATS FINAUX")
        print("-" * 40)
        
        final_stats = simulator.get_statistics()
        print(f"⏱️ Étapes exécutées: {final_stats['steps']}")
        print(f"🔢 Nœuds/Arêtes: {final_stats['nodes']}/{final_stats['edges']}")
        print(f"📏 Diamètre final: {final_stats.get('diameter', 'N/A')}")
        
        # Évolution temporelle
        history = simulator.get_evolution_history()
        if len(history) > 1:
            print(f"\n📈 ÉVOLUTION TEMPORELLE")
            print("-" * 40)
            print("Étape | Densité | Clustering | Diamètre")
            print("-" * 40)
            for entry in history:
                step = entry['step']
                m = entry['metrics']
                print(f"{step:5d} | {m.get('density', 0):7.3f} | {m.get('average_clustering', 0):10.3f} | {m.get('diameter', 'N/A'):8}")
        
        # Export final
        print(f"\n💾 EXPORT DES DONNÉES")
        print("-" * 40)
        exports = simulator.export_to_formats()
        
        if 'basic_info' in exports:
            info = exports['basic_info']
            print(f"✅ Export réussi:")
            print(f"   Nœuds: {info['node_count']}")
            print(f"   Arêtes: {info['edge_count']}")
            print(f"   Formats disponibles: {list(exports.keys())}")
        
        print(f"\n🎯 ANALYSE FINALE NETWORKX")
        print("-" * 40)
        print("✅ Simulation terminée avec succès!")
        print("🔬 Fonctionnalités NetworkX utilisées:")
        print("   • Calcul de métriques topologiques")
        print("   • Analyse de centralités multiples")
        print("   • Détection automatique de communautés")
        print("   • Calcul de plus courts chemins")
        print("   • Historique d'évolution des métriques")
        print("   • Export multi-format des données")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = demo_networkx_simulator()
    
    if success:
        print(f"\n🎉 DÉMONSTRATION RÉUSSIE!")
        print("Le simulateur NetworkX est pleinement opérationnel.")
    else:
        print(f"\n❌ DÉMONSTRATION ÉCHOUÉE")
    
    sys.exit(0 if success else 1)

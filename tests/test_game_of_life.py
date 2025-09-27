#!/usr/bin/env python3
"""
Test du Game of Life sur graphe avec le nouveau DSL
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.parser import GraphDSLParser
from src.simulator import GraphSimulator, SimulationConfig

def test_game_of_life():
    """Test du Game of Life sur graphe"""
    print("🎮 Test du Game of Life sur graphe")
    print("=" * 40)
    
    # Parser le fichier
    parser = GraphDSLParser()
    example_file = os.path.join(os.path.dirname(__file__), 'src', 'examples', 'test_game_of_life.dsl')
    
    try:
        with open(example_file, 'r') as f:
            content = f.read()
        
        model = parser.parse_to_model(content)
        print(f"✅ Graphe parsé: {model}")
        
        # Afficher l'état initial
        print(f"\n📊 État initial:")
        for node_id, node in model.nodes.items():
            state = node.properties.get('state', 'unknown')
            pos = node.properties.get('position', '?')
            neighbors = model.get_neighbors(node_id)
            neighbor_count = len(neighbors)
            live_neighbors = model.count_neighbors_with_state(node_id, 'live')
            print(f"  {node_id}: {state} @ {pos} | {neighbor_count} voisins ({live_neighbors} vivants) -> {neighbors}")
        
        # Tester les règles individuellement
        print(f"\n🔄 Test des règles:")
        from src.semantics import SemanticEngine
        semantic_engine = SemanticEngine(model)
        
        for rule in model.rules:
            print(f"\n📋 Règle {rule.name}:")
            print(f"   Condition: {rule.condition}")
            print(f"   Action: {rule.action}")
            
            # Tester la règle sur chaque nœud
            for node_id, node in model.nodes.items():
                context = semantic_engine.get_node_context(node_id)
                result = semantic_engine.evaluate_condition(rule.condition, context)
                print(f"   {node_id}: {'✓' if result else '✗'}")
        
        # Simulation
        print(f"\n🎮 Simulation:")
        config = SimulationConfig()
        config.max_steps = 3
        config.step_delay = 0
        config.verbose = False
        
        def print_step(graph, step):
            print(f"\n=== Étape {step} ===")
            for node_id, node in graph.nodes.items():
                state = node.properties.get('state', 'unknown')
                live_neighbors = graph.count_neighbors_with_state(node_id, 'live')
                print(f"  {node_id}: {state} ({live_neighbors} voisins vivants)")
        
        simulator = GraphSimulator(model, config)
        simulator.add_observer(print_step)
        
        print_step(model, 0)  # État initial
        steps = simulator.run()
        
        print(f"\n✅ Simulation terminée après {steps} étapes")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_game_of_life()

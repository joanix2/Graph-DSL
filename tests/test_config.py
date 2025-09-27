#!/usr/bin/env python3
"""
Test du DSL amélioré avec configuration des itérations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.parser import GraphDSLParser
from src.simulator import GraphSimulator

def test_config_iterations():
    """Test de la nouvelle fonctionnalité config avec itérations"""
    print("🚀 TEST DSL AMÉLIORÉ - Configuration des itérations")
    print("=" * 55)
    
    # Test avec l'exemple quick_test
    print("\n📝 1. Test avec quick_test.dsl")
    parser = GraphDSLParser()
    example_file = os.path.join(os.path.dirname(__file__), 'src', 'examples', 'quick_test.dsl')
    
    try:
        with open(example_file, 'r') as f:
            content = f.read()
        
        model = parser.parse_to_model(content)
        print(f"✅ Graphe parsé: {model}")
        print(f"⚙️ Configuration: {model.config}")
        
        # Afficher l'état initial
        print(f"\n📊 État initial:")
        for node_id, node in model.nodes.items():
            state = node.properties.get('state', 'unknown')
            live_neighbors = model.count_neighbors_with_state(node_id, 'live')
            print(f"  {node_id}: {state} ({live_neighbors} voisins vivants)")
        
        # Simulation avec la config du DSL
        print(f"\n🎮 Simulation (utilisant config du DSL: {model.config.iterations} itérations):")
        
        def print_step(graph, step):
            print(f"\n--- Étape {step} ---")
            for node_id, node in graph.nodes.items():
                state = node.properties.get('state', 'unknown')
                live_neighbors = graph.count_neighbors_with_state(node_id, 'live')
                print(f"  {node_id}: {state} ({live_neighbors} voisins vivants)")
        
        simulator = GraphSimulator(model)  # Sans config externe, utilise celle du DSL
        simulator.add_observer(print_step)
        
        print_step(model, 0)  # État initial
        steps = simulator.run()
        
        print(f"\n✅ Simulation terminée après {steps} étapes")
        print(f"📈 Config utilisée: max_steps={simulator.config.max_steps}, delay={simulator.config.step_delay}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test avec l'exemple Game of Life configuré
    print(f"\n" + "="*55)
    print("📝 2. Test avec test_game_of_life.dsl (config avancée)")
    
    try:
        example_file2 = os.path.join(os.path.dirname(__file__), 'src', 'examples', 'test_game_of_life.dsl')
        with open(example_file2, 'r') as f:
            content2 = f.read()
        
        model2 = parser.parse_to_model(content2)
        print(f"✅ Graphe parsé: {model2}")
        print(f"⚙️ Configuration avancée:")
        print(f"   • Itérations: {model2.config.iterations}")
        print(f"   • Délai entre étapes: {model2.config.step_delay}s")
        print(f"   • Arrêt automatique: {model2.config.auto_stop}")
        print(f"   • Mode verbose: {model2.config.verbose}")
        
        # Test rapide de la simulation (on va juste simuler 2 étapes)
        from src.simulator import SimulationConfig
        quick_config = SimulationConfig()
        quick_config.max_steps = 2
        quick_config.step_delay = 0
        quick_config.verbose = False
        
        simulator2 = GraphSimulator(model2, quick_config)  # Override avec config rapide
        steps2 = simulator2.run()
        
        print(f"✅ Test rapide terminé après {steps2} étapes")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_parsing_only():
    """Test du parsing seul pour vérifier la grammaire"""
    print(f"\n" + "="*55)
    print("🔍 3. Test de parsing (grammaire)")
    
    parser = GraphDSLParser()
    
    # Test de parsing DSL minimal avec config
    dsl_test = """
types {
    entity Node { attr state: {live, dead} }
    relation Edge {}
}

graph TestConfig {
    config {
        iterations: 42
        step_delay: 1.5
        auto_stop: false
        verbose: true
    }
    
    entities {
        n1: Node(state=live)
    }
    
    rules {
        Test: if neighbor_count(node, state=live) == 0 then node.state = dead
    }
}
"""
    
    try:
        model = parser.parse_to_model(dsl_test)
        print("✅ Parsing DSL inline réussi")
        print(f"⚙️ Config parsée: iterations={model.config.iterations}, delay={model.config.step_delay}")
        print(f"                auto_stop={model.config.auto_stop}, verbose={model.config.verbose}")
        return True
    except Exception as e:
        print(f"❌ Erreur de parsing: {e}")
        return False

def main():
    print("🔧 TEST AMÉLIORATION DSL - Configuration des itérations")
    print("🎯 Nouvelles fonctionnalités:")
    print("   • Bloc config {} dans le DSL")
    print("   • iterations: nombre d'étapes de simulation")  
    print("   • step_delay: délai entre étapes (en secondes)")
    print("   • auto_stop: arrêt automatique si stable")
    print("   • verbose: mode verbeux")
    
    success1 = test_parsing_only()
    success2 = test_config_iterations()
    
    if success1 and success2:
        print(f"\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ Le DSL supporte maintenant la configuration des itérations")
        print("✅ Le simulateur utilise automatiquement la config du DSL")
        print("✅ La grammaire Lark a été étendue correctement")
        return True
    else:
        print(f"\n❌ Certains tests ont échoué")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

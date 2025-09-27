#!/usr/bin/env python3
"""
Test complet du Graph DSL - parsing, simulation et affichage
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.parser import GraphDSLParser
from src.simulator import GraphSimulator, SimulationConfig
from src.semantics import SemanticEngine

def print_graph_state(graph, step):
    """Affiche l'état actuel du graphe"""
    print(f"=== Étape {step} ===")
    for node_id, node in graph.nodes.items():
        state = node.properties.get('state', 'unknown')
        pos = node.properties.get('position', '(?,?)')
        print(f"  {node_id}: {state} @ {pos}")
    print()

def test_complete_pipeline():
    """Test complet : parsing + simulation"""
    print("🚀 Test du pipeline complet Graph DSL")
    print()
    
    # 1. Parser le fichier DSL
    print("📝 1. Parsing du fichier DSL...")
    parser = GraphDSLParser()
    
    example_file = os.path.join(os.path.dirname(__file__), 'src', 'examples', 'graph1.dsl')
    
    try:
        with open(example_file, 'r') as f:
            content = f.read()
        
        model = parser.parse_to_model(content)
        print(f"   ✅ Graphe parsé: {model}")
        print(f"   📊 Types définis: {list(model.types.keys())}")
        print(f"   🔗 Nœuds: {list(model.nodes.keys())}")
        print(f"   📏 Arêtes: {len(model.edges)}")
        print(f"   📋 Règles: {[r.name for r in model.rules]}")
        print()
        
    except Exception as e:
        print(f"   ❌ Erreur de parsing: {e}")
        return False
    
    # 2. Afficher l'état initial
    print("📊 2. État initial du graphe:")
    print_graph_state(model, 0)
    
    # 3. Tester le moteur sémantique
    print("⚙️ 3. Test du moteur sémantique...")
    semantic_engine = SemanticEngine(model)
    
    try:
        # Appliquer les règles une fois
        print("   Application des règles...")
        changed = semantic_engine.apply_rules()
        print(f"   📈 Changements détectés: {changed}")
        print()
        
        # Afficher l'état après application des règles
        if changed:
            print("📊 État après application des règles:")
            print_graph_state(model, 1)
        
    except Exception as e:
        print(f"   ❌ Erreur dans le moteur sémantique: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Tester le simulateur
    print("🎮 4. Test du simulateur...")
    config = SimulationConfig()
    config.max_steps = 5
    config.step_delay = 0
    config.verbose = True
    
    simulator = GraphSimulator(model, config)
    simulator.add_observer(print_graph_state)
    
    try:
        steps = simulator.run()
        print(f"   ✅ Simulation terminée après {steps} étapes")
        
        # Afficher les statistiques
        stats = simulator.get_statistics()
        print(f"   📈 Statistiques: {stats}")
        
    except Exception as e:
        print(f"   ❌ Erreur dans le simulateur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_rule_details():
    """Test détaillé des règles"""
    print("\n🔍 Test détaillé des règles...")
    
    parser = GraphDSLParser()
    example_file = os.path.join(os.path.dirname(__file__), 'src', 'examples', 'graph1.dsl')
    
    with open(example_file, 'r') as f:
        content = f.read()
    
    model = parser.parse_to_model(content)
    
    print("📋 Règles parsées:")
    for rule in model.rules:
        print(f"  - {rule.name}:")
        print(f"    Condition: {rule.condition}")
        print(f"    Action: {rule.action}")
    print()

def main():
    print("=" * 60)
    print("           TEST COMPLET - GRAPH DSL")
    print("=" * 60)
    
    try:
        # Test des détails des règles
        test_rule_details()
        
        # Test du pipeline complet
        success = test_complete_pipeline()
        
        if success:
            print("🎉 Tous les tests sont passés avec succès!")
            print("\n📝 Le Graph DSL fonctionne correctement :")
            print("   ✅ Parsing des types et du graphe")
            print("   ✅ Création du modèle interne")
            print("   ✅ Moteur sémantique fonctionnel")
            print("   ✅ Simulateur opérationnel")
            return True
        else:
            print("❌ Certains tests ont échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

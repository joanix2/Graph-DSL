#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.parser import GraphDSLParser

# Test simple de parsing de la config
dsl_simple = """
types {
    entity Node { attr state: {live, dead} }
    relation Edge {}
}

graph Test {
    config {
        iterations: 42
    }
    
    entities {
        n1: Node(state=live)
    }
    
    rules {
        R: if neighbor_count(node, state=live) == 0 then node.state = dead
    }
}
"""

parser = GraphDSLParser()
try:
    # Juste parser l'arbre syntaxique d'abord
    tree = parser.parse(dsl_simple)
    print("Arbre syntaxique:", tree.pretty())
    print("\n" + "="*50)
    
    # Maintenant transformer
    model = parser.parse_to_model(dsl_simple)
    print("Modèle:", model)
    print("Config:", model.config)
    
except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()

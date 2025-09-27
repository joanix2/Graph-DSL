#!/usr/bin/env python3
"""
Script de test pour le Graph DSL
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser import GraphDSLParser
from model import GraphModel
from simulator import GraphSimulator

def test_parser():
    """Test basique du parser"""
    print("Test du parser...")
    try:
        parser = GraphDSLParser()
        print("✅ Parser initialisé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du parser: {e}")
        return False

def test_model():
    """Test basique du modèle"""
    print("Test du modèle...")
    try:
        graph = GraphModel("test_graph")
        print(f"✅ Modèle créé: {graph}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du modèle: {e}")
        return False

def main():
    print("=== Tests Graph DSL ===")
    
    tests = [
        test_parser,
        test_model
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Résultats: {passed}/{total} tests réussis")
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)


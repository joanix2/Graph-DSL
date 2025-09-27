# Tests du Graph DSL

Ce dossier contient tous les tests pour le système Graph DSL.

## Structure des tests

- `test_parser.py` - Tests du parser DSL
- `test_model.py` - Tests du modèle de données
- `test_simulator.py` - Tests du simulateur de base
- `test_networkx.py` - Tests de l'intégration NetworkX
- `test_semantics.py` - Tests du moteur sémantique
- `test_cli.py` - Tests de l'interface CLI
- `conftest.py` - Configuration partagée pour pytest

## Exécution des tests

```bash
# Tous les tests
python -m pytest tests/

# Tests spécifiques
python -m pytest tests/test_parser.py
python -m pytest tests/test_networkx.py -v

# Avec couverture
python -m pytest tests/ --cov=src/
```

## Tests manuels

```bash
# Test CLI
python cli.py parse src/examples/cellular.dsl -v
python cli.py simulate src/examples/cellular.dsl --steps 10
python cli.py analyze src/examples/cellular.dsl --format json
```

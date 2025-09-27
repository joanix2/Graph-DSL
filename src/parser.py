"""
Parser pour le Graph DSL utilisant Lark
"""

from lark import Lark, Transformer, v_args
from pathlib import Path
import os
from .model import GraphModel, Node, Edge, Rule, TypeDef, AttrDef

class GraphDSLParser:
    def __init__(self):
        grammar_path = Path(__file__).parent.parent / 'grammar' / 'graph_dsl.lark'
        with open(grammar_path, 'r') as f:
            self.parser = Lark(f.read(), start='start', parser='lalr')
    
    def parse(self, text):
        """Parse le texte DSL et retourne l'arbre syntaxique"""
        return self.parser.parse(text)
    
    def parse_file(self, file_path):
        """Parse un fichier DSL"""
        with open(file_path, 'r') as f:
            return self.parse(f.read())
    
    def parse_to_model(self, text):
        """Parse et transforme directement en modèle"""
        tree = self.parse(text)
        transformer = GraphTransformer()
        return transformer.transform(tree)

class GraphTransformer(Transformer):
    """Transforme l'arbre syntaxique en modèle interne"""
    
    def __init__(self):
        super().__init__()
        self.types = {}
        self.current_graph = None
    
    def start(self, children):
        """Point d'entrée : types_block + graph"""
        types_block, graph = children
        # Ajouter les types au graphe
        if graph and hasattr(graph, 'types'):
            graph.types.update(self.types)
        return graph
    
    def types_block(self, children):
        """Traite le bloc types"""
        for type_def in children:
            self.types[type_def.name] = type_def
        return self.types
    
    def type_def(self, children):
        """Définition d'un type (entity ou relation)"""
        # Premier élément est le token du type (entity/relation)
        type_kind = str(children[0])
        name = str(children[1])
        attrs = children[2:] if len(children) > 2 else []
        
        return TypeDef(name, type_kind, attrs)
    
    def attr_def(self, children):
        """Définition d'attribut"""
        name, attr_type = children
        return AttrDef(str(name), attr_type)
    
    def enum_type(self, children):
        """Type énumération"""
        return {'type': 'enum', 'values': [str(child) for child in children]}
    
    def graph(self, children):
        """Définition du graphe"""
        name = children[0]
        self.current_graph = GraphModel(str(name))
        
        # Traiter les blocs (entities, relations, rules)
        for stmt in children[1:]:
            if hasattr(stmt, '__iter__') and not isinstance(stmt, str):
                for item in stmt:
                    if isinstance(item, Node):
                        self.current_graph.add_node(item)
                    elif isinstance(item, Edge):
                        self.current_graph.add_edge(item)
                    elif isinstance(item, Rule):
                        self.current_graph.add_rule(item)
        
        return self.current_graph
    
    def entities_block(self, children):
        """Bloc entités"""
        return children
    
    def entity_inst(self, children):
        """Instance d'entité"""
        instance_name = str(children[0])
        type_name = str(children[1])
        
        params = {}
        # Récupérer les paramètres s'ils existent
        for i in range(2, len(children)):
            param = children[i]
            if isinstance(param, list) and len(param) == 2:
                key, value = param
                params[str(key)] = self._extract_value(value)
        
        return Node(instance_name, params, type_name=type_name)
    
    def relations_block(self, children):
        """Bloc relations"""
        return children
    
    def relation_inst(self, children):
        """Instance de relation"""
        instance_name = str(children[0])
        type_name = str(children[1])
        source = str(children[2])
        target = str(children[3])
        
        params = {}
        # Récupérer les paramètres s'ils existent
        for i in range(4, len(children)):
            param = children[i]
            if isinstance(param, list) and len(param) == 2:
                key, value = param
                params[str(key)] = self._extract_value(value)
        
        return Edge(source, target, params, 
                   relation_name=instance_name, type_name=type_name)
    
    def rules_block(self, children):
        """Bloc règles"""
        return children
    
    def rule(self, children):
        """Définition d'une règle"""
        rule_name = str(children[0])
        condition = children[1]
        action = children[2]
        return Rule(rule_name, condition, action)
    
    def param(self, children):
        """Paramètre key=value"""
        return children
    
    def value(self, children):
        """Valeur (number, string, name, tuple)"""
        return self._extract_value(children[0])
    
    def _extract_value(self, child):
        """Extrait une valeur selon son type"""
        if hasattr(child, 'type'):
            if child.type == 'NUMBER':
                return int(child.value)
            elif child.type == 'ESCAPED_STRING':
                return str(child.value[1:-1])  # Enlever les guillemets
            elif child.type == 'NAME':
                return str(child.value)
        elif isinstance(child, tuple):
            return child
        elif hasattr(child, '__iter__') and len(child) == 2:
            # Tuple (x,y)
            return tuple(child)
        return str(child)
    
    def expr(self, children):
        """Expression de condition (peut être simple ou composée)"""
        if len(children) == 1:
            # Expression simple
            return children[0]
        else:
            # Expression composée (OR, AND)
            return self.simple_expr(children)
    
    def comparator(self, children):
        """Traite le comparateur"""
        return str(children[0]) if children else "=="
    
    def simple_expr(self, children):
        """Expression simple de condition"""
        # neighbor_count(node, state=NAME) comparator NUMBER
        if len(children) >= 3:
            state_value = str(children[0])
            comparator_val = children[1] if isinstance(children[1], str) else "=="
            number = int(children[2])
            
            return {
                'type': 'neighbor_count',
                'target': 'node',
                'state_filter': state_value,
                'comparator': comparator_val,
                'value': number
            }
        else:
            return {
                'type': 'unknown',
                'children': children
            }
    
    def expr_or(self, children):
        """Expression OR"""
        return {
            'type': 'or',
            'left': children[0],
            'right': children[1]
        }
    
    def expr_and(self, children):
        """Expression AND"""
        return {
            'type': 'and',
            'left': children[0],
            'right': children[1]
        }
    
    def action(self, children):
        """Action à exécuter"""
        # node.NAME = NAME
        attribute = str(children[0])
        value = str(children[1])
        
        return {
            'type': 'set_attribute',
            'target': 'node',
            'attribute': attribute,
            'value': value
        }

if __name__ == '__main__':
    parser = GraphDSLParser()
    # Test avec l'exemple
    try:
        example_path = Path(__file__).parent / 'examples' / 'graph1.dsl'
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            model = parser.parse_to_model(content)
            print(f"✅ Parser testé avec succès sur {example_path}")
            print(f"Graphe parsé: {model}")
            print(f"Nœuds: {list(model.nodes.keys())}")
            print(f"Règles: {[r.name for r in model.rules]}")
        else:
            print("✅ Parser initialisé avec succès")
            print("📁 Fichier d'exemple non trouvé pour le test")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


"""
Moteur sémantique pour appliquer les règles au graphe
"""

from .model import GraphModel, Rule, Node
from typing import List, Dict, Any

class SemanticEngine:
    """Moteur pour appliquer les règles sémantiques au graphe"""
    
    def __init__(self, graph_model: GraphModel):
        self.graph = graph_model
    
    def apply_rules(self) -> bool:
        """
        Applique toutes les règles au graphe
        Retourne True si des changements ont eu lieu
        """
        changed = False
        for rule in self.graph.rules:
            if self.apply_rule(rule):
                changed = True
        return changed
    
    def apply_rule(self, rule: Rule) -> bool:
        """
        Applique une règle spécifique
        Retourne True si la règle a provoqué des changements
        """
        print(f"🔄 Application de la règle: {rule.name}")
        changed = False
        
        # Appliquer la règle à tous les nœuds
        for node_id, node in self.graph.nodes.items():
            context = self.get_node_context(node_id)
            
            if self.evaluate_condition(rule.condition, context):
                print(f"  ✓ Condition satisfaite pour le nœud {node_id}")
                self.execute_action(rule.action, context)
                changed = True
            
        return changed
    
    def evaluate_condition(self, condition: Any, context: Dict[str, Any]) -> bool:
        """Évalue une condition dans un contexte donné"""
        if isinstance(condition, dict):
            if condition.get('type') == 'neighbor_count':
                return self._evaluate_neighbor_count_condition(condition, context)
            elif condition.get('type') == 'unknown':
                # Gérer les conditions "unknown" qui contiennent en fait la vraie condition
                children = condition.get('children', [])
                if children and isinstance(children[0], dict):
                    return self.evaluate_condition(children[0], context)
            elif condition.get('type') == 'or':
                left = self.evaluate_condition(condition.get('left'), context)
                right = self.evaluate_condition(condition.get('right'), context)
                return left or right
            elif condition.get('type') == 'and':
                left = self.evaluate_condition(condition.get('left'), context)
                right = self.evaluate_condition(condition.get('right'), context)
                return left and right
        
        return False
    
    def _evaluate_neighbor_count_condition(self, condition: Dict, context: Dict[str, Any]) -> bool:
        """Évalue une condition de type neighbor_count"""
        node = context['node']
        node_id = node.id
        
        # Récupérer les paramètres de la condition
        state_filter = condition.get('state_filter', 'live')
        comparator = condition.get('comparator', '==')
        expected_value = condition.get('value', 0)
        
        # Compter les voisins avec l'état donné
        actual_count = self.graph.count_neighbors_with_state(node_id, state_filter)
        
        # Évaluer selon le comparateur
        if comparator == '==':
            return actual_count == expected_value
        elif comparator == '<':
            return actual_count < expected_value
        elif comparator == '>':
            return actual_count > expected_value
        elif comparator == '<=':
            return actual_count <= expected_value
        elif comparator == '>=':
            return actual_count >= expected_value
        
        return False
    
    def execute_action(self, action: Any, context: Dict[str, Any]):
        """Exécute une action dans un contexte donné"""
        if isinstance(action, dict):
            if action.get('type') == 'set_attribute':
                self._execute_set_attribute_action(action, context)
    
    def _execute_set_attribute_action(self, action: Dict, context: Dict[str, Any]):
        """Exécute une action de type set_attribute"""
        node = context['node']
        attribute = action.get('attribute')
        value = action.get('value')
        
        if attribute and value:
            print(f"    → Mise à jour: {node.id}.{attribute} = {value}")
            self.graph.update_node_property(node.id, attribute, value)
    
    def get_node_context(self, node_id: str) -> Dict[str, Any]:
        """Retourne le contexte d'un nœud (voisins, propriétés, etc.)"""
        node = self.graph.nodes[node_id]
        neighbors = self.graph.get_neighbors(node_id)
        
        return {
            'node': node,
            'neighbors': neighbors,
            'neighbor_count': len(neighbors)
        }


"""
Moteur de simulation pour l'exécution du graphe avec ses règles
"""

import time
from typing import List, Callable, Optional
from .model import GraphModel
from .semantics import SemanticEngine

class SimulationConfig:
    """Configuration de la simulation"""
    
    def __init__(self):
        self.max_steps: int = 100
        self.step_delay: float = 0.1  # secondes
        self.auto_stop_on_stable: bool = True
        self.verbose: bool = True

class GraphSimulator:
    """Simulateur principal pour l'exécution des graphes"""
    
    def __init__(self, graph_model: GraphModel, config: Optional[SimulationConfig] = None):
        self.graph = graph_model
        self.semantic_engine = SemanticEngine(graph_model)
        self.config = config or SimulationConfig()
        self.step_count = 0
        self.history: List[GraphModel] = []
        self.observers: List[Callable] = []
    
    def add_observer(self, observer: Callable):
        """Ajoute un observateur qui sera notifié à chaque étape"""
        self.observers.append(observer)
    
    def notify_observers(self):
        """Notifie tous les observateurs"""
        for observer in self.observers:
            observer(self.graph, self.step_count)
    
    def step(self) -> bool:
        """
        Exécute une étape de simulation
        Retourne True si des changements ont eu lieu
        """
        if self.config.verbose:
            print(f"Étape {self.step_count + 1}")
        
        # Sauvegarder l'état actuel
        # TODO: Implémenter la copie profonde du graphe
        # self.history.append(copy.deepcopy(self.graph))
        
        # Appliquer les règles
        changed = self.semantic_engine.apply_rules()
        
        self.step_count += 1
        self.notify_observers()
        
        if self.config.step_delay > 0:
            time.sleep(self.config.step_delay)
        
        return changed
    
    def run(self) -> int:
        """
        Lance la simulation complète
        Retourne le nombre d'étapes exécutées
        """
        if self.config.verbose:
            print(f"Démarrage de la simulation de '{self.graph.name}'...")
        
        for i in range(self.config.max_steps):
            changed = self.step()
            
            # Arrêt automatique si plus de changements
            if self.config.auto_stop_on_stable and not changed:
                if self.config.verbose:
                    print(f"Simulation stabilisée après {self.step_count} étapes")
                break
        else:
            if self.config.verbose:
                print(f"Simulation terminée après {self.config.max_steps} étapes maximum")
        
        return self.step_count
    
    def reset(self):
        """Remet la simulation à zéro"""
        self.step_count = 0
        self.history.clear()
        # TODO: Restaurer l'état initial du graphe
    
    def get_statistics(self) -> dict:
        """Retourne des statistiques sur la simulation"""
        return {
            'steps': self.step_count,
            'nodes': len(self.graph.nodes),
            'edges': len(self.graph.edges),
            'rules': len(self.graph.rules)
        }

if __name__ == '__main__':
    # Test basique
    print("Module simulator initialisé")


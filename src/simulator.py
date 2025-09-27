"""
Moteur de simulation pour l'exécution du graphe avec ses règles
Utilise NetworkX comme moteur sous-jacent pour les calculs de graphe
"""

import time
import copy
import networkx as nx
from typing import List, Callable, Optional, Dict, Any
from .model import GraphModel
from .semantics import SemanticEngine

class SimulationConfig:
    """Configuration de la simulation"""
    
    def __init__(self):
        self.max_steps: int = 100
        self.step_delay: float = 0.1  # secondes
        self.auto_stop_on_stable: bool = True
        self.verbose: bool = True

class NetworkXSimulator:
    """Simulateur avancé utilisant NetworkX pour les calculs de graphe"""
    
    def __init__(self, graph_model: GraphModel, config: Optional[SimulationConfig] = None):
        self.graph_model = graph_model
        self.nx_graph = graph_model.graph.copy()  # Copie du graphe NetworkX
        self.semantic_engine = SemanticEngine(graph_model)
        
        # Configuration
        if config is None:
            config = SimulationConfig()
            config.max_steps = graph_model.config.iterations
            config.step_delay = graph_model.config.step_delay
            config.auto_stop_on_stable = graph_model.config.auto_stop
            config.verbose = graph_model.config.verbose
        
        self.config = config
        self.step_count = 0
        self.history: List[Dict[str, Any]] = []  # Historique des états
        self.observers: List[Callable] = []
        
        # Métadonnées NetworkX
        self.initial_state = self._save_graph_state()
    
    def _save_graph_state(self) -> Dict[str, Any]:
        """Sauvegarde l'état actuel du graphe"""
        state = {}
        for node_id in self.nx_graph.nodes():
            state[node_id] = dict(self.nx_graph.nodes[node_id])
        return state
    
    def _restore_graph_state(self, state: Dict[str, Any]):
        """Restaure un état du graphe"""
        for node_id, attributes in state.items():
            if node_id in self.nx_graph.nodes():
                self.nx_graph.nodes[node_id].update(attributes)
                # Synchroniser avec le modèle
                if node_id in self.graph_model.nodes:
                    self.graph_model.nodes[node_id].properties.update(attributes)
    
    def get_graph_metrics(self) -> Dict[str, Any]:
        """Calcule des métriques avancées du graphe avec NetworkX"""
        metrics = {
            'nodes_count': self.nx_graph.number_of_nodes(),
            'edges_count': self.nx_graph.number_of_edges(),
            'density': nx.density(self.nx_graph),
            'is_connected': nx.is_connected(self.nx_graph) if self.nx_graph.number_of_nodes() > 0 else False,
        }
        
        if self.nx_graph.number_of_nodes() > 0:
            try:
                metrics['diameter'] = nx.diameter(self.nx_graph) if nx.is_connected(self.nx_graph) else None
                metrics['radius'] = nx.radius(self.nx_graph) if nx.is_connected(self.nx_graph) else None
                metrics['average_clustering'] = nx.average_clustering(self.nx_graph)
                metrics['average_shortest_path'] = nx.average_shortest_path_length(self.nx_graph) if nx.is_connected(self.nx_graph) else None
            except (nx.NetworkXError, ZeroDivisionError):
                pass
        
        return metrics
    
    def get_node_centralities(self) -> Dict[str, Dict[str, float]]:
        """Calcule les centralités des nœuds avec NetworkX"""
        centralities = {}
        
        if self.nx_graph.number_of_nodes() > 0:
            try:
                centralities['degree'] = nx.degree_centrality(self.nx_graph)
                centralities['closeness'] = nx.closeness_centrality(self.nx_graph)
                centralities['betweenness'] = nx.betweenness_centrality(self.nx_graph)
                centralities['eigenvector'] = nx.eigenvector_centrality(self.nx_graph, max_iter=1000)
            except (nx.NetworkXError, nx.PowerIterationFailedConvergence):
                if self.config.verbose:
                    print("⚠️ Certaines centralités n'ont pas pu être calculées")
        
        return centralities
    
    def analyze_communities(self) -> List[List[str]]:
        """Détecte les communautés dans le graphe"""
        try:
            communities = list(nx.community.greedy_modularity_communities(self.nx_graph))
            return [list(community) for community in communities]
        except (nx.NetworkXError, ImportError):
            return []
    
    def find_shortest_paths(self, source: str = None) -> Dict[str, Dict[str, List[str]]]:
        """Calcule les plus courts chemins"""
        paths = {}
        
        if source:
            if source in self.nx_graph.nodes():
                try:
                    paths[source] = dict(nx.single_source_shortest_path(self.nx_graph, source))
                except nx.NetworkXError:
                    pass
        else:
            try:
                paths = dict(nx.all_pairs_shortest_path(self.nx_graph))
            except nx.NetworkXError:
                pass
        
        return paths
    
    def add_observer(self, observer: Callable):
        """Ajoute un observateur qui sera notifié à chaque étape"""
        self.observers.append(observer)
    
    def notify_observers(self):
        """Notifie tous les observateurs"""
        for observer in self.observers:
            observer(self.graph_model, self.step_count)
    
    def step(self) -> bool:
        """
        Exécute une étape de simulation avec NetworkX
        Retourne True si des changements ont eu lieu
        """
        if self.config.verbose:
            print(f"Étape {self.step_count + 1}")
        
        # Sauvegarder l'état actuel
        current_state = self._save_graph_state()
        self.history.append({
            'step': self.step_count,
            'state': current_state,
            'metrics': self.get_graph_metrics()
        })
        
        # Appliquer les règles
        changed = self.semantic_engine.apply_rules()
        
        # Synchroniser les changements avec NetworkX
        if changed:
            self._sync_model_to_nx()
        
        self.step_count += 1
        self.notify_observers()
        
        if self.config.step_delay > 0:
            time.sleep(self.config.step_delay)
        
        return changed
    
    def _sync_model_to_nx(self):
        """Synchronise les changements du modèle vers NetworkX"""
        for node_id, node in self.graph_model.nodes.items():
            if node_id in self.nx_graph.nodes():
                # Mettre à jour les attributs du nœud dans NetworkX
                self.nx_graph.nodes[node_id].update(node.properties)
    
    def run(self) -> int:
        """
        Lance la simulation complète avec analyse NetworkX
        Retourne le nombre d'étapes exécutées
        """
        if self.config.verbose:
            print(f"🚀 Démarrage de la simulation de '{self.graph_model.name}'...")
            print(f"📊 État initial: {self.get_graph_metrics()}")
        
        for i in range(self.config.max_steps):
            changed = self.step()
            
            # Afficher les métriques si verbose
            if self.config.verbose and changed:
                metrics = self.get_graph_metrics()
                print(f"📈 Métriques étape {self.step_count}: densité={metrics.get('density', 0):.3f}, "
                      f"clustering={metrics.get('average_clustering', 0):.3f}")
            
            # Arrêt automatique si plus de changements
            if self.config.auto_stop_on_stable and not changed:
                if self.config.verbose:
                    print(f"🔒 Simulation stabilisée après {self.step_count} étapes")
                break
        else:
            if self.config.verbose:
                print(f"⏱️ Simulation terminée après {self.config.max_steps} étapes maximum")
        
        # Afficher le résumé final
        if self.config.verbose:
            self._print_final_summary()
        
        return self.step_count
    
    def _print_final_summary(self):
        """Affiche un résumé final avec les analyses NetworkX"""
        print(f"\n📋 RÉSUMÉ FINAL - {self.graph_model.name}")
        print("=" * 40)
        
        # Métriques finales
        final_metrics = self.get_graph_metrics()
        print("📊 Métriques finales:")
        for metric, value in final_metrics.items():
            if value is not None:
                if isinstance(value, float):
                    print(f"   {metric}: {value:.3f}")
                else:
                    print(f"   {metric}: {value}")
        
        # Centralités
        centralities = self.get_node_centralities()
        if centralities.get('degree'):
            print("\n🎯 Centralités (top 3):")
            for centrality_type, values in centralities.items():
                top_nodes = sorted(values.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"   {centrality_type}: {top_nodes}")
        
        # Communautés
        communities = self.analyze_communities()
        if communities:
            print(f"\n🏘️ Communautés détectées: {len(communities)}")
            for i, community in enumerate(communities):
                print(f"   Communauté {i+1}: {community}")
        
        print("=" * 40)
    
    def reset(self):
        """Remet la simulation à zéro"""
        self.step_count = 0
        self.history.clear()
        # Restaurer l'état initial
        self._restore_graph_state(self.initial_state)
    
    def get_statistics(self) -> dict:
        """Retourne des statistiques complètes sur la simulation"""
        base_stats = {
            'steps': self.step_count,
            'nodes': len(self.graph_model.nodes),
            'edges': len(self.graph_model.edges),
            'rules': len(self.graph_model.rules)
        }
        
        # Ajouter les métriques NetworkX
        nx_metrics = self.get_graph_metrics()
        base_stats.update(nx_metrics)
        
        return base_stats
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Retourne l'historique complet de l'évolution"""
        return self.history
    
    def export_to_formats(self) -> Dict[str, Any]:
        """Exporte le graphe vers différents formats NetworkX"""
        exports = {}
        
        try:
            # Export vers différents formats
            try:
                adj_matrix = nx.adjacency_matrix(self.nx_graph)
                exports['adjacency_matrix'] = adj_matrix.todense().tolist()
            except Exception:
                exports['adjacency_matrix'] = None
                
            exports['edge_list'] = list(self.nx_graph.edges(data=True))
            exports['node_list'] = list(self.nx_graph.nodes(data=True))
            exports['graph_dict'] = nx.node_link_data(self.nx_graph)
            
            # Informations de base
            exports['basic_info'] = {
                'nodes': list(self.nx_graph.nodes()),
                'edges': list(self.nx_graph.edges()),
                'node_count': self.nx_graph.number_of_nodes(),
                'edge_count': self.nx_graph.number_of_edges()
            }
            
        except Exception as e:
            if self.config.verbose:
                print(f"⚠️ Erreur d'export partielle: {e}")
            exports['error'] = str(e)
        
        return exports


# Alias pour compatibilité avec l'ancienne interface
class GraphSimulator(NetworkXSimulator):
    """Alias pour maintenir la compatibilité"""
    pass

if __name__ == '__main__':
    # Test basique
    print("Module simulator initialisé")


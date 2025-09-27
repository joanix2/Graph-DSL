#!/usr/bin/env python3
"""
Interface en ligne de commande pour le Graph DSL
"""

import click
import os
import sys
from pathlib import Path

# Ajouter le module src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.parser import GraphDSLParser
from src.simulator import NetworkXSimulator, SimulationConfig
from src.model import GraphModel

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🚀 Graph DSL - Interface en ligne de commande
    
    Un langage spécifique au domaine (DSL) pour définir et simuler des graphes
    avec des règles d'évolution utilisant NetworkX.
    """
    pass

@cli.command()
@click.argument('dsl_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--verbose', '-v', is_flag=True, help='Mode verbeux')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Fichier de sortie pour les résultats')
def parse(dsl_file, verbose, output):
    """
    📝 Parse un fichier DSL et affiche la structure du graphe
    
    DSL_FILE: Chemin vers le fichier .dsl à parser
    """
    try:
        parser = GraphDSLParser()
        
        if verbose:
            click.echo(f"🔍 Parsing du fichier: {dsl_file}")
        
        # Lire et parser le fichier
        content = dsl_file.read_text(encoding='utf-8')
        model = parser.parse_to_model(content)
        
        # Afficher les informations du graphe
        click.echo(f"\n📊 GRAPHE PARSÉ: {model.name}")
        click.echo("=" * 40)
        click.echo(f"🔢 Nœuds: {len(model.nodes)}")
        click.echo(f"🔗 Arêtes: {len(model.edges)}")
        click.echo(f"📋 Règles: {len(model.rules)}")
        click.echo(f"🏷️ Types: {len(model.types)}")
        
        # Configuration
        if model.config:
            click.echo(f"\n⚙️ CONFIGURATION:")
            click.echo(f"   Itérations: {model.config.iterations}")
            click.echo(f"   Délai: {model.config.step_delay}s")
            click.echo(f"   Arrêt automatique: {model.config.auto_stop}")
            click.echo(f"   Mode verbeux: {model.config.verbose}")
        
        # Détails des nœuds
        if verbose:
            click.echo(f"\n🎯 NŒUDS:")
            for node_id, node in model.nodes.items():
                props = ', '.join(f"{k}={v}" for k, v in node.properties.items())
                click.echo(f"   {node_id}: {props}")
        
        # Détails des règles
        click.echo(f"\n📜 RÈGLES:")
        for rule in model.rules:
            click.echo(f"   {rule.name}: {rule.condition} → {rule.action}")
        
        # Sauvegarder si demandé
        if output:
            import json
            result = {
                'name': model.name,
                'nodes': {nid: n.properties for nid, n in model.nodes.items()},
                'edges': len(model.edges),
                'rules': [{'name': r.name, 'condition': str(r.condition), 'action': str(r.action)} for r in model.rules],
                'config': {
                    'iterations': model.config.iterations,
                    'step_delay': model.config.step_delay,
                    'auto_stop': model.config.auto_stop,
                    'verbose': model.config.verbose
                }
            }
            
            output.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            click.echo(f"\n💾 Résultats sauvegardés dans: {output}")
        
        click.echo(f"\n✅ Parsing réussi!")
        
    except Exception as e:
        click.echo(f"❌ Erreur lors du parsing: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)

@cli.command()
@click.argument('dsl_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--steps', '-s', type=int, help='Nombre d\'étapes de simulation (override la config DSL)')
@click.option('--delay', '-d', type=float, help='Délai entre étapes en secondes (override la config DSL)')
@click.option('--no-auto-stop', is_flag=True, help='Désactive l\'arrêt automatique')
@click.option('--quiet', '-q', is_flag=True, help='Mode silencieux')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Fichier de sortie pour les résultats')
@click.option('--export-format', type=click.Choice(['json', 'csv', 'networkx']), default='json', help='Format d\'export')
def simulate(dsl_file, steps, delay, no_auto_stop, quiet, output, export_format):
    """
    🎮 Simule l'évolution d'un graphe DSL
    
    DSL_FILE: Chemin vers le fichier .dsl à simuler
    """
    try:
        parser = GraphDSLParser()
        
        if not quiet:
            click.echo(f"🚀 Simulation du graphe: {dsl_file}")
        
        # Parser le fichier
        content = dsl_file.read_text(encoding='utf-8')
        model = parser.parse_to_model(content)
        
        # Configuration de simulation
        config = None
        if any([steps, delay, no_auto_stop, quiet]):
            config = SimulationConfig()
            config.max_steps = steps or model.config.iterations
            config.step_delay = delay if delay is not None else model.config.step_delay
            config.auto_stop_on_stable = not no_auto_stop and model.config.auto_stop
            config.verbose = not quiet and model.config.verbose
        
        # Créer le simulateur
        simulator = NetworkXSimulator(model, config)
        
        # Observer pour afficher les étapes
        def step_observer(graph, step):
            if not quiet:
                alive_count = sum(1 for node in graph.nodes.values() 
                                if node.properties.get('state') in ['alive', 'active', 'live'])
                click.echo(f"Étape {step}: {alive_count} nœuds actifs")
        
        if not quiet:
            simulator.add_observer(step_observer)
        
        # Lancer la simulation
        if not quiet:
            click.echo(f"▶️ Démarrage...")
        
        steps_executed = simulator.run()
        
        # Résultats
        stats = simulator.get_statistics()
        metrics = simulator.get_graph_metrics()
        
        if not quiet:
            click.echo(f"\n📊 RÉSULTATS:")
            click.echo(f"   Étapes exécutées: {steps_executed}")
            click.echo(f"   Densité finale: {metrics.get('density', 0):.3f}")
            click.echo(f"   Clustering moyen: {metrics.get('average_clustering', 0):.3f}")
            click.echo(f"   Graphe connecté: {metrics.get('is_connected', False)}")
        
        # Export des résultats
        if output:
            export_data = {
                'simulation': {
                    'steps': steps_executed,
                    'final_state': {nid: n.properties for nid, n in model.nodes.items()},
                    'metrics': metrics,
                    'statistics': stats
                },
                'history': simulator.get_evolution_history(),
                'exports': simulator.export_to_formats()
            }
            
            if export_format == 'json':
                import json
                output.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))
            elif export_format == 'csv':
                # Export CSV simplifié
                import csv
                with open(output, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['step', 'density', 'clustering', 'connected'])
                    for entry in export_data['history']:
                        m = entry['metrics']
                        writer.writerow([
                            entry['step'],
                            m.get('density', 0),
                            m.get('average_clustering', 0),
                            m.get('is_connected', False)
                        ])
            
            if not quiet:
                click.echo(f"💾 Résultats exportés vers: {output}")
        
        click.echo(f"✅ Simulation terminée!")
        
    except Exception as e:
        click.echo(f"❌ Erreur lors de la simulation: {e}", err=True)
        if not quiet:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)

@cli.command()
@click.argument('dsl_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--format', 'output_format', type=click.Choice(['text', 'json', 'dot', 'graphml']), 
              default='text', help='Format d\'analyse')
def analyze(dsl_file, output_format):
    """
    🔬 Analyse les propriétés NetworkX d'un graphe DSL
    
    DSL_FILE: Chemin vers le fichier .dsl à analyser
    """
    try:
        parser = GraphDSLParser()
        
        click.echo(f"🔬 Analyse NetworkX: {dsl_file}")
        
        # Parser et créer simulateur
        content = dsl_file.read_text(encoding='utf-8')
        model = parser.parse_to_model(content)
        simulator = NetworkXSimulator(model)
        
        # Métriques de base
        metrics = simulator.get_graph_metrics()
        centralities = simulator.get_node_centralities()
        communities = simulator.analyze_communities()
        
        if output_format == 'text':
            click.echo(f"\n📊 MÉTRIQUES DU GRAPHE:")
            click.echo("=" * 30)
            for metric, value in metrics.items():
                if value is not None:
                    if isinstance(value, float):
                        click.echo(f"{metric}: {value:.3f}")
                    else:
                        click.echo(f"{metric}: {value}")
            
            click.echo(f"\n🎯 CENTRALITÉS (top 3):")
            for centrality_type, values in centralities.items():
                if values:
                    top3 = sorted(values.items(), key=lambda x: x[1], reverse=True)[:3]
                    click.echo(f"{centrality_type}:")
                    for node, score in top3:
                        click.echo(f"  {node}: {score:.3f}")
            
            if communities:
                click.echo(f"\n🏘️ COMMUNAUTÉS ({len(communities)}):")
                for i, community in enumerate(communities):
                    click.echo(f"  Communauté {i+1}: {community}")
        
        elif output_format == 'json':
            import json
            result = {
                'metrics': metrics,
                'centralities': centralities,
                'communities': [list(c) for c in communities]
            }
            click.echo(json.dumps(result, indent=2))
        
        elif output_format == 'dot':
            # Export format DOT pour Graphviz
            try:
                import networkx as nx
                dot_data = nx.nx_pydot.to_pydot(simulator.nx_graph).to_string()
                click.echo(dot_data)
            except ImportError:
                click.echo("❌ Format DOT nécessite pydot: pip install pydot", err=True)
                sys.exit(1)
            except Exception as e:
                click.echo(f"❌ Erreur lors de l'export DOT: {e}", err=True)
                sys.exit(1)
        
        elif output_format == 'graphml':
            # Export GraphML
            try:
                import networkx as nx
                import io
                buffer = io.StringIO()
                nx.write_graphml(simulator.nx_graph, buffer)
                click.echo(buffer.getvalue())
            except ImportError:
                click.echo("❌ Format GraphML nécessite lxml: pip install lxml", err=True)
                sys.exit(1)
            except Exception as e:
                click.echo(f"❌ Erreur lors de l'export GraphML: {e}", err=True)
                sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Erreur lors de l'analyse: {e}", err=True)
        sys.exit(1)

@cli.command()
def examples():
    """
    📚 Affiche des exemples de fichiers DSL
    """
    click.echo("📚 EXEMPLES DE FICHIERS DSL")
    click.echo("=" * 40)
    
    examples_dir = Path(__file__).parent / 'src' / 'examples'
    
    if examples_dir.exists():
        for example_file in examples_dir.glob('*.dsl'):
            click.echo(f"\n📄 {example_file.name}:")
            click.echo("-" * 20)
            content = example_file.read_text(encoding='utf-8')
            # Afficher les premières lignes
            lines = content.split('\n')[:15]
            for line in lines:
                click.echo(f"  {line}")
            if len(content.split('\n')) > 15:
                click.echo("  ...")
    else:
        click.echo("❌ Aucun exemple trouvé")

@cli.command()
@click.option('--port', '-p', type=int, default=8080, help='Port pour le serveur web')
def serve(port):
    """
    🌐 Lance un serveur web pour l'interface graphique (TODO)
    """
    click.echo(f"🌐 Serveur web pas encore implémenté")
    click.echo(f"   Port prévu: {port}")
    click.echo(f"   TODO: Interface web pour visualiser et simuler les graphes")

if __name__ == '__main__':
    cli()

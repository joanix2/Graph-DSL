"""
Tests pour l'interface CLI Graph DSL
"""

import pytest
import json
from pathlib import Path
from click.testing import CliRunner
from cli import cli

class TestCLI:
    
    def setup_method(self):
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test aide générale de la CLI"""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'Graph DSL' in result.output
        assert 'parse' in result.output
        assert 'simulate' in result.output
        assert 'analyze' in result.output
    
    def test_parse_command_help(self):
        """Test aide pour la commande parse"""
        result = self.runner.invoke(cli, ['parse', '--help'])
        
        assert result.exit_code == 0
        assert 'Parse un fichier DSL' in result.output
        assert '--verbose' in result.output
        assert '--output' in result.output
    
    def test_parse_nonexistent_file(self):
        """Test parse d'un fichier inexistant"""
        result = self.runner.invoke(cli, ['parse', 'nonexistent.dsl'])
        
        assert result.exit_code != 0
    
    def test_parse_valid_file(self, tmp_dsl_file):
        """Test parse d'un fichier DSL valide"""
        result = self.runner.invoke(cli, ['parse', str(tmp_dsl_file)])
        
        assert result.exit_code == 0
        assert 'GRAPHE PARSÉ' in result.output
        assert 'CellularTest' in result.output
        assert 'Nœuds: 3' in result.output
        assert 'Arêtes: 3' in result.output
        assert 'Règles: 2' in result.output
    
    def test_parse_with_verbose(self, tmp_dsl_file):
        """Test parse en mode verbeux"""
        result = self.runner.invoke(cli, ['parse', str(tmp_dsl_file), '--verbose'])
        
        assert result.exit_code == 0
        assert 'Parsing du fichier' in result.output
        assert 'NŒUDS:' in result.output
        assert 'cell1:' in result.output
    
    def test_parse_with_output(self, tmp_dsl_file, tmp_path):
        """Test parse avec sortie vers fichier"""
        output_file = tmp_path / "output.json"
        
        result = self.runner.invoke(cli, [
            'parse', str(tmp_dsl_file), 
            '--output', str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Vérifier le contenu du fichier de sortie
        data = json.loads(output_file.read_text())
        assert 'name' in data
        assert data['name'] == 'CellularTest'
        assert 'nodes' in data
        assert 'config' in data
    
    def test_simulate_command_help(self):
        """Test aide pour la commande simulate"""
        result = self.runner.invoke(cli, ['simulate', '--help'])
        
        assert result.exit_code == 0
        assert 'Simule l\'évolution' in result.output
        assert '--steps' in result.output
        assert '--delay' in result.output
    
    def test_simulate_valid_file(self, tmp_dsl_file):
        """Test simulation d'un fichier DSL valide"""
        result = self.runner.invoke(cli, [
            'simulate', str(tmp_dsl_file), 
            '--steps', '3', '--quiet'
        ])
        
        assert result.exit_code == 0
        assert 'Simulation terminée' in result.output
    
    def test_simulate_with_custom_steps(self, tmp_dsl_file):
        """Test simulation avec nombre d'étapes personnalisé"""
        result = self.runner.invoke(cli, [
            'simulate', str(tmp_dsl_file),
            '--steps', '2', '--delay', '0'
        ])
        
        assert result.exit_code == 0
        assert 'Étape' in result.output
        assert 'RÉSULTATS:' in result.output
    
    def test_simulate_with_output(self, tmp_dsl_file, tmp_path):
        """Test simulation avec export"""
        output_file = tmp_path / "simulation.json"
        
        result = self.runner.invoke(cli, [
            'simulate', str(tmp_dsl_file),
            '--steps', '2', '--quiet',
            '--output', str(output_file),
            '--export-format', 'json'
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Vérifier le contenu
        data = json.loads(output_file.read_text())
        assert 'simulation' in data
        assert 'history' in data
    
    def test_simulate_csv_export(self, tmp_dsl_file, tmp_path):
        """Test export CSV"""
        output_file = tmp_path / "simulation.csv"
        
        result = self.runner.invoke(cli, [
            'simulate', str(tmp_dsl_file),
            '--steps', '2', '--quiet',
            '--output', str(output_file),
            '--export-format', 'csv'
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Vérifier que c'est bien du CSV
        content = output_file.read_text()
        assert 'step,density,clustering,connected' in content
    
    def test_analyze_command_help(self):
        """Test aide pour la commande analyze"""
        result = self.runner.invoke(cli, ['analyze', '--help'])
        
        assert result.exit_code == 0
        assert 'Analyse les propriétés NetworkX' in result.output
        assert '--format' in result.output
    
    def test_analyze_text_format(self, tmp_dsl_file):
        """Test analyse en format texte"""
        result = self.runner.invoke(cli, [
            'analyze', str(tmp_dsl_file),
            '--format', 'text'
        ])
        
        assert result.exit_code == 0
        assert 'MÉTRIQUES DU GRAPHE' in result.output
        assert 'CENTRALITÉS' in result.output
        assert 'density:' in result.output
    
    def test_analyze_json_format(self, tmp_dsl_file):
        """Test analyse en format JSON"""
        result = self.runner.invoke(cli, [
            'analyze', str(tmp_dsl_file),
            '--format', 'json'
        ])
        
        assert result.exit_code == 0
        
        # Vérifier que la sortie est du JSON valide
        try:
            data = json.loads(result.output.strip())
            assert 'metrics' in data
            assert 'centralities' in data
            assert 'communities' in data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
    
    def test_examples_command(self):
        """Test commande examples"""
        result = self.runner.invoke(cli, ['examples'])
        
        assert result.exit_code == 0
        assert 'EXEMPLES DE FICHIERS DSL' in result.output
    
    def test_serve_command(self):
        """Test commande serve (TODO)"""
        result = self.runner.invoke(cli, ['serve', '--port', '9000'])
        
        assert result.exit_code == 0
        assert 'pas encore implémenté' in result.output
        assert '9000' in result.output
    
    def test_version_option(self):
        """Test option --version"""
        result = self.runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert '1.0.0' in result.output
    
    def test_invalid_dsl_file(self, tmp_path):
        """Test avec fichier DSL invalide"""
        invalid_file = tmp_path / "invalid.dsl"
        invalid_file.write_text("invalid dsl content")
        
        result = self.runner.invoke(cli, ['parse', str(invalid_file)])
        
        assert result.exit_code != 0
        assert 'Erreur lors du parsing' in result.output
    
    def test_parse_error_verbose(self, tmp_path):
        """Test erreur de parsing en mode verbose"""
        invalid_file = tmp_path / "invalid.dsl"
        invalid_file.write_text("graph { invalid syntax }")
        
        result = self.runner.invoke(cli, [
            'parse', str(invalid_file), '--verbose'
        ])
        
        assert result.exit_code != 0
        assert 'Erreur lors du parsing' in result.output
        # En mode verbose, devrait afficher la stack trace
    
    def test_analyze_dot_format(self, tmp_dsl_file):
        """Test analyse en format DOT"""
        result = self.runner.invoke(cli, [
            'analyze', str(tmp_dsl_file),
            '--format', 'dot'
        ])
        
        assert result.exit_code == 0
        # Format DOT contient généralement 'digraph' ou 'graph'
        assert ('digraph' in result.output) or ('graph' in result.output)
    
    def test_analyze_graphml_format(self, tmp_dsl_file):
        """Test analyse en format GraphML"""
        result = self.runner.invoke(cli, [
            'analyze', str(tmp_dsl_file),
            '--format', 'graphml'
        ])
        
        assert result.exit_code == 0
        # Format GraphML contient du XML
        assert '<?xml' in result.output
        assert 'graphml' in result.output
    
    def test_simulate_no_auto_stop(self, tmp_dsl_file):
        """Test simulation sans arrêt automatique"""
        result = self.runner.invoke(cli, [
            'simulate', str(tmp_dsl_file),
            '--steps', '2',
            '--no-auto-stop',
            '--quiet'
        ])
        
        assert result.exit_code == 0
        assert 'Simulation terminée' in result.output

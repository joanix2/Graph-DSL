"""
Configuration partagée pour pytest
"""

import pytest
import os
import sys
from pathlib import Path

# Ajouter le src au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

@pytest.fixture
def sample_dsl_content():
    """Contenu DSL d'exemple pour les tests"""
    return """
types {
    entity Node {
        attr state: string
        attr energy: int
    }
}

graph CellularTest {
    config {
        iterations 5
        step_delay 0.1
        auto_stop false
        verbose true
    }

    entities {
        cell1: Node(state=alive, energy=10)
        cell2: Node(state=dead, energy=0) 
        cell3: Node(state=alive, energy=8)
    }

    relations {
        e1: Edge(cell1, cell2)
        e2: Edge(cell2, cell3)
        e3: Edge(cell3, cell1)
    }

    rules {
        birth: if energy > 5 then state = "alive"
        death: if energy < 2 then state = "dead"
    }
}
"""

@pytest.fixture
def tmp_dsl_file(tmp_path, sample_dsl_content):
    """Fichier DSL temporaire pour les tests"""
    dsl_file = tmp_path / "test.dsl"
    dsl_file.write_text(sample_dsl_content)
    return dsl_file

@pytest.fixture
def simple_graph_dsl():
    """DSL simple pour tests rapides"""
    return """
types {
    entity Cell {
        attr alive: {true, false}
    }
}

graph SimpleTest {
    config {
        iterations 3
        step_delay 0
        verbose false
    }

    entities {
        a: Cell(alive=true)
        b: Cell(alive=false)
    }
    
    relations {
        r1: Edge(a, b)
    }

    rules {
        toggle: if alive == true then alive = false
    }
}
"""

types {
    entity Cell {
        attr state: {alive, dead}
        attr age: int
        attr connections: int
    }
    relation Link {
        attr strength: int
        attr type: {strong, weak}
    }
}

rules LifeRules {
    Birth: if neighbor_count(node, state=alive) >= 3 then node.state = alive
    Death: if neighbor_count(node, state=alive) <= 1 then node.state = dead
    Aging: if neighbor_count(node, state=alive) >= 2 then node.age = node.age + 1
}

graph CellularNetwork {
    entities {
        c1: Cell(state=alive, age=0, connections=3)
        c2: Cell(state=dead, age=1, connections=2)
        c3: Cell(state=alive, age=2, connections=4)
        c4: Cell(state=alive, age=0, connections=2)
    }

    relations {
        l1: Link(c1, c2, strength=8, type=strong)
        l2: Link(c1, c3, strength=5, type=weak)
        l3: Link(c2, c4, strength=7, type=strong)
    }
}

render CellularNetworkRender {
    entity Cell {
        color: if state == alive then "green" else "gray"
        text:  "age=" + age
        shape: "circle"
    }

    relation Link {
        color: if type == strong then "red" else "blue"
        width: strength / 2
        text: "s=" + strength
    }
}

system LifeSimulation {
    config {
        iterations: 5
        step_delay: 0.2
        auto_stop: false
        verbose: true
    }
    graph : CellularNetwork
    rules : LifeRules
    render: CellularNetworkRender
}

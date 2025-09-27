types {
    entity Node {
        attr position: (int, int)
        attr state: {live, dead}
    }

    relation Edge {
        attr color: string
    }
}

graph TestGraph {
    config {
        iterations: 10
        step_delay: 0.5
        auto_stop: false
        verbose: true
    }

    entities {
        n1: Node(position=(0,0), state=live)
        n2: Node(position=(1,0), state=live)
        n3: Node(position=(0,1), state=dead)
        n4: Node(position=(1,1), state=live)
    }

    relations {
        e1: Edge(n1, n2, color="red")
        e2: Edge(n1, n3, color="blue")
        e3: Edge(n2, n4, color="green")
        e4: Edge(n3, n4, color="yellow")
    }

    rules {
        Birth: if neighbor_count(node, state=live) == 3 then node.state = live
        Death: if neighbor_count(node, state=live) < 2 then node.state = dead
        Overpopulation: if neighbor_count(node, state=live) > 3 then node.state = dead
    }
}

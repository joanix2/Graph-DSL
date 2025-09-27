types {
    entity Node {
        attr position: (int, int)
        attr state: {live, dead}
    }

    relation Edge {
        attr color: string
    }
}

graph MyGraph {
    entities {
        a: Node(position=(0,0), state=live)
        b: Node(position=(1,2), state=dead)
        c: Node(position=(2,3), state=live)
    }

    relations {
        e1: Edge(a, b, color="red")
        e2: Edge(b, c, color="blue")
    }

    rules {
        R1: if neighbor_count(node, state=live) == 2 then node.state = live
        R2: if neighbor_count(node, state=live) < 2 then node.state = dead
        R3: if neighbor_count(node, state=live) > 3 then node.state = dead
    }
}

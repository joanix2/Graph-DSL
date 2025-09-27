types {
    entity Node {
        attr state: {live, dead}
    }
    relation Edge {}
}

graph QuickTest {
    config {
        iterations: 5
        step_delay: 0
        auto_stop: true
        verbose: true
    }

    entities {
        a: Node(state=live)
        b: Node(state=dead)
        c: Node(state=live)
    }

    relations {
        e1: Edge(a, b)
        e2: Edge(b, c)
    }

    rules {
        SimpleRule: if neighbor_count(node, state=live) == 1 then node.state = live
    }
}

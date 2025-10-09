from node import Edge, Node

EDGE_LIST = [
    Edge(Node(0), Node(1)),
    Edge(Node(0), Node(2)),
    Edge(Node(0), Node(3)),

    Edge(Node(1), Node(4)),

    Edge(Node(2), Node(4)),
    Edge(Node(2), Node(5)),

    Edge(Node(3), Node(5)),
    Edge(Node(3), Node(6)),

    Edge(Node(4), Node(8)),
    Edge(Node(5), Node(4)),
    Edge(Node(5), Node(9)),
    Edge(Node(5), Node(7)),

    Edge(Node(6), Node(7)),

    Edge(Node(7), Node(9)),

    Edge(Node(9), Node(8)),
]

EDGE_LIST2 = [
    Edge(Node(0), Node(1)),
    Edge(Node(0), Node(2)),
    Edge(Node(1), Node(3)),
    Edge(Node(1), Node(4)),
    Edge(Node(2), Node(5)),
    Edge(Node(2), Node(6)),
]

EDGE_LIST3 = [
    Edge(Node(0), Node(1)),
    Edge(Node(1), Node(2)),
    Edge(Node(2), Node(0)),
    Edge(Node(2), Node(3)),
]


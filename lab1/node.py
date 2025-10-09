
class Node:
    def __init__(self, number):
        self.number = number

    def __str__(self):
        return f'{self.number}'


class Edge:
    def __init__(self, StartNode: Node, endNode: Node):
        self.start = StartNode
        self.end = endNode
        self.used = False
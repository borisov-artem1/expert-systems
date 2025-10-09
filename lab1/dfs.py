from node import Edge, Node
from stack import Stack

class GraphDFS:
    def __init__(self, edgeList: list[Edge]):
        self.edgeList = edgeList
        self.opened = Stack()
        self.closed = list()
        self.goal = None
        self.isSolutionFound = False
        self.childCounter = True

    def find(self, start: int, goal: int):
        self.opened.push(Node(start))
        self.goal = goal

        while self.childCounter and not self.isSolutionFound:
            print("Стек: ", end="")
            self.opened.print()

            self.childSearch()
            if self.isSolutionFound:
                break

            if self.childCounter is False and self.opened.length() > 1:
                currentNode = self.opened.pop()
                self.closed.append(currentNode.number)
                self.childCounter = True

        if not self.isSolutionFound:
            return None

        return self.opened

    def childSearch(self):
        self.childCounter = False
        currentNode = self.opened.peek()

        for edge in self.edgeList:
            if edge.start.number != currentNode.number \
                    or edge.used \
                    or self.opened.isExist(edge.end.number) \
                    or edge.end.number in self.closed:
                continue

            edge.used = True
            self.opened.push(edge.end)
            self.childCounter = True

            if edge.end.number == self.goal:
                self.isSolutionFound = True
            break

    @classmethod
    def showResult(cls, res: Stack | None) -> None:
        if res is None:
            print("\nНе удалось определить путь")
        else:
            print()
            res.show()

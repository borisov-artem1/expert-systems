from node import Edge, Node
from queue import Queue


class GraphBFS:
    def __init__(self, edgeList: list[Edge]):
        self.edgeList = edgeList
        self.opened = Queue()
        self.closed = list()
        self.goal = None
        self.isSolutionFound = False
        self.childCounter = True
        self.resultPath = {}

    def find(self, start: int, goal: int):
        self.opened.push(Node(start))
        self.goal = goal

        while self.childCounter and not self.isSolutionFound:
            print("Очередь: ", end="")
            self.opened.print()

            self.childsSearch()
            if self.isSolutionFound:
                break

            currentNode = self.opened.pop()
            self.closed.append(currentNode.number)

            if self.opened.size() != 0:
                self.childCounter = True

        if not self.isSolutionFound:
            return None

        return self.getResultPath(start)

    def childsSearch(self):
        self.childCounter = False
        currentNode = self.opened.top()

        for edge in self.edgeList:
            if edge.start.number != currentNode.number \
                    or edge.used \
                    or self.opened.exist(edge.end.number) \
                    or edge.end.number in self.closed:
                continue

            edge.used = True
            self.opened.push(edge.end)
            self.resultPath[edge.end.number] = edge.start.number
            self.childCounter = True

            if edge.end.number == self.goal:
                self.isSolutionFound = True
                break

    def getResultPath(self, start: int):
        current = self.goal
        result = [current]
        while current != start:
            current = self.resultPath[current]
            result.append(current)

        return result

    @classmethod
    def showResult(cls, res: list) -> None:
        print()
        if res is not None:
            for i in range(len(res) - 1, -1, -1):
                if i != 0:
                    print(f'{res[i]} -> ', end='')
                else:
                    print(f'{res[i]}')
        else:
            print("\nНе удалось определить путь")
        print()
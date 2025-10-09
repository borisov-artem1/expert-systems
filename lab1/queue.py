class Queue:
    def __init__(self):
        self.elements = []

    def push(self, elem):
        self.elements.append(elem)

    def size(self):
        return len(self.elements)

    def pop(self):
        if self.size() > 0:
            return self.elements.pop(0)
        return None

    def top(self):
        if self.size() > 0:
            return self.elements[0]
        return None

    def exist(self, elem):
        return elem in self.elements

    def print(self):
        for i in range(self.size()):
            print(self.elements[i], end=" ")
        print()
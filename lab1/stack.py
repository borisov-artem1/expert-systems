

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.length() == 0:
            return None
        return self.items.pop()

    def length(self):
        return len(self.items)

    def peek(self):
        return self.items[-1] if self.items else None

    def isExist(self, item):
        return item in self.items

    def show(self):
        for i in range(self.length()):
            if i == self.length() - 1:
                print(self.items[i])
            else:
                print(self.items[i], end=" -> ")

    def print(self):
        for i in range(self.length()):
            print(self.items[i], end=' ')
        print()



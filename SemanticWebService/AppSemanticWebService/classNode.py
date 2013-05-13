class Node():

    def __init__(self, uri, label):
        self.children = []
        self.uri = uri
        self.label = label

    def has_children(self):
        return self.children

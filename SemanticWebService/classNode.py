class Node():

    def __init__(self, uri, label):
        self.children = []
        self.uri = uri
        self.label = label

    def has_children(self):
        return self.children


class Element():

    def __init__(self, txt_content):
        self.txtContent = txt_content

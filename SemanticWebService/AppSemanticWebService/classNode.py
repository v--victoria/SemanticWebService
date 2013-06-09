class Node():

    def __init__(self, uri, label):
        self.children = []
        self.uri = uri
        self.label = label

    def has_children(self):
        return self.children

    def __str__(self):
        res =  "uri:" + str(self.uri) + ";label:" + str(self.label) + ";children:["
        for ch in self.children:
            res = res + ch.__str__()
        res = res + "]"
        return res

    def get_tree_list(self):
        ch_list = []
        for ch in self.children:
            ch_list.append(ch.label)
            res = ch.get_tree_list()
            if res:
                ch_list.append(res)
        return ch_list

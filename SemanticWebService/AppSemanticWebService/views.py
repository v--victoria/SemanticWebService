from django.shortcuts import render_to_response
from classNode import Node
from django.template import RequestContext

def test(request):
    """

    :param request:
    """
    r = Node()
    r.name = "root"
    ch1 = Node()
    ch2 = Node()
    ch1.name = "ch1"
    ch2.name = "ch2"
    r.children.append(ch1)
    r.children.append(ch2)
    #r.children = []
    r2 = Node()
    r2.name = "root2"
    #r2.children = []
    roots = []
    roots.append(r)
    roots.append(r2)
    return render_to_response('trees.html', {'roots': roots}, context_instance=RequestContext(request))
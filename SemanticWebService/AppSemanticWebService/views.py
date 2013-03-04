from django.shortcuts import render_to_response
from classNode import Node, Element
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
    elements = []
    el1 = Element()
    el2 = Element()
    el1.txtContent = "1"
    el2.txtContent = "2"
    elements.append(el1)
    elements.append(el2)

    return render_to_response('content.html', {'roots': roots, 'elements' : elements}, context_instance=RequestContext(request))
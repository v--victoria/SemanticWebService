from django.shortcuts import render_to_response
from classNode import Node, Element
from django.template import RequestContext
from rdflib import Namespace
from Connection import Connection
from DBBackends import AllegroBackend
from SemanticObjects import Factory

def get_factory():
    db = AllegroBackend(u"http://172.16.1.14:10035/repositories/SWS")
    c = Connection(db)
    f = Factory(c)
    return f

def fill_tree(cl, node_uri, node_label):
    base = Namespace("http://www.owl-ontologies.com/Ontology1359802755.owl#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    n = Node(node_uri, node_label)
    kwargs = {base.subSectionOf: node_uri}
    for ch in cl.filter(kwargs):
        label = getattr(ch, rdfs.label)['en']
        n.children.append(fill_tree(cl, ch.uri, label))
    return n

def get_roots(factory):
    base = Namespace("http://www.owl-ontologies.com/Ontology1359802755.owl#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    f = factory
    roots = []
    #get objects of class Section without attribute subSectionOf    
    cl = f.get_class(base.Section)
    for possible_root in cl.get_objects():
        try:
            getattr(possible_root, base.subSectionOf)
        except AttributeError:
            root = possible_root
            label = getattr(root, rdfs.label)['en']
            roots.append(fill_tree(cl, root.uri, label))
    return roots

def test(request):
    return render_to_response("main.html", {}, context_instance=RequestContext(request))

def show_base(request):
    return render_to_response("main.html", {}, context_instance=RequestContext(request))

def show_sections(request):
    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    f = get_factory()
    
    #get hierarchy of sections
    roots = []
    roots = get_roots(f)
    
    return render_to_response("sections.html", {"roots": roots}, context_instance=RequestContext(request))

def show_section(request, section_short_uri):
    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    f = get_factory()
    test = ""
    
    #get hierarchy of sections
    roots = []
    roots = get_roots(f)
    
    #get section elements of current section
    current_section = f.get_object(str_base + section_short_uri)
    kwargs = {base.belongsToSection: current_section.uri}

    #get different subclasses of class SectionElement to display different current section elements
    section_elements_f = []
    main_cl = f.get_class(base.SectionElement)
    for sub_cl in main_cl.get_subclasses():
        section_elements_f = section_elements_f + f.get_class(sub_cl.uri).filter(kwargs)

    res_elements = []    
    for section_element in section_elements_f:
        res_elements.append(Element(section_element.uri))#TODO: getattr(section_element, base.hasTxtContent ,"")

    return render_to_response("section.html", {"roots": roots, "elements" : res_elements, "test": test}, context_instance=RequestContext(request))

def show_section_element(request, section_element_short_uri):
    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    f = get_factory()
    test = ""
    
    #get hierarchy of sections
    roots = []
    roots = get_roots(f)

    #
    prop_list = []
    current_section_element = f.get_object(str_base + section_element_short_uri)
    test = current_section_element.uri
    
    for p in current_section_element.properties:
        prop_value = getattr(current_section_element, p)
        if type(prop_value) is dict:
            prop_value = prop_value['en']#TODO:
        prop_list.append([p, prop_value]) 

    return render_to_response("section_element_standard.html", {"roots": roots, "prop_list" : prop_list, "test": test}, context_instance=RequestContext(request))
    

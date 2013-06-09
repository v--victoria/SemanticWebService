from DBBackends import AllegroBackend
from Connection import Connection
from SemanticObjects import Factory
from rdflib import Namespace
from classNode import Node

str_rdfs = "http://www.w3.org/2000/01/rdf-schema#"
rdfs = Namespace(str_rdfs)
str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
base = Namespace(str_base)
conn_string = "http://192.168.0.102:10035/repositories/SWS"

def get_factory():
    db = AllegroBackend(conn_string)
    c = Connection(db)
    f = Factory(c)
    return f

def get_short_uri(uri):
    return uri.split("#")[1]

def get_section_element_types():
    base = Namespace("http://www.owl-ontologies.com/Ontology1359802755.owl#")
    res = []
    f = get_factory()
    main_cl = f.get_class(base.SectionElement)
    for sub_cl in main_cl.get_subclasses():
        res.append((sub_cl.uri, get_short_uri(sub_cl.uri)))
    return res

def get_label(obj, lang):
    res = "no label"
    label = getattr(obj, rdfs.label)
    if lang == "ru" and hasattr(label, 'ru'):
        res = getattr(obj, rdfs.label).ru
    if lang == "en" and hasattr(label, 'en'):
        res = getattr(obj, rdfs.label).en
    if hasattr(label, 'en'):
        res = getattr(obj, rdfs.label).en
    return str(res)

def get_section_roots(factory, lang):
    f = factory
    roots = []
    #get objects of class Section without attribute subSectionOf    
    cl = f.get_class(base.Section)
    for possible_root in cl.get_objects():
        v = getattr(possible_root, base.subSectionOf)
        if get_short_uri(possible_root.uri) == "HarryPotter":#TODO: !
            v = None
        if not v:  
            root = possible_root
            label = get_label(root, lang)
            roots.append(fill_section_tree(f, root.uri, label, lang))
    return roots

def fill_section_tree(factory, node_uri, node_label, lang):
    f = factory
    cl = f.get_class(base.Section)
    
    n = Node(get_short_uri(node_uri), node_label)
    kwargs = {str_base + "subSectionOf": node_uri}
    for ch in cl.filter(kwargs):
        label = get_label(ch, lang)
        n.children.append(fill_section_tree(f, ch.uri, label, lang))
    return n

def check_is_auth(cookies):
    isAuth = False;
    if cookies and "USER" in cookies:
        user = cookies["USER"]
        isAuth = True#TODO: check real isAuth value
    return isAuth

def get_cookie_value(cookies, parm):
    if parm != "LANG" and parm != "WS":#supported parms
        return None
    if not cookies or not parm in cookies:
        if parm == "LANG":#lang
            value = "en"#default value for lang
        else:#workspace
            value = "not defined"#default value for ws
    else:
        value = cookies[parm]
    return value

def get_comment_text(factory, sub_cl_uri, comment_uri):
    base = Namespace("http://www.owl-ontologies.com/Ontology1359802755.owl#")
    f = factory
    comment = f.get_object(comment_uri)
    if get_short_uri(sub_cl_uri) == "Like":
        text = "like"
        return text
    if get_short_uri(sub_cl_uri) == "Unlike":
        text = "unlike"
        return text
    try:
        text = getattr(comment, base.hasCommentContent)
    except AttributeError:
        text = "no text"
    return text

def fill_comment_tree(factory, main_cl, node_uri, node_text, prop, lang):#fill tree with subclasses instances
    base = Namespace("http://www.owl-ontologies.com/Ontology1359802755.owl#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    f = factory
    n = Node(node_uri, node_text)
    kwargs = {prop: node_uri}
    for sub_cl in main_cl.get_subclasses():
        children_sub = f.get_class(sub_cl.uri).filter(kwargs)
        for ch_sub in children_sub:
            n.children.append(fill_comment_tree(f, main_cl, ch_sub.uri, get_comment_text(f, sub_cl.uri, ch_sub.uri), prop, lang))
    return n

def is_section_element_subclass(factory, cl):
    f = factory
    main_cl = f.get_class(base.SectionElement)
    for sub_cl in main_cl.get_subclasses():
        if cl == sub_cl:
            return True
    return False

def get_obj_class_name(obj):
    try:
        return get_short_uri(str(type(obj).uri))
    except Exception:
        return None

def get_obj_name(obj):
    try:
        return get_short_uri(obj.uri)
    except Exception:
        return None

from DBBackends import AllegroBackend
from Connection import Connection
from SemanticObjects import Factory
from rdflib import Namespace

def get_factory():
    db = AllegroBackend(u"http://172.16.1.14:10035/repositories/SWS")
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

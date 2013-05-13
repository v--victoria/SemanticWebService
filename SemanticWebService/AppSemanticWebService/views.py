from django.shortcuts import render_to_response
from classNode import Node
from django.template import RequestContext
from rdflib import Namespace
from forms import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from ContextProcessors import UserProcessor
from utils2 import get_factory, get_short_uri
from django.contrib import messages

#----------AUXILIARY----------

def fill_tree(cl, node_uri, node_label, lang):
    base = Namespace("http://www.owl-ontologies.com/Ontology1359802755.owl#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    n = Node(get_short_uri(node_uri), node_label)
    kwargs = {base.subSectionOf: node_uri}
    for ch in cl.filter(kwargs):
        label = getattr(ch, rdfs.label)[lang]
        n.children.append(fill_tree(cl, ch.uri, label, lang))
    return n

def get_roots(factory, lang):
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
            label = getattr(root, rdfs.label)[lang]
            roots.append(fill_tree(cl, root.uri, label, lang))
    return roots

def check_is_auth(cookies):
    isAuth = False;
    if cookies and "CURRENT_USER" in cookies:
        user = cookies["CURRENT_USER"]
        isAuth = True#TODO: check real isAuth value
    return isAuth

def get_lang(cookies):
    if not cookies or not "LANG" in cookies:
        lang = "en"#default value
    else:
        lang = cookies["LANG"]
    return lang

#----------VIEWS----------

@csrf_exempt
def login(request):

    if request.method == 'POST':
        #second request
        form = LoginForm(request.POST)
        if form.is_valid():
            #form is valid
            cd = form.cleaned_data
            user = cd['user']
            password = cd['password']
            #check (user, password) is correct
            str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
            base = Namespace(str_base)
            f = get_factory()
            try:
                current_user = f.get_object(str_base + user)
                right_password = getattr(current_user, base.hasPassword)['en']#password is always in english
                if right_password == password:
                    #that's ok
                    #authenticate user
                    #TODO: set property isAuth value to true
                    
                    #create cookie and return response
                    response = HttpResponseRedirect("/base")
                    response.set_cookie("CURRENT_USER", current_user.uri)
                    lang = getattr(current_user, base.knowsLang)['en']
                    response.set_cookie("LANG", lang)
                    return response
                else:
                    #wrong password
                    messages.error(request, "wrong password")
            except Exception:
                #no such user
                messages.error(request, "no such user")
        else:
            #form is not valid
            messages.error(request, "form is not valid")
            
    form = LoginForm()
    return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))

@csrf_exempt
def logout(request):

    response = HttpResponseRedirect("/login")
    cookies = request.COOKIES
    if "CURRENT_USER" in cookies:
        response.delete_cookie("CURRENT_USER")
        if "LANG" in cookies:
            response.delete_cookie("LANG")
        #TODO: check CURRENT_USER isAuth
        isAuth = True#TODO: replace with real value
        if isAuth:
            isAuth = False#TODO: set property isAuth value to false
            messages.info(request, "Logout is successfull")
    else:
        messages.error(request, "Logout is failed")
        
    return response

def show_base(request):
    return render_to_response("base.html", {}, context_instance=RequestContext(request, processors=[UserProcessor]))

def show_sections(request):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    lang = get_lang(request.COOKIES)

    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    f = get_factory()
    
    #get hierarchy of sections
    roots = []
    roots = get_roots(f, lang)
    
    return render_to_response("sections.html", {"roots": roots}, context_instance=RequestContext(request, processors=[UserProcessor]))

def show_section(request, section_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    lang = get_lang(request.COOKIES)
    
    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    f = get_factory()
    test = ""
    
    #get hierarchy of sections
    roots = []
    roots = get_roots(f, lang)
    
    #get section elements of current section
    current_section = f.get_object(str_base + section_short_uri)
    kwargs = {base.belongsToSection: current_section.uri}

    #get different subclasses of class SectionElement to display different current section elements
    section_elements_f = []#list of current section elements
    main_cl = f.get_class(base.SectionElement)
    for sub_cl in main_cl.get_subclasses():
        section_elements_f = section_elements_f + f.get_class(sub_cl.uri).filter(kwargs)

    res_elements = []    
    for section_element in section_elements_f:
        res_dict = getattr(section_element, rdfs.label)
        if lang in res_dict:
            label = res_dict[lang]
        else:
            if "en" in res_dict:
                label = res_dict["en"]
        res_elements.append((get_short_uri(section_element.uri), label))

    #add form to add new instances
    form = SelectSectionElementTypeForm()

    return render_to_response("section.html", {"roots": roots, "elements" : res_elements, "form": form, "test": test}, context_instance=RequestContext(request, processors=[UserProcessor]))

def show_section_element(request, section_element_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    lang = get_lang(request.COOKIES)

    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    f = get_factory()
    
    #get hierarchy of sections
    roots = []
    roots = get_roots(f, lang)

    #
    prop_list = []
    current_section_element = f.get_object(str_base + section_element_short_uri)
    test = current_section_element.uri
    
    for p in current_section_element.properties:
        prop_value = getattr(current_section_element, p)       
        if type(prop_value) is dict:
            prop_value = prop_value['en']
        prop_list.append([p, prop_value])

    #TODO: add comments

    return render_to_response("section_element_standard.html", {"roots": roots, "prop_list" : prop_list, "test": test}, context_instance=RequestContext(request, processors=[UserProcessor]))
    
def add_section_element (request, s_el_subcl_short_uri):#s_el_subcl_short_uri - low level subclass

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    lang = get_lang(request.COOKIES)
    
    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    f = get_factory()

    #get hierarchy of sections
    roots = []
    roots = get_roots(f, lang)
    
    #fill properties base on choosed subclass
    main_cl = f.get_class(str_base + s_el_subcl_short_uri)
    res_properties = []
    test = ""
    
    for cl in main_cl.__mro__:
        try:
            #for class (not for object) cl.properties is set of URLs without types
            properties = cl.properties
            for p in properties:
                res_properties.append(p)
        except AttributeError:
            pass
    form = NewSectionElementForm(properties=res_properties)
    

    
    return render_to_response("add_section_element.html", {"roots": roots, "form" : form, "test": test}, context_instance=RequestContext(request, processors=[UserProcessor]))

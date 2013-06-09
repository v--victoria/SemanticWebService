from django.shortcuts import render_to_response
from django.template import RequestContext
from rdflib import Namespace
from utils2 import *
from forms import *
from ContextProcessors import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from settings import *
from django.contrib import messages
from classNode import Node

#----------PARAMETERS----------

str_rdfs = "http://www.w3.org/2000/01/rdf-schema#"
rdfs = Namespace(str_rdfs)
str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
base = Namespace(str_base)

#----------LOGIN/LOGOUT----------

#login to system
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
            f = get_factory()
            try:
                user = f.get_object(str_base + user)
                right_password = str(getattr(user, base.hasPassword)[0])
                if right_password == password:
                    #that's ok
                    #authenticate user
                    #create cookie and return response
                    response = HttpResponseRedirect("/base/Section/")
                    response.set_cookie("USER", user.uri)
                    lang = str(getattr(user, base.knowsLang)[0])
                    response.set_cookie("LANG", lang)
                    workspaces = f.get_class(base.Workspace)
                    kwargs = {base.addedBy: user.uri}
                    created_workspaces = workspaces.filter(kwargs)
                    if created_workspaces:
                        response.set_cookie("WS", created_workspaces[0].uri)
                    else:
                        #user-participated workspaces
                        pass
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

#logout from system
@csrf_exempt
def logout(request):
    response = HttpResponseRedirect("/login")
    cookies = request.COOKIES
    if "USER" in cookies:
        response.delete_cookie("USER")
        if "LANG" in cookies:
            response.delete_cookie("LANG")
        #TODO: check USER isAuth
        isAuth = True#TODO: replace with real value
        if isAuth:
            isAuth = False#TODO: set property isAuth value to false
            messages.info(request, "Logout is successfull")
    else:
        messages.error(request, "Logout is failed")
    return response

#----------SHOW----------

#show main page
def show_base(request):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")
    
    return render_to_response("sections.html", {}, context_instance=RequestContext(request, processors=[UserProcessor, SectionsProcessor]))

#show current section elements
@csrf_exempt
def show_section(request, section_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")
    lang = get_cookie_value(request.COOKIES, "LANG")
    ws = get_cookie_value(request.COOKIES, "WS")
    
    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    f = get_factory()
    test = ""

    if request.method == 'POST':
        #second request
        formId = request.POST['formId']
        if formId == 'addSection':
            form = AddSectionForm(request.POST)
        if form.is_valid():
            #form is valid
            cd = form.cleaned_data
            if formId == 'addSection':
                section_id = cd['sectionId']
                section_name = cd['sectionName']
                messages.info(request, 'New section with id=[' + section_id + '], name=[' + section_name + '] was added.')
        else:
            #form is not valid
            messages.error(request, "form is not valid")
    
    #get section elements of current section
    current_section = f.get_object(str_base + section_short_uri)
    
    kwargs = {base.belongsToSection: current_section.uri, base.belongsToWorkspace: ws}

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

    #form to add new section element
    form_new_section_element = SelectSectionElementTypeForm()

    #form to add new section
    form_new_section = AddSectionForm()
     
    return render_to_response("section.html", {"elements" : res_elements, "form_new_section_element": form_new_section_element, "form_new_section" : form_new_section}, context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

#show section element
def show_section_element(request, section_element_short_uri):
    #TODO: check section_element belongs to current current workspace
    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    lang = get_cookie_value(request.COOKIES, "LANG")

    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    f = get_factory()

    #
    prop_list = []
    current_section_element = f.get_object(str_base + section_element_short_uri)
    
    for p in current_section_element.__dict__:
              
        #if type(prop_value) is dict:
        #    prop_value = prop_value['en']
        #if get_short_uri(p) == "hasImage":
        #    prop_value = getattr(f.get_object(prop_value.uri), base.hasLocation)['en']
        if p != 'uri':
            values = getattr(current_section_element, p)
            for v in values:
                
                prop_list.append([get_short_uri(p), prop_value])

    #comments
    root_comments = []
    res_comments = []
    kwargs = {base.addedTo: str_base + section_element_short_uri}
    main_cl = f.get_class(base.Comment)
    for sub_cl in main_cl.get_subclasses():
        for root_comment in f.get_class(sub_cl.uri).filter(kwargs):
            res_comments.append(
                fill_comment_tree(f, main_cl, root_comment.uri, get_comment_text(f, sub_cl.uri, root_comment.uri), base.addedTo, 'en'))

    #for res_comment in res_comments:
    #    res = res_comment.get_tree_list()
    n = Node(None, "Comments")
    n.children = res_comments
    res = n.get_tree_list()
    
    return render_to_response("section_element_standard.html", {"prop_list" : prop_list, "comments": res}, context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

@csrf_exempt
def show_user(request, user_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    lang = get_cookie_value(request.COOKIES, "LANG")
    
    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    f = get_factory()

    #fill workspaces
    user_uri = str_base + user_short_uri
    workspaces = f.get_class(base.Workspace)

    #fill user workspaces
    kwargs = {base.addedBy: user_uri}
    created_workspaces = workspaces.filter(kwargs)
    created_workspaces_f = []
    for cw in created_workspaces:
        created_workspaces_f.append((get_short_uri(cw.uri), getattr(cw, rdfs.label)[0]))

    #fill user-participated workspaces
    #TODO:
    user_p_workspaces = []
    user_p_workspaces_f = []

    #forms
    #fill lang form
    lang_form = SetPrefferedLangForm()

    #fill workspaces form
    res_workspaces = created_workspaces_f + user_p_workspaces_f
    workspaces_form = SetCurrentWorkspaceForm(workspaces=res_workspaces)

    if request.method == 'POST':
        #second request
        formId = request.POST['formId']
        if formId == 'lang':
            form = SetPrefferedLangForm(request.POST)
        else:
            form = SetCurrentWorkspaceForm(request.POST, workspaces=res_workspaces)
        if form.is_valid():
            #form is valid
            cd = form.cleaned_data
            if formId == 'lang':
                lang = cd['lang']
                messages.info(request, 'Language was set to ' + lang)
                #TODO: set lang
            else:
                ws = cd['currWs']
                messages.info(request, 'Workspace was set to ' + ws)
                #TODO: set workspace
        else:
            #form is not valid
            messages.error(request, "form is not valid")

    return render_to_response("user.html", {"lang_form" : lang_form, "workspaces_form": workspaces_form,
                                            "created_workspaces": created_workspaces_f, "user_p_workspaces": user_p_workspaces_f,
                                            "show settings": False},
                              context_instance=RequestContext(request, processors=[UserProcessor]))

def show_workspace(request, ws_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    f = get_factory()
    ws = f.get_object(str_base + ws_short_uri)
    kwargs = {base.belongsToWorkspace: ws}
    
    elements = []#section elements of current workspace
    main_cl = f.get_class(base.SectionElement)
    for sub_cl in main_cl.get_subclasses():
        elements = elements + f.get_class(sub_cl.uri).filter(kwargs)    

    start_el = None
    for el in elements:
        if not hasattr(el, base.follows):
            start_el = el
            break
    
    while start_el:
        elements.append(start_el)
        kwargs = {base.belongsToWorkspace: ws, base.follows: start_el.uri}
        res = section_elements.filter(kwargs)
        if res:
            res_elements.append(res[0])
            start_el = res[0]
        else:
            start_el = None

    return render_to_response("workspace.html", {"elements" : res_elements}, context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

#----------ADD----------
    
def add_section_element(request, s_el_subcl_short_uri):#s_el_subcl_short_uri - low level subclass

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")
    
    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    f = get_factory()
    
    #fill properties base on choosed subclass
    main_cl = f.get_class(str_base + s_el_subcl_short_uri)
    res_properties = []
    test = ""
    i = 0

    for cl in main_cl.__mro__:
        properties = cl.__dict__
        for p in properties:
            #if p == 'properties'
            res_properties.append((p, type(getattr(cl, p)[0])))
        if i == 1:
            test = test + None
        i= i + 1

    form = NewSectionElementForm(properties=res_properties)
    
    return render_to_response("add_section_element_standard.html", {"form" : form, "test": test}, context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

def add_workspace(request):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    if request.method == 'POST':
        #second request
        if form.is_valid():
            #form is valid
            cd = form.cleaned_data
            answer = cd['wsName']
            #TODO:
            messages.info(request, "workspace was successfully deleted")
        else:
            #form is not valid
            messages.error(request, "form is not valid")
        user = get_short_uri(request.cookies["CURRENT_USER"])
        return HttpResponseRedirect("/base/User/" + user + "/edit/")
    else:
        form = AddWorkspaceForm()
        return render_to_response("add_workspace.html",
                                  {"form" : form},
                                  context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))    

#----------EDIT----------

def edit_section_element(request, section_element_short_uri):
    #TODO: check section_element belongs to current current workspace
    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    lang = get_cookie_value(request.COOKIES, "LANG")

    str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
    base = Namespace(str_base)
    f = get_factory()

    properties = []
    obj = f.get_object(str_base + section_element_short_uri)

    for p in obj.__dict__:
        properties.append((p, type(getattr(obj, p)[0]), getattr(obj, p)))

    form = EditSectionElementForm(properties=properties)
    
    return render_to_response("section_element_standard_edit.html",
                              {"form" : form},
                              context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))
    
#----------DELETE----------

@csrf_exempt
def delete_workspace(request, ws_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    if request.method == 'POST':
        #second request
        if form.is_valid():
            #form is valid
            cd = form.cleaned_data
            answer = cd['answer']
            if answer == 'Y':
                #TODO:
                messages.error(request, "workspace was successfully deleted")
        else:
            #form is not valid
            messages.error(request, "form is not valid")
        user = get_short_uri(request.cookies["CURRENT_USER"])
        return HttpResponseRedirect("/base/User/" + user + "/edit/")
    else:
        form = DeleteConfirmationForm()
        workspace = ws_short_uri
        f = get_factory()
        count = 0
        main_cl = f.get_class(base.SectionElement)
        for sub_cl in main_cl.get_subclasses():
            count = count + len(f.get_class(sub_cl.uri).get_objects())
        return render_to_response("delete_workspace.html",
                                  {"form" : form, "workspace": workspace, "count": count},
                                  context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

@csrf_exempt
def delete_section(request, section_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    if request.method == 'POST':
        #second request
        if form.is_valid():
            #form is valid
            cd = form.cleaned_data
            answer = cd['answer']
            if answer == 'Y':
                #TODO:
                messages.info(request, "section was successfully deleted")
                #TODO:
                return HttpResponseRedirect("/base/")
            else:
                messages.info(request, "section was not deleted")
                return HttpResponseRedirect("/base/Section/" + section_short_uri + "/")
        else:
            #form is not valid
            messages.error(request, "form is not valid")
            return HttpResponseRedirect("/base/Section/" + section_short_uri + "/")
    else:
        form = DeleteConfirmationForm()
        section = section_short_uri
        ws = get_cookie_value(request.COOKIES, "WS")
        f = get_factory()
        
        your_count = 0
        common_count = 0
        kwargs1 = {base.belongsToWorkspace: ws, base.belongsToSection: str_base + section_short_uri}
        kwargs2 = {base.belongsToSection: str_base + section_short_uri}
        
        main_cl = f.get_class(base.SectionElement)
        for sub_cl in main_cl.get_subclasses():
            your_count = your_count + len(f.get_class(sub_cl.uri).filter(kwargs1))
            common_count = common_count + len(f.get_class(sub_cl.uri).filter(kwargs2))
            
        return render_to_response("delete_section.html",
                                  {"form" : form, "section": section, "your_count": your_count, "common_count": common_count},
                                  context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

@csrf_exempt
def delete_section_element(request, section_element_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    if request.method == 'POST':
        #second request
        if form.is_valid():
            #form is valid
            cd = form.cleaned_data
            answer = cd['answer']
            if answer == 'Y':
                #TODO:
                messages.error(request, "section element was successfully deleted")
        else:
            #form is not valid
            messages.error(request, "form is not valid")
        return HttpResponseRedirect("/base/")
    else:
        form = DeleteConfirmationForm()
        section_element = section_element_short_uri
        return render_to_response("delete_section_element.html",
                                  {"form" : form},
                                  context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))    

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
    
    f = get_factory()

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
    for el in section_elements_f:
        label = get_label(el, lang)
        res_elements.append((get_short_uri(el.uri), label))

    #form to add new section element
    form_new_section_element = SelectSectionElementTypeForm()

    #form to add new section
    form_new_section = AddSectionForm()
     
    return render_to_response("section.html", {"elements" : res_elements, "form_new_section_element": form_new_section_element, "form_new_section" : form_new_section}, context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

#show section element
def show_section_element(request, section_element_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    lang = get_cookie_value(request.COOKIES, "LANG")

    f = get_factory()

    properties = []
    current_element = f.get_object(str_base + section_element_short_uri)

    #check section element belongs to current current workspace
    if not getattr(current_element, base.belongsToWorkspace)[0] == f.get_object(get_cookie_value(request.COOKIES, "WS")):
        messages.error(request, 'Address to this section element is prohibited: it is not in current workspace')

    for p in dir(current_element):
        if not str_base in p:
            continue

        values = getattr(current_element, p)
        if values:
            for v in values:
                if p == str_base + "hasImage":
                    tmp = str(getattr(f.get_object(v.uri), base.hasLocation)[0])
                    v = str(getattr(f.get_object(v.uri), base.hasLocation)[0])
                else:
                    v_class_name = get_obj_class_name(v)
                    if not v_class_name:
                        t = 'unsupported'
                    else:
                        is_s_el_sub = is_section_element_subclass(f, type(v))
                        if is_s_el_sub:
                            v_class_name = 'SectionElement' 
                        if v_class_name == 'SectionElement' or v_class_name == 'Section' or v_class_name == 'Workspace':#supported types
                            t = v_class_name
                            v = get_short_uri(v.uri)
                        else:
                            t = 'unsupported'
                            v = get_obj_name(v)
                properties.append((get_short_uri(p), v, t))
      
    #comments
    comments = []
    
    kwargs = {base.addedTo: str_base + section_element_short_uri}
    main_cl = f.get_class(base.Comment)
    for sub_cl in main_cl.get_subclasses():
        for comment in f.get_class(sub_cl.uri).filter(kwargs):
            comments.append(
                fill_comment_tree(f, main_cl, comment.uri, get_comment_text(f, sub_cl.uri, comment.uri), base.addedTo, 'en'))

    n = Node(None, "Comments")
    n.children = comments
    comments = n.get_tree_list()
    
    return render_to_response("section_element_standard.html", {"properties" : properties, "comments": comments, "element": section_element_short_uri}, context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

@csrf_exempt
def show_user(request, user_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    lang = get_cookie_value(request.COOKIES, "LANG")
    
    f = get_factory()

    #fill workspaces
    workspaces = f.get_class(base.Workspace)

    #fill user workspaces
    kwargs = {base.addedBy: str_base + user_short_uri}
    created_workspaces = workspaces.filter(kwargs)
    created_workspaces_f = []
    for cw in created_workspaces:
        created_workspaces_f.append((get_short_uri(cw.uri), get_label(cw, lang)))

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
                              context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

def show_workspace(request, ws_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")
    
    #find current workspace elements
    f = get_factory()
    ws = f.get_object(str_base + ws_short_uri)
    kwargs = {base.belongsToWorkspace: ws}
    elements = []#section elements of current workspace
    main_cl = f.get_class(base.SectionElement)
    for sub_cl in main_cl.get_subclasses():
        for obj in f.get_class(sub_cl.uri).get_objects():
            if getattr(obj, base.belongsToWorkspace)[0] == ws:
                elements.append(obj)

    #find start element            
    start_el = None
    for el in elements:
        if not getattr(el, base.follows) or get_short_uri(el.uri) == 'ArticleAboutAuthor':#TODO: !
            start_el = el
            break

    #order current workspace elements starting with start element
    ordered_elements = []
    while start_el:
        ordered_elements.append(start_el)
        elements.remove(start_el)
        flag = False
        for el in elements:
            if getattr(el, base.follows)[0] == start_el:
                flag = True
                start_el = el
                break
        if not flag:
            start_el = None

    res_elements = []
    for el in ordered_elements:
        res_elements.append((get_short_uri(el.uri), get_label(el, get_cookie_value(request.COOKIES, 'LANG'))))
            
    return render_to_response("workspace.html",
                              {"elements" : res_elements},
                              context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

#----------ADD----------
    
def add_section_element(request, s_el_subcl_short_uri):#s_el_subcl_short_uri - low level subclass

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")
    
    f = get_factory()
    
    #fill properties base on choosed subclass
    cl = f.get_class(str_base + s_el_subcl_short_uri)
    properties = []
    for p in dir(cl):
        if not str_base in p:
            continue
        else:
            properties.append((get_short_uri(p), type(p)))

    form = NewSectionElementForm(properties=properties)
    
    return render_to_response("add_section_element.html",
                              {"form" : form},
                              context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))


@csrf_exempt
def add_workspace(request):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    if request.method == 'POST':
        #second request
        form = AddWorkspaceForm(request.POST)
        if form.is_valid():
            #form is valid
            cd = form.cleaned_data
            answer = cd['wsName']
            #TODO:
            messages.info(request, "workspace was successfully added")
        else:
            #form is not valid
            messages.error(request, "form is not valid")
        user = get_short_uri(request.COOKIES["USER"])
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

    f = get_factory()

    properties = []
    current_element = f.get_object(str_base + section_element_short_uri)

    for p in dir(current_element):
        if not str_base in p:
            continue

        values = getattr(current_element, p)
        if values:
            for v in values:
                v_class_name = get_obj_class_name(v)
                if not v_class_name:
                    continue
                
                is_s_el_sub = is_section_element_subclass(f, type(v))
                if is_s_el_sub:
                    v_class_name = 'SectionElement' 
                if v_class_name == 'SectionElement' or v_class_name == 'Section' or v_class_name == 'Workspace':#supported types
                    t = v_class_name
                    v = get_short_uri(v.uri)
                else:
                    t = 'unsupported'
                    v = get_obj_name(v)
                properties.append((p, v, t))   

    form = EditSectionElementForm(properties=properties)
    
    return render_to_response("edit_section_element.html",
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
        form = DeleteConfirmationForm(request.POST)
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
        user = get_short_uri(request.COOKIES["USER"])
        return HttpResponseRedirect("/base/User/" + user + "/edit/")
    else:
        form = DeleteConfirmationForm()
        workspace = ws_short_uri
        f = get_factory()
        count = 0
        main_cl = f.get_class(base.SectionElement)
        kwargs = {base.belongsToWorkspace: str_base + ws_short_uri}
        for sub_cl in main_cl.get_subclasses():
            count = count + len(f.get_class(sub_cl.uri).filter(kwargs))
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
        form = DeleteConfirmationForm(request.POST)
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
        other_count = common_count - your_count
        
        return render_to_response("delete_section.html",
                                  {"form" : form, "section": section, "your_count": your_count, "other_count": other_count},
                                  context_instance=RequestContext(request, processors=[UserProcessor,SectionsProcessor]))

@csrf_exempt
def delete_section_element(request, section_element_short_uri):

    if not check_is_auth(request.COOKIES):
        messages.error(request, "Please authenticate first")
        return HttpResponseRedirect("/login")

    if request.method == 'POST':
        form = DeleteConfirmationForm(request.POST)
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

from django import forms
from utils2 import get_section_element_types, get_factory, get_short_uri, get_obj_name
from rdflib import Namespace

str_rdfs = "http://www.w3.org/2000/01/rdf-schema#"
rdfs = Namespace(str_rdfs)
str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
base = Namespace(str_base)

#login
class LoginForm(forms.Form):
    user = forms.CharField(required=True, label='User')
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs = {}), label='Password')

#edit
#edit user
class SetPrefferedLangForm(forms.Form):
    formId = forms.CharField(widget=forms.HiddenInput(), initial='lang')
    lang = forms.ChoiceField(required=True, label='Language', choices=[('ru', 'Russian'),('en', 'English')])

class SetCurrentWorkspaceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        workspaces = kwargs.pop('workspaces', None)
        
        super(SetCurrentWorkspaceForm, self).__init__(*args, **kwargs)
        self.fields['currWs'] = forms.ChoiceField(required=True, label='Current workspace', choices=workspaces)
        self.fields['formId'] = forms.CharField(widget=forms.HiddenInput(), initial='ws')
    
class EditSectionElementForm(forms.Form):
    def __init__(self, *args, **kwargs):        
        f = get_factory()
        properties = kwargs.pop('properties', None)
        super(EditSectionElementForm, self).__init__(*args, **kwargs)
        for p, v, t in properties:
            #TODO: differ types of properties (object property - dropdownlist, data property with different ranges - charfield, calendar)
            if t == 'unsupported':
                self.fields[p] = forms.CharField(required=False, label=get_short_uri(p))
            else:#supported
                choices = []
                for obj in f.get_class(str_base + t).get_objects():
                    choices.append((obj.uri, get_obj_name(obj)))
                self.fields[p] = forms.ChoiceField(required=False, label=get_short_uri(p), choices=choices, initial=obj.uri)

#add
class AddWorkspaceForm(forms.Form):
    wsName = forms.CharField(required=True, label='Enter new workspace name')

class AddSectionForm(forms.Form):#used in show_section
    formId = forms.CharField(widget=forms.HiddenInput(), initial='addSection')
    sectionId = forms.CharField(required=True, label='Enter new section id')#section name
    sectionName = forms.CharField(required=True, label='Enter new section name')#section label

class SelectSectionElementTypeForm(forms.Form):#used in show_section
    choices=get_section_element_types()
    res_choices = []
    for c in choices:
        res_choices.append(("/base/" + c[1] + "/add", c[1]))
    section_element_type = forms.ChoiceField(required=True,
                                             label='Section Element type',
                                             choices=res_choices,
                                             widget=forms.Select(attrs={'onChange':'window.document.location.href=this.options[this.selectedIndex].value;'}))
    formId = forms.CharField(widget=forms.HiddenInput(), initial='selectType')

class NewSectionElementForm(forms.Form):
    def __init__(self, *args, **kwargs):
        properties = kwargs.pop('properties', None)
        super(NewSectionElementForm, self).__init__(*args, **kwargs)
        for p in properties:
            #TODO: differ types of properties (object property - dropdownlist, data property with different ranges - charfield, calendar) 
            self.fields[p[0]] = forms.CharField(required=False, label='property ' + p[0])

#delete
#delete_workspace, delete_section, delete_section_element
class DeleteConfirmationForm(forms.Form):
    choices=[('Y','Yes'),('N','No')]
    answer = forms.ChoiceField(required=True, choices=choices, widget=forms.RadioSelect(), label='Confirm your choice please')

from django import forms
from utils2 import get_section_element_types, get_factory
from rdflib import Namespace

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
        str_base = "http://www.owl-ontologies.com/Ontology1359802755.owl#"
        rdfs_base = "http://www.w3.org/2000/01/rdf-schema#"
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        
        f = get_factory()
        properties = kwargs.pop('properties', None)#TODO: support different types
        super(EditSectionElementForm, self).__init__(*args, **kwargs)
        for p in properties:
            p_uri = str(p[0])
            #TODO: differ types of properties (object property - dropdownlist, data property with different ranges - charfield, calendar)
            if 'class' in str(p[1]):
                try:
                    cl = f.get_class(str_base+str(p[1]).split(" ")[1])
                    objects = []
                    for obj in cl.get_objects():
                        objects.append((obj.uri, obj.uri))
                    self.fields[p_uri] = forms.ChoiceField(required=True, label=str(p[0]), choices=objects)
                except Exception:
                    self.fields[p_uri] = forms.CharField(required=False, label=p_uri)    
            else:
                self.fields[p_uri] = forms.CharField(required=False, label=p_uri)

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
                                             choices=res_choices#,
                                             widget=forms.Select(attrs={'onChange':'window.document.location.href=this.options[this.selectedIndex].value;'})
                                             )
    formId = forms.CharField(widget=forms.HiddenInput(), initial='selectType')

class NewSectionElementForm(forms.Form):
    def __init__(self, *args, **kwargs):
        properties = kwargs.pop('properties', None)
        super(NewSectionElementForm, self).__init__(*args, **kwargs)
        for p in properties:
            #TODO: differ types of properties (object property - dropdownlist, data property with different ranges - charfield, calendar) 
            self.fields[p[1]] = forms.CharField(required=False, label=('property name: ' + p[1] + '; property type: ' + p[2]))

#delete
#delete_workspace, delete_section, delete_section_element
class DeleteConfirmationForm(forms.Form):
    choices=[('Y','YES'),('N','MO')]
    answer = forms.ChoiceField(required=True, choices=choices, widget=forms.RadioSelect(), label='Confirm your choice please')

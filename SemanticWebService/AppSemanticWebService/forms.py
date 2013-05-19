from django import forms
from utils2 import get_section_element_types

class LoginForm(forms.Form):
    user = forms.CharField(required=True, label='User')
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs = {}), label='Password')

class SelectSectionElementTypeForm(forms.Form):
    choices=get_section_element_types()
    res_choices = []
    for c in choices:
        res_choices.append(("/base/" + c[1] + "/add", c[1]))
    section_element_type = forms.ChoiceField(required=True,
                                             label='Section Element type',
                                             choices=res_choices,
                                             widget=forms.Select(attrs={'onChange':'window.document.location.href=this.options[this.selectedIndex].value;'}))

class SetPrefferedLangForm(forms.Form):
    formId = forms.CharField(widget=forms.HiddenInput(), initial='lang')
    lang = forms.ChoiceField(required=True, label='Language', choices=[('ru', 'Russian'),('en', 'English')])

class SetCurrentWorkspaceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        workspaces = kwargs.pop('workspaces', None)
        super(SetCurrentWorkspaceForm, self).__init__(*args, **kwargs)
        self.fields['currWs'] = forms.ChoiceField(required=True, label='Current workspace', choices=workspaces)
        self.fields['formId'] = forms.CharField(widget=forms.HiddenInput(), initial='ws')

class NewSectionElementForm(forms.Form):
    def __init__(self, *args, **kwargs):
        properties = kwargs.pop('properties', None)#TODO: support different types
        super(NewSectionElementForm, self).__init__(*args, **kwargs)
        for p in properties:
            #TODO: differ types of properties (object property - dropdownlist, data property with different ranges - charfield, calendar) 
            self.fields[p] = forms.CharField(required=False, label=p)

        

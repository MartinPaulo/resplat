from django import forms


class CollectionsSearchForm(forms.Form):
    code = forms.CharField(label='Code', max_length=50, required=False)
    name = forms.CharField(label='Name', max_length=100, required=False)
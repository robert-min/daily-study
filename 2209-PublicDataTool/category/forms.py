from django import forms

class IndexForm(forms.Form):
    index_name = forms.CharField(label="Set index", max_length=10)

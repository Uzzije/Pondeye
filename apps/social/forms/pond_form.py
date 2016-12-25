from django import forms


class PondEntryForm(forms.Form):
	name_of_pond = forms.CharField(required=True, max_length=245,
                                  widget=forms.TextInput(attrs={'class':'form-control input-lg', 'placeholder':'Enter Name of Pond'}))
	purpose = forms.CharField(required=False, max_length=100,
                                  widget=forms.TextInput(attrs={'class':'form-control input-lg','placeholder':'The purpose of this pond in 100 word or less'}))

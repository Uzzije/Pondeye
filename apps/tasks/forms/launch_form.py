from django import forms


class LaunchForm(forms.Form):
	email = forms.EmailField(label='Email', max_length=100, required=True,
							 widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}))
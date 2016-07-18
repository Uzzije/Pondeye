from django import forms


class PictureUploadForm(forms.Form):
    picture = forms.ImageField(label="upload picture", required=True)

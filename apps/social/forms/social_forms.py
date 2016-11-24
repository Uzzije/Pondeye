from django import forms


class PictureUploadForm(forms.Form):
    picture = forms.ImageField(label="Upload Picture", required=True)


class CommentForms(forms.Form):
    comment_form = forms.CharField(max_length=1500, required=False, widget=forms.TextInput(
        attrs={
            'placeholder':'Journal Thoughts to Project',
            'class':'materialize-textarea',
        }
    ))
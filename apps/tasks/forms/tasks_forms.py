from django import forms
from ..models import User
from form_choices import LIST_OF_MINUTES
from functools import partial
from datetimewidget.widgets import DateTimeWidget
from form_module import get_current_datetime
from django.contrib.auth import authenticate


class RegisterForm(forms.Form):

    user_name = forms.CharField(label='User Name', max_length=100, required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}))
    first_name = forms.CharField(label='First Name', max_length=100, required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label='Last Name', max_length=100, required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))
    email = forms.EmailField(label='Email', max_length=100, required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}),
                               required=True)
    verify_password = forms.CharField(label='Verify Password', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Verify Password'}), required=True)

    def clean(self):
            cleaned_data = super(RegisterForm, self).clean()
            user_password = self.cleaned_data.get('password')
            user_verify_password = self.cleaned_data.get('verify_password')

            if user_password and user_verify_password:
                if user_password != user_verify_password:
                    msg = "Passwords does not match"
                    self.add_error('password', msg)
            return cleaned_data

    def clean_user_name(self):
        cleaned_data = super(RegisterForm, self).clean()
        user_name = self.cleaned_data['user_name']
        try:
            User.objects.get(username=user_name)
            msg = "Username already in use"
            self.add_error('user_name', msg)
        except User.DoesNotExist:
            if len(user_name) < 3:
                msg = "Username already in use"
                self.add_error('user_name', msg)
            elif user_name is not "guest":
                return user_name

    def clean_email(self):
        cleaned_data = super(RegisterForm, self).clean()
        email = self.cleaned_data['email']
        try:
            email_value = User.objects.get(email=email)
            msg = "hmm, this email is already in use"
            self.add_error('email', msg)
        except User.DoesNotExist:
            return email


class LoginForm(forms.Form):
    my_default_errors = {
        'invalid': 'Make sure username and password are correct'
    }
    name = forms.CharField(error_messages=my_default_errors, required=True, label='User Name', max_length=100, widget=forms.TextInput(attrs={'class':"input pass", 'placeholder':'Username'}))
    password = forms.CharField(required=True, label='Password', widget=forms.PasswordInput(attrs={'class':"input pass", 'placeholder':'Password'}), error_messages=my_default_errors)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        name = self.cleaned_data.get('name')
        password = self.cleaned_data.get('password')
        user = authenticate(username=name, password=password)
        if user is None:
            msg = " Oops username and password combination is invalid"
            self.add_error('name', msg)
            raise forms.ValidationError(
                    "Oops username and password combination is invalid"
                )
        else:
            return cleaned_data


class AddTaskForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddTaskForm, self).__init__(*args, **kwargs)

    DateInput = partial(forms.DateInput, {'class': 'datepicker'})

    to_do_item = forms.CharField(max_length=300, label="what needs to get done", required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'e.g put air in my tires'}))
    start_time = forms.DateTimeField(required=False, initial=None,
                                     widget=DateTimeWidget(attrs={'id':"startid"}, usel10n = True, bootstrap_version=3), label="When?")
    end_time = forms.ChoiceField(required=False, label="For How Long?", choices=LIST_OF_MINUTES, widget=forms.Select())
    new_project = forms.CharField(required=False, label='Add to New Project',
                                  widget=forms.TextInput(attrs={'placeholder':'i.e this is part of studying for a test plan'}))

    def clean_start_time(self):
        super(AddTaskForm, self).clean()
        time = self.cleaned_data['start_time']
        if time:
            if time.time() < get_current_datetime().time():
                if time.date() > get_current_datetime().date():
                    return time
                msg = "Hey, your work is not history yet"
                self.add_error('start_time', msg)
            else:
                if time.date() >= get_current_datetime().date():
                    return time
                msg = "Hey, your work is not history yet"
                self.add_error('start_time', msg)


class PictureUploadForm(forms.Form):
    picture = forms.ImageField(label="Upload Visual", required=True)


class AddProjectForm(forms.Form):
    DateInput = partial(forms.DateInput, {'class': 'datepicker'})
    project_date = forms.DateTimeField(required=True, initial=None,
                                       widget=DateTimeWidget(attrs={'id':"proj_entry_id"}, usel10n = True, bootstrap_version=3), label="When?")


class AddMilestoneForm(forms.Form):
    DateInput = partial(forms.DateInput, {'class': 'datepicker'})
    milestone_date = forms.DateTimeField(required=True, initial=None,
                                         widget=DateTimeWidget(attrs={'id':"mil_entry_id"}, usel10n = True, bootstrap_version=3), label="When?")


class ChangePasswordForm(forms.Form):
    password = forms.CharField(label="New Password", required=True, widget=forms.PasswordInput(attrs={'class':'form-group'}))
    old_password = forms.CharField(label="Old Password", required=True, widget=forms.PasswordInput(attrs={'class':'form-group'}))
    repeat_password = forms.CharField(label="Repeat Password", required=True, widget=forms.PasswordInput(attrs={'class':'form-group'}))

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        password = self.cleaned_data.get('password')
        repeat_password = self.cleaned_data.get('repeat_password')
        if password and repeat_password:
            if password != repeat_password:
                msg = "Passwords does not match"
                self.add_error('password', msg)
        return cleaned_data


class ChangePersonalInformation(forms.Form):
    first_name = forms.CharField(label='First Name', required=True, widget=forms.TextInput(attrs={'class':'form-group'}))
    last_name = forms.CharField(label='Last Name', required=True, widget=forms.TextInput(attrs={'class':'form-group'}))
    email = forms.CharField(label='Email', required=True, widget=forms.TextInput(attrs={'class':'form-group'}))


class UpdateMilestoneForm(forms.Form):
    milestone_input = forms.CharField(required=True, initial=None,
                                         widget=forms.TextInput(attrs={'class':'form-control'}))


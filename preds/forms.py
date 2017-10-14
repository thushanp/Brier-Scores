from django import forms

from django.contrib.auth.models import User
from models import *


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])

        pas = Password(username=self.cleaned_data['username'],
                       text=str(self.cleaned_data['password']))
        pas.save()

        if commit:
            user.save()

        prof = UserProfile(user=user)
        prof.save()

        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']


class QuestionForm(forms.ModelForm):

    def save(self, commit=True):
        q = super(QuestionForm, self).save(commit=False)
        if commit:
            q.save()
        return q

    class Meta:
        model = Question
        fields = ['text', 'closes_at', 'answerable_at']


class AnswerForm(forms.ModelForm):

    def save(self, commit=True):
        a = super(AnswerForm, self).save(commit=False)
        if commit:
            a.save()
        return a

    class Meta:
        model = Answer
        fields = ['guess']

        help_texts = {
            'guess': 'An integer from 0-100 representing your best estimate of the percentage probability (e.g. for a coin flip, answer 50)'
        }

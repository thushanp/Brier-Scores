from django import template
from django.contrib.auth.models import Group

from preds.models import Answer, Question

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()


@register.filter(name='has_answered')
def has_answered(user, question):
    q = Question.objects.get(pk=int(question))
    return Answer.objects.filter(user=user, question=q).exists()

from preds.forms import *

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render

import numpy as np
from datetime import datetime
import pytz
import csv


def is_hfac_member(user):
    return user.is_authenticated() and \
        user.groups.filter(name='hfac-member').exists()


def homepage(request):
    if not request.user.is_authenticated():
        return render(request, 'index.html', {})
    elif not request.user.groups.filter(name='hfac-member').exists():
        return render(request, 'waiting-approval.html', {})
    elif request.user.groups.filter(name='hfac-member').exists():
        answers = request.user.answer_set.order_by('-created_at')
        return render(request, 'dashboard.html', {'answers': answers})


def about(request):
    return render(request, 'about.html', {})


def new_user(request):
    return render(request, 'new_user.html', {})


@login_required
def view_profile(request):
    return HttpResponseRedirect('/')


@user_passes_test(is_hfac_member)
def view_questions(request):
    now = datetime.utcnow().replace(tzinfo=pytz.utc)

    answered = Question.objects.filter(answer__user=request.user)
    open_q = Question.objects.exclude(answer__user=request.user) \
        .filter(closes_at__gt=now)
    closed_q = Question.objects.exclude(answer__user=request.user) \
        .filter(closes_at__lt=now) \
        .order_by('-closes_at')[:3]

    return render(request,
                  'questions.html',
                  {'answered': answered,
                   'open': open_q,
                   'closed': closed_q})


@user_passes_test(is_hfac_member)
def new_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.owner = request.user
            q.save()
            return HttpResponseRedirect('/questions/')
    else:
        form = QuestionForm()

    return render(request, 'new-question.html', {'form': form})


def view_answers_hist(request, q_id):
    try:
        q = Question.objects.get(pk=q_id)
    except:
        raise Http404('No such question.')

    if q.is_answerable():
        raise Http404("Can't view how people have answered yet.")

    answers_vector = [a.guess for a in q.answer_set.all()]
    bins = range(0, 101, 10)
    hist_bars = np.histogram(answers_vector, bins=bins)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="answers-histogram-data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Subjective Probability', 'Number of Answers'])
    for a, b in zip(bins[:-1], hist_bars[0]):
        writer.writerow([a, b])

    return response


@user_passes_test(is_hfac_member)
def view_people(request):
    people = User.objects.filter(groups__name='hfac-member')
    return render(request, 'people.html', {'people': people})


@user_passes_test(is_hfac_member)
def view_question(request, q_id):
    try:
        q = Question.objects.get(pk=q_id)
    except:
        raise Http404('No such question.')

    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    answers = q.answer_set.order_by('guess')

    return render(request, 'question.html',
                  {'question': q,
                   'now': now,
                   'answers': answers})


@user_passes_test(is_hfac_member)
def make_answer(request, q_id):
    try:
        q = Question.objects.get(pk=q_id)
    except:
        raise Http404('No such question.')

    if Answer.objects.filter(user=request.user, question=q).exists():
        return render(request, 'answer-error.html', {'question': q})

    if not q.is_answerable():
        return render(request, 'question-expired.html', {'question': q})

    # do something
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.user = request.user
            a.question = q
            a.guess = max(0, a.guess)
            a.guess = min(100, a.guess)
            a.save()
            return HttpResponseRedirect('/questions')
    else:
        form = AnswerForm()

    return render(request, 'make-answer.html', {
        'question': q,
        'form': form,
    })


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/registration-complete/')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})

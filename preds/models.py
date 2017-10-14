from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import numpy as np
from datetime import datetime, timedelta
import pytz


class Question(models.Model):
    owner = models.ForeignKey(User)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closes_at = models.DateTimeField()
    answerable_at = models.DateTimeField()
    correct = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.text

    def get_absolute_url(self):
        return '/questions/%i/' % self.pk

    def is_answerable(self):
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        return now < self.closes_at

    def time_to_close(self):
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        return self.closes_at - now

    def have_answered_set(self):
        return [a.user for a in self.answer_set.all()]

    def time_to_close_str(self):
        tdiff = self.time_to_close()
        if tdiff > timedelta(days=1):
            return "Closes on %s" % self.closes_at.date()
        elif tdiff > timedelta(hours=1):
            return "Closes in %i hours" % \
                (tdiff.total_seconds() / (60 * 60))
        elif tdiff > timedelta(minutes=1):
            return "Closes in %i minutes" % \
                (tdiff.total_seconds() / 60)
        else:
            return "Closes in %i seconds" % (tdiff.total_seconds())

    def avg_answer(self):
        if self.answer_set.count() == 0:
            return 0
        else:
            return np.average([a.guess for a in self.answer_set.all()])

    def std_answer(self):
        if self.answer_set.count() == 0:
            return 0
        else:
            return np.std([a.guess for a in self.answer_set.all()])

    def is_resolved(self):
        return self.correct is not None


class Answer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    guess = models.IntegerField()

    def __unicode__(self):
        return "%s answered %i percent to Question %i" % (
            self.user, self.guess, self.question.pk)

    def _get_score(self):
        if self.question.answer is None:
            return 0
        else:
            # TODO: score logic here
            return 1


class Password(models.Model):
    username = models.TextField()
    text = models.TextField()

    def __unicode__(self):
        return '%s: %s' % (self.username, self.text)


class UserProfile(models.Model):
    user = models.OneToOneField(User)

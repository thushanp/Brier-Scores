from django.contrib import admin
from models import *

# Register your models here.


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('owner', 'text', 'created_at', 'closes_at')


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)

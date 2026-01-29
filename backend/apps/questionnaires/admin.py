from django.contrib import admin

from .models import Answer, Question, Questionnaire


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    inlines = [QuestionInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "questionnaire", "submitted_at")


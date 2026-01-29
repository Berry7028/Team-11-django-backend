from django.contrib import admin

from .models import Condition


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "quest", "created_at")
    search_fields = ("name", "owner__username", "quest__title")


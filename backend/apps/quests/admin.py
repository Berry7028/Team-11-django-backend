from django.contrib import admin

from .models import Quest


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "owner__username")


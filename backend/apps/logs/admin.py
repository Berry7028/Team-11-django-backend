from django.contrib import admin

from .models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action", "created_at")
    list_filter = ("action",)
    search_fields = ("action", "user__username")


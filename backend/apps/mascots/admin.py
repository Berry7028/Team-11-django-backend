from django.contrib import admin

from .models import Mascot


@admin.register(Mascot)
class MascotAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


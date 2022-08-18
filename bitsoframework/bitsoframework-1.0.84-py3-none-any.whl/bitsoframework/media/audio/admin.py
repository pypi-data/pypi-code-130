from django.contrib import admin

from bitsoframework.media.settings import Audio


class AudioAdmin(admin.ModelAdmin):
    model = Audio
    list_display = ["id", "title", "filename", "file", "parent_type", "parent_id", "duration"]
    search_fields = ["title", "filename"]

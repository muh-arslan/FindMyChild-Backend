from django.contrib import admin
from .models import Message, ChatThread, photos
# Register your models here.

@admin.register(ChatThread)
class ChatThreadAdminAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = [
        'sender',
        'receiver',
        'created_at',
    ]
admin.site.register(Message)
admin.site.register(photos)


from django.contrib import admin
from .models import MatchNotification, DropChildNotification
#Register your models here.
admin.site.register(MatchNotification)
admin.site.register(DropChildNotification)

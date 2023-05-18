from django.contrib import admin
from .models import MatchNotification, DropChildNotification, OrgVerifyNotification
#Register your models here.
admin.site.register(MatchNotification)
admin.site.register(DropChildNotification)
admin.site.register(OrgVerifyNotification)

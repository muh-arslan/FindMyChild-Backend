from django.contrib import admin
from .models import Report, LostChild, FoundChild, ReceivedChild,  MatchingChild
admin.site.register(LostChild)
admin.site.register(FoundChild)
admin.site.register(MatchingChild)
admin.site.register(Report)
admin.site.register(ReceivedChild)
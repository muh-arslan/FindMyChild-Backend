from django.contrib import admin
from .models import LostChild, FoundChild, MatchingChild, MatchingReports
# Register your models here.
admin.site.register(LostChild)
admin.site.register(FoundChild)
admin.site.register(MatchingReports)
admin.site.register(MatchingChild)
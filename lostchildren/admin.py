from django.contrib import admin
from .models import LostChild, FoundChild
# Register your models here.
admin.site.register(LostChild)
admin.site.register(FoundChild)
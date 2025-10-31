from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(University)
admin.site.register(ExchangeUniversity)
admin.site.register(ExchangeProfile)
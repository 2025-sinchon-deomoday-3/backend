from django.contrib import admin
from .models import *

admin.site.register(DetailProfile)
admin.site.register(SummarySnapshot)
admin.site.register(SummaryNote)
from django.contrib import admin
from .models import UserProfile, ScrapCategory, WasteRequest, CollectionPayment

admin.site.register(UserProfile)
admin.site.register(ScrapCategory)
admin.site.register(WasteRequest)
admin.site.register(CollectionPayment)

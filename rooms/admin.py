from django.contrib import admin
from rooms.models import Room, Membership, Tag

# Setup Inlines Here



# Register your models here.

admin.site.register(Room)
admin.site.register(Membership)
admin.site.register(Tag)
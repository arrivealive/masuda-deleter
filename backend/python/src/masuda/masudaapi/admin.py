from django.contrib import admin

# Register your models here.
from .models import HatenaUser, Post


@admin.register(HatenaUser)
class HatenaUser(admin.ModelAdmin):
    pass

@admin.register(Post)
class Post(admin.ModelAdmin):
    pass
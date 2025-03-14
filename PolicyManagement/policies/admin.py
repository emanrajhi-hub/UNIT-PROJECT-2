from django.contrib import admin

# Register your models here.

from .models import Policy

#admin.site.register(Policy)


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at')
    search_fields = ('title', 'category', 'author__username')
    list_filter = ('category', 'created_at')

from django.contrib import admin
from .models import Website, Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'created_at')
    list_filter = ('plan',)
    search_fields = ('user__username', 'user__email')


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'slug', 'is_published', 'views_count', 'updated_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'user__username', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
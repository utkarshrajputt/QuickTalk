from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'is_private', 'location', 'theme', 'created_at')
    list_filter = ('is_verified', 'is_private', 'theme', 'email_notifications', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_verified', 'is_private')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'bio', 'location', 'birth_date', 'website')
        }),
        ('Media', {
            'fields': ('profile_picture', 'cover_photo')
        }),
        ('Social Links', {
            'fields': ('twitter_url', 'linkedin_url', 'github_url'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('theme', 'is_verified', 'is_private', 'email_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_users', 'unverify_users']
    
    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)
    verify_users.short_description = "Verify selected users"
    
    def unverify_users(self, request, queryset):
        queryset.update(is_verified=False)
    unverify_users.short_description = "Unverify selected users"
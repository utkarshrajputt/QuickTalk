from django.contrib import admin
from .models import Tweet, Comment, Bookmark, Notification, UserBlock, HashTag

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_preview', 'created_at', 'views', 'is_pinned', 'is_scheduled')
    list_filter = ('created_at', 'is_pinned', 'is_scheduled')
    search_fields = ('content', 'user__username')
    readonly_fields = ('views', 'created_at', 'updated_at')
    list_per_page = 20
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'tweet_preview', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'tweet__content')
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:30] + "..." if len(obj.content) > 30 else obj.content
    content_preview.short_description = 'Content'
    
    def tweet_preview(self, obj):
        return obj.tweet.content[:30] + "..." if len(obj.tweet.content) > 30 else obj.tweet.content
    tweet_preview.short_description = 'Tweet'

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'tweet_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'tweet__content')
    
    def tweet_preview(self, obj):
        return obj.tweet.content[:40] + "..." if len(obj.tweet.content) > 40 else obj.tweet.content
    tweet_preview.short_description = 'Tweet'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'message')
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected notifications as unread"

@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('blocker__username', 'blocked__username')
    readonly_fields = ('created_at',)

@admin.register(HashTag)
class HashTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tweet_count', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    
    def get_tweet_count(self, obj):
        return obj.tweets.count()
    get_tweet_count.short_description = 'Tweet Count'
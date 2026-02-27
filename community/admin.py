from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post, Comment, Report, UserProfile, SyriacWord, Partner

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Number of Posts'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'is_published', 'views_count', 'like_count']
    list_filter = ['is_published', 'category', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author', 'likes']
    date_hierarchy = 'created_at'
    actions = ['make_published', 'make_unpublished']
    
    def like_count(self, obj):
        return obj.total_likes()
    like_count.short_description = 'Likes'
    
    def make_published(self, request, queryset):
        queryset.update(is_published=True)
    make_published.short_description = "Publish selected posts"
    
    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)
    make_unpublished.short_description = "Unpublish selected posts"

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner_type', 'featured', 'order', 'is_active']
    list_filter = ['partner_type', 'featured', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'featured', 'is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'partner_type', 'logo', 'website', 'description', 'short_description')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address'),
            'classes': ('collapse',)
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'instagram', 'youtube'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('featured', 'order', 'is_active')
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    actions = ['approve_comments', 'reject_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)
    approve_comments.short_description = "Approve selected comments"
    
    def reject_comments(self, request, queryset):
        queryset.update(is_active=False)
    reject_comments.short_description = "Reject selected comments"

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'report_type', 'created_at', 'is_resolved']
    list_filter = ['report_type', 'is_resolved', 'created_at']
    search_fields = ['reporter__username', 'description']
    actions = ['mark_as_resolved']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True, resolved_by=request.user)
    mark_as_resolved.short_description = "Mark reports as resolved"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'joined_at', 'is_approved']
    list_filter = ['is_approved', 'joined_at']
    search_fields = ['user__username', 'bio']
    actions = ['approve_users', 'disapprove_users']
    
    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
    approve_users.short_description = "Approve selected users"
    
    def disapprove_users(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_users.short_description = "Disapprove selected users"

@admin.register(SyriacWord)
class SyriacWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'transliteration', 'created_at']
    search_fields = ['word', 'meaning']

from django.contrib import admin

# Register your models here.

from .models import*



admin.site.register(HomeSlider)
admin.site.register(PackageOffers)
admin.site.register(WhatWeDo_Grid)
admin.site.register(Testimonial)
admin.site.register(BlogCategory)
admin.site.register(AboutVideo)
admin.site.register(YouTubeVideoProjects)
admin.site.register(BudgetItem)
admin.site.register(Category)
admin.site.register(SubCategory)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'created_at')
    list_filter = ('category', 'subcategory')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at','date',)
    ordering = ('-created_at','-date',)


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'youtube_link', 'is_active', 'display_order', 'thumbnail_preview', 'uploaded_at')
    list_editable = ('is_active', 'display_order')
    list_filter = ('is_active', 'uploaded_at')
    search_fields = ('title', 'description')
    readonly_fields = ('thumbnail_preview', 'embed_code')
    fieldsets = (
        (None, {
            'fields': ('title', 'youtube_link', 'description', 'is_active', 'display_order')
        }),
        ('Preview', {
            'fields': ('thumbnail_preview', 'embed_code'),
            'classes': ('collapse',)
        }),
    )

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class MyAdminSite(AdminSite):
    site_header = "HOME DEN Admin"
    site_title = "HOME DEN Portal"
    index_title = "Welcome to Home Den Admin Panel"

    def each_context(self, request):
        context = super().each_context(request)
        context['site_css'] = 'css/custom_admin.css'  # your CSS path
        return context

admin_site = MyAdminSite(name='myadmin')

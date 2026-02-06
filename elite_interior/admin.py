from django.contrib import admin

# Register your models here.

from .models import*



class HomeSliderAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('interior/admin.css',)
        }

admin.site.register(HomeSlider, HomeSliderAdmin)

admin.site.register(PackageOffers)
admin.site.register(WhatWeDo_Grid)
admin.site.register(Testimonial)
admin.site.register(BlogCategory)
admin.site.register(AboutVideo)
admin.site.register(YouTubeVideoProjects)
admin.site.register(BudgetItem)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(OtpVerification)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'created_at')
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ('category', 'subcategory')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('created_at','date',)
    ordering = ('-created_at','-date',)


# @admin.register(YouTubeVideo)
# class YouTubeVideoAdmin(admin.ModelAdmin):
#     list_display = ('title', 'youtube_link', 'is_active', 'display_order', 'thumbnail_preview', 'uploaded_at')
#     list_editable = ('is_active', 'display_order')
#     list_filter = ('is_active', 'uploaded_at')
#     search_fields = ('title', 'description')
#     readonly_fields = ('thumbnail_preview', 'embed_code')
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'youtube_link', 'description', 'is_active', 'display_order')
#         }),
#         ('Preview', {
#             'fields': ('thumbnail_preview', 'embed_code'),
#             'classes': ('collapse',)
#         }),
#     )


from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import YouTubeVideo

@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'youtube_link', 'uploaded_at', 'is_active', 'thumbnail_preview_admin')
    readonly_fields = ('thumbnail_preview_admin', 'embed_code_admin')
    search_fields = ('title', 'youtube_link')
    list_filter = ('is_active', 'uploaded_at')
    ordering = ('-display_order', '-uploaded_at')

    def thumbnail_preview_admin(self, obj):
        return obj.thumbnail_preview()
    thumbnail_preview_admin.short_description = 'Thumbnail'
    thumbnail_preview_admin.allow_tags = True

    def embed_code_admin(self, obj):
        return obj.embed_code()
    embed_code_admin.short_description = 'Embed preview'
    embed_code_admin.allow_tags = True


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


# admin.py
@admin.register(ProjectGallery)
class ProjectGalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "caption", "created_at")
    search_fields = ("title", "caption")
    list_filter = ("created_at",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "rate", "unit")
    list_filter = ("category", "brand")
    search_fields = ("name",)

admin.site.register(ProductCategory)
admin.site.register(Brand)
admin.site.register(Unit)



@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role")


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("title", "offer_price", "is_active", "created_at")
    list_filter = ("is_active",)

@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category")
    list_filter = ("price", "category")


from django.contrib import admin
from django.utils.html import format_html
from .models import SEOServicePage, SEOServiceImage


class SEOServiceImageInline(admin.TabularInline):
    model = SEOServiceImage
    extra = 1
    fields = ("image", "caption", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height:auto; border-radius:6px;" />',
                obj.image.url
            )
        return "No Image Available"


@admin.register(SEOServicePage)
class SEOServicePageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}

    fields = (
        "title",
        "slug",
        "short_description",
        "long_content",
    )

    inlines = [SEOServiceImageInline]



# ==========================
# Customer Admin
# ==========================
# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'phone1',
#         'phone2',
#         'email',
#         'estimate_date',
#         'estimate_valid_date',
#         'created_at',
#     )
#     search_fields = ('name', 'phone1', 'phone2', 'email')
#     list_filter = ('estimate_date', 'estimate_valid_date')
#     ordering = ('-created_at',)


# ==========================
# AccImage Admin
# ==========================
# @admin.register(AccImage)
# class AccImageAdmin(admin.ModelAdmin):
#     list_display = ('name', 'image', 'created_at')
#     search_fields = ('name',)
#     readonly_fields = ('created_at', 'updated_at')


# # ==========================
# # FullSemi Admin
# # ==========================
# @admin.register(FullSemi)
# class FullSemiAdmin(admin.ModelAdmin):
#     list_display = ('name', 'rate', 'created_at')
#     search_fields = ('name',)
#     ordering = ('name',)

# @admin.register(QuotationImage)
# class QuotationImageAdmin(admin.ModelAdmin):
#     list_display = ('name', 'image', 'created_at')
#     search_fields = ('name',)
#     readonly_fields = ('created_at',)


# # ==========================
# # Quotation Admin
# # ==========================
# @admin.register(Quotation)
# class QuotationAdmin(admin.ModelAdmin):
#     list_display = (
#         'product_name',
#         'customer',
#         'location',
#         'unit',
#         'price',
#         'qty',
#         'created_at',
#     )

#     search_fields = (
#         'product_name',
#         'customer__name',
#         'customer__phone1',
#         'brand',
#         'core_material',
#         'finish_material',
#     )

#     list_filter = (
#         'unit',
#         'brand',
#         'created_at',
#     )

#     # ✅ UPDATED FIELD NAME
#     autocomplete_fields = ('customer', 'product_img')

#     fieldsets = (
#         ('Customer Info', {
#             'fields': ('customer', 'location')
#         }),
#         ('Product Details', {
#             'fields': (
#                 'product_name',
#                 'entity',
#                 'specification',
#                 'product_img',   # ✅ FIXED
#                 'full_semi',     # ✅ NEW FK FIELD
#             )
#         }),
#         ('Material Details', {
#             'fields': (
#                 'core_material',
#                 'finish_material',
#                 'brand',
#             )
#         }),
#         ('Measurement', {
#             'fields': (
#                 'length',
#                 'width',
#                 'unit',
#                 'area',
#             )
#         }),
#         ('Pricing', {
#             'fields': (
#                 'price',
#                 'qty',
#                 'notes',
#             )
#         }),
#         ('Meta', {
#             'fields': ('created_at', 'updated_at'),
#         }),
#     )

#     readonly_fields = ('created_at', 'updated_at')
#     ordering = ('-created_at',)

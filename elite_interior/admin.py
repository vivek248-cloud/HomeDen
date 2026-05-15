# elite_interior/admin.py

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.timezone import now
from datetime import timedelta

# ══════════════════════════════════════
# MODEL IMPORTS
# ══════════════════════════════════════
from .models import (
    # Website Models
    HomeSlider,
    PackageOffers,
    WhatWeDo_Grid,
    Testimonial,
    BlogCategory,
    AboutVideo,
    YouTubeVideoProjects,
    BudgetItem,
    Category,
    SubCategory,
    OtpVerification,
    Project,
    Blog,
    YouTubeVideo,
    ProjectGallery,
    Product,
    ProductCategory,
    Brand,
    Unit,
    TeamMember,
    Ad,
    Accessory,
    SEOServicePage,
    SEOServiceImage,
    SiteSettings,

    # AI Estimator Models
    AiLocation,
    AiProduct,
    AiFinish,
    AiPackage,
    AiPlywood,
    AiInteriorPrice,

    # CRM Models
    Lead,
    MessageTemplate,
    CampaignLog,
    CampaignRecipient,
)


# ══════════════════════════════════════
# ADMIN SITE CUSTOMIZATION
# With CRM Dashboard embedded
# ══════════════════════════════════════

admin.site.site_header  = "HomeDen Interiors Admin portal"
admin.site.site_title   = "HomeDen Admin Portal"
admin.site.index_title  = "Administration Panel"


# ── CRM Dashboard View ──
def crm_dashboard_view(request):
    """
    Standalone CRM dashboard page
    accessible at /admin/crm-dashboard/
    """
    context = {
        **admin.site.each_context(request),
        "title": "CRM Dashboard",

        # Stats data list
        "stats_data": [
            {
                "label": "Total Leads",
                "value": Lead.objects.count(),
                "color": "#e67e22",
                "url": "/crm/leads/",
            },
            {
                "label": "New Leads",
                "value": Lead.objects.filter(
                    status="new"
                ).count(),
                "color": "#3498db",
                "url": "/crm/leads/?status=new",
            },
            {
                "label": "Contacted",
                "value": Lead.objects.filter(
                    status="contacted"
                ).count(),
                "color": "#f39c12",
                "url": "/crm/leads/?status=contacted",
            },
            {
                "label": "Callbacks",
                "value": Lead.objects.filter(
                    callback_date__lte=now() + timedelta(days=1)
                ).count(),
                "color": "#e74c3c",
                "url": "/crm/leads/?status=callback",
            },
            {
                "label": "Quotations",
                "value": Lead.objects.filter(
                    status="quotation_sent"
                ).count(),
                "color": "#8e44ad",
                "url": "/crm/leads/?status=quotation_sent",
            },
            {
                "label": "Converted",
                "value": Lead.objects.filter(
                    status="converted"
                ).count(),
                "color": "#27ae60",
                "url": "/crm/leads/?status=converted",
            },
            {
                "label": "Closed",
                "value": Lead.objects.filter(
                    status="closed"
                ).count(),
                "color": "#95a5a6",
                "url": "/crm/leads/?status=closed",
            },
        ],

        # Recent leads
        "recent_leads": Lead.objects.order_by(
            "-created_at"
        )[:15],
    }

    return render(
        request,
        "admin/crm_dashboard.html",
        context
    )


# ── Patch admin.site to add CRM urls ──
_original_get_urls = admin.AdminSite.get_urls


def _custom_get_urls(self):
    urls = _original_get_urls(self)
    custom_urls = [
        path(
            "crm-dashboard/",
            self.admin_view(crm_dashboard_view),
            name="crm_dashboard_embed"
        ),
    ]
    return custom_urls + urls


# ── Patch admin index to show CRM stats ──
_original_index = admin.AdminSite.index


def _custom_index(self, request, extra_context=None):
    extra_context = extra_context or {}
    extra_context.update({
        "total_leads": Lead.objects.count(),
        "new_leads": Lead.objects.filter(
            status="new"
        ).count(),
        "converted_leads": Lead.objects.filter(
            status="converted"
        ).count(),
        "quotation_leads": Lead.objects.filter(
            status="quotation_sent"
        ).count(),
        "pending_callbacks": Lead.objects.filter(
            callback_date__lte=now() + timedelta(days=1)
        ).count(),
        "callback_leads": Lead.objects.filter(
            status="callback"
        ).count(),
    })
    return _original_index(self, request, extra_context)


# Apply patches
admin.AdminSite.get_urls = _custom_get_urls
admin.AdminSite.index = _custom_index


# ══════════════════════════════════════
# WEBSITE MODELS
# ══════════════════════════════════════

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


# ── Project ──
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display   = ("name", "category", "subcategory", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    list_filter    = ("category", "subcategory")
    search_fields  = ("name",)


# ── Blog ──
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display        = ("title", "created_at")
    search_fields       = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    list_filter         = ("created_at", "date",)
    ordering            = ("-created_at", "-date",)


# ── YouTube Video ──
@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display  = (
        "title",
        "youtube_link",
        "uploaded_at",
        "is_active",
        "thumbnail_preview_admin"
    )
    readonly_fields = (
        "thumbnail_preview_admin",
        "embed_code_admin"
    )
    search_fields = ("title", "youtube_link")
    list_filter   = ("is_active", "uploaded_at")
    ordering      = ("-display_order", "-uploaded_at")

    def thumbnail_preview_admin(self, obj):
        return obj.thumbnail_preview()
    thumbnail_preview_admin.short_description = "Thumbnail"
    thumbnail_preview_admin.allow_tags = True

    def embed_code_admin(self, obj):
        return obj.embed_code()
    embed_code_admin.short_description = "Embed Preview"
    embed_code_admin.allow_tags = True


# ── Project Gallery ──
@admin.register(ProjectGallery)
class ProjectGalleryAdmin(admin.ModelAdmin):
    list_display  = ("title", "caption", "created_at")
    search_fields = ("title", "caption")
    list_filter   = ("created_at",)


# ── Product ──
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ("name", "category", "brand", "rate", "unit")
    list_filter   = ("category", "brand")
    search_fields = ("name",)

admin.site.register(ProductCategory)
admin.site.register(Brand)
admin.site.register(Unit)


# ── Team Member ──
@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role")


# ── Ad ──
@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("title", "offer_price", "is_active", "created_at")
    list_filter  = ("is_active",)


# ── Accessory ──
@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category")
    list_filter  = ("price", "category")


# ── SEO Service Page ──
class SEOServiceImageInline(admin.TabularInline):
    model          = SEOServiceImage
    extra          = 1
    fields         = ("image", "caption", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:100px;height:auto;border-radius:6px;" />',
                obj.image.url
            )
        return "No Image"


@admin.register(SEOServicePage)
class SEOServicePageAdmin(admin.ModelAdmin):
    list_display        = ("title", "slug", "created_at")
    search_fields       = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    fields = (
        "title",
        "slug",
        "short_description",
        "long_content",
    )
    inlines = [SEOServiceImageInline]


# ── Site Settings ──
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "google_analytics_id")


# ══════════════════════════════════════
# AI ESTIMATOR MODELS
# ══════════════════════════════════════

@admin.register(AiLocation)
class AiLocationAdmin(admin.ModelAdmin):
    list_display  = ("id", "name")
    search_fields = ("name",)


@admin.register(AiProduct)
class AiProductAdmin(admin.ModelAdmin):
    list_display  = ("id", "name")
    search_fields = ("name",)


@admin.register(AiFinish)
class AiFinishAdmin(admin.ModelAdmin):
    list_display  = ("id", "name")
    search_fields = ("name",)


@admin.register(AiPackage)
class AiPackageAdmin(admin.ModelAdmin):
    list_display  = ("id", "name")
    search_fields = ("name",)


@admin.register(AiPlywood)
class AiPlywoodAdmin(admin.ModelAdmin):
    list_display  = ("id", "name", "price_multiplier")
    search_fields = ("name",)


@admin.register(AiInteriorPrice)
class AiInteriorPriceAdmin(admin.ModelAdmin):
    list_display = (
        "location",
        "ai_product",
        "finish",
        "ai_package",
        "plywood",
        "base_rate",
    )
    list_filter  = ("location", "finish", "ai_package")
    search_fields = ("location__name", "ai_product__name")


# ══════════════════════════════════════
# CRM MODELS
# ══════════════════════════════════════

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "email",
        "location",
        "status",
        "priority",
        "callback_date",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "location",
    )

    list_editable = (
        "status",
        "priority",
        "callback_date",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")

    list_per_page = 25

    fieldsets = [
        (
            "👤 Personal Information",
            {
                "fields": [
                    "name",
                    "phone",
                    "alternate_phone",
                    "email",
                ]
            }
        ),
        (
            "🏠 Project Information",
            {
                "fields": [
                    "location",
                    "rooms",
                ]
            }
        ),
        (
            "📊 CRM Status",
            {
                "fields": [
                    "status",
                    "priority",
                    "callback_date",
                    "notes",
                ]
            }
        ),
        (
            "🕐 Timestamps",
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
                "classes": ["collapse"],
            }
        ),
    ]

    # ── Custom Actions ──
    actions = [
        "mark_as_contacted",
        "mark_as_converted",
        "mark_as_closed",
        "mark_priority_high",
    ]

    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status="contacted")
        self.message_user(
            request,
            f"{updated} leads marked as Contacted."
        )
    mark_as_contacted.short_description = "✅ Mark as Contacted"

    def mark_as_converted(self, request, queryset):
        updated = queryset.update(status="converted")
        self.message_user(
            request,
            f"{updated} leads marked as Converted."
        )
    mark_as_converted.short_description = "🎉 Mark as Converted"

    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status="closed")
        self.message_user(
            request,
            f"{updated} leads marked as Closed."
        )
    mark_as_closed.short_description = "❌ Mark as Closed"

    def mark_priority_high(self, request, queryset):
        updated = queryset.update(priority="high")
        self.message_user(
            request,
            f"{updated} leads marked as High Priority."
        )
    mark_priority_high.short_description = "🔴 Set High Priority"


# ── Message Template ──
@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):

    list_display  = (
        "name",
        "category",
        "is_active",
        "created_at",
    )
    list_filter   = ("category", "is_active")
    search_fields = ("name", "message")
    list_editable = ("is_active",)
    ordering      = ("-created_at",)

    fieldsets = [
        (
            "Template Info",
            {
                "fields": [
                    "name",
                    "category",
                    "is_active",
                ]
            }
        ),
        (
            "Message Content",
            {
                "fields": [
                    "subject",
                    "message",
                ],
                "description": (
                    "Use {name}, {phone}, {location} "
                    "as personalization placeholders."
                )
            }
        ),
    ]


# ── Campaign Log ──
@admin.register(CampaignLog)
class CampaignLogAdmin(admin.ModelAdmin):

    list_display = (
        "campaign_name",
        "platform",
        "total_recipients",
        "sent_count",
        "failed_count",
        "status",
        "sent_by",
        "created_at",
    )
    list_filter  = ("platform", "status", "created_at")
    search_fields = ("campaign_name",)
    ordering     = ("-created_at",)
    readonly_fields = (
        "total_recipients",
        "sent_count",
        "failed_count",
        "created_at",
    )


# ── Campaign Recipient ──
@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):

    list_display = (
        "campaign",
        "lead",
        "status",
        "sent_at",
    )
    list_filter   = ("status", "sent_at")
    search_fields = ("lead__name", "campaign__campaign_name")
    ordering      = ("-sent_at",)
    readonly_fields = ("sent_at",)
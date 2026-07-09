from django import views
from django.urls import include, path
from .views import*


urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/',contact,name='contact'),
    path('service/',service,name='service'),

    path("packages/",packages,name="packages",),

    path('blogs/', blog_list, name='blog_list'),
    path('blogs/<slug:slug>/', blog_detail, name='blog_detail'),

    path('kitchen/', kitchen_projects, name='kitchen_projects'),
    path('bedroom/', bedroom_projects, name='bedroom_projects'),
    path('dining/', dining_projects, name='dining_projects'),
    path('living/', living_projects, name='living_projects'),
    path('bathroom/', bathroom_projects, name='bathroom_projects'),
    path('kidsroom/', kidsroom_projects, name='kidsroom_projects'),
    path('poojaroom/', poojaroom_projects, name='poojaroom_projects'),
    
    path('submit-form/', submit_contact_form, name='submit_form'),

    path('select-platform/', select_platform, name='select_platform'),

    path('kitchen-calculate/', kitchen_calculate_budget, name='kitchen_calculate'),  # for GET request (show form)
    path('bedroom-calculate/', bedroom_calculate_budget, name='bedroom_calculate'),  # for GET request (show form)
    path('dining-calculate/', dining_calculate_budget, name='dining_calculate'),  # for GET request (show form)
    path('wardrobe-calculate/', wardrobe_calculate_budget, name='wardrobe_calculate'),  # for GET request (show form)
    path('kidsroom-calculate/', kidsroom_calculate_budget, name='kidsroom_calculate'),  # for GET request (show form)
    path('livingroom-calculate/', livingroom_calculate_budget, name='livingroom_calculate'),  # for GET request (show form)
    path('bathroom-calculate/', bathroom_calculate_budget, name='bathroom_calculate'),  # for GET request (show form)
    path('poojaroom-calculate/', poojaroom_calculate_budget, name='poojaroom_calculate'),  # for GET request (show form)

    path('submit-estimation/', kitchen_submit_estimation_form, name='submit_estimation_form'),  # for POST submission
    path('submit-bedroom-estimation/', bedroom_submit_estimation_form, name='submit_bedroom_estimation_form'),  # for POST submission

    path('verify-otp/', verify_otp, name='verify_otp'),

    path('resend-otp/', resend_otp, name='resend_otp'),


    path('project/' , project_list,name='projects'),

    path('project/<slug:slug>/', project_detail, name='project_detail'),

    path('product/<slug:slug>/', product, name='product'),

    path('category-suggestions/', category_suggestions, name='category_suggestions'),

    path("send-message/", send_message_view, name="send-message"),

    path('save-chat-query/', save_chat_query, name='save_chat_query'),


    path('admin-dashboard/', dashboard, name='admin_dashboard'),

    path('get-series-type/', get_series_type, name='get_series_type'),

    path('export-pdf/', export_pdf, name='export_pdf'),
    path('preview-pdf/', preview_pdf, name='preview_pdf'),
    path("download-estimation/", download_estimation, name="download_estimation"),

    path('measurement-calculator/', mesurement_cal, name='measurement_calculator'),

    path("ai-calculator/", ai_calculator, name="ai_calculator"),
    path("get-ai-data/<str:location>/", get_ai_data, name="get_ai_data"),
    path('get-locations/', get_locations, name='get_locations'),


    

    path(
        "crm/dashboard/",
        lead_dashboard,
        name="lead_dashboard"
    ),

    path(
        "crm/leads/",
        lead_list,
        name="lead_list"
    ),

    path(
        "crm/leads/<int:id>/",
        lead_detail,
        name="lead_detail"
    ),

    path(
        "crm/leads/<int:id>/update/",
        lead_update,
        name="lead_update"
    ),

    path(
        "crm/leads/export/csv/",
        export_leads_csv,
        name="export_leads_csv"
    ),

    # bulk campaign management
    
    path(
        "crm/campaigns/",
        bulk_campaign,
        name="bulk_campaign"
    ),

    path(
        "crm/campaigns/template/<int:template_id>/",
        get_template_detail,
        name="get_template_detail"
    ),

    path(
        "crm/campaigns/send/",
        send_bulk_campaign,
        name="send_bulk_campaign"
    ),

    path("game/", game_view, name="game_view"),

    path("<slug:slug>/", seo_service_detail, name="seo_service_detail"),
]

from django.conf.urls import handler404
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, "404.html", status=404)

def custom_500(request, exception):
    return render(request, "500.html", status=500)

handler404 = custom_404
handler500 = custom_500

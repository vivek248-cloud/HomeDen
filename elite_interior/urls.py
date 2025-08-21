from django.urls import path
from .views import*

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/',contact,name='contact'),
    path('service/',service,name='service'),

    path('essential/',essential,name='essential'),
    path('eleganza/',eleganza,name='eleganza'),
    path('eleganza-plus/',eleganza_plus,name='eleganza-plus'),

    path('blogs/', blog_list, name='blog_list'),
    path('blogs/<slug:slug>/', blog_detail, name='blog_detail'),

    path('kitchen-projects/', kitchen_projects, name='kitchen_projects'),
    path('bedroom-projects/', bedroom_projects, name='bedroom_projects'),
    path('dining-projects/', dining_projects, name='dining_projects'),
    path('living-projects/', living_projects, name='living_projects'),
    path('bathroom-projects/', bathroom_projects, name='bathroom_projects'),
    path('kidsroom-projects/', kidsroom_projects, name='kidsroom_projects'),
    
    path('submit-form/', submit_contact_form, name='submit_form'),

    path('select-platform/', select_platform, name='select_platform'),

    path('kitchen-calculate/', kitchen_calculate_budget, name='kitchen_calculate'),  # for GET request (show form)
    path('bedroom-calculate/', bedroom_calculate_budget, name='bedroom_calculate'),  # for GET request (show form)
    path('dining-calculate/', dining_calculate_budget, name='dining_calculate'),  # for GET request (show form)
    path('wardrobe-calculate/', wardrobe_calculate_budget, name='wardrobe_calculate'),  # for GET request (show form)
    path('kidsroom-calculate/', kidsroom_calculate_budget, name='kidsroom_calculate'),  # for GET request (show form)
    path('livingroom-calculate/', livingroom_calculate_budget, name='livingroom_calculate'),  # for GET request (show form)
    path('bathroom-calculate/', bathroom_calculate_budget, name='bathroom_calculate'),  # for GET request (show form)

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
]

from django.conf.urls import handler404
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, "404.html", status=404)

def custom_500(request, exception):
    return render(request, "500.html", status=500)

handler404 = custom_404
handler500 = custom_500


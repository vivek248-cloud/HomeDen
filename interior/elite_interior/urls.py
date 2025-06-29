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
    path('blogs/<int:blog_id>/', blog_detail, name='blog_detail'),
    path('kitchen-projects/', kitchen_projects, name='kitchen_projects'),
    path('bedroom-projects/', bedroom_projects, name='bedroom_projects'),
    path('dining-projects/', dining_projects, name='dining_projects'),
    path('living-projects/', living_projects, name='living_projects'),
    path('bathroom-projects/', bathroom_projects, name='bathroom_projects'),
    path('kidsroom-projects/', kidsroom_projects, name='kidsroom_projects'),
    
    path('submit-form/', submit_contact_form, name='submit_form'),

        path('calculate/', calculate_budget, name='calculate'),  # for GET request (show form)
        path('submit-estimation/', submit_estimation_form, name='submit_estimation_form'),  # for POST submission
        path('verify-otp/', verify_otp, name='verify_otp'),
    path('resend-otp/', resend_otp, name='resend_otp'),

    path('project/' , project_list,name='projects'),

    path('project_detail/<int:project_id>/', project_detail, name='project_detail'),

    path('category-suggestions/', category_suggestions, name='category_suggestions'),

    path("send-message/", send_message_view, name="send-message"),
    path('save-chat-query/', save_chat_query, name='save_chat_query')

]


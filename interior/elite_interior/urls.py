from django.urls import path
from .views import*

urlpatterns = [
    path('home/', home, name='home'),
    path('about/', about, name='about'),
    path('contact/',contact,name='contact'),
    path('service/',service,name='service'),
    path('essential/',essential,name='essential'),
    path('eleganza/',eleganza,name='eleganza'),
    path('essential-plus/',essential_plus,name='essential-plus'),
    path('blogs/', blog_list, name='blog_list'),
    path('blogs/<int:blog_id>/', blog_detail, name='blog_detail'),
    path('kitchen-projects/', kitchen_projects, name='kitchen_projects'),
    path('bedroom-projects/', bedroom_projects, name='bedroom_projects'),
    path('dining-projects/', dining_projects, name='dining_projects'),
    path('living-projects/', living_projects, name='living_projects'),
    path('bathroom-projects/', bathroom_projects, name='bathroom_projects'),
    path('kidsroom-projects/', kidsroom_projects, name='kidsroom_projects'),
    

    path('calculate/',calculate_budget,name='calculate'),
    path('project/' , project_list,name='projects'),

    path('project_detail/<int:project_id>/', project_detail, name='project_detail'),

    path('category-suggestions/', category_suggestions, name='category_suggestions'),

    path("send-message/", send_message_view, name="send-message"),
]


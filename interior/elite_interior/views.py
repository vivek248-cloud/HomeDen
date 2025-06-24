from django.shortcuts import render,get_object_or_404
from django.conf import settings
import os
from django.http import HttpResponse, Http404
import mimetypes
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from twilio.rest import Client
from django.core.mail import send_mail
import json
from .models import HomeSlider,PackageOffers
from .models import WhatWeDo_Grid,Testimonial,YouTubeVideo
from .models import Blog,BlogCategory
from .models import*
from django.db.models import Q
from django.templatetags.static import static
from django.db.models import F
from django.shortcuts import render
from django.db.models import Q
from .models import Blog, BlogCategory
from .models import Project
from django.shortcuts import render, get_object_or_404
import random

# from .models import DiagonalImages

from django.views.decorators.csrf import csrf_exempt


# Create your views here.


def home(request):
    home_slider = HomeSlider.objects.all()
    package_offers = PackageOffers.objects.all()
    grid = WhatWeDo_Grid.objects.all()
    test = Testimonial.objects.all().order_by('-created_at')
    videos = YouTubeVideo.objects.filter(is_active=True)
    blogs = Blog.objects.all().order_by('-created_at')

    
    context = {'home_sliders': home_slider,
               'offers':package_offers,
               'grid':grid,
               'test':test,
               'videos':videos,
               'blogs':blogs,
               }
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        location = request.POST.get('location')

        subject = "Design Consultant Request"
        full_message = f"Name: {name}\nContact: {contact}\nEmail: {email}\nLocation: {location}"

        # Send email
        try:
            send_mail(
                subject,
                full_message,
                settings.EMAIL_HOST_USER,
                [settings.ADMIN_EMAIL],
                fail_silently=False
            )
        except Exception as e:
            print(f"EMAIL ERROR: {e}")
            messages.error(request, "Failed to send email. Please try again.")

        # Send WhatsApp message via Twilio
        try:
            # option 1

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER,
                to='whatsapp:' + settings.ADMIN_WHATSAPP_NUMBER,
                content_sid='HX3a1c16c275e148062bd56b604c5bd609',  # WhatsApp approved template SID
                content_variables=json.dumps({
                    "1": name,
                    "2": contact,
                    "3":email,
                    "4": location
                })
            )
            # option 2

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                    from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER,
                    to='whatsapp:' + settings.ADMIN_WHATSAPP_NUMBER,
                    body=f"New Design Consultant Request:\nName: {name}\nContact: {contact}\nEmail: {email}\nLocation: {location}"
                )

        except Exception as e:
            print(f"WHATSAPP ERROR: {e}")
            messages.error(request, "Failed to send WhatsApp message.")

        messages.success(request, 'Thank you! Our design consultant will contact you soon.')
        return redirect('home')
    
    return render(request, 'elite_interior/home.html', context)





from django.db.models import Q

def blog_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')

    
    # Start with all blogs ordered by latest
    blogs_qs = Blog.objects.all().order_by('-created_at')

    # Apply search query
    if query:
        blogs_qs = blogs_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(keyword__icontains=query)
        )

    # Apply category filter
    if category_id:
        blogs_qs = blogs_qs.filter(category_id=category_id)

    # Final filtered list
    blogs = list(blogs_qs)

    # Featured blogs from the same filtered list
    featured_blogs = blogs_qs.filter(is_featured=True)[:5]

    # Most viewed blogs (optional)
    most_viewed_blogs = Blog.objects.all().order_by('-views')[:5]

    # All blog categories
    categories = BlogCategory.objects.all()

    # Prepare context
    context = {
        'featured_blogs': featured_blogs,
        'most_viewed_blogs': most_viewed_blogs,
        'all_blogs': blogs,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    }

    # If no blogs found, try suggesting blogs only based on query (ignoring category)
    if not blogs and query and category_id:
        fallback_qs = Blog.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(keyword__icontains=query)
        ).order_by('-created_at')
        context['suggested_results'] = fallback_qs[:5]

    return render(request, 'elite_interior/blog_list.html', context)





from django.shortcuts import render, get_object_or_404
from .models import Blog  # assuming your Blog model is here

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    recent_blogs = Blog.objects.exclude(id=blog_id).order_by('-created_at')[:3]
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    session_key = f'viewed_blog_{blog_id}'

    if not request.session.get(session_key, False):
        blog.views += 1
        blog.save(update_fields=['views'])
        request.session[session_key] = True
        
    # Start with all blogs ordered by latest
    blogs_qs = Blog.objects.all().order_by('-created_at')

    # Apply search query
    if query:
        blogs_qs = blogs_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(keyword__icontains=query)
        )



    # Apply category filter
    if category_id:
        blogs_qs = blogs_qs.filter(category_id=category_id)

    # Final filtered list
    blogs = list(blogs_qs)

    # Featured blogs from the same filtered list
    featured_blogs = blogs_qs.filter(is_featured=True)[:5]

    # All blog categories
    categories = BlogCategory.objects.all()


    # If no blogs found, try suggesting blogs only based on query (ignoring category)
    if not blogs and query and category_id:
        fallback_qs = Blog.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(keyword__icontains=query)
        ).order_by('-created_at')
        context['suggested_results'] = fallback_qs[:5]
    context = {
        'blog': blog,
        'recent_blogs': recent_blogs,
         'featured_blogs': featured_blogs,
        'all_blogs': blogs,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    }
    return render(request, 'elite_interior/blog_detail.html', context)

from django.http import JsonResponse
from .models import BlogCategory

def category_suggestions(request):
    term = request.GET.get('term', '')
    suggestions = []

    if term:
        categories = BlogCategory.objects.filter(name__icontains=term).values_list('name', flat=True)[:10]
        suggestions = list(categories)

    return JsonResponse(suggestions, safe=False)



def about(request):
    videos = AboutVideo.objects.all()
    context = {'videos': videos,
    }
    return render(request, 'elite_interior/about.html', context)



def project_list(request):
    videos = YouTubeVideoProjects.objects.all()
    projects = Project.objects.all()[:20]
    context = {
        'videos':videos,
        'projects': projects,
        'category': "Our Projects"
    }
    return render(request, 'elite_interior/projects.html', context)




def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # All projects with the same subcategory (excluding current one)
    all_projects = Project.objects.filter(subcategory=project.subcategory).exclude(pk=project.pk)[:8]

    # Related projects from the same category (limit to 3)
    related_projects = list(
        Project.objects.filter(category=project.category).exclude(pk=project.pk)
    )
    random.shuffle(related_projects)
    related_projects = related_projects[:6]

    # Distinct subcategories in the same category (excluding current subcategory)
    subcategories = (
        Project.objects
        .filter(category=project.category)
        .exclude(subcategory=project.subcategory)
        .values_list('subcategory', flat=True)
        .distinct()
    )

    return render(request, 'elite_interior/project_detail.html', {
        'project': project,
        'related_projects': related_projects,
        'all_projects': all_projects,
        'subcategories': subcategories
    })

from collections import OrderedDict
def get_unique_projects_by_category(category_name):
    all_projects = Project.objects.filter(category__name__iexact=category_name).order_by('subcategory')
    unique_projects = OrderedDict()

    for project in all_projects:
        if project.subcategory not in unique_projects:
            unique_projects[project.subcategory] = project

    return list(unique_projects.values())

def kitchen_projects(request):
    projects = get_unique_projects_by_category('Kitchen')
    first_project = projects[0] if projects else None

    return render(request, 'elite_interior/kitchen.html', {
        'projects': projects,
        'first_project': first_project
    })

def bedroom_projects(request):
    projects = get_unique_projects_by_category('Bedroom')
    first_project = projects[0] if projects else None

    return render(request, 'elite_interior/bedroom_projects.html', {
        'projects': projects,
        'first_project': first_project
    })

def dining_projects(request):
    projects = get_unique_projects_by_category('Dining Room')
    first_project = projects[0] if projects else None
    return render(request, 'elite_interior/dining_projects.html', {
        'projects': projects,
        'first_project': first_project
    })

def living_projects(request):
    projects = get_unique_projects_by_category('Living Room')
    first_project = projects[0] if projects else None
    return render(request, 'elite_interior/living_projects.html', {
        'projects': projects,
        'first_project': first_project
    })

def bathroom_projects(request):
    projects = get_unique_projects_by_category('Bathroom')
    first_project = projects[0] if projects else None
    return render(request, 'elite_interior/bathroom_projects.html', {
        'projects': projects,
        'first_project': first_project
    })

def kidsroom_projects(request):
    projects = get_unique_projects_by_category('kidsroom')
    first_project = projects[0] if projects else None
    return render(request, 'elite_interior/bathroom_projects.html', {
        'projects': projects,
        'first_project': first_project
    })

def essential(request):
    package_offers = PackageOffers.objects.all()
    context={
        'offers':package_offers
    }
    return render(request,'elite_interior/essential.html',context)

def eleganza(request):
    package_offers = PackageOffers.objects.all()
    context={
        'offers':package_offers
    }
    return render(request,'elite_interior/eleganza.html',context)

def essential_plus(request):
    package_offers = PackageOffers.objects.all()
    context={
        'offers':package_offers
    }
    return render(request,'elite_interior/essential_plus.html',context)



def contact(request):
    return render(request,'elite_interior/contact.html')

from .forms import BudgetCalculationForm
from .models import BudgetItem

def calculate_budget(request):
    form = BudgetCalculationForm()
    return render(request, 'elite_interior/calculate.html', {'form': form})

def service(request):
    grid = WhatWeDo_Grid.objects.all()
    context ={
        'grid':grid
    }
    return render(request,'elite_interior/service.html',context)

# def design_consultant(request):
#     home_slider = HomeSlider.objects.all()
#     package_offers =PackageOffers.objects.all()
#     grid = WhatWeDo_Grid.objects.all()
#     test = Testimonial.objects.all()
#     context = {'home_sliders': home_slider,
#                'offers':package_offers,
#                'grid':grid,
#                'test':test,
#                }
    
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         contact = request.POST.get('contact')
#         email = request.POST.get('email')
#         location = request.POST.get('location')

#         subject = "Design Consultant Request"
#         full_message = f"Name: {name}\nContact: {contact}\nEmail: {email}\nLocation: {location}"

#         # Send email
#         try:
#             send_mail(
#                 subject,
#                 full_message,
#                 settings.EMAIL_HOST_USER,
#                 [settings.ADMIN_EMAIL],
#                 fail_silently=False
#             )
#         except Exception as e:
#             print(f"EMAIL ERROR: {e}")
#             messages.error(request, "Failed to send email. Please try again.")

#         # Send WhatsApp message via Twilio
#         try:
#             client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#             client.messages.create(
#                 from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER,
#                 to='whatsapp:' + settings.ADMIN_WHATSAPP_NUMBER,
#                 content_sid='HX3a1c16c275e148062bd56b604c5bd609',  # WhatsApp approved template SID
#                 content_variables=json.dumps({
#                     "1": name,
#                     "2": contact,
#                     "3":email,
#                     "4": location
#                 })
#             )
#         except Exception as e:
#             print(f"WHATSAPP ERROR: {e}")
#             messages.error(request, "Failed to send WhatsApp message.")

#         messages.success(request, 'Thank you! Our design consultant will contact you soon.')
#         return redirect('home')

#     return render(request, 'elite_interior/home.html', context)


def send_whatsapp_template(name, contact,email, location):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER,
        to='whatsapp:' + settings.ADMIN_WHATSAPP_NUMBER,
        content_sid='HX3a1c16c275e148062bd56b604c5bd609',
        content_variables=json.dumps({
            "1": name,
            "2": contact,
            "3": email,
            "4": location
        })
    )


def serve_media(request, path):
    """ Serve media files securely """
    file_path = os.path.join(settings.MEDIA_ROOT, path)

    if not os.path.exists(file_path):
        raise Http404("File not found")

    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or "application/octet-stream"

    with open(file_path, 'rb') as f:
        return HttpResponse(f.read(), content_type=content_type)
    




# yourapp/views.py
from django.http import JsonResponse
from elite_interior.utils.whatsapp import send_whatsapp_message


def send_message_view(request):
    response = send_whatsapp_message("919786224099")  # change to your number
    return JsonResponse(response)

from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

def submit_contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        location = request.POST.get('location')

        subject_admin = f"New Enquiry from {name}"
        message_admin = f"Name: {name}\nContact: {contact}\nEmail: {email}\nLocation: {location}"
        subject_client = "Thanks for contacting Home Den"
        message_client = f"Hi {name},\n\nThank you for contacting us! We will be in touch soon.\n\nYour Details:\nContact: {contact}\nLocation: {location}"

        try:
            send_mail(subject_admin, message_admin, settings.EMAIL_HOST_USER, [settings.ADMIN_EMAIL])
            send_mail(subject_client, message_client, settings.EMAIL_HOST_USER, [email])
            messages.success(request, "Enquiry submitted successfully.")
        except Exception as e:
            print("Email error:", e)
            messages.error(request, "Error sending email. Try again later.")

    return redirect(request.META.get('HTTP_REFERER', '/'))  
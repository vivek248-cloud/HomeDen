from datetime import timedelta
from unicodedata import category
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


from .models import*
from django.db.models import Q
from django.templatetags.static import static
from django.db.models import F


from django.shortcuts import render, get_object_or_404
import random

from django.core.paginator import Paginator

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
    ad = Ad.objects.filter(is_active=True).order_by('-created_at').first()
    
    context = {'home_sliders': home_slider,
               'offers':package_offers,
               'grid':grid,
               'test':test,
               'ad': ad,
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





def blog_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    page_number = request.GET.get('page', 1)

    blogs_qs = Blog.objects.all().order_by('-created_at')

    if query:
        blogs_qs = blogs_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(keyword__icontains=query)
        )

    if category_id:
        blogs_qs = blogs_qs.filter(category__category__id=category_id)

    paginator = Paginator(blogs_qs, 6)  # 6 blogs per page
    blogs_page = paginator.get_page(page_number)

    featured_blogs = blogs_qs.filter(is_featured=True)[:5]
    most_viewed_blogs = Blog.objects.all().order_by('-views')[:5]
    categories = BlogCategory.objects.all()

    context = {
        'featured_blogs': featured_blogs,
        'most_viewed_blogs': most_viewed_blogs,
        'blogs_page': blogs_page,  # paginated page
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    }

    return render(request, 'elite_interior/blog_list.html', context)






def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    recent_blogs = Blog.objects.exclude(id=blog.id).order_by('-created_at')[:3]
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    session_key = f'viewed_blog_{blog.id}'

    # Count unique views
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

    # Featured blogs
    featured_blogs = blogs_qs.filter(is_featured=True)[:5]

    # All categories
    categories = BlogCategory.objects.all()

    # Suggested fallback if no blogs found
    suggested_results = []
    if not blogs and query and category_id:
        fallback_qs = Blog.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(keyword__icontains=query)
        ).order_by('-created_at')
        suggested_results = fallback_qs[:5]

    context = {
        'blog': blog,
        'recent_blogs': recent_blogs,
        'featured_blogs': featured_blogs,
        'all_blogs': blogs,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'suggested_results': suggested_results,
    }
    return render(request, 'elite_interior/blog_detail.html', context)






def category_suggestions(request):
    query = request.GET.get('term', '').strip()
    suggestions = []

    if query:
        # Blog Categories (via related Category model)
        category_matches = BlogCategory.objects.filter(
            category__name__icontains=query
        )[:5]
        suggestions += [
            {"id": cat.id, "label": f"{cat.category.name}", "value": cat.category.name}
            for cat in category_matches if cat.category
        ]

        # Project Categories
        project_matches = Category.objects.filter(
            name__icontains=query
        )[:5]
        suggestions += [
            {"id": proj.id, "label": f"{proj.name}", "value": proj.name}
            for proj in project_matches
        ]

        # Blogs (Title + Keywords)
        blog_matches = Blog.objects.filter(
            Q(title__icontains=query) | Q(keyword__icontains=query)
        )[:10]
        suggestions += [
            {"id": blog.id, "label": f" {blog.title}", "value": blog.title}
            for blog in blog_matches
        ]

    return JsonResponse(suggestions, safe=False)



def about(request):
    members = TeamMember.objects.all()
    
    videos = AboutVideo.objects.all()
    context = {'videos': videos, 'members': members}
    return render(request, 'elite_interior/about.html', context)






# def project_list(request):
#     videos = YouTubeVideoProjects.objects.all()
    
#     # DO NOT slice here
#     all_projects = Project.objects.all()
    
#     paginator = Paginator(all_projects, 6)  # Paginate full queryset
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     context = {
#         'videos': videos,
#         'projects': page_obj,  # Paginated result
#         'category': "Our Projects",
#         'is_paginated': page_obj.has_next(),
#         'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
#     }
#     return render(request, 'elite_interior/projects.html', context)


def project_list(request):
    all_projects = ProjectGallery.objects.all()
    all_videos = YouTubeVideoProjects.objects.all()

    # Paginate projects
    project_paginator = Paginator(all_projects, 6)
    project_page_number = request.GET.get('page')
    project_page_obj = project_paginator.get_page(project_page_number)

    # Paginate videos
    video_paginator = Paginator(all_videos, 3)
    video_page_number = request.GET.get('video_page')
    video_page_obj = video_paginator.get_page(video_page_number)

    context = {
        'projects': project_page_obj,
        'videos': video_page_obj,
        'category': "Our Projects",

        # Pagination flags
        'is_project_paginated': project_page_obj.has_next(),
        'next_project_page': project_page_obj.next_page_number() if project_page_obj.has_next() else None,

        'is_video_paginated': video_page_obj.has_next(),
        'next_video_page': video_page_obj.next_page_number() if video_page_obj.has_next() else None,
    }

    return render(request, 'elite_interior/projects.html', context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)

    all_projects = Project.objects.filter(subcategory=project.subcategory).exclude(pk=project.pk)[:8]

    related_projects = list(
        Project.objects.filter(subcategory=project.subcategory).exclude(pk=project.pk)
    )
    random.shuffle(related_projects)
    related_projects = related_projects[:6]

    subcategories = (
        SubCategory.objects
        .filter(category=project.category)
        .exclude(id=project.subcategory.id if project.subcategory else None)
        .values_list('name', flat=True)
        .distinct()
    )

    return render(request, 'elite_interior/project_detail.html', {
        'project': project,
        'related_projects': related_projects,
        'all_projects': all_projects,
        'subcategories': subcategories
    })

def product(request, slug):
    project = get_object_or_404(Project, slug=slug)
    related_projects = Project.objects.filter(subcategory=project.subcategory).all()

    context = {
        "project": project,
        "all_projects": related_projects,  # send all without pagination
    }
    return render(request, "elite_interior/product.html", context)




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
    projects = get_unique_projects_by_category('Dining')
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
    projects = get_unique_projects_by_category("kid's room")
    first_project = projects[0] if projects else None
    return render(request, 'elite_interior/kids.html', {
        'projects': projects,
        'first_project': first_project
    })



def poojaroom_projects(request):
    projects = get_unique_projects_by_category("pooja room")
    first_project = projects[0] if projects else None
    return render(request, 'elite_interior/poojaroom.html', {
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

def eleganza_plus(request):
    package_offers = PackageOffers.objects.all()
    context={
        'offers':package_offers
    }
    return render(request,'elite_interior/essential_plus.html',context)



def contact(request):
    return render(request,'elite_interior/contact.html')

from .forms import BudgetCalculationForm


def kitchen_calculate_budget(request):

    kitchen_sizes = [
        "7 ft. × 10 ft.",
        "8 ft. × 9 ft.",
        "9 ft. × 10 ft.",
        "10 ft. × 10 ft.",
        "11.5 ft. × 10 ft.",
        "Custom"
    ]

    # ✅ Fetch category named "Kitchen"
    try:
        kitchen_category = Category.objects.get(name__iexact="kitchen")
        accessories = Accessory.objects.filter(category=kitchen_category)
    except Category.DoesNotExist:
        accessories = []   # No category => no accessories

    packages = ['silver', 'gold', 'platinum']

    form = BudgetCalculationForm()

    context = {
        'form': form,
        'kitchen_sizes': kitchen_sizes,
        'packages': packages,
        'accessories': accessories,
    }
    return render(request, 'calculate/kitchencalculate.html', context)



# def bedroom_calculate_budget(request):

#     bedroom_sizes = [
#         "7 ft. × 10 ft.",
#         "8 ft. × 9 ft.",
#         "9 ft. × 10 ft.",
#         "10 ft. × 10 ft.",
#         "11.5 ft. × 10 ft.",
#         "Custom"
#     ]

#     packages = ['silver', 'gold', 'platinum']

#     form = BudgetCalculationForm()
#     context = {
#         'form': form,
#         'bedroom_sizes': bedroom_sizes,
#         'packages': packages,
#     }
#     return render(request, 'calculate/bedroomcalculate.html', context)




def bedroom_calculate_budget(request):

    bedroom_sizes = [
        "7 ft. × 10 ft.",
        "8 ft. × 9 ft.",
        "9 ft. × 10 ft.",
        "10 ft. × 10 ft.",
        "11.5 ft. × 10 ft.",
        "Custom"
    ]

    packages = ['silver', 'gold', 'platinum']

    # 🔥 Load accessories using category "Bedroom"
    bedroom_accessories = Accessory.objects.filter(category__name="bedroom")

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'bedroom_sizes': bedroom_sizes,
        'packages': packages,
        'accessories': bedroom_accessories,   # 👈 IMPORTANT
    }
    return render(request, 'calculate/bedroomcalculate.html', context)



# def bathroom_calculate_budget(request):

#     bathroom_sizes = [
#         "7 ft. × 10 ft.",
#         "8 ft. × 9 ft.",
#         "9 ft. × 10 ft.",
#         "10 ft. × 10 ft.",
#         "11.5 ft. × 10 ft.",
#         "Custom"
#     ]

#     packages = ['silver', 'gold', 'platinum']

#     form = BudgetCalculationForm()
#     context = {
#         'form': form,
#         'bathroom_sizes': bathroom_sizes,
#         'packages': packages,
#     }
#     return render(request, 'calculate/bathroomcalculation.html', context)

# def kidsroom_calculate_budget(request):

#     kidsroom_sizes = [
#         "7 ft. × 10 ft.",
#         "8 ft. × 9 ft.",
#         "9 ft. × 10 ft.",
#         "10 ft. × 10 ft.",
#         "11.5 ft. × 10 ft.",
#         "Custom"
#     ]

#     packages = ['silver', 'gold', 'platinum']

#     form = BudgetCalculationForm()
#     context = {
#         'form': form,
#         'kids_room_sizes': kidsroom_sizes,
#         'packages': packages,
#     }
#     return render(request, 'calculate/Kidsroomcalculate.html', context)


# def livingroom_calculate_budget(request):

#     livingroom_sizes = [
#         "7 ft. × 10 ft.",
#         "8 ft. × 9 ft.",
#         "9 ft. × 10 ft.",
#         "10 ft. × 10 ft.",
#         "11.5 ft. × 10 ft.",
#         "Custom"
#     ]

#     packages = ['silver', 'gold', 'platinum']

#     form = BudgetCalculationForm()
#     context = {
#         'form': form,
#         'living_room_sizes': livingroom_sizes,
#         'packages': packages,
#     }
#     return render(request, 'calculate/livingroomcalculate.html', context)


# def wardrobe_calculate_budget(request):

#     wardrobe_sizes = [
#         "7 ft. × 10 ft.",
#         "8 ft. × 9 ft.",
#         "9 ft. × 10 ft.",
#         "10 ft. × 10 ft.",
#         "11.5 ft. × 10 ft.",
#         "Custom"
#     ]

#     packages = ['silver', 'gold', 'platinum']

#     form = BudgetCalculationForm()
#     context = {
#         'form': form,
#         'wardrobe_sizes': wardrobe_sizes,
#         'packages': packages,
#     }
#     return render(request, 'calculate/wardrobescalculate.html', context)

# def dining_calculate_budget(request):

#     dining_sizes = [
#         "7 ft. × 10 ft.",
#         "8 ft. × 9 ft.",
#         "9 ft. × 10 ft.",
#         "10 ft. × 10 ft.",
#         "11.5 ft. × 10 ft.",
#         "Custom"
#     ]

#     packages = ['silver', 'gold', 'platinum']

#     form = BudgetCalculationForm()
#     context = {
#         'form': form,
#         'dining_sizes': dining_sizes,
#         'packages': packages,
#     }
#     return render(request, 'calculate/diningcalculate.html', context)


# BATHROOM
def bathroom_calculate_budget(request):

    bathroom_sizes = [
        "7 ft. × 10 ft.",
        "8 ft. × 9 ft.",
        "9 ft. × 10 ft.",
        "10 ft. × 10 ft.",
        "11.5 ft. × 10 ft.",
        "Custom"
    ]

    packages = ['silver', 'gold', 'platinum']

    # Load Bathroom accessories
    accessories = Accessory.objects.filter(category__name="Bathroom")

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'bathroom_sizes': bathroom_sizes,
        'packages': packages,
        'accessories': accessories,
    }
    return render(request, 'calculate/bathroomcalculation.html', context)



# KIDS ROOM
def kidsroom_calculate_budget(request):

    kidsroom_sizes = [
        "7 ft. × 10 ft.",
        "8 ft. × 9 ft.",
        "9 ft. × 10 ft.",
        "10 ft. × 10 ft.",
        "11.5 ft. × 10 ft.",
        "Custom"
    ]

    packages = ['silver', 'gold', 'platinum']

    # Load Kids Room accessories
    accessories = Accessory.objects.filter(category__name="kid's room")

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'kids_room_sizes': kidsroom_sizes,
        'packages': packages,
        'accessories': accessories,
    }
    return render(request, 'calculate/Kidsroomcalculate.html', context)



# LIVING ROOM
def livingroom_calculate_budget(request):

    livingroom_sizes = [
        "7 ft. × 10 ft.",
        "8 ft. × 9 ft.",
        "9 ft. × 10 ft.",
        "10 ft. × 10 ft.",
        "11.5 ft. × 10 ft.",
        "Custom"
    ]

    packages = ['silver', 'gold', 'platinum']

    # Load Living Room accessories
    accessories = Accessory.objects.filter(category__name="living room")

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'living_room_sizes': livingroom_sizes,
        'packages': packages,
        'accessories': accessories,
    }
    return render(request, 'calculate/livingroomcalculate.html', context)



# WARDROBE
def wardrobe_calculate_budget(request):

    wardrobe_sizes = [
        "7 ft. × 10 ft.",
        "8 ft. × 9 ft.",
        "9 ft. × 10 ft.",
        "10 ft. × 10 ft.",
        "11.5 ft. × 10 ft.",
        "Custom"
    ]

    packages = ['silver', 'gold', 'platinum']

    # Load Wardrobe accessories
    accessories = Accessory.objects.filter(category__name="wardrobes")

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'wardrobe_sizes': wardrobe_sizes,
        'packages': packages,
        'accessories': accessories,
    }
    return render(request, 'calculate/wardrobescalculate.html', context)

#pooja room
def poojaroom_calculate_budget(request):

    poojaroom_sizes = [
        "7 ft. × 10 ft.",
        "8 ft. × 9 ft.",
        "9 ft. × 10 ft.",
        "10 ft. × 10 ft.",
        "11.5 ft. × 10 ft.",
        "Custom"
    ]

    packages = ['silver', 'gold', 'platinum']

    # Load Wardrobe accessories
    accessories = Accessory.objects.filter(category__name="pooja room")

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'poojaroom_sizes': poojaroom_sizes,
        'packages': packages,
        'accessories': accessories,
    }
    return render(request, 'calculate/poojaroomcalculate.html', context)

# DINING
def dining_calculate_budget(request):

    dining_sizes = [
        "7 ft. × 10 ft.",
        "8 ft. × 9 ft.",
        "9 ft. × 10 ft.",
        "10 ft. × 10 ft.",
        "11.5 ft. × 10 ft.",
        "Custom"
    ]

    packages = ['silver', 'gold', 'platinum']

    # Load Dining accessories
    accessories = Accessory.objects.filter(category__name="Dining")

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'dining_sizes': dining_sizes,
        'packages': packages,
        'accessories': accessories,
    }
    return render(request, 'calculate/diningcalculate.html', context)



def service(request):
    grid = WhatWeDo_Grid.objects.all()
    context ={
        'grid':grid
    }
    return render(request,'elite_interior/service.html',context)




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

from elite_interior.utils.whatsapp import send_whatsapp_message


def send_message_view(request):
    response = send_whatsapp_message("919786224099")  # change to your number
    return JsonResponse(response)

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

def submit_contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        contact = request.POST.get('contact', '').strip()
        contact2 = request.POST.get('contact2', '').strip()
        email = request.POST.get('email', '').strip()
        bhk_raw = request.POST.get('bhk', '')
        location = request.POST.get('location', '').strip()

        # Format BHK properly
        bhk_list = []
        if bhk_raw:
            for item in bhk_raw.split(','):
                room, count = item.split(':')
                bhk_list.append(f"{room} - {count}")
        bhk_formatted = "\n".join(bhk_list) if bhk_list else "Not specified"

        subject_admin = f"New Enquiry from {name}"
        message_admin = (
            f"Name: {name}\n"
            f"Contact: {contact}\n"
            f"Contact 2: {contact2}\n"
            f"Email: {email}\n"
            f"Location: {location}\n\n"
            f"Selected Rooms:\n{bhk_formatted}"
        )

        subject_client = "Thanks for contacting Home Den"
        message_client = (
            f"Hi {name},\n\n"
            f"Thank you for contacting us! We will be in touch soon.\n\n"
            f"Your Details:\n"
            f"Contact: {contact}\n"
            f"Contact 2: {contact2}\n"
            f"Email: {email}\n"
            f"Location: {location}\n"
            f"Rooms:\n{bhk_formatted}\n\n"
            f"Best regards,\nHome Den Team"
        )

        try:
            send_mail(subject_admin, message_admin, settings.EMAIL_HOST_USER, [settings.ADMIN_EMAIL])
            send_mail(subject_client, message_client, settings.EMAIL_HOST_USER, [email])
            messages.success(request, "Thank you! Your inquiry was sent successfully.")
        except Exception as e:
            logger.error("Email sending failed", exc_info=e)
            messages.error(request, "Error sending email. Try again later.")

    return redirect(request.META.get('HTTP_REFERER', '/'))



###############################################################################

import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from decimal import Decimal

from .models import OtpVerification


def kitchen_submit_estimation_form(request):
    if request.method == "POST":
        size = request.POST.get("size")
        custom_length = request.POST.get("custom_length")
        custom_width = request.POST.get("custom_width")

        # If custom size
        if size == "Custom" and custom_length and custom_width:
            size = f"{custom_length} ft × {custom_width} ft"

        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # OTP
        otp = str(random.randint(1000, 9999))
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing logic
        if size == '7 ft. × 10 ft.':
            price = Decimal('50000')
        elif size == '8 ft. × 9 ft.':
            price = Decimal('60000')
        elif size == '9 ft. × 10 ft.':
            price = Decimal('70000')
        elif size == '10 ft. × 10 ft.':
            price = Decimal('80000')
        elif size == '11.5 ft. × 10 ft.':
            price = Decimal('90000')
        elif "ft ×" in size:  
            l = Decimal(custom_length)
            w = Decimal(custom_width)
            sqft = l * w
            price = sqft * Decimal('500')
        else:
            price = Decimal('0')


        # 🔥 Collect accessories using ID
        accessories = []
        total_accessory_cost = Decimal("0")

        for key, value in request.POST.items():
            if key.startswith("accessory_qty_"):
                accessory_id = key.replace("accessory_qty_", "")

                try:
                    accessory_obj = Accessory.objects.get(id=accessory_id)
                except Accessory.DoesNotExist:
                    continue

                qty = int(value)
                if qty <= 0:
                    continue

                # SAFE PRICE
                acc_price = accessory_obj.price or Decimal("0")
                item_total = acc_price * qty

                total_accessory_cost += item_total

                accessories.append({
                    "id": accessory_obj.id,
                    "name": accessory_obj.name,
                    "qty": qty,
                    "price": float(acc_price),
                    "total": float(item_total)
                })




        # Package adjustment
        if package == 'silver':
            price *= Decimal('0.8')

        elif package == 'gold':
            price *= Decimal('1.2')
        elif package == 'platinum':
            price *= Decimal('1.5')

        # Add accessory cost to total price 
        # Ensure all values are floats, not Decimal
        price = float(price) + float(total_accessory_cost)


        # Save / update OTP
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Save all form data in session
        request.session["form_data"] = {
            "size": size,
            "shape": shape,
            "package": package,
            "price": price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
            "room_type": request.session.get("room_type"),
            "style": request.session.get("style"),
            "accessories": accessories,
        }

        # Send OTP email
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("kitchen_calculate")



from decimal import Decimal

def bedroom_submit_estimation_form(request):
    if request.method == "POST":

        size = request.POST.get("size")
        custom_length = request.POST.get("custom_length")
        custom_width = request.POST.get("custom_width")

        # Custom size formatting
        if size == "Custom" and custom_length and custom_width:
            size = f"{custom_length} ft × {custom_width} ft"

        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # OTP
        otp = str(random.randint(1000, 9999))
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Base pricing logic (converted to Decimal like kitchen)
        if size == '7 ft. × 10 ft.':
            price = Decimal('50000')
        elif size == '8 ft. × 9 ft.':
            price = Decimal('60000')
        elif size == '9 ft. × 10 ft.':
            price = Decimal('70000')
        elif size == '10 ft. × 10 ft.':
            price = Decimal('80000')
        elif size == '11.5 ft. × 10 ft.':
            price = Decimal('90000')
        elif "ft ×" in size:
            l = Decimal(custom_length)
            w = Decimal(custom_width)
            sqft = l * w
            price = sqft * Decimal('500')
        else:
            price = Decimal('0')

        # Package adjustment (same as kitchen)
        if package == 'silver':
            price *= Decimal('0.8')
        elif package == 'gold':
            price *= Decimal('1.2')
        elif package == 'platinum':
            price *= Decimal('1.5')

        # -----------------------------------------
        # 🔥 Collect accessories (safe like kitchen)
        # -----------------------------------------
        accessories = []
        total_accessory_cost = Decimal("0")

        for key, value in request.POST.items():
            if key.startswith("accessory_qty_"):
                accessory_id = key.replace("accessory_qty_", "")

                try:
                    accessory_obj = Accessory.objects.get(id=accessory_id)
                except Accessory.DoesNotExist:
                    continue

                qty = int(value)
                if qty <= 0:
                    continue

                # SAFE PRICE
                acc_price = accessory_obj.price or Decimal("0")
                item_total = acc_price * qty

                total_accessory_cost += item_total

                accessories.append({
                    "id": accessory_obj.id,
                    "name": accessory_obj.name,
                    "qty": qty,
                    "price": float(acc_price),
                    "total": float(item_total),
                })

        # FINAL PRICE = BASE PRICE + ACCESSORIES
        final_price = float(price) + float(total_accessory_cost)

        # Save OTP to DB
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Save to session
        request.session["form_data"] = {
            "room_type": request.session.get("room_type"),
            "size": size,
            "shape": shape,
            "package": package,
            "price": final_price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
            "accessories": accessories,
        }

        # Send OTP email
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("bedroom_calculate")






from decimal import Decimal

def living_submit_estimation_form(request):
    if request.method == "POST":

        size = request.POST.get("size")
        custom_length = request.POST.get("custom_length")
        custom_width = request.POST.get("custom_width")

        # Custom size formatting
        if size == "Custom" and custom_length and custom_width:
            size = f"{custom_length} ft × {custom_width} ft"

        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # OTP
        otp = str(random.randint(1000, 9999))
        expiry_time = timezone.now() + timedelta(minutes=5)

        # --------------------------
        # 🔥 Base pricing (Decimal)
        # --------------------------
        if size == '7 ft. × 10 ft.':
            price = Decimal('50000')
        elif size == '8 ft. × 9 ft.':
            price = Decimal('60000')
        elif size == '9 ft. × 10 ft.':
            price = Decimal('70000')
        elif size == '10 ft. × 10 ft.':
            price = Decimal('80000')
        elif size == '11.5 ft. × 10 ft.':
            price = Decimal('90000')
        elif "ft ×" in size:
            l = Decimal(custom_length)
            w = Decimal(custom_width)
            sqft = l * w
            price = sqft * Decimal('500')
        else:
            price = Decimal('0')

        # --------------------------
        # 🔥 Package adjustment
        # --------------------------
        if package == 'silver':
            price *= Decimal('0.8')
        elif package == 'gold':
            price *= Decimal('1.2')
        elif package == 'platinum':
            price *= Decimal('1.5')

        # -----------------------------------------
        # 🔥 Collect accessories (same as kitchen)
        # -----------------------------------------
        accessories = []
        total_accessory_cost = Decimal("0")

        for key, value in request.POST.items():
            if key.startswith("accessory_qty_"):
                accessory_id = key.replace("accessory_qty_", "")

                try:
                    accessory_obj = Accessory.objects.get(id=accessory_id)
                except Accessory.DoesNotExist:
                    continue

                qty = int(value)
                if qty <= 0:
                    continue

                acc_price = accessory_obj.price or Decimal("0")
                item_total = acc_price * qty

                total_accessory_cost += item_total

                accessories.append({
                    "id": accessory_obj.id,
                    "name": accessory_obj.name,
                    "qty": qty,
                    "price": float(acc_price),
                    "total": float(item_total)
                })

        # --------------------------
        # 🔥 Final Price
        # --------------------------
        final_price = float(price) + float(total_accessory_cost)

        # Save/update OTP
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Save session data
        request.session["form_data"] = {
            "room_type": request.session.get("room_type"),
            "size": size,
            "shape": shape,
            "package": package,
            "price": final_price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
            "accessories": accessories,
        }

        # Send OTP email
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("living_room_calculate")


# def bathroom_submit_estimation_form(request):
#     if request.method == "POST":
#         size = request.POST.get("size")
#         custom_length = request.POST.get("custom_length")
#         custom_width = request.POST.get("custom_width")

#         # If custom, convert to numeric size
#         if size == "Custom" and custom_length and custom_width:
#             size = f"{custom_length} ft × {custom_width} ft"

#         shape = request.POST.get("shape")
#         package = request.POST.get("package")
#         name = request.POST.get("name")
#         contact = request.POST.get("contact")
#         email = request.POST.get("email")
#         location = request.POST.get("location")

#         # Generate OTP
#         otp = random.randint(1000, 9999)
#         expiry_time = timezone.now() + timedelta(minutes=5)

#         # Pricing logic
#         if size == '7 ft. × 10 ft.':
#             price = 50000
#         elif size == '8 ft. × 9 ft.':
#             price = 60000
#         elif size == '9 ft. × 10 ft.':
#             price = 70000
#         elif size == '10 ft. × 10 ft.':
#             price = 80000
#         elif size == '11.5 ft. × 10 ft.':
#             price = 90000
#         elif "ft ×" in size:  # custom size logic
#             l = float(custom_length)
#             w = float(custom_width)
#             sqft = l * w
#             price = sqft * 500  # price per sq ft — adjust your price logic
#         else:
#             price = 0


#         if package == 'silver':
#             price *= 0.8  # Apply 20% discount
#         elif package == 'gold':
#             price *= 1.2  # Apply 20% premium
#         elif package == 'platinum':
#             price *= 1.5  # Apply 50% premium


#         # ✅ Save or update OTP in DB (unique per email)
#         OtpVerification.objects.update_or_create(
#             email=email,
#             defaults={
#                 "otp": otp,
#                 "expires_at": expiry_time
#             }
#         )

#         # Store OTP + form data in session
#         request.session["otp"] = str(otp)
#         request.session["otp_expiry"] = expiry_time.isoformat()
#         request.session["form_data"] = {
#             "room_type": request.session.get("room_type", "N/A"),
#             "size": size,
#             "shape": shape,
#             "package": package,
#             "price": price,
#             "name": name,
#             "contact": contact,
#             "email": email,
#             "location": location,
#         }

#         # Send OTP
#         send_mail(
#             subject="Your OTP for Budget Estimation Confirmation",
#             message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[email],
#         )

#         return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

#     return redirect("bath_room_calculate")

from decimal import Decimal

def bathroom_submit_estimation_form(request):
    if request.method == "POST":

        size = request.POST.get("size")
        custom_length = request.POST.get("custom_length")
        custom_width = request.POST.get("custom_width")

        # Custom size formatting
        if size == "Custom" and custom_length and custom_width:
            size = f"{custom_length} ft × {custom_width} ft"

        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        otp = str(random.randint(1000, 9999))
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing (Base)
        if size == '7 ft. × 10 ft.':
            price = Decimal('50000')
        elif size == '8 ft. × 9 ft.':
            price = Decimal('60000')
        elif size == '9 ft. × 10 ft.':
            price = Decimal('70000')
        elif size == '10 ft. × 10 ft.':
            price = Decimal('80000')
        elif size == '11.5 ft. × 10 ft.':
            price = Decimal('90000')

        elif "ft ×" in size:
            l = Decimal(custom_length)
            w = Decimal(custom_width)
            sqft = l * w
            price = sqft * Decimal('500')

        else:
            price = Decimal('0')

        # Package adjustment
        if package == 'silver':
            price *= Decimal('0.8')
        elif package == 'gold':
            price *= Decimal('1.2')
        elif package == 'platinum':
            price *= Decimal('1.5')

        # Accessory collection
        accessories = []
        total_accessory_cost = Decimal("0")

        for key, value in request.POST.items():
            if key.startswith("accessory_qty_"):
                acc_id = key.replace("accessory_qty_", "")

                try:
                    acc_obj = Accessory.objects.get(id=acc_id)
                except Accessory.DoesNotExist:
                    continue

                qty = int(value)
                if qty <= 0:
                    continue

                acc_price = acc_obj.price or Decimal("0")
                item_total = acc_price * qty
                total_accessory_cost += item_total

                accessories.append({
                    "id": acc_obj.id,
                    "name": acc_obj.name,
                    "qty": qty,
                    "price": float(acc_price),
                    "total": float(item_total)
                })

        final_price = float(price + total_accessory_cost)

        OtpVerification.objects.update_or_create(
            email=email,
            defaults={"otp": otp, "expires_at": expiry_time}
        )

        request.session["form_data"] = {
            "room_type": "bathroom",
            "size": size,
            "shape": shape,
            "package": package,
            "price": final_price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
            "accessories": accessories,
        }

        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name}, your OTP is {otp}. It expires in 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("bath_room_calculate")







def dining_submit_estimation_form(request):
    if request.method == "POST":

        size = request.POST.get("size")
        custom_length = request.POST.get("custom_length")
        custom_width = request.POST.get("custom_width")

        if size == "Custom" and custom_length and custom_width:
            size = f"{custom_length} ft × {custom_width} ft"

        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        otp = str(random.randint(1000, 9999))
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing
        if size == '7 ft. × 10 ft.':
            price = Decimal('50000')
        elif size == '8 ft. × 9 ft.':
            price = Decimal('60000')
        elif size == '9 ft. × 10 ft.':
            price = Decimal('70000')
        elif size == '10 ft. × 10 ft.':
            price = Decimal('80000')
        elif size == '11.5 ft. × 10 ft.':
            price = Decimal('90000')
        elif "ft ×" in size:
            price = Decimal(custom_length) * Decimal(custom_width) * Decimal('500')
        else:
            price = Decimal('0')

        if package == 'silver':
            price *= Decimal('0.8')
        elif package == 'gold':
            price *= Decimal('1.2')
        elif package == 'platinum':
            price *= Decimal('1.5')

        accessories = []
        total_accessory_cost = Decimal("0")

        for key, value in request.POST.items():
            if key.startswith("accessory_qty_"):
                acc_id = key.replace("accessory_qty_", "")

                try:
                    acc_obj = Accessory.objects.get(id=acc_id)
                except Accessory.DoesNotExist:
                    continue

                qty = int(value)
                if qty <= 0:
                    continue

                acc_price = acc_obj.price or Decimal("0")
                item_total = acc_price * qty

                total_accessory_cost += item_total

                accessories.append({
                    "id": acc_obj.id,
                    "name": acc_obj.name,
                    "qty": qty,
                    "price": float(acc_price),
                    "total": float(item_total)
                })

        final_price = float(price + total_accessory_cost)

        OtpVerification.objects.update_or_create(
            email=email,
            defaults={"otp": otp, "expires_at": expiry_time}
        )

        request.session["form_data"] = {
            "room_type": "dining",
            "size": size,
            "shape": shape,
            "package": package,
            "price": final_price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
            "accessories": accessories,
        }

        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name}, your OTP is {otp}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("dining_calculate")


# def kids_submit_estimation_form(request):
#     if request.method == "POST":
#         size = request.POST.get("size")
#         custom_length = request.POST.get("custom_length")
#         custom_width = request.POST.get("custom_width")

#         # If custom, convert to numeric size
#         if size == "Custom" and custom_length and custom_width:
#             size = f"{custom_length} ft × {custom_width} ft"

#         shape = request.POST.get("shape")
#         package = request.POST.get("package")
#         name = request.POST.get("name")
#         contact = request.POST.get("contact")
#         email = request.POST.get("email")
#         location = request.POST.get("location")

#         # Generate OTP
#         otp = random.randint(1000, 9999)
#         expiry_time = timezone.now() + timedelta(minutes=5)

#         # Pricing logic
#         if size == '7 ft. × 10 ft.':
#             price = 50000
#         elif size == '8 ft. × 9 ft.':
#             price = 60000
#         elif size == '9 ft. × 10 ft.':
#             price = 70000
#         elif size == '10 ft. × 10 ft.':
#             price = 80000
#         elif size == '11.5 ft. × 10 ft.':
#             price = 90000
#         elif "ft ×" in size:  # custom size logic
#             l = float(custom_length)
#             w = float(custom_width)
#             sqft = l * w
#             price = sqft * 500  # price per sq ft — adjust your price logic
#         else:
#             price = 0

#         if package == 'silver':
#             price *= 0.8  # Apply 20% discount
#         elif package == 'gold':
#             price *= 1.2  # Apply 20% premium
#         elif package == 'platinum':
#             price *= 1.5  # Apply 50% premium


#         # ✅ Save or update OTP in DB (unique per email)
#         OtpVerification.objects.update_or_create(
#             email=email,
#             defaults={
#                 "otp": otp,
#                 "expires_at": expiry_time
#             }
#         )

#         # Store OTP + form data in session
#         request.session["otp"] = str(otp)
#         request.session["otp_expiry"] = expiry_time.isoformat()
#         request.session["form_data"] = {
#             "room_type": request.session.get("room_type", "N/A"),
#             "size": size,
#             "shape": shape,
#             "package": package,
#             "price": price,
#             "name": name,
#             "contact": contact,
#             "email": email,
#             "location": location,
#         }

#         # Send OTP
#         send_mail(
#             subject="Your OTP for Budget Estimation Confirmation",
#             message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[email],
#         )

#         return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

#     return redirect("kids_room_calculate")



from decimal import Decimal

def kids_submit_estimation_form(request):
    if request.method == "POST":

        size = request.POST.get("size")
        custom_length = request.POST.get("custom_length")
        custom_width = request.POST.get("custom_width")

        if size == "Custom" and custom_length and custom_width:
            size = f"{custom_length} ft × {custom_width} ft"

        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        otp = str(random.randint(1000, 9999))
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing
        if size == '7 ft. × 10 ft.':
            price = Decimal('50000')
        elif size == '8 ft. × 9 ft.':
            price = Decimal('60000')
        elif size == '9 ft. × 10 ft.':
            price = Decimal('70000')
        elif size == '10 ft. × 10 ft.':
            price = Decimal('80000')
        elif size == '11.5 ft. × 10 ft.':
            price = Decimal('90000')
        elif "ft ×" in size:
            price = Decimal(custom_length) * Decimal(custom_width) * Decimal('500')
        else:
            price = Decimal('0')

        if package == 'silver':
            price *= Decimal('0.8')
        elif package == 'gold':
            price *= Decimal('1.2')
        elif package == 'platinum':
            price *= Decimal('1.5')

        # Accessories
        accessories = []
        total_accessory_cost = Decimal("0")

        for key, value in request.POST.items():
            if key.startswith("accessory_qty_"):
                acc_id = key.replace("accessory_qty_", "")

                try:
                    acc_obj = Accessory.objects.get(id=acc_id)
                except Accessory.DoesNotExist:
                    continue

                qty = int(value)
                if qty <= 0:
                    continue

                acc_price = acc_obj.price or Decimal("0")
                item_total = acc_price * qty
                total_accessory_cost += item_total

                accessories.append({
                    "id": acc_obj.id,
                    "name": acc_obj.name,
                    "qty": qty,
                    "price": float(acc_price),
                    "total": float(item_total)
                })

        final_price = float(price + total_accessory_cost)

        OtpVerification.objects.update_or_create(
            email=email,
            defaults={"otp": otp, "expires_at": expiry_time}
        )

        request.session["form_data"] = {
            "room_type": "kids room",
            "size": size,
            "shape": shape,
            "package": package,
            "price": final_price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
            "accessories": accessories,
        }

        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name}, your OTP is {otp}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("kids_room_calculate")


# def wardrobes_submit_estimation_form(request):
#     if request.method == "POST":
#         size = request.POST.get("size")
#         custom_length = request.POST.get("custom_length")
#         custom_width = request.POST.get("custom_width")

#         # If custom, convert to numeric size
#         if size == "Custom" and custom_length and custom_width:
#             size = f"{custom_length} ft × {custom_width} ft"

#         shape = request.POST.get("shape")
#         package = request.POST.get("package")
#         name = request.POST.get("name")
#         contact = request.POST.get("contact")
#         email = request.POST.get("email")
#         location = request.POST.get("location")

#         # Generate OTP
#         otp = random.randint(1000, 9999)
#         expiry_time = timezone.now() + timedelta(minutes=5)

#         # Pricing logic
#         if size == '7 ft. × 10 ft.':
#             price = 50000
#         elif size == '8 ft. × 9 ft.':
#             price = 60000
#         elif size == '9 ft. × 10 ft.':
#             price = 70000
#         elif size == '10 ft. × 10 ft.':
#             price = 80000
#         elif size == '11.5 ft. × 10 ft.':
#             price = 90000
#         elif "ft ×" in size:  # custom size logic
#             l = float(custom_length)
#             w = float(custom_width)
#             sqft = l * w
#             price = sqft * 500  # price per sq ft — adjust your price logic
#         else:
#             price = 0


#         if package == 'silver':
#             price *= 0.8  # Apply 20% discount
#         elif package == 'gold':
#             price *= 1.2  # Apply 20% premium
#         elif package == 'platinum':
#             price *= 1.5  # Apply 50% premium



#         # ✅ Save or update OTP in DB (unique per email)
#         OtpVerification.objects.update_or_create(
#             email=email,
#             defaults={
#                 "otp": otp,
#                 "expires_at": expiry_time
#             }
#         )

#         # Store OTP + form data in session
#         request.session["otp"] = str(otp)
#         request.session["otp_expiry"] = expiry_time.isoformat()
#         request.session["form_data"] = {
#             "room_type": request.session.get("room_type", "N/A"),
#             "size": size,
#             "shape": shape,
#             "package": package,
#             "price": price,
#             "name": name,
#             "contact": contact,
#             "email": email,
#             "location": location,
#         }

#         # Send OTP
#         send_mail(
#             subject="Your OTP for Budget Estimation Confirmation",
#             message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[email],
#         )

#         return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

#     return redirect("wardrobes_calculate")



from decimal import Decimal

def wardrobes_submit_estimation_form(request):
    if request.method == "POST":

        size = request.POST.get("size")
        custom_length = request.POST.get("custom_length")
        custom_width = request.POST.get("custom_width")

        if size == "Custom" and custom_length and custom_width:
            size = f"{custom_length} ft × {custom_width} ft"

        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        otp = str(random.randint(1000, 9999))
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing
        if size == '7 ft. × 10 ft.':
            price = Decimal('50000')
        elif size == '8 ft. × 9 ft.':
            price = Decimal('60000')
        elif size == '9 ft. × 10 ft.':
            price = Decimal('70000')
        elif size == '10 ft. × 10 ft.':
            price = Decimal('80000')
        elif size == '11.5 ft. × 10 ft.':
            price = Decimal('90000')
        elif "ft ×" in size:
            price = Decimal(custom_length) * Decimal(custom_width) * Decimal('500')
        else:
            price = Decimal('0')

        if package == 'silver':
            price *= Decimal('0.8')
        elif package == 'gold':
            price *= Decimal('1.2')
        elif package == 'platinum':
            price *= Decimal('1.5')

        # Accessories
        accessories = []
        total_accessory_cost = Decimal("0")

        for key, value in request.POST.items():
            if key.startswith("accessory_qty_"):
                acc_id = key.replace("accessory_qty_", "")

                try:
                    acc_obj = Accessory.objects.get(id=acc_id)
                except Accessory.DoesNotExist:
                    continue

                qty = int(value)
                if qty <= 0:
                    continue

                acc_price = acc_obj.price or Decimal("0")
                item_total = acc_price * qty

                total_accessory_cost += item_total

                accessories.append({
                    "id": acc_obj.id,
                    "name": acc_obj.name,
                    "qty": qty,
                    "price": float(acc_price),
                    "total": float(item_total)
                })

        final_price = float(price + total_accessory_cost)

        OtpVerification.objects.update_or_create(
            email=email,
            defaults={"otp": otp, "expires_at": expiry_time}
        )

        request.session["form_data"] = {
            "room_type": "wardrobes",
            "size": size,
            "shape": shape,
            "package": package,
            "price": final_price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
            "accessories": accessories,
        }

        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name}, your OTP is {otp}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("wardrobes_calculate")


from decimal import Decimal

def poojaroom_submit_estimation_form(request):
    if request.method == "POST":

        size = request.POST.get("size")
        custom_length = request.POST.get("custom_length")
        custom_width = request.POST.get("custom_width")

        # Custom size formatting
        if size == "Custom" and custom_length and custom_width:
            size = f"{custom_length} ft × {custom_width} ft"

        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # OTP
        otp = str(random.randint(1000, 9999))
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Base pricing logic (converted to Decimal like kitchen)
        if size == '7 ft. × 10 ft.':
            price = Decimal('50000')
        elif size == '8 ft. × 9 ft.':
            price = Decimal('60000')
        elif size == '9 ft. × 10 ft.':
            price = Decimal('70000')
        elif size == '10 ft. × 10 ft.':
            price = Decimal('80000')
        elif size == '11.5 ft. × 10 ft.':
            price = Decimal('90000')
        elif "ft ×" in size:
            l = Decimal(custom_length)
            w = Decimal(custom_width)
            sqft = l * w
            price = sqft * Decimal('500')
        else:
            price = Decimal('0')

        # Package adjustment (same as kitchen)
        if package == 'silver':
            price *= Decimal('0.8')
        elif package == 'gold':
            price *= Decimal('1.2')
        elif package == 'platinum':
            price *= Decimal('1.5')

        # -----------------------------------------
        # 🔥 Collect accessories (safe like kitchen)
        # -----------------------------------------
        accessories = []
        total_accessory_cost = Decimal("0")

        for key, value in request.POST.items():
            if key.startswith("accessory_qty_"):
                accessory_id = key.replace("accessory_qty_", "")

                try:
                    accessory_obj = Accessory.objects.get(id=accessory_id)
                except Accessory.DoesNotExist:
                    continue

                qty = int(value)
                if qty <= 0:
                    continue

                # SAFE PRICE
                acc_price = accessory_obj.price or Decimal("0")
                item_total = acc_price * qty

                total_accessory_cost += item_total

                accessories.append({
                    "id": accessory_obj.id,
                    "name": accessory_obj.name,
                    "qty": qty,
                    "price": float(acc_price),
                    "total": float(item_total),
                })

        # FINAL PRICE = BASE PRICE + ACCESSORIES
        final_price = float(price) + float(total_accessory_cost)

        # Save OTP to DB
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Save to session
        request.session["form_data"] = {
            "room_type": request.session.get("room_type"),
            "size": size,
            "shape": shape,
            "package": package,
            "price": final_price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
            "accessories": accessories,
        }

        # Send OTP email
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("bedroom_calculate")

######################################################################################################


from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from PyPDF2 import PdfMerger
import os
from django.http import FileResponse


from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus.flowables import HRFlowable
from PyPDF2 import PdfReader, PdfWriter
import os, base64

from .models import OtpVerification
from django.conf import settings




def verify_otp(request):
    # ---------- GET: show OTP page ----------
    if request.method == "GET":
        form_data = request.session.get("form_data")
        if not form_data:
            messages.error(request, "Session expired. Please start again.")
            return redirect("select_platform")

        return render(request, "elite_interior/verify_otp.html", {"email": form_data["email"]})

    # ---------- POST: validate OTP and generate/send PDF ----------
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        email = request.POST.get("email")  # hidden field in form

        # Fetch OTP entry from DB
        try:
            otp_entry = OtpVerification.objects.get(email=email)
        except OtpVerification.DoesNotExist:
            messages.error(request, "No OTP found for this email. Please try again.")
            return redirect("select_platform")

        # Check expiry
        if otp_entry.is_expired():
            otp_entry.delete()
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect("select_platform")

        # Validate OTP
        if otp_entry.otp != user_otp:
            messages.error(request, "Invalid OTP. Please try again.")
            # show OTP page again with the email filled
            return render(request, "elite_interior/verify_otp.html", {"email": email})

        # OTP valid -> get form_data
        form_data = request.session.get("form_data")
        if not form_data:
            messages.error(request, "Session expired. Please fill the form again.")
            return redirect("select_platform")

        # prepare values from form_data
        name = form_data.get("name")
        contact = form_data.get("contact")
        location = form_data.get("location")
        room_type = form_data.get("room_type", "N/A")
        shape = form_data.get("shape", "N/A")
        price = form_data.get("price", 0)
        package_name = form_data.get("package")
        dimension = form_data.get("size")

        # --- Generate Styled PDF into memory ---
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30)
        elements = []
        styles = getSampleStyleSheet()

        centered_heading = ParagraphStyle(
            name="CenteredHeading",
            parent=styles["Heading1"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#3a5169"),
            fontName="Helvetica-Bold"
        )

        elements.append(HRFlowable(width="100%", thickness=1, color="#3a5169"))
        elements.append(Paragraph("BUDGET ESTIMATION REPORT", centered_heading))
        elements.append(Spacer(1, 20))

        # Format accessories safely if present
        accessories_list = form_data.get("accessories", [])
        if isinstance(accessories_list, list) and accessories_list:
            accessories_text = ", ".join(
                [f"{acc.get('name','')} (x{acc.get('qty',0)})" for acc in accessories_list]
            )
        else:
            accessories_text = "N/A"

        normal_style = styles["Normal"]

        label_style = ParagraphStyle(
            name="LabelStyle",
            parent=styles["Normal"],
            textColor=colors.HexColor("#3a5169"),
            fontName="Helvetica-Bold",
        )

        value_style = ParagraphStyle(
            name="ValueStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
        )

        client_info = [
            [Paragraph("Name :", label_style), Paragraph(name, value_style)],
            [Paragraph("Contact :", label_style), Paragraph(contact, value_style)],
            [Paragraph("Email :", label_style), Paragraph(email, value_style)],
            [Paragraph("Location :", label_style), Paragraph(location, value_style)],
            [Paragraph("Room Type :", label_style), Paragraph(room_type.replace("_", " ").title(), value_style)],
            [Paragraph("Style :", label_style), Paragraph(shape.replace("_", " ").title(), value_style)],
            [Paragraph("Accessories :", label_style), Paragraph(accessories_text, value_style)],
            [Paragraph("Package :", label_style), Paragraph(package_name, value_style)],
            [Paragraph("Dimension :", label_style), Paragraph(dimension, value_style)],
            [Paragraph("Estimated Price :", label_style), Paragraph(f"Rs: {price}", value_style)],
        ]

        table = Table(client_info, colWidths=[140, 360], hAlign="CENTER")
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        doc.build(elements)
        buffer.seek(0)

        # --- Merge with existing.pdf ---
        pdf_writer = PdfWriter()
        existing_pdf_path = os.path.join(settings.STATIC_ROOT, "pdf/existing.pdf")
        if not os.path.exists(existing_pdf_path):
            return HttpResponse("Error: existing.pdf not found", status=500)

        existing_reader = PdfReader(existing_pdf_path)
        for page in existing_reader.pages:
            pdf_writer.add_page(page)

        new_reader = PdfReader(buffer)
        for page in new_reader.pages:
            pdf_writer.add_page(page)

        # Write merged PDF into memory
        final_buffer = BytesIO()
        pdf_writer.write(final_buffer)
        final_buffer.seek(0)

        # Send email with in-memory PDF to admin
        subject = f"New Estimation Request - {name}"
        body = (
            f"A new estimation request has been submitted.\n\n"
            f"Name: {name}\n"
            f"Contact: {contact}\n"
            f"Email: {email}\n"
            f"Location: {location}\n"
            f"Package: {package_name}\n"
            f"Dimension: {dimension}\n"
            f"Estimated Price: Rs {price}\n\n"
            "Please find the attached PDF for details."
        )

        email_message = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.ADMIN_EMAIL],
        )
        email_message.attach(f"estimation_{name}.pdf", final_buffer.read(), "application/pdf")
        email_message.send(fail_silently=False)

        # Save PDF bytes in session for download BEFORE clearing form_data
        request.session["last_verified_data"] = form_data
        request.session["last_pdf"] = base64.b64encode(final_buffer.getvalue()).decode("utf-8")

        # Cleanup: remove OTP DB entry and form_data from session
        otp_entry.delete()
        request.session.pop("form_data", None)

        # Finally render success state (page shows download + countdown)
        return render(
            request,
            "elite_interior/verify_otp.html",
            {
                "email": email,
                "price": price,
                "download_pdf": reverse("download_estimation"),
                "home_url": reverse("home"),
            }
        )

    # any other HTTP method
    return redirect("select_platform")



from django.http import HttpResponse

def download_estimation(request):
    pdf_data_b64 = request.session.get("last_pdf")
    if not pdf_data_b64:
        return HttpResponse("No PDF available", status=404)

    pdf_data = base64.b64decode(pdf_data_b64)

    form_data = request.session.get("last_verified_data", {})
    name = form_data.get("name", "estimation")

    response = HttpResponse(pdf_data, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="estimation_{name}.pdf"'
    return response









def resend_otp(request):
    form_data = request.session.get("form_data")

    if not form_data:
        messages.error(request, "Session expired. Please start again.")
        return redirect("kitchen_calculate")

    # GET email from SESSION (recommended)
    email = form_data.get("email")

    if not email:
        messages.error(request, "Email missing. Please start again.")
        return redirect("kitchen_calculate")

    # Generate new OTP
    otp = str(random.randint(1000, 9999))

    # Update DB
    otp_entry, _ = OtpVerification.objects.get_or_create(email=email)
    otp_entry.otp = otp
    otp_entry.created_at = timezone.now()
    otp_entry.save()

    # Optional: store in session
    request.session["otp"] = otp

    # Send mail
    send_mail(
        subject="Your OTP for Budget Estimation (Resent)",
        message=f"Hi {form_data['name']},\n\nYour new OTP is: {otp}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("verify_otp")




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json

@csrf_exempt
def save_chat_query(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        query = data.get('query')

        if email and query:
            send_mail(
                subject="New Chat Query",
                message=f"Query: {query}\nEmail: {email}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False
            )
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'}, status=400)

    return JsonResponse({'status': 'invalid'}, status=405)






from django.shortcuts import render
from .forms import ClientForm, MaterialForm

def dashboard(request):
    client_form = ClientForm()
    material_form = MaterialForm()
    return render(request, "elite_interior/admin_dashboard.html", {
        "client_form": client_form,
        "material_form": material_form
    })




from django.http import JsonResponse
from .models import Product

def get_series_type(request):
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            return JsonResponse({
                'series_type': product.series or '',
                'thickness': product.thickness or '',  # if you want thickness later
                'price_per_cm': float(product.rate) if product.rate else 0,
                'unit_name': product.unit.name.lower() if product.unit else '',
                'origin': product.origin or '',
            })
        except Product.DoesNotExist:
            return JsonResponse({'series_type': '', 'thickness': '', 'price_per_cm': 0, 'unit_name': '', 'origin': ''})
    return JsonResponse({'series_type': '', 'thickness': '', 'price_per_cm': 0, 'unit_name': '', 'origin': ''})







import json
from itertools import groupby
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

import os
import io
import json
from itertools import groupby
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from PyPDF2 import PdfReader, PdfWriter
from reportlab.platypus import HRFlowable
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors


@csrf_exempt
def export_pdf(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    try:
        data = json.loads(request.body)
        materials = data.get("materials", [])
        client_data = data.get("client", {})

        # --- Generate MATERIAL PDF in memory ---
        material_buffer = io.BytesIO()
        doc = SimpleDocTemplate(material_buffer, pagesize=A4, topMargin=30)
        elements = []
        styles = getSampleStyleSheet()

        # Create a centered style
        centered_heading = ParagraphStyle(
            name="CenteredHeading",
            parent=styles["Heading1"],
            alignment=TA_CENTER,textColor=colors.HexColor("#3a5169"),
            fontName="Helvetica-Bold"
                )

   # Define a right-aligned style
        right_align_style = ParagraphStyle(
            name="RightAlign",
            parent=styles["Normal"],
            alignment=TA_RIGHT
        )

        # Title
        elements.append(HRFlowable(
        width="100%",        # full width of page/content
        thickness=1,         # line thickness
        lineCap='round',     # end style
        color='#3a5169',       # line color
        spaceBefore=10,      # space above the line
        spaceAfter=10,       # space below the line
        hAlign='CENTER',     # alignment
        vAlign='BOTTOM'      # vertical alignment
    ))
        elements.append(Paragraph("CLIENT DETAILS", centered_heading))
        elements.append(Spacer(1, 12))

       # Client info
        client_info = [
            ["Client Name :", client_data.get("client_name", "")],
            ["Address :", client_data.get("client_address", "")],
            ["Phone :", client_data.get("phone_number", "")],
            ["Email :", client_data.get("email_address", "")],
            ["Shop :", client_data.get("shop_name", "")]
        ]

        # Center the whole table
        client_table = Table(client_info, colWidths=[120, 200], hAlign="CENTER")

        # Center text inside each cell too
        client_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),  # <-- Center text in all cells
        ]))

        elements.append(client_table)
        elements.append(Spacer(1, 20))



 
        elements.append(HRFlowable(
            width="100%",        # full width of page/content
            thickness=1,         # line thickness
            lineCap='round',     # end style
            color='black',       # line color
            spaceBefore=10,      # space above the line
            spaceAfter=10,       # space below the line
            hAlign='CENTER',     # alignment
            vAlign='BOTTOM'      # vertical alignment
        ))

        elements.append(Paragraph("MATERIAL USED", centered_heading))
        elements.append(Spacer(1, 12))

        # Table header
        table_data = [["#", "Item", "Finish/Brand", "Material/Origin", "Unit", "Size", "Qty", "Price", "Offer Price"]]
        row_index = 1

        # Sort and group
        materials_sorted = sorted(materials, key=lambda m: m.get("design_place", ""))
        grouped_materials = groupby(materials_sorted, key=lambda m: m.get("design_place", ""))

        for design_place, group in grouped_materials:
            table_data.append([design_place] + [""] * (len(table_data[0]) - 1))

            for m in group:
                size = f"{m.get('height', '')} * {m.get('width', '')}"
                if m.get("thickness"):
                    size += f" * ({m.get('thickness', '')})"

                table_data.append([
                    row_index,
                    m.get("product", ""),
                    m.get("brand", ""),
                    m.get("origin", ""),
                    m.get("unit", ""),
                    size,
                    m.get("qty", ""),
                    m.get("total", ""),
                    m.get("offer", "")
                ])
                row_index += 1

        materials_table = Table(table_data, repeatRows=1,
                                colWidths=[25, 100, 80, 80, 40, 80, 40, 60, 60])
        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3a5169")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),

            # Add borders for all cells
            ("BOX", (0, 0), (-1, -1), 1, colors.black),     # outer border
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),  # inner grid
        ]

        for i, row in enumerate(table_data):
            if i > 0 and row[1] == "":
                style_commands.append(("SPAN", (0, i), (-1, i)))
                style_commands.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#dce6f1")))
                style_commands.append(("FONTNAME", (0, i), (-1, i), "Helvetica-Bold"))
                style_commands.append(("ALIGN", (0, i), (-1, i), "LEFT"))

        materials_table.setStyle(TableStyle(style_commands))
        elements.append(materials_table)

        
        # Grand total
        grand_total = sum(float(str(m.get("offer", "0")).replace("Rs", "").strip() or 0) for m in materials)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>GRAND TOTAL: {grand_total:.2f} Rs</b>", right_align_style))

        # Build material PDF in memory
        doc.build(elements)
        material_buffer.seek(0)

        # --- Merge with existing.pdf ---
        pdf_writer = PdfWriter()

        # Existing.pdf (static)
        existing_pdf_path = os.path.join(settings.STATIC_ROOT, "pdf/existing.pdf")
        existing_reader = PdfReader(existing_pdf_path)
        for page in existing_reader.pages:
            pdf_writer.add_page(page)

        # Material.pdf (from memory)
        material_reader = PdfReader(material_buffer)
        for page in material_reader.pages:
            pdf_writer.add_page(page)

        # Final merged PDF
        merged_buffer = io.BytesIO()
        pdf_writer.write(merged_buffer)
        merged_buffer.seek(0)

        return HttpResponse(
            merged_buffer,
            content_type="application/pdf",
            headers={"Content-Disposition": 'inline; filename="merged.pdf"'}
        )

    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)







def preview_pdf(request):
    return render(request, "elite_interior/preview_pdf.html")



import os
from django.http import FileResponse
from django.conf import settings
from PyPDF2 import PdfReader, PdfWriter

def merged_pdf_view(request):
    # Paths to your PDFs
    existing_pdf_path = os.path.join(settings.STATIC_ROOT, "pdf/existing.pdf")
    material_pdf_path = os.path.join(settings.STATIC_ROOT, "pdf/material.pdf")
    merged_pdf_path = os.path.join(settings.MEDIA_ROOT, "merged.pdf")

    pdf_writer = PdfWriter()

    # Add existing.pdf pages first
    existing_reader = PdfReader(existing_pdf_path)
    for page in existing_reader.pages:
        pdf_writer.add_page(page)

    # Add material.pdf pages after
    material_reader = PdfReader(material_pdf_path)
    for page in material_reader.pages:
        pdf_writer.add_page(page)

    # Save merged file
    with open(merged_pdf_path, "wb") as output_file:
        pdf_writer.write(output_file)

    return FileResponse(open(merged_pdf_path, "rb"), content_type="application/pdf")



def select_platform(request):
    if request.method == "POST":
        selected = request.POST.get("platform")

        # Save room_type in session
        request.session["room_type"] = selected  

        # Redirect to respective calculate page
        if selected == "kitchen":
            return redirect("kitchen_calculate")
        elif selected == "bedroom":
            return redirect("bedroom_calculate")
        elif selected == "bathroom":
            return redirect("bathroom_calculate")
        elif selected == "dining":
            return redirect("dining_calculate")
        elif selected == "living":
            return redirect("livingroom_calculate")
        elif selected == "kids":
            return redirect("kidsroom_calculate")
        elif selected == "wardrobes":
            return redirect("wardrobe_calculate")
        elif selected == "poojaroom":
            return redirect("poojaroom_calculate")

    return render(request, "select_platform.html")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import send_mail
from django.conf import settings

@csrf_exempt
def save_chat_query(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            email = data.get("email")
            query = data.get("query")

            if not email or "@" not in email:
                return JsonResponse({"status": "error", "message": "Invalid email"})

            subject_admin = f"Chat Query: {query}"
            message_admin = f"User Email: {email}\nQuery: {query}"

            subject_client = "Thanks for contacting Home Den"
            message_client = f"Hi,\n\nWe received your request about: {query}\nOur team will reach out to you at {email}.\n\nBest,\nHome Den"

            # Send emails
            send_mail(subject_admin, message_admin, settings.EMAIL_HOST_USER, [settings.ADMIN_EMAIL])
            send_mail(subject_client, message_client, settings.EMAIL_HOST_USER, [email])

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request"})







from django.shortcuts import render, get_object_or_404
from .models import SEOServicePage

def seo_service_detail(request, slug):
    grid = WhatWeDo_Grid.objects.all()
    page = get_object_or_404(SEOServicePage, slug=slug)
    return render(request, "seo_page.html", {"page": page, "grid":grid})




def mesurement_cal(request):
    return render(request, "elite_interior/measurement_cal.html")



#################################################

from django.contrib.auth import authenticate, login
from django.contrib import messages


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("quotation_index")   # go to quotation dashboard
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "registration/login.html")




from django.forms import modelform_factory
from .models import Client
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404


ClientForm = modelform_factory(Client, fields="__all__")


# 📋 (optional but useful) Client list

from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required
def client_index(request):

    search = request.GET.get("search", "")

    clients = Client.objects.all()

    if search:
        clients = clients.filter(
            Q(name__icontains=search) |
            Q(phone1__icontains=search) |
            Q(phone2__icontains=search) |
            Q(id__icontains=search)
        )

    return render(request, "client/index.html", {
        "clients": clients,
        "search": search
    })



# ➕ Create client
# ➕ Create client
@login_required
def client_create(request):
    if request.method == "POST":
        Client.objects.create(
            name=request.POST["name"],
            phone1=request.POST["phone1"],
            phone2=request.POST.get("phone2"),
            email=request.POST.get("email"),
            location=request.POST["location"],
            GST=request.POST.get("GST"),

            discount_percent=request.POST.get("discount_percent") or 0,
            discount_amount=request.POST.get("discount_amount") or 0,
            discount_mode=request.POST.get("discount_mode") or "percent",

            notes=request.POST.get("notes"),
        )

        return redirect("quotation_index")

    return render(request, "client/create.html")


# ✏️ Edit client
# ✏️ Edit client
@login_required
def client_update(request, id):
    client = get_object_or_404(Client, id=id)

    if request.method == "POST":
        client.name = request.POST["name"]
        client.phone1 = request.POST["phone1"]
        client.phone2 = request.POST.get("phone2")
        client.email = request.POST.get("email")
        client.location = request.POST["location"]
        client.GST = request.POST.get("GST")

        client.discount_percent = request.POST.get("discount_percent") or 0
        client.discount_amount = request.POST.get("discount_amount") or 0
        client.discount_mode = request.POST.get("discount_mode") or "percent"

        client.notes = request.POST.get("notes")

        client.save()

        return redirect("quotation_index")

    return render(request, "client/update.html", {
        "client": client
    })

# 🗑 Delete client (with confirmation)
@login_required
def client_delete(request, id):
    client = get_object_or_404(Client, id=id)

    if request.method == "POST":
        client.delete()
        return redirect("quotation_index")

    return render(
        request,
        "quotation/client/confirm_delete.html",
        {"client": client},
    )


###################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from .models import Client, Quotation


QuotationForm = modelform_factory(
    Quotation,
    exclude=("created_at",)
)


# 🚪 /quotation/
@login_required
def quotation_entry(request):
    return redirect("quotation_index")


# 📋 All quotations list
from django.db.models import Sum


from django.shortcuts import render
from django.db.models import Count, Sum
from .models import Client, Quotation
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # Total counts
    total_clients = Client.objects.count()
    total_quotations = Quotation.objects.count() # Total line items
    
    # Financials (Sum of all Quotation totals)
    total_revenue = Quotation.objects.aggregate(Sum('total'))['total__sum'] or 0

    # Unique Client Quotes (Groups)
    quotation_groups = Quotation.objects.values("client").distinct().count()

    # Get the 5 most recent quotations for the "Recent Activity" table
    recent_activity = Quotation.objects.select_related('client').order_by('-created_at')[:5]

    return render(request, "quotation/dashboard.html", {
        "total_clients": total_clients,
        "total_quotations": total_quotations,
        "quotation_groups": quotation_groups,
        "total_revenue": total_revenue,
        "recent_activity": recent_activity,
    })




from django.db.models import Sum, Q

@login_required
def quotation_index(request):

    search = request.GET.get("search", "")

    quotations = (
        Quotation.objects
        .values(
            "client__id",
            "client__name",
            "client__phone1",
        )
        .annotate(
            total_qty=Sum("qty"),
            grand_total=Sum("total"),
        )
    )

    if search:
        quotations = quotations.filter(
            Q(client__name__icontains=search) |
            Q(client__phone1__icontains=search)
        )

    quotations = quotations.order_by("-client__id")

    return render(request, "quotation/index.html", {
        "quotations": quotations,
        "search": search
    })


@login_required
def quotation_create(request):

    if request.method == "POST":

        client_id = request.POST.get("client")

        start_date = request.POST.get("estimate_start_date")
        end_date = request.POST.get("estimate_end_date")

        Client.objects.filter(id=client_id).update(
            estimate_start_date=start_date,
            estimate_end_date=end_date,
        )

        floors = request.POST.getlist("floor[]")
        locations = request.POST.getlist("location[]")
        elements = request.POST.getlist("element[]")

        images = request.POST.getlist("image[]")
        fullsemis = request.POST.getlist("full_semi[]")

        core_materials = request.POST.getlist("core_material[]")
        finish_materials = request.POST.getlist("finish_material[]")
        brands = request.POST.getlist("brand[]")
        specifications = request.POST.getlist("specification[]")

        units = request.POST.getlist("unit[]")
        lengths = request.POST.getlist("length[]")
        widths = request.POST.getlist("width[]")
        qtys = request.POST.getlist("qty[]")

        quotation_rows = []

        for i in range(len(elements)):

            if not elements[i]:
                continue

            length = float(lengths[i] or 0)
            width = float(widths[i] or 0)
            qty = int(qtys[i] or 1)

            area = length * width

            # get price from FullSemi
            price = 0
            fullsemi_id = fullsemis[i] if i < len(fullsemis) else None

            if fullsemi_id:
                try:
                    price = FullSemi.objects.get(id=fullsemi_id).rate
                except FullSemi.DoesNotExist:
                    price = 0

            total = area * price * qty

            quotation_rows.append(
                Quotation(
                    client_id=client_id,
                    floor=floors[i] if i < len(floors) else "",
                    location=locations[i] if i < len(locations) else "",
                    element=elements[i],

                    image_id=images[i] if i < len(images) and images[i] else None,
                    full_semi_id=fullsemi_id,

                    core_material=core_materials[i] if i < len(core_materials) else "",
                    finish_material=finish_materials[i] if i < len(finish_materials) else "",
                    brand=brands[i] if i < len(brands) else "",
                    specification=specifications[i] if i < len(specifications) else "",

                    unit=units[i] if i < len(units) else "",

                    length=length,
                    width=width,
                    area=area,

                    price=price,
                    qty=qty,
                    total=total,
                )
            )

        if quotation_rows:
            Quotation.objects.bulk_create(quotation_rows)

        return redirect("quotation_index")

    return render(request, "quotation/create.html", {
        "clients": Client.objects.all(),
        "images": Image.objects.all(),
        "fullsemis": FullSemi.objects.all(),
        "previous_specs": list(
        Quotation.objects.exclude(specification="")
            .values_list("specification", flat=True)
            .distinct()[:200]
        )

    })



from django.db import transaction

@login_required
def quotation_update(request, id):

    rows = Quotation.objects.filter(client_id=id)

    if not rows.exists():
        return redirect("quotation_index")

    client_id = id

    if request.method == "POST":

        start_date = request.POST.get("estimate_start_date")
        end_date = request.POST.get("estimate_end_date")

        Client.objects.filter(id=client_id).update(
            estimate_start_date=start_date,
            estimate_end_date=end_date,
        )

        floors = request.POST.getlist("floor[]")
        locations = request.POST.getlist("location[]")
        elements = request.POST.getlist("element[]")

        images = request.POST.getlist("image[]")
        fullsemis = request.POST.getlist("full_semi[]")

        core_materials = request.POST.getlist("core_material[]")
        finish_materials = request.POST.getlist("finish_material[]")
        brands = request.POST.getlist("brand[]")
        specifications = request.POST.getlist("specification[]")

        units = request.POST.getlist("unit[]")
        lengths = request.POST.getlist("length[]")
        widths = request.POST.getlist("width[]")
        qtys = request.POST.getlist("qty[]")

        quotation_rows = []

        # preload fullsemi rates
        fullsemi_rates = {f.id: f.rate for f in FullSemi.objects.all()}

        for i in range(len(elements)):

            if not elements[i]:
                continue

            try:
                length = float(lengths[i])
            except:
                length = 0

            try:
                width = float(widths[i])
            except:
                width = 0

            qty = int(qtys[i] or 1)

            area = length * width

            fullsemi_id = fullsemis[i] if i < len(fullsemis) else None
            price = fullsemi_rates.get(int(fullsemi_id), 0) if fullsemi_id else 0

            total = area * price * qty

            quotation_rows.append(
                Quotation(
                    client_id=client_id,

                    floor=floors[i].strip() if i < len(floors) else "",
                    location=locations[i].strip() if i < len(locations) else "",
                    element=elements[i].strip(),

                    image_id=int(images[i]) if i < len(images) and images[i] else None,
                    full_semi_id=fullsemi_id,

                    core_material=core_materials[i] if i < len(core_materials) else "",
                    finish_material=finish_materials[i] if i < len(finish_materials) else "",
                    brand=brands[i] if i < len(brands) else "",
                    specification=specifications[i] if i < len(specifications) else "",

                    unit=units[i] if i < len(units) else "",

                    length=length,
                    width=width,
                    area=area,

                    price=price,
                    qty=qty,
                    total=total,
                )
            )

        with transaction.atomic():
            rows.delete()
            if quotation_rows:
                Quotation.objects.bulk_create(quotation_rows)

        return redirect("quotation_index")

    return render(request, "quotation/update.html", {
        "quotation_rows": rows,
        "clients": Client.objects.all(),
        "images": Image.objects.all(),
        "fullsemis": FullSemi.objects.all(),
        "previous_specs": list(
            Quotation.objects.exclude(specification="")
            .values_list("specification", flat=True)
            .distinct()[:200]
        )
    })



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Client, Quotation


@login_required
def quotation_detail(request, client_id):

    rows = Quotation.objects.select_related(
        "client", "image", "full_semi"
    ).filter(client_id=client_id)

    if not rows.exists():
        return redirect("quotation_index")

    client = rows.first().client

    # Subtotal
    subtotal = sum(r.total for r in rows)

    # GST
    gst_rate = float(client.GST or 0)
    gst_amount = round(subtotal * gst_rate / 100, 2)

    # Total after GST
    total_with_gst = subtotal + gst_amount


    # ---------------------------
    # Discount Handling
    # ---------------------------

    discount_amount = 0
    discount_percent = 0
    discount_mode = "amount"

    if client.discount_mode == "percent":

        discount_percent = float(client.discount_percent or 0)
        discount_amount = round(subtotal * discount_percent / 100, 2)
        discount_mode = "percent"

    else:

        discount_amount = float(client.discount_amount or 0)

        if subtotal > 0:
            discount_percent = round((discount_amount / subtotal) * 100, 2)

        discount_mode = "amount"


    # Final total
    grand_total = max(
        round(total_with_gst - discount_amount, 2),
        0
    )


    return render(request, "quotation/detail.html", {
        "client": client,
        "rows": rows,

        "subtotal": subtotal,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,

        "discount_amount": discount_amount,
        "discount_percent": discount_percent,
        "discount_mode": discount_mode,

        "grand_total": grand_total,
    })


from io import BytesIO
from datetime import date
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from PyPDF2 import PdfMerger
from xhtml2pdf import pisa
import os
from django.db.models.functions import Lower
from django.db.models import Case, When, Value, IntegerField



@login_required
def quotation_pdf(request, client_id):

    client = Client.objects.get(id=client_id)

    # Order rows for grouping
    # rows = Quotation.objects.filter(
    #     client_id=client_id
    # ).annotate(
    #     floor_lower=Lower("floor"),
    #     location_lower=Lower("location")
    # ).order_by("floor_lower", "location_lower", "id")

    rows = Quotation.objects.filter(
        client_id=client_id
    ).annotate(
        floor_lower=Lower("floor"),
        location_lower=Lower("location"),
        end_priority=Case(
            When(element__iexact="FLASE CEILING - PLAIN", then=Value(1)),
            When(element__iexact="ELECTRICAL LABOUR", then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by("end_priority", "id")

    # Subtotal
    subtotal = sum(r.total for r in rows)


    # GST
    gst_rate = float(client.GST or 0)
    gst_amount = round(subtotal * gst_rate / 100, 2)

    # NEW → subtotal + GST

    total_with_gst = subtotal + gst_amount

    # -------------------------
    # Discount Handling
    # -------------------------

    discount_amount = 0

    if client.discount_mode == "percent":

        percent = float(client.discount_percent or 0)
        discount_amount = round(subtotal * percent / 100, 2)

    else:

        discount_amount = float(client.discount_amount or 0)


    # Final total
    grand_total = max(
        round((subtotal + gst_amount) - discount_amount, 2),
        0
    )


    quotation_number = f"QTN-{client.id}-{date.today().strftime('%m%y')}"


    # Render HTML
    template = get_template("quotation/pdf.html")

    html = template.render({
        "client": client,
        "rows": rows,

        "total_amount": subtotal,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,

        "discount": discount_amount,
        "grand_total": grand_total,

        "quotation_number": quotation_number,
        "total_with_gst": total_with_gst,
        "today": date.today(),
    })


    # Generate quotation PDF
    quotation_buffer = BytesIO()

    pisa_status = pisa.CreatePDF(
        html,
        dest=quotation_buffer,
        link_callback=fetch_resources
    )

    if pisa_status.err:
        return HttpResponse("PDF generation error", status=500)

    quotation_buffer.seek(0)


    # Static PDFs
    front_pdf = os.path.join(settings.MEDIA_ROOT, "pdfs", "front.pdf")
    back_pdf = os.path.join(settings.MEDIA_ROOT, "pdfs", "back.pdf")

    merger = PdfMerger()

    if os.path.exists(front_pdf):
        merger.append(front_pdf)

    merger.append(quotation_buffer)

    if os.path.exists(back_pdf):
        merger.append(back_pdf)


    final_buffer = BytesIO()

    merger.write(final_buffer)
    merger.close()

    final_buffer.seek(0)


    response = HttpResponse(
        final_buffer.read(),
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'inline; filename="QTN_{client.name}_{date.today().strftime("%Y%m%d")}.pdf"'
    )

    return response





@login_required
def save_quotation_totals(request, client_id):

    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":

        def safe_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return 0

        gst_percent = safe_float(request.POST.get("gst_percent"))
        discount_value = safe_float(request.POST.get("discount_value"))
        discount_type = request.POST.get("discount_type") or "amount"

        # Save GST
        client.GST = gst_percent

        subtotal = sum(
            r.total for r in Quotation.objects.filter(client_id=client_id)
        )

        # Save discount correctly
        if discount_type == "percent":

            client.discount_percent = discount_value
            client.discount_amount = round(subtotal * discount_value / 100, 2)

            client.discount_mode = "percent"

        else:

            client.discount_amount = discount_value
            client.discount_percent = 0

            client.discount_mode = "amount"

        client.save()

    return redirect("quotation_detail", client_id=client_id)






import os
from django.conf import settings
from urllib.parse import urlparse


def fetch_resources(uri, rel):
    path = urlparse(uri).path

    if path.startswith(settings.MEDIA_URL):
        return os.path.join(settings.MEDIA_ROOT, path.replace(settings.MEDIA_URL, ""))

    if path.startswith(settings.STATIC_URL):
        return os.path.join(settings.STATIC_ROOT, path.replace(settings.STATIC_URL, ""))

    return uri


##delete all quotations of a client (with confirmation)
@login_required
def quotation_delete(request, id):

    # id is CLIENT ID
    rows = Quotation.objects.filter(client_id=id)

    if not rows.exists():
        return redirect("quotation_index")

    if request.method == "POST":
        rows.delete()
        return redirect("quotation_index")

    return render(request, "quotation/confirm_delete.html", {
        "client": rows.first().client
    })


###################################################

@login_required
def fullsemi_index(request):
    data = FullSemi.objects.all()
    return render(request, "fullsemi/index.html", {"data": data})


@login_required
def fullsemi_create(request):
    if request.method == "POST":
        FullSemi.objects.create(
            name=request.POST["name"],
            rate=request.POST["rate"]
        )
        return redirect("fullsemi_index")

    return render(request, "fullsemi/create.html")


@login_required
def fullsemi_update(request, id):
    obj = get_object_or_404(FullSemi, id=id)

    if request.method == "POST":
        obj.name = request.POST["name"]
        obj.rate = request.POST["rate"]
        obj.save()
        return redirect("fullsemi_index")

    return render(request, "fullsemi/update.html", {
        "item": obj
    })


@login_required
def fullsemi_delete(request, id):
    obj = get_object_or_404(FullSemi, id=id)

    if request.method == "POST":
        obj.delete()
        return redirect("fullsemi_index")

    return render(request, "fullsemi/confirm_delete.html", {
        "item": obj
    })


################################################


from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelform_factory
from .models import Image
from django.contrib.auth.decorators import login_required

ImageForm = modelform_factory(Image, fields="__all__")


@login_required
def image_index(request):
    data = Image.objects.all()
    return render(request, "image/index.html", {"data": data})


@login_required
def image_create(request):
    if request.method == "POST":
        Image.objects.create(
            name=request.POST["name"],
            image=request.FILES["image"]
        )
        return redirect("image_index")

    return render(request, "image/create.html")


@login_required
def image_update(request, id):
    image = get_object_or_404(Image, id=id)

    if request.method == "POST":

        image.name = request.POST["name"]

        if "image" in request.FILES:
            image.image = request.FILES["image"]

        image.save()
        return redirect("image_index")

    return render(request, "image/update.html", {
        "image": image
    })




@login_required
def image_delete(request, id):
    obj = get_object_or_404(Image, id=id)

    if request.method == "POST":
        obj.delete()
        return redirect("image_index")

    return render(request, "image/confirm_delete.html", {
        "image": obj
    })




from django.shortcuts import render

def ai_calculator(request):
    return render(request, "ai/calculator.html")



# views.py

from django.http import JsonResponse
from .models import InteriorPrice


def get_products(request, location):

    products = InteriorPrice.objects.filter(location__iexact=location)

    data = []

    for p in products:
        data.append({
            "product": p.product,
            "base": p.base_rate,
            "laminate": p.laminate_price,
            "acrylic": p.acrylic_price,
            "veneer": p.veneer_price,
            "silver": p.silver_package,
            "gold": p.gold_package,
            "platinum": p.platinum_package
        })

    return JsonResponse(data, safe=False)

    
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, "404.html", status=404)

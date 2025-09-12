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
    return render(request, 'elite_interior/kids.html', {
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

    packages = ['silver', 'gold', 'platinum']

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'kitchen_sizes': kitchen_sizes,
        'packages': packages,
    }
    return render(request, 'calculate/kitchencalculate.html', context)

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

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'bedroom_sizes': bedroom_sizes,
        'packages': packages,
    }
    return render(request, 'calculate/bedroomcalculate.html', context)

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

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'bathroom_sizes': bathroom_sizes,
        'packages': packages,
    }
    return render(request, 'calculate/bathroomcalculation.html', context)

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

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'kids_room_sizes': kidsroom_sizes,
        'packages': packages,
    }
    return render(request, 'calculate/Kidsroomcalculate.html', context)


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

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'living_room_sizes': livingroom_sizes,
        'packages': packages,
    }
    return render(request, 'calculate/livingroomcalculate.html', context)


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

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'wardrobe_sizes': wardrobe_sizes,
        'packages': packages,
    }
    return render(request, 'calculate/wardrobescalculate.html', context)

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

    form = BudgetCalculationForm()
    context = {
        'form': form,
        'dining_sizes': dining_sizes,
        'packages': packages,
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

from .models import OtpVerification


def kitchen_submit_estimation_form(request):
    if request.method == "POST":
        size = request.POST.get("size")
        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # Generate OTP
        otp = str(random.randint(1000, 9999))
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing logic
        if size == '7 ft. × 10 ft.':
            price = 50000
        elif size == '8 ft. × 9 ft.':
            price = 60000
        elif size == '9 ft. × 10 ft.':
            price = 70000
        elif size == '10 ft. × 10 ft.':
            price = 80000
        elif size == '11.5 ft. × 10 ft.':
            price = 90000
        else:
            price = 0  # Default price

        if package == 'silver':
            price *= 0.8  # Apply 20% discount
        elif package == 'gold':
            price *= 1.2  # Apply 20% premium
        elif package == 'platinum':
            price *= 1.5  # Apply 50% premium

        # ✅ Save or update OTP in DB (unique per email)
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Store form data in session (without OTP)
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





def bedroom_submit_estimation_form(request):
    if request.method == "POST":
        size = request.POST.get("size")
        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # Generate OTP
        otp = random.randint(1000, 9999)
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing logic
        if size == '7 ft. × 10 ft.':
            price = 50000
        elif size == '8 ft. × 9 ft.':
            price = 60000
        elif size == '9 ft. × 10 ft.':
            price = 70000
        elif size == '10 ft. × 10 ft.':
            price = 80000
        elif size == '11.5 ft. × 10 ft.':
            price = 90000
        else:
            price = 0

        if package == 'silver':
            price *= 0.8  # Apply 20% discount
        elif package == 'gold':
            price *= 1.2  # Apply 20% premium
        elif package == 'platinum':
            price *= 1.5  # Apply 50% premium

        # ✅ Save or update OTP in DB (unique per email)
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Store OTP + form data in session
        request.session["otp"] = str(otp)
        request.session["otp_expiry"] = expiry_time.isoformat()
        request.session["form_data"] = {
            "room_type": request.session.get("room_type"),
            "size": size,
            "shape": shape,
            "package": package,
            "price": price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
        }

        # Send OTP
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("bedroom_calculate")


def living_submit_estimation_form(request):
    if request.method == "POST":
        size = request.POST.get("size")
        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # Generate OTP
        otp = random.randint(1000, 9999)
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing logic
        if size == '7 ft. × 10 ft.':
            price = 50000
        elif size == '8 ft. × 9 ft.':
            price = 60000
        elif size =='9 ft. × 10 ft.':
            price =70000
        elif size == '10 ft. × 10 ft.':
            price = 80000
        elif size == '11.5 ft. × 10 ft.':
            price = 90000
        else:
            price = 0

        if package == 'silver':
            price *= 0.8  # Apply 20% discount
        elif package == 'gold':
            price *= 1.2  # Apply 20% premium
        elif package == 'platinum':
            price *= 1.5  # Apply 50% premium


        # ✅ Save or update OTP in DB (unique per email)
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Store OTP + form data in session
        request.session["otp"] = str(otp)
        request.session["otp_expiry"] = expiry_time.isoformat()
        request.session["form_data"] = {
            "room_type": request.session.get("room_type"),  # ✅ Pull it from session
            "size": size,
            "shape": shape,
            "package": package,
            "price": price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
        }

        # Send OTP
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("living_room_calculate")

def bathroom_submit_estimation_form(request):
    if request.method == "POST":
        size = request.POST.get("size")
        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # Generate OTP
        otp = random.randint(1000, 9999)
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing logic
        if size == '7 ft. × 10 ft.':
            price = 50000
        elif size == '8 ft. × 9 ft.':
            price = 60000
        elif size == '9 ft. × 10 ft.':
            price = 70000
        elif size == '10 ft. × 10 ft.':
            price = 80000
        elif size == '11.5 ft. × 10 ft.':
            price = 90000
        else:
            price = 0


        if package == 'silver':
            price *= 0.8  # Apply 20% discount
        elif package == 'gold':
            price *= 1.2  # Apply 20% premium
        elif package == 'platinum':
            price *= 1.5  # Apply 50% premium


        # ✅ Save or update OTP in DB (unique per email)
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Store OTP + form data in session
        request.session["otp"] = str(otp)
        request.session["otp_expiry"] = expiry_time.isoformat()
        request.session["form_data"] = {
            "room_type": request.session.get("room_type", "N/A"),
            "size": size,
            "shape": shape,
            "package": package,
            "price": price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
        }

        # Send OTP
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("bath_room_calculate")


def dining_submit_estimation_form(request):
    if request.method == "POST":
        size = request.POST.get("size")
        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # Generate OTP
        otp = random.randint(1000, 9999)
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing logic
        if size == '7 ft. × 10 ft.':
            price = 50000
        elif size == '8 ft. × 9 ft.':
            price = 60000
        elif size == '9 ft. × 10 ft.':
            price = 70000
        elif size == '10 ft. × 10 ft.':
            price = 80000
        elif size == '11.5 ft. × 10 ft.':
            price = 90000
        else:
            price = 0


        if package == 'silver':
            price *= 0.8  # Apply 20% discount
        elif package == 'gold':
            price *= 1.2  # Apply 20% premium
        elif package == 'platinum':
            price *= 1.5  # Apply 50% premium


        # ✅ Save or update OTP in DB (unique per email)
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Store OTP + form data in session
        request.session["otp"] = str(otp)
        request.session["otp_expiry"] = expiry_time.isoformat()
        request.session["form_data"] = {
            "room_type": request.session.get("room_type", "N/A"),
            "size": size,
            "shape": shape,
            "package": package,
            "price": price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
        }

        # Send OTP
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("dining_calculate")

def kids_submit_estimation_form(request):
    if request.method == "POST":
        size = request.POST.get("size")
        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # Generate OTP
        otp = random.randint(1000, 9999)
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing logic
        if size == '7 ft. × 10 ft.':
            price = 50000
        elif size == '8 ft. × 9 ft.':
            price = 60000
        elif size == '9 ft. × 10 ft.':
            price = 70000
        elif size == '10 ft. × 10 ft.':
            price = 80000
        elif size == '11.5 ft. × 10 ft.':
            price = 90000
        else:
            price = 0

        if package == 'silver':
            price *= 0.8  # Apply 20% discount
        elif package == 'gold':
            price *= 1.2  # Apply 20% premium
        elif package == 'platinum':
            price *= 1.5  # Apply 50% premium


        # ✅ Save or update OTP in DB (unique per email)
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Store OTP + form data in session
        request.session["otp"] = str(otp)
        request.session["otp_expiry"] = expiry_time.isoformat()
        request.session["form_data"] = {
            "room_type": request.session.get("room_type", "N/A"),
            "size": size,
            "shape": shape,
            "package": package,
            "price": price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
        }

        # Send OTP
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("kids_room_calculate")


def wardrobes_submit_estimation_form(request):
    if request.method == "POST":
        size = request.POST.get("size")
        shape = request.POST.get("shape")
        package = request.POST.get("package")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # Generate OTP
        otp = random.randint(1000, 9999)
        expiry_time = timezone.now() + timedelta(minutes=5)

        # Pricing logic
        if size == '7 ft. × 10 ft.':
            price = 50000
        elif size == '8 ft. × 9 ft.':
            price = 60000
        elif size == '9 ft. × 10 ft.':
            price = 70000
        elif size == '10 ft. × 10 ft.':
            price = 80000
        elif size == '11.5 ft. × 10 ft.':
            price = 90000
        else:
            price = 0


        if package == 'silver':
            price *= 0.8  # Apply 20% discount
        elif package == 'gold':
            price *= 1.2  # Apply 20% premium
        elif package == 'platinum':
            price *= 1.5  # Apply 50% premium



        # ✅ Save or update OTP in DB (unique per email)
        OtpVerification.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "expires_at": expiry_time
            }
        )

        # Store OTP + form data in session
        request.session["otp"] = str(otp)
        request.session["otp_expiry"] = expiry_time.isoformat()
        request.session["form_data"] = {
            "room_type": request.session.get("room_type", "N/A"),
            "size": size,
            "shape": shape,
            "package": package,
            "price": price,
            "name": name,
            "contact": contact,
            "email": email,
            "location": location,
        }

        # Send OTP
        send_mail(
            subject="Your OTP for Budget Estimation Confirmation",
            message=f"Hi {name},\n\nYour OTP is: {otp}. It will expire in 5 minutes.\n\nThank you.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return render(request, "elite_interior/verify_otp.html", {"email": email, "name": name})

    return redirect("wardrobes_calculate")

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
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        email = request.POST.get("email")  # should be passed as hidden field in form

        # ✅ Fetch OTP entry from DB
        try:
            otp_entry = OtpVerification.objects.get(email=email)
        except OtpVerification.DoesNotExist:
            messages.error(request, "No OTP found for this email. Please try again.")
            return redirect("select_platform")

        # ✅ Check expiry
        if otp_entry.is_expired():
            otp_entry.delete()
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect("select_platform")

        # ✅ Validate OTP
        if otp_entry.otp != user_otp:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, "elite_interior/verify_otp.html", {"email": email})

        # ✅ OTP valid → use form_data from session
        form_data = request.session.get("form_data")
        if not form_data:
            messages.error(request, "Session expired. Please fill the form again.")
            return redirect("select_platform")

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

        # Title
        elements.append(HRFlowable(width="100%", thickness=1, color="#3a5169"))
        elements.append(Paragraph("BUDGET ESTIMATION REPORT", centered_heading))
        elements.append(Spacer(1, 20))

        client_info = [
            ["Name :", name],
            ["Contact :", contact],
            ["Email :", email],
            ["Location :", location],
            ["Room Type :", room_type.replace("_", " ").title()],
            ["Style :", shape.replace("_", " ").title()],
            ["Package :", package_name],
            ["Dimension :", dimension],
            ["Estimated Price :", f"Rs: {price}"],
        ]

        table = Table(client_info, colWidths=[150, 350], hAlign="CENTER")
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#3a5169")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWHEIGHT", (0, 0), (-1, -1), 22),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
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

        # ✅ Write merged PDF into memory
        final_buffer = BytesIO()
        pdf_writer.write(final_buffer)
        final_buffer.seek(0)

        # ✅ Send email with in-memory PDF
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

        # ✅ Cleanup: remove OTP + session data
        otp_entry.delete()
        request.session.pop("form_data", None)

        # ✅ Save PDF bytes in session for download
        request.session["last_verified_data"] = form_data
        request.session["last_pdf"] = base64.b64encode(final_buffer.getvalue()).decode("utf-8")

        return render(
            request,
            "elite_interior/verify_otp.html",
            {
                "price": price,
                "download_pdf": reverse("download_estimation"),
                "home_url": reverse("home"),
            }
        )

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
    if form_data:
        otp = random.randint(1000, 9999)
        request.session["otp"] = str(otp)

        send_mail(
            subject="Your OTP for Budget Estimation Confirmation (Resent)",
            message=f"Hi {form_data['name']},\n\nYour new OTP is: {otp}. Please enter this to confirm your estimation request.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[form_data["email"]],
        )

        messages.success(request, "A new OTP has been sent to your email.")
    else:
        messages.error(request, "Session expired. Please start again.")
        return redirect("kitchen_calculate")

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





def mesurement_cal(request):
    return render(request, "elite_interior/measurement_cal.html")


from django.shortcuts import render

def custom_404(request, exception):
    return render(request, "404.html", status=404)

"""
URL configuration for interior project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
# from django.urls import path, include, re_path
# from django.conf import settings
# from django.conf.urls.static import static
# from elite_interior.views import serve_media
# import os

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('elite_interior.urls')),  # link app urls
#     path('i18n/', include('django.conf.urls.i18n')), 
# ]



# # Development: Serve media and static files
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
#         urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# # Production: Secure media serving
# else:
#     urlpatterns += [
#         re_path(r'^media/(?P<path>.*)$', serve_media),
#     ]


from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

# 👇 Media security view (if you're using one)
from elite_interior.views import serve_media

# 🧭 Sitemap imports
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

# 📝 Import models for dynamic sitemaps
from elite_interior.models import Blog, Project, Product  # make sure these are correct

# =============================
# Static Pages Sitemap
# =============================
class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return [
            'home', 'about', 'contact', 'service',
            'silver', 'gold', 'platinum',
            'blog_list', 'projects',
            'kitchen_projects', 'bedroom_projects', 'dining_projects',
            'living_projects', 'bathroom_projects', 'kidsroom_projects',
        ]

    def location(self, item):
        return reverse(item)

# =============================
# Blog Sitemap (Dynamic)
# =============================
class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Blog.objects.all()

    def location(self, obj):
        return reverse('blog_detail', args=[obj.slug])

# =============================
# Project Sitemap (Dynamic)
# =============================
class ProjectSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Project.objects.all()

    def location(self, obj):
        return reverse('project_detail', args=[obj.slug])

# =============================
# Product Sitemap (Dynamic)
# =============================
class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return reverse('product', args=[obj.slug])

# =============================
# Combine All Sitemaps
# =============================
sitemaps = {
    'static': StaticViewSitemap,
    'blogs': BlogSitemap,
    'projects': ProjectSitemap,
    'products': ProductSitemap,
}

# =============================
# URL Patterns
# =============================
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('elite_interior.urls')),  # 👈 app urls
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# =============================
# Robots.txt (Optional for SEO)
# =============================
urlpatterns += [re_path(r'^robots\.txt$', lambda r: static('robots.txt'))]

# =============================
# Static & Media Handling
# =============================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media),
    ]


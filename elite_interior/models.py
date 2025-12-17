from django.db import models
import datetime
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os


# Create your models here.
class HomeSlider(models.Model):
    headline = models.CharField(max_length=255, null=True)
    sub_headline = models.CharField(max_length=255, null=True)
    quotes = models.TextField(blank=True, null=True)  # Optional quotes field
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='home_slider/')
    description = models.TextField(blank=True, null=True)  # Optional description
    location = models.CharField(max_length=255, null=True, blank=True)  # ✅ New field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
# ✅ Auto delete image file when model instance is deleted
@receiver(post_delete, sender=HomeSlider)
def delete_image_on_instance_delete(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

# models.py

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product Category"

class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name 

    class Meta:
        verbose_name = "Product sub category"


class Project(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='project_images/')
    slug = models.SlugField(default="", null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = f"{self.category.name}-{self.name}" if self.category else self.name
            slug_candidate = slugify(base_slug)
            unique_slug = slug_candidate
            counter = 1
            while Project.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{slug_candidate}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name}{' - ' + self.subcategory.name if self.subcategory else ''})"
    
    class Meta:
        verbose_name = "Product"

# ✅ Auto delete image file when Project is deleted
@receiver(post_delete, sender=Project)
def delete_project_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        instance.image.delete(save=False)

class ProjectGallery(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='project_gallery/')
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


from django.dispatch import receiver
import os
import re


class PackageOffers(models.Model):
    title = models.CharField(max_length=225)
    subtitle = models.CharField(max_length=225,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discription = models.CharField(max_length=225)
    image = models.ImageField(upload_to='offer_images/')

    # ✅ YouTube link field
    youtube_link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Paste full YouTube URL"
    )

   # ✅ ADD THIS METHOD INSIDE THE MODEL
    def youtube_embed_url(self):
        if not self.youtube_link:
            return ""

        url = self.youtube_link.strip()

        # If already embed URL
        if "/embed/" in url:
            return url.split("?")[0]

        video_id = ""
        start_time = ""

        # watch?v=VIDEO_ID&t=1s
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
            match = re.search(r"[?&]t=(\d+)s?", url)
            if match:
                start_time = match.group(1)

        # youtu.be/VIDEO_ID?t=10
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            match = re.search(r"[?&]t=(\d+)", url)
            if match:
                start_time = match.group(1)

        if not video_id:
            return ""

        embed_url = f"https://www.youtube.com/embed/{video_id}"
        if start_time:
            embed_url += f"?start={start_time}"

        return embed_url



    def __str__(self):
        return self.title





# ✅ Auto delete image file when PackageOffers is deleted
@receiver(post_delete, sender=PackageOffers)
def delete_package_offers_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        instance.image.delete(save=False)

class WhatWeDo_Grid(models.Model):
    title = models.CharField(max_length=225)
    image = models.ImageField(upload_to='what_we_do_images/')
    size = models.CharField(max_length=10, choices=(('large', 'Large'), ('small', 'Small'), ('tall', 'tall')))

    def __str__(self):
        return self.title
    
    def get_slug(self):
        return slugify(self.title)
    
    class Meta:
        verbose_name = "OUR SERVICE GRID"

# ✅ Auto delete image file when WhatWeDo_Grid is deleted
@receiver(post_delete, sender=WhatWeDo_Grid)
def delete_what_we_do_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        instance.image.delete(save=False)

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='review_img/' , blank=True, null=True)
    comment = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"{self.name} - {self.rating}/5"

# ✅ Auto delete image file when Testimonial is deleted
@receiver(post_delete, sender=Testimonial)
def delete_testimonial_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        instance.image.delete(save=False)
# youtube videos

class YouTubeVideo(models.Model):
    title = models.CharField(max_length=200)
    youtube_link = models.CharField(
        max_length=100,
        help_text="Paste the YouTube video ID only (e.g. FT9g4LLrR5c)"
    )
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True, help_text="Show this video on the site")
    display_order = models.PositiveIntegerField(default=0, help_text="Higher numbers appear first")

    class Meta:
        ordering = ['-display_order', '-uploaded_at']
        verbose_name = "YouTube Video"
        verbose_name_plural = "YouTube Videos"

    def __str__(self):
        return self.title

    def embed_url(self):
        """Returns the embed URL for the video"""
        return f"https://www.youtube.com/embed/{self.youtube_link}"

    def watch_url(self):
        """Returns the regular watch URL"""
        return f"https://www.youtube.com/watch?v={self.youtube_link}"

    def thumbnail_url(self):
        """Returns URL for the video thumbnail"""
        return f"https://img.youtube.com/vi/{self.youtube_link}/hqdefault.jpg"

    def thumbnail_preview(self):
        """Admin thumbnail preview"""
        return mark_safe(f'<img src="{self.thumbnail_url()}" width="150" />')
    
    thumbnail_preview.short_description = 'Thumbnail'

    def embed_code(self):
        """Full embed code for templates"""
        return mark_safe(
            f'<iframe width="560" height="315" src="{self.embed_url()}" '
            'frameborder="0" allow="accelerometer; autoplay; clipboard-write; '
            'encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        )


class BlogCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='category_blogs'
    )

    def __str__(self):
        return self.category.name if self.category else "Unnamed Category"


class Blog(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='blog_images/')
    project_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True)
    keyword = models.CharField(max_length=255)
    is_featured = models.BooleanField(default=False) 
    description = models.TextField()
    slug = models.SlugField(unique=True, default="", null=True, blank=True)  # remove unique=True for now
    created_at = models.DateTimeField(default=timezone.now)
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            category_name = getattr(self.category, 'name', None)  # works even if category is None
            base_slug = f"{category_name}-{self.title}" if category_name else self.title
            slug_candidate = slugify(base_slug)
            unique_slug = slug_candidate
            counter = 1
            while Blog.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{slug_candidate}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

        

    def __str__(self):
        return self.title

# ✅ Auto delete image file when Blog is deleted
@receiver(post_delete, sender=Blog)
def delete_blog_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        instance.image.delete(save=False)

import re
from django.db import models

YOUTUBE_ID_RE = re.compile(r"(?:v=|youtu\.be/|embed/)?([A-Za-z0-9_-]{11})")


class AboutVideo(models.Model):
    title = models.CharField(max_length=225)
    youtube_link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Paste YouTube URL or video ID"
    )

    def __str__(self):
        return self.title

    # ✅ Normalize input → store only video ID
    def clean(self):
        if not self.youtube_link:
            return

        url = self.youtube_link.strip()
        match = YOUTUBE_ID_RE.search(url)

        if not match:
            raise ValueError("Invalid YouTube URL or Video ID")

        # store only the 11-char ID
        self.youtube_link = match.group(1)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    # ✅ Same API as PackageOffers / YouTubeVideo
    def youtube_embed_url(self):
        if not self.youtube_link:
            return ""
        return f"https://www.youtube.com/embed/{self.youtube_link}"


class BudgetItem(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ₹{self.unit_price}"


class YouTubeVideoProjects(models.Model):
    title = models.CharField(max_length=200)
    
    youtube_link = models.CharField(
        max_length=100,
        help_text="Paste the YouTube video ID only (e.g. FT9g4LLrR5c)"
    )

    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def get_embed_url(self):
        return f"https://www.youtube.com/embed/{self.youtube_link}"
    


class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Material Category"

class Brand(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Material Brand"

class Unit(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Material Unit"


           
class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/',blank=True, null=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    thickness = models.CharField(max_length=10, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    series = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "material"

# ✅ Auto delete image file when Product is deleted
@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        instance.image.delete(save=False)


class Accessory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="accessories")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="accessories/")

    def __str__(self):
        return self.name
    
# ✅ Auto delete image file when Accessory is deleted
@receiver(post_delete, sender=Accessory)
def delete_accessory_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        instance.image.delete(save=False)


from django.db import models
from django.utils import timezone
from datetime import timedelta

class OtpVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="team_photos/")  # requires MEDIA setup

    def __str__(self):
        return self.name

# ✅ Auto delete image file when TeamMember is deleted
@receiver(post_delete, sender=TeamMember)
def delete_team_member_photo(sender, instance, **kwargs):
    if instance.photo and os.path.isfile(instance.photo.path):
        instance.photo.delete(save=False)


# models.py
from django.db import models

class Ad(models.Model):
    
    title = models.CharField(max_length=200 , null=True)
    description = models.TextField(blank=True, null=True)
    offer_price = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='ads/')
    is_active = models.BooleanField(default=True)  # show only active ad
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ✅ Auto delete image file when Ad is deleted
@receiver(post_delete, sender=Ad)
def delete_ad_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        instance.image.delete(save=False)




class SEOServicePage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    long_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SEOServiceImage(models.Model):
    page = models.ForeignKey(SEOServicePage, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="seo_pages/")
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.page.title} - Image"
    
# ✅ Auto delete image file when Ad is deleted
@receiver(post_delete, sender=SEOServiceImage)
def delete_ad_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        instance.image.delete(save=False)
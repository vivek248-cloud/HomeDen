from django.db import models
import datetime
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.text import slugify

# Create your models here.
class HomeSlider(models.Model):
    healine = models.CharField(max_length=255)
    sub_headline = models.CharField(max_length=255)
    quotes = models.TextField(blank=True, null=True)  # Optional quotes field
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='home_slider/')
    description = models.TextField(blank=True, null=True)  # Optional description
    location = models.CharField(max_length=255, null=True, blank=True)  # ✅ New field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
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


class ProjectGallery(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='project_gallery/')
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PackageOffers(models.Model):
    title = models.CharField(max_length=225)
    subtitle = models.CharField(max_length=225,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discription = models.CharField(max_length=225)
    image = models.ImageField(upload_to='offer_images/')

    def __str__(self):
        return self.title
    
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

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='review_img/' , blank=True, null=True)
    comment = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"{self.name} - {self.rating}/5"

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

class AboutVideo(models.Model):
    title = models.CharField(max_length=225)
    youtube_id = models.CharField(
        max_length=100,
        help_text="Paste only the YouTube video ID (e.g. FT9g4LLrR5c)"
    )

    def __str__(self):
        return self.title


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

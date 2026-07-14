from django.db import models
import datetime
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os


# Create your models here.
from PIL import Image

from io import BytesIO

from django.core.files.base import ContentFile

import os


from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete

from PIL import Image

from io import BytesIO

from django.core.files.base import ContentFile

import os


class HomeSlider(models.Model):

    headline = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    sub_headline = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    quotes = models.TextField(
        blank=True,
        null=True
    )

    title = models.CharField(
        max_length=255
    )

    image = models.ImageField(
        upload_to="home_slider/"
    )

    mobile_image = models.ImageField(
        upload_to="slider_mobile/",
        blank=True,
        null=True,
        help_text="Upload mobile version (Recommended: 1080 × 1920)"
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    # =====================================================
    # Convert Image to WEBP
    # =====================================================

    def convert_to_webp(self, field_name, max_width):

        image_field = getattr(self, field_name)

        if not image_field:
            return

        if image_field.name.endswith(".webp"):
            return

        try:

            old_path = image_field.path

            img = Image.open(old_path)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            if img.width > max_width:

                ratio = max_width / img.width

                new_height = int(img.height * ratio)

                img = img.resize(
                    (max_width, new_height),
                    Image.LANCZOS
                )

            webp_io = BytesIO()

            img.save(
                webp_io,
                format="WEBP",
                quality=70,
                optimize=True
            )

            filename = os.path.splitext(
                os.path.basename(image_field.name)
            )[0]

            webp_name = f"{filename}.webp"

            image_field.save(
                webp_name,
                ContentFile(webp_io.getvalue()),
                save=False
            )

            super().save(
                update_fields=[field_name]
            )

            if os.path.exists(old_path):

                if not old_path.endswith(".webp"):

                    os.remove(old_path)

        except Exception as e:

            print(f"{field_name} WEBP Error :", e)

    # =====================================================
    # SAVE
    # =====================================================

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        # Desktop Banner
        self.convert_to_webp(
            "image",
            max_width=1920
        )

        # Mobile Banner
        self.convert_to_webp(
            "mobile_image",
            max_width=1080
        )


# =====================================================
# DELETE IMAGES WHEN RECORD IS DELETED
# =====================================================

@receiver(post_delete, sender=HomeSlider)
def delete_slider_images(sender, instance, **kwargs):

    if instance.image:

        if os.path.isfile(instance.image.path):

            os.remove(instance.image.path)

    if instance.mobile_image:

        if os.path.isfile(instance.mobile_image.path):

            os.remove(instance.mobile_image.path)





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

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='project_images/'
    )

    slug = models.SlugField(
        default="",
        null=True,
        blank=True,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # =====================================
    # SAVE
    # =====================================

    def save(self, *args, **kwargs):

        # =====================================
        # AUTO SLUG
        # =====================================

        if not self.slug:

            base_slug = (
                f"{self.category.name}-{self.name}"
                if self.category
                else self.name
            )

            slug_candidate = slugify(base_slug)

            unique_slug = slug_candidate

            counter = 1

            while Project.objects.filter(
                slug=unique_slug
            ).exclude(pk=self.pk).exists():

                unique_slug = (
                    f"{slug_candidate}-{counter}"
                )

                counter += 1

            self.slug = unique_slug

        # =====================================
        # SAVE ORIGINAL IMAGE FIRST
        # =====================================

        super().save(*args, **kwargs)

        # =====================================
        # SKIP IF NO IMAGE
        # =====================================

        if not self.image:
            return

        # =====================================
        # SKIP IF ALREADY WEBP
        # =====================================

        if self.image.name.endswith(".webp"):
            return

        try:

            # =====================================
            # STORE OLD FILE PATH
            # =====================================

            old_image_path = self.image.path

            # =====================================
            # OPEN IMAGE
            # =====================================

            img = Image.open(old_image_path)

            # Convert transparent images properly
            if img.mode in ("RGBA", "P"):

                img = img.convert("RGB")

            # =====================================
            # RESIZE LARGE IMAGES
            # =====================================

            max_width = 1920

            if img.width > max_width:

                ratio = max_width / img.width

                new_height = int(img.height * ratio)

                img = img.resize(
                    (max_width, new_height),
                    Image.LANCZOS
                )

            # =====================================
            # CONVERT TO WEBP
            # =====================================

            webp_io = BytesIO()

            img.save(
                webp_io,
                format="WEBP",
                quality=65,
                optimize=True
            )

            # =====================================
            # CREATE WEBP NAME
            # =====================================

            filename = os.path.splitext(
                os.path.basename(self.image.name)
            )[0]

            webp_filename = f"{filename}.webp"

            # =====================================
            # SAVE WEBP FILE
            # =====================================

            self.image.save(
                webp_filename,
                ContentFile(webp_io.getvalue()),
                save=False
            )

            # Save updated webp image
            super().save(update_fields=["image"])

            # =====================================
            # DELETE ORIGINAL JPG/PNG
            # =====================================

            if os.path.exists(old_image_path):

                if not old_image_path.endswith(".webp"):

                    os.remove(old_image_path)

        except Exception as e:

            print("WEBP Conversion Error:", e)

    def __str__(self):

        return (
            f"{self.name} "
            f"({self.category.name}"
            f"{' - ' + self.subcategory.name if self.subcategory else ''})"
        )

    class Meta:

        verbose_name = "Product"


# =====================================
# AUTO DELETE IMAGE WHEN PROJECT DELETED
# =====================================

@receiver(post_delete, sender=Project)
def delete_project_image(sender, instance, **kwargs):

    if instance.image:

        if os.path.isfile(instance.image.path):

            os.remove(instance.image.path)



class ProjectGallery(models.Model):

    title = models.CharField(
        max_length=200
    )

    image = models.ImageField(
        upload_to='project_gallery/'
    )

    caption = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # =====================================
    # SAVE
    # =====================================

    def save(self, *args, **kwargs):

        # Save original image first
        super().save(*args, **kwargs)

        # Skip if no image
        if not self.image:
            return

        # Skip if already webp
        if self.image.name.endswith(".webp"):
            return

        try:

            # =====================================
            # STORE OLD FILE PATH
            # =====================================

            old_image_path = self.image.path

            # =====================================
            # OPEN IMAGE
            # =====================================

            img = Image.open(old_image_path)

            # Convert transparent images properly
            if img.mode in ("RGBA", "P"):

                img = img.convert("RGB")

            # =====================================
            # RESIZE LARGE IMAGES
            # =====================================

            max_width = 1920

            if img.width > max_width:

                ratio = max_width / img.width

                new_height = int(img.height * ratio)

                img = img.resize(
                    (max_width, new_height),
                    Image.LANCZOS
                )

            # =====================================
            # CONVERT TO WEBP
            # =====================================

            webp_io = BytesIO()

            img.save(
                webp_io,
                format="WEBP",
                quality=75,
                optimize=True
            )

            # =====================================
            # CREATE WEBP NAME
            # =====================================

            filename = os.path.splitext(
                os.path.basename(self.image.name)
            )[0]

            webp_filename = f"{filename}.webp"

            # =====================================
            # SAVE WEBP FILE
            # =====================================

            self.image.save(
                webp_filename,
                ContentFile(webp_io.getvalue()),
                save=False
            )

            # Save updated webp image
            super().save(update_fields=["image"])

            # =====================================
            # DELETE ORIGINAL JPG/PNG
            # =====================================

            if os.path.exists(old_image_path):

                if not old_image_path.endswith(".webp"):

                    os.remove(old_image_path)

        except Exception as e:

            print("WEBP Conversion Error:", e)

    def __str__(self):

        return self.title


# =====================================
# AUTO DELETE IMAGE WHEN MODEL DELETED
# =====================================

@receiver(post_delete, sender=ProjectGallery)
def delete_gallery_image(sender, instance, **kwargs):

    if instance.image:

        if os.path.isfile(instance.image.path):

            os.remove(instance.image.path)






################################################ FINAL PCAKAGE #################


from django.db import models
from django.utils.text import slugify


class InteriorPackage(models.Model):

    PLAN_CHOICES = [
        ("comfort", "Comfort"),
        ("compact", "Compact"),
        ("signature", "Signature"),
        ("luxury", "Luxury"),
        ("royal", "Royal"),
    ]

    BHK_CHOICES = [
        ("1bhk", "1 BHK"),
        ("2bhk", "2 BHK"),
        ("3bhk", "3 BHK"),
        ("4bhk", "4 BHK"),
        ("villa", "Villa"),
        ("commercial", "Commercial"),
    ]

    name = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        unique=True,
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    subtitle = models.CharField(
        max_length=200,
        blank=True,
    )

    suitable_for = models.CharField(
        max_length=20,
        choices=BHK_CHOICES,
    )

    original_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )

    offer_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    warranty_years = models.PositiveIntegerField(
        default=20,
    )

    description = models.TextField(
        blank=True,
    )

    image = models.ImageField(
        upload_to="package_images/",
        blank=True,
        null=True,
    )

    brochure = models.FileField(
        upload_to="package_brochures/",
        blank=True,
        null=True,
    )

    youtube_link = models.URLField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["display_order"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_name_display()
    


class PackageSection(models.Model):

    package = models.ForeignKey(
        InteriorPackage,
        on_delete=models.CASCADE,
        related_name="sections",
    )

    title = models.CharField(
        max_length=100,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.package} - {self.title}"

class PackageItem(models.Model):

    section = models.ForeignKey(
        PackageSection,
        on_delete=models.CASCADE,
        related_name="items",
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.title





class WhatWeDo_Grid(models.Model):

    SIZE_CHOICES = (
        ('large', 'Large'),
        ('small', 'Small'),
        ('tall', 'Tall'),
    )

    title = models.CharField(
        max_length=225
    )

    image = models.ImageField(
        upload_to='what_we_do_images/'
    )

    size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES
    )

    # =====================================
    # SAVE
    # =====================================

    def save(self, *args, **kwargs):

        # Save original image first
        super().save(*args, **kwargs)

        # Skip if no image
        if not self.image:
            return

        # Skip if already webp
        if self.image.name.endswith(".webp"):
            return

        try:

            # =====================================
            # STORE OLD FILE PATH
            # =====================================

            old_image_path = self.image.path

            # =====================================
            # OPEN IMAGE
            # =====================================

            img = Image.open(old_image_path)

            # Convert transparent images properly
            if img.mode in ("RGBA", "P"):

                img = img.convert("RGB")

            # =====================================
            # RESIZE LARGE IMAGES
            # =====================================

            max_width = 1920

            if img.width > max_width:

                ratio = max_width / img.width

                new_height = int(img.height * ratio)

                img = img.resize(
                    (max_width, new_height),
                    Image.LANCZOS
                )

            # =====================================
            # CONVERT TO WEBP
            # =====================================

            webp_io = BytesIO()

            img.save(
                webp_io,
                format="WEBP",
                quality=75,
                optimize=True
            )

            # =====================================
            # CREATE WEBP NAME
            # =====================================

            filename = os.path.splitext(
                os.path.basename(self.image.name)
            )[0]

            webp_filename = f"{filename}.webp"

            # =====================================
            # SAVE WEBP FILE
            # =====================================

            self.image.save(
                webp_filename,
                ContentFile(webp_io.getvalue()),
                save=False
            )

            # Save updated webp image
            super().save(update_fields=["image"])

            # =====================================
            # DELETE ORIGINAL JPG/PNG
            # =====================================

            if os.path.exists(old_image_path):

                if not old_image_path.endswith(".webp"):

                    os.remove(old_image_path)

        except Exception as e:

            print("WEBP Conversion Error:", e)

    # =====================================
    # STRING
    # =====================================

    def __str__(self):

        return self.title

    # =====================================
    # SLUG
    # =====================================

    def get_slug(self):

        return slugify(self.title)

    # =====================================
    # ADMIN NAME
    # =====================================

    class Meta:

        verbose_name = "OUR SERVICE GRID"


# =====================================
# AUTO DELETE IMAGE WHEN MODEL DELETED
# =====================================

@receiver(post_delete, sender=WhatWeDo_Grid)
def delete_what_we_do_image(sender, instance, **kwargs):

    if instance.image:

        if os.path.isfile(instance.image.path):

            os.remove(instance.image.path)





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

    title = models.CharField(
        max_length=255
    )

    image = models.ImageField(
        upload_to='blog_images/'
    )

    project_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True
    )

    keyword = models.CharField(
        max_length=255
    )

    is_featured = models.BooleanField(
        default=False
    )

    description = models.TextField()

    slug = models.SlugField(
        unique=True,
        default="",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    date = models.DateField()

    views = models.PositiveIntegerField(
        default=0
    )

    # =====================================
    # SAVE
    # =====================================

    def save(self, *args, **kwargs):

        # =====================================
        # AUTO SLUG
        # =====================================

        if not self.slug:

            category_name = getattr(
                self.category,
                'name',
                None
            )

            base_slug = (
                f"{category_name}-{self.title}"
                if category_name
                else self.title
            )

            slug_candidate = slugify(base_slug)

            unique_slug = slug_candidate

            counter = 1

            while Blog.objects.filter(
                slug=unique_slug
            ).exclude(pk=self.pk).exists():

                unique_slug = (
                    f"{slug_candidate}-{counter}"
                )

                counter += 1

            self.slug = unique_slug

        # =====================================
        # SAVE ORIGINAL IMAGE FIRST
        # =====================================

        super().save(*args, **kwargs)

        # =====================================
        # SKIP IF NO IMAGE
        # =====================================

        if not self.image:
            return

        # =====================================
        # SKIP IF ALREADY WEBP
        # =====================================

        if self.image.name.endswith(".webp"):
            return

        try:

            # =====================================
            # STORE OLD FILE PATH
            # =====================================

            old_image_path = self.image.path

            # =====================================
            # OPEN IMAGE
            # =====================================

            img = Image.open(old_image_path)

            # Convert transparent images properly
            if img.mode in ("RGBA", "P"):

                img = img.convert("RGB")

            # =====================================
            # RESIZE LARGE IMAGES
            # =====================================

            max_width = 1920

            if img.width > max_width:

                ratio = max_width / img.width

                new_height = int(img.height * ratio)

                img = img.resize(
                    (max_width, new_height),
                    Image.LANCZOS
                )

            # =====================================
            # CONVERT TO WEBP
            # =====================================

            webp_io = BytesIO()

            img.save(
                webp_io,
                format="WEBP",
                quality=75,
                optimize=True
            )

            # =====================================
            # CREATE WEBP NAME
            # =====================================

            filename = os.path.splitext(
                os.path.basename(self.image.name)
            )[0]

            webp_filename = f"{filename}.webp"

            # =====================================
            # SAVE WEBP FILE
            # =====================================

            self.image.save(
                webp_filename,
                ContentFile(webp_io.getvalue()),
                save=False
            )

            # Save updated webp image
            super().save(update_fields=["image"])

            # =====================================
            # DELETE ORIGINAL JPG/PNG
            # =====================================

            if os.path.exists(old_image_path):

                if not old_image_path.endswith(".webp"):

                    os.remove(old_image_path)

        except Exception as e:

            print("WEBP Conversion Error:", e)

    # =====================================
    # STRING
    # =====================================

    def __str__(self):

        return self.title


# =====================================
# AUTO DELETE IMAGE WHEN BLOG DELETED
# =====================================

@receiver(post_delete, sender=Blog)
def delete_blog_image(sender, instance, **kwargs):

    if instance.image:

        if os.path.isfile(instance.image.path):

            os.remove(instance.image.path)


            

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





# models.py

class Lead(models.Model):

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("callback", "Callback"),
        ("quotation_sent", "Quotation Sent"),
        ("converted", "Converted"),
        ("closed", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    name = models.CharField(max_length=200)

    phone = models.CharField(max_length=20)

    alternate_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(blank=True, null=True)

    location = models.CharField(max_length=255)

    rooms = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="new"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium"
    )

    callback_date = models.DateTimeField(
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



# models.py

class MessageTemplate(models.Model):

    CATEGORY_CHOICES = [
        ("festival", "Festival Greetings"),
        ("offer", "Discount Offers"),
        ("launch", "New Launch"),
        ("followup", "Follow-up"),
        ("custom", "Custom"),
    ]

    name = models.CharField(max_length=200)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="custom"
    )

    subject = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="Email subject line"
    )

    message = models.TextField(
        help_text="Use {name}, {phone}, {location} as placeholders"
    )

    image = models.ImageField(
        upload_to="templates/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]


class CampaignLog(models.Model):

    PLATFORM_CHOICES = [
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("both", "Both"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    campaign_name = models.CharField(max_length=200)

    template = models.ForeignKey(
        MessageTemplate,
        on_delete=models.SET_NULL,
        null=True
    )

    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES
    )

    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    sent_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.campaign_name

    class Meta:
        ordering = ["-created_at"]


class CampaignRecipient(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    campaign = models.ForeignKey(
        CampaignLog,
        on_delete=models.CASCADE,
        related_name="recipients"
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    sent_at = models.DateTimeField(
        blank=True,
        null=True
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-sent_at"]


        

    # seo
    
class SEOServicePage(models.Model):

    title = models.CharField(max_length=255)

    slug = models.SlugField(unique=True)

    short_description = models.TextField()

    long_content = models.TextField()

    # SEO
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    meta_description = models.TextField(
        blank=True,
        null=True
    )

    meta_keywords = models.TextField(
        blank=True,
        null=True
    )

    canonical_url = models.URLField(
        blank=True,
        null=True
    )

    # OpenGraph
    og_title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    og_description = models.TextField(
        blank=True,
        null=True
    )

    og_image = models.ImageField(
        upload_to="seo_og/",
        blank=True,
        null=True
    )

    # Schema
    schema_type = models.CharField(
        max_length=100,
        default="Service"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

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





#quotation models.py




# quotation/models.py

from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=200)
    phone1 = models.CharField(max_length=20)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    location = models.CharField(max_length=200)

    GST = models.CharField(max_length=50, blank=True, null=True)

    discount_percent = models.FloatField(default=0)
    discount_amount = models.FloatField(default=0)

    discount_mode = models.CharField(
        max_length=10,
        choices=[("percent","Percent"),("amount","Amount")],
        default="percent"
    )

    notes = models.TextField(blank=True, null=True)

    estimate_start_date = models.DateField(blank=True, null=True)
    estimate_end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return self.name

class FullSemi(models.Model):
    name = models.CharField(max_length=100)
    rate = models.FloatField()

    def __str__(self):
        return self.name


class QuotationImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="quotation_images/")

    def __str__(self):
        return self.name


class Quotation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    floor = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    element = models.CharField(max_length=100)

    image = models.ForeignKey(QuotationImage, on_delete=models.SET_NULL, null=True, blank=True)
    full_semi = models.ForeignKey(FullSemi, on_delete=models.SET_NULL, null=True, blank=True)

    core_material = models.CharField(max_length=100)
    finish_material = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    specification = models.TextField()

    unit = models.CharField(max_length=50)

    length = models.FloatField()
    width = models.FloatField()

    area = models.FloatField(editable=False)
    price = models.FloatField()
    qty = models.IntegerField()

    total = models.FloatField(editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # auto area
        self.area = self.length * self.width

        # auto price from FullSemi if selected
        if self.full_semi:
            self.price = self.full_semi.rate

        # auto total
        self.total = self.area * self.price * self.qty

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client.name} - {self.element}"





class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default="Home Den")

    google_site_verification = models.CharField(
        max_length=255,
        blank=True,
        help_text="Google Search Console verification code"
    )

    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="GA4 Measurement ID (G-XXXXXXX)"
    )

    def __str__(self):
        return "Website Settings"



# models.py

class AiLocation(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class AiProduct(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class AiPlywood(models.Model):
    name = models.CharField(max_length=100)
    price_multiplier = models.FloatField(default=1.0)

    def __str__(self):
        return f"{self.name} (x{self.price_multiplier})"
    

class AiFinish(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

    
class AiPackage(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class AiInteriorPrice(models.Model):

    location = models.ForeignKey("AiLocation", on_delete=models.CASCADE)
    ai_product = models.ForeignKey("AiProduct", on_delete=models.CASCADE)

    finish = models.ForeignKey("AiFinish", on_delete=models.CASCADE)
    ai_package = models.ForeignKey("AiPackage", on_delete=models.CASCADE)

    plywood = models.ForeignKey("AiPlywood", on_delete=models.CASCADE)

    base_rate = models.FloatField()

    def __str__(self):
        return f"{self.location} | {self.ai_product} | {self.finish} | {self.ai_package} | {self.plywood}"
    



# admin.py

from django.contrib import admin
from django.utils.timezone import now
from datetime import timedelta


class CustomAdminSite(admin.AdminSite):
    site_header = "HomeDen Admin"
    site_title = "HomeDen Admin Portal"
    index_title = "Administration"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        # CRM Stats for admin index
        extra_context["total_leads"] = Lead.objects.count()
        extra_context["new_leads"] = Lead.objects.filter(
            status="new"
        ).count()
        extra_context["converted_leads"] = Lead.objects.filter(
            status="converted"
        ).count()
        extra_context["pending_callbacks"] = Lead.objects.filter(
            callback_date__lte=now() + timedelta(days=1)
        ).count()

        return super().index(request, extra_context)


# Replace default admin site
admin_site = CustomAdminSite(name="admin")
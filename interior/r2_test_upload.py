from django.core.files import File
from elite_interior.models import HomeSlider

with open("media/home_slider/test_upload.jpg", "rb") as f:
    obj = HomeSlider.objects.create(
        healine="Test Upload",
        sub_headline="Subtitle",
        title="Upload Test",
        image=File(f),
    )
    print("Uploaded to:", obj.image.url)



from elite_interior.models import HomeSlider
from django.core.files import File
import os

# Adjust this path to point to an actual file on your local system
file_path = os.path.join("media", "home_slider", "about-hall.jpeg")

if os.path.exists(file_path):
    with open(file_path, "rb") as f:
        obj = HomeSlider.objects.create(
            healine="Test Upload",
            sub_headline="Subtitle",
            title="Upload Test",
            image=File(f),
        )
        print("✅ Uploaded to:", obj.image.url)
else:
    print("❌ File not found:", file_path)

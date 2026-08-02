from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('business', 'Business'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    website_limit = models.PositiveIntegerField(default=3)  # Free: 3, Pro: 20, Business: 100
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_plan_display()})"

    def get_website_limit(self):
        limits = {
            'free': 3,
            'pro': 20,
            'business': 100,
        }
        return limits.get(self.plan, 3)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='websites')
    
    # Asosiy ma'lumotlar
    title = models.CharField(max_length=200, verbose_name="Sayt nomi")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=70, blank=True, help_text="Google uchun (70 belgidan oshmasin)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="Google uchun (160 belgidan oshmasin)")
    
    # Dizayn
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='favicons/', blank=True, null=True)
    background_color = models.CharField(max_length=20, default="#0f172a")
    text_color = models.CharField(max_length=20, default="#f8fafc")
    accent_color = models.CharField(max_length=20, default="#6366f1")
    
    # Kontent (bo‘limlar)
    hero_title = models.CharField(max_length=200, blank=True, verbose_name="Hero sarlavha")
    hero_subtitle = models.CharField(max_length=300, blank=True, verbose_name="Hero pastki matn")
    hero_button_text = models.CharField(max_length=50, blank=True, default="Bog‘lanish")
    hero_button_link = models.CharField(max_length=200, blank=True, default="#contact")
    
    about_title = models.CharField(max_length=150, blank=True, default="Men haqimda")
    about_content = models.TextField(blank=True)
    
    services_title = models.CharField(max_length=150, blank=True, default="Xizmatlar")
    services_content = models.TextField(blank=True, help_text="Har bir xizmatni yangi qatordan yozing")
    
    contact_title = models.CharField(max_length=150, blank=True, default="Bog‘lanish")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_address = models.CharField(max_length=255, blank=True)
    contact_telegram = models.CharField(max_length=100, blank=True)
    contact_instagram = models.CharField(max_length=100, blank=True)
    
    # Qo‘shimcha
    custom_css = models.TextField(blank=True, help_text="Qo‘shimcha CSS (ixtiyoriy)")
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Sayt"
        verbose_name_plural = "Saytlar"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "sayt"
            slug = base_slug
            counter = 1
            while Website.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # SEO default qiymatlar
        if not self.meta_title:
            self.meta_title = self.title[:70]
        if not self.meta_description and self.hero_subtitle:
            self.meta_description = self.hero_subtitle[:160]
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def get_absolute_url(self):
        return f"/s/{self.slug}/"

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])




class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('paid', 'To‘langan'),
        ('cancelled', 'Bekor qilingan'),
    ]

    PLAN_CHOICES = [
        ('pro', 'Pro — 5 so‘m'),
        ('business', 'Business — 10 so‘m'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.PositiveIntegerField()  # so‘m
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    note = models.TextField(blank=True, help_text="Admin izohi")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.get_plan_display()} ({self.status})"



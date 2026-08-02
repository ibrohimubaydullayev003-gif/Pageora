from django.contrib import admin
from django.utils import timezone
from .models import Website, Profile, Order


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'created_at')
    list_filter = ('plan',)
    search_fields = ('user__username', 'user__email')
    list_editable = ('plan',)  # Superuser to‘g‘ridan-to‘g‘ri o‘zgartira oladi


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'slug', 'is_published', 'views_count', 'updated_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'user__username', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'status', 'created_at', 'paid_at')
    list_filter = ('status', 'plan')
    search_fields = ('user__username',)
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    actions = ['mark_as_paid']

    @admin.action(description="Tanlangan buyurtmalarni To‘langan qilish va tarifni berish")
    def mark_as_paid(self, request, queryset):
        for order in queryset.filter(status='pending'):
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save()

            # Foydalanuvchi tarifini yangilash
            profile = order.user.profile
            profile.plan = order.plan
            profile.save()

        self.message_user(request, f"{queryset.count()} ta buyurtma to‘langan deb belgilandi va tarif berildi.")
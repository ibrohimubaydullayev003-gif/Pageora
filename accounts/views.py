from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Sum
from .forms import SignUpForm, LoginForm, WebsiteForm, ProfileForm
from .models import Website, Profile


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Xush kelibsiz! Hisobingiz muvaffaqiyatli yaratildi.")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}!")
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def dashboard(request):
    websites = Website.objects.filter(user=request.user)
    total_views = websites.aggregate(total=Sum('views_count'))['total'] or 0
    
    profile, created = Profile.objects.get_or_create(user=request.user)

    context = {
        'websites': websites,
        'total_views': total_views,
        'website_count': websites.count(),
        'website_limit': profile.get_website_limit(),
        'plan': profile.get_plan_display(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def create_website(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    current_count = Website.objects.filter(user=request.user).count()

    if current_count >= profile.get_website_limit():
        messages.warning(request, f"Sizning {profile.get_plan_display()} tarifingizda faqat {profile.get_website_limit()} ta sayt yaratish mumkin.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = WebsiteForm(request.POST, request.FILES)
        if form.is_valid():
            website = form.save(commit=False)
            website.user = request.user

            # Tarifga qarab cheklash
            if profile.plan == 'free':
                website.logo = None
                website.favicon = None
                website.hero_image = None
                website.about_image = None
                website.custom_css = ''
                website.custom_domain = ''
                website.remove_branding = False

            website.save()
            messages.success(request, "Sayt muvaffaqiyatli yaratildi!")
            return redirect('dashboard')
    else:
        form = WebsiteForm()

    return render(request, 'accounts/create_edit.html', {
        'form': form,
        'title': 'Yangi sayt yaratish',
        'button_text': 'Yaratish',
        'plan': profile.plan,
    })


@login_required
def edit_website(request, pk):
    website = get_object_or_404(Website, pk=pk, user=request.user)
    if request.method == 'POST':
        form = WebsiteForm(request.POST, request.FILES, instance=website)
        if form.is_valid():
            form.save()
            messages.success(request, "Sayt muvaffaqiyatli yangilandi!")
            return redirect('dashboard')
    else:
        form = WebsiteForm(instance=website)
    return render(request, 'accounts/create_edit.html', {
        'form': form,
        'title': 'Saytni tahrirlash',
        'button_text': 'Saqlash',
        'website': website
    })


@login_required
def delete_website(request, pk):
    website = get_object_or_404(Website, pk=pk, user=request.user)
    if request.method == 'POST':
        website.delete()
        messages.success(request, "Sayt o‘chirildi.")
    return redirect('dashboard')


def public_site(request, slug):
    website = get_object_or_404(Website, slug=slug, is_published=True)
    website.increment_views()
    return render(request, 'accounts/public_site.html', {'website': website})


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil yangilandi!")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parol muvaffaqiyatli o‘zgartirildi!")
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


def pricing(request):
    return render(request, 'accounts/pricing.html')




from django.utils import timezone
from .models import Website, Profile, Order


@login_required
def buy_plan(request, plan):
    """Tarif sotib olish (buyurtma yaratish)"""
    if plan not in ['pro', 'business']:
        messages.error(request, "Noto‘g‘ri tarif.")
        return redirect('pricing')

    prices = {
        'pro': 5,
        'business': 10,
    }
    amount = prices[plan]

    # Oldingi pending buyurtmani bekor qilish (ixtiyoriy)
    Order.objects.filter(user=request.user, status='pending').update(status='cancelled')

    order = Order.objects.create(
        user=request.user,
        plan=plan,
        amount=amount,
        status='pending'
    )

    messages.success(
        request,
        f"Buyurtma yaratildi! {amount} so‘m to‘lang va admin tasdiqlashini kuting. "
        f"Buyurtma raqami: #{order.id}"
    )
    return redirect('my_orders')


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'accounts/my_orders.html', {'orders': orders})







import stripe
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_checkout_session(request, plan):
    if plan not in ['pro', 'business']:
        messages.error(request, "Noto‘g‘ri tarif")
        return redirect('pricing')

    # Allaqachon shu tarif yoki undan yuqori bo‘lsa
    current_plan = request.user.profile.plan
    if current_plan == 'business' or (current_plan == 'pro' and plan == 'pro'):
        messages.info(request, "Sizda bu tarif allaqachon bor.")
        return redirect('dashboard')

    prices = getattr(settings, 'PLAN_PRICES', {'pro': 5, 'business': 10})
    amount = prices.get(plan, 5)

    try:
        order = Order.objects.create(
            user=request.user,
            plan=plan,
            amount=amount,
            status='pending'
        )

        # Test uchun USD (1$ = Pro, 2$ = Business)
        unit_amount = 100 if plan == 'pro' else 200

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Pageora {plan.upper()} tarif',
                        'description': f'Pageora {plan} rejasi',
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('payment_success')
            ) + f'?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}',
            cancel_url=request.build_absolute_uri(reverse('pricing')),
            client_reference_id=str(order.id),
            metadata={
                'order_id': str(order.id),
                'user_id': str(request.user.id),
                'plan': plan,
            }
        )

        order.stripe_session_id = session.id
        order.save()

        return redirect(session.url, code=303)

    except Exception as e:
        messages.error(request, f"To‘lovni boshlashda xato: {str(e)}")
        return redirect('pricing')


@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    order_id = request.GET.get('order_id')

    if not session_id or not order_id:
        messages.error(request, "Noto‘g‘ri so‘rov")
        return redirect('dashboard')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        order = Order.objects.get(id=order_id, user=request.user)

        if session.payment_status == 'paid' and order.status != 'paid':
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.stripe_payment_intent = session.payment_intent or ''
            order.save()

            profile = request.user.profile
            profile.plan = order.plan
            profile.save()

            messages.success(request, f"Tabriklaymiz! «{order.get_plan_display()}» tarifi muvaffaqiyatli faollashtirildi!")
        else:
            messages.warning(request, "To‘lov hali tasdiqlanmagan. Bir oz kutib, qayta tekshiring.")

    except Order.DoesNotExist:
        messages.error(request, "Buyurtma topilmadi")
    except Exception as e:
        messages.error(request, f"Xato: {str(e)}")

    return redirect('dashboard')
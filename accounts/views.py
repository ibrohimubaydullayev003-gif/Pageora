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
    profile = request.user.profile
    current_count = Website.objects.filter(user=request.user).count()

    if current_count >= profile.get_website_limit():
        messages.warning(request, f"Sizning {profile.get_plan_display()} tarifingizda faqat {profile.get_website_limit()} ta sayt yaratish mumkin. Pro tarifga o‘ting.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = WebsiteForm(request.POST, request.FILES)
        if form.is_valid():
            website = form.save(commit=False)
            website.user = request.user
            website.save()
            messages.success(request, "Sayt muvaffaqiyatli yaratildi!")
            return redirect('dashboard')
    else:
        form = WebsiteForm()
    return render(request, 'accounts/create_edit.html', {
        'form': form,
        'title': 'Yangi sayt yaratish',
        'button_text': 'Yaratish'
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
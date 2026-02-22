from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.models import User
from weasyprint import HTML
import tempfile
from .models import Post, Category, Comment, Report, UserProfile, SyriacWord
from .forms import (
    UserRegisterForm, UserLoginForm, PostForm, CommentForm, 
    ReportForm, UserProfileForm, SearchForm, SyriacWordForm
)
from .utils import generate_pdf_with_qr
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def form_handler(request, form_id):
    """Handle form submissions"""
    return HttpResponse(f"Form {form_id} received")

# Homepage View
def home(request):
    """Public homepage with feed of posts"""
    posts = Post.objects.filter(is_published=True)
    
    # Search and filter
    form = SearchForm(request.GET, categories=Category.objects.all())
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category_slug = form.cleaned_data.get('category')
        
        if query:
            posts = posts.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        if category_slug:
            posts = posts.filter(category__slug=category_slug)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get Syriac word of the week
    syriac_word = SyriacWord.objects.last()
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'syriac_word': syriac_word,
        'popular_posts': Post.objects.filter(is_published=True).order_by('-views_count')[:5],
    }
    return render(request, 'index.html', context)

# Authentication Views
def register_view(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Nasrani Heritage Community, {user.username}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    """User login"""
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
    else:
        form = UserLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

# Post Views
def post_detail(request, slug):
    """View single post with comments"""
    post = get_object_or_404(Post, slug=slug, is_published=True)
    
    # Increment view count (doesn't need request)
    post.views_count += 1
    post.save()
    
    # Get comments
    comments = post.comments.filter(parent=None, is_active=True)
    
    # Comment form
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Check if it's a reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)
            
            comment.save()
            messages.success(request, 'Your comment has been posted!')
            return redirect('post_detail', slug=post.slug)
    else:
        comment_form = CommentForm()
    
    # Check if user liked the post
    user_liked = False
    if request.user.is_authenticated:
        user_liked = post.likes.filter(id=request.user.id).exists()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_liked': user_liked,
        'related_posts': Post.objects.filter(category=post.category, is_published=True).exclude(id=post.id)[:3],
    }
    return render(request, 'post_detail.html', context)

def generate_qr_code(self, request=None):
    """Generate QR code for the post"""
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    
    # Get the full URL
    if request:
        url = request.build_absolute_uri(self.get_absolute_url())
    else:
        # Fallback to settings
        from django.conf import settings
        base_url = getattr(settings, 'SITE_URL')
        url = f"{base_url}{self.get_absolute_url()}"
    
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    
    filename = f'qr_post_{self.id}.png'
    self.qr_code.save(filename, File(buffer), save=False)

def contact_view(request):
    """Contact page with Instagram only"""
    # Get Syriac word for the sidebar
    syriac_word = SyriacWord.objects.last()
    
    context = {
        'syriac_word': syriac_word,
        'popular_posts': Post.objects.filter(is_published=True).order_by('-views_count')[:5],
    }
    return render(request, 'contact.html', context)

@login_required
def create_post(request):
    """Create new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # Don't save to DB yet
            post = form.save(commit=False)
            post.author = request.user
            
            # Clear the slug to let the model generate it
            post.slug = None
            
            # IMPORTANT: Pass the request to save method for QR code
            post.save(request=request)
            
            # Save many-to-many (tags)
            form.save_m2m()
            
            messages.success(request, 'Your post has been created successfully!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'create_post.html', {'form': form})

def post_list(request):
    """List all published posts"""
    posts = Post.objects.filter(is_published=True)
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'post_list.html', {'page_obj': page_obj})

@login_required
def edit_post(request, slug):
    """Edit existing post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check permission
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('post_detail', slug=post.slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            # IMPORTANT: Pass the request to save method for QR code
            post.save(request=request)
            form.save_m2m()
            messages.success(request, 'Your post has been updated!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'create_post.html', {'form': form, 'editing': True})

@login_required
def delete_post(request, slug):
    """Delete post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check permission
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('post_detail', slug=post.slug)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post has been deleted.')
        return redirect('home')
    
    return render(request, 'confirm_delete.html', {'post': post})

def download_pdf(request, slug):
    """Generate and download PDF of post"""
    post = get_object_or_404(Post, slug=slug, is_published=True)
    
    # Get the base URL (site URL without trailing slash)
    base_url = request.build_absolute_uri('/')[:-1]
    
    # Generate the full URL for QR code
    qr_code_full_url = None
    if post.qr_code:
        qr_code_full_url = request.build_absolute_uri(post.qr_code.url)
        print(f"QR Code URL: {qr_code_full_url}")  # For debugging in Render logs
    
    # Generate HTML with context
    context = {
        'post': post,
        'site_url': base_url,
        'qr_code_full_url': qr_code_full_url,  # Pass the full URL
    }
    
    html_string = render_to_string('pdf_template.html', context)
    
    # Create PDF using WeasyPrint
    from weasyprint import HTML
    import io
    
    try:
        # Generate PDF with base_url for resolving relative paths
        pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()
        
        # Create response
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{post.slug}.pdf"'
        response['Content-Length'] = len(pdf_bytes)
        
        return response
        
    except Exception as e:
        # Log the error and return a friendly message
        print(f"PDF generation error: {str(e)}")
        return HttpResponse(f"PDF generation failed: {str(e)}", status=500)
# Like/Unlike
@login_required
def like_post(request):
    """AJAX view for liking/unliking posts"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'total_likes': post.total_likes(),
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def syriac_words_view(request):
    """Display all Syriac words with filtering and learning features"""
    words = SyriacWord.objects.all()
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        words = words.filter(
            Q(word__icontains=query) | 
            Q(transliteration__icontains=query) | 
            Q(meaning__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(words, 20)  # Show 20 words per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get random word for highlight
    import random
    if words.exists():
        random_word = random.choice(words)
    else:
        random_word = None
    
    context = {
        'page_obj': page_obj,
        'random_word': random_word,
        'total_words': words.count(),
        'popular_posts': Post.objects.filter(is_published=True).order_by('-views_count')[:5],
    }
    return render(request, 'syriac_words.html', context)

# Comment Moderation
@login_required
def delete_comment(request, comment_id):
    """Delete comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check permission
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('post_detail', slug=comment.post.slug)
    
    comment.is_active = False
    comment.save()
    messages.success(request, 'Comment has been deleted.')
    
    return redirect('post_detail', slug=comment.post.slug)

# Reporting
@login_required
def report_content(request):
    """Report a post or comment"""
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            
            post_id = request.POST.get('post_id')
            comment_id = request.POST.get('comment_id')
            
            if post_id:
                report.post = get_object_or_404(Post, id=post_id)
            elif comment_id:
                report.comment = get_object_or_404(Comment, id=comment_id)
            else:
                messages.error(request, 'Invalid report target.')
                return redirect('home')
            
            report.save()
            messages.success(request, 'Thank you for your report. Our moderators will review it.')
            
            # Redirect back
            if report.post:
                return redirect('post_detail', slug=report.post.slug)
            else:
                return redirect('post_detail', slug=report.comment.post.slug)
    
    return redirect('home')

# Profile Views
@login_required
def profile_view(request, username):
    """View user profile"""
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user, is_published=True)[:10]
    
    context = {
        'profile_user': user,
        'posts': posts,
        'total_posts': user.posts.count(),
        'total_comments': Comment.objects.filter(author=user).count(),
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    """Edit own profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'edit_profile.html', {'form': form})

# Admin/Moderator Views
@staff_member_required
def admin_dashboard(request):
    """Admin dashboard for moderation"""
    # Get stats
    total_posts = Post.objects.count()
    total_users = User.objects.count()
    pending_reports = Report.objects.filter(is_resolved=False).count()
    
    # Get recent reports
    recent_reports = Report.objects.filter(is_resolved=False)[:20]
    
    # Get flagged content
    flagged_posts = Post.objects.annotate(
        report_count=Count('reports')
    ).filter(report_count__gt=0)[:10]
    
    context = {
        'total_posts': total_posts,
        'total_users': total_users,
        'pending_reports': pending_reports,
        'recent_reports': recent_reports,
        'flagged_posts': flagged_posts,
    }
    return render(request, 'admin_dashboard.html', context)

@staff_member_required
def resolve_report(request, report_id):
    """Mark report as resolved"""
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        report.is_resolved = True
        report.resolved_by = request.user
        report.save()
        messages.success(request, 'Report has been resolved.')
    
    return redirect('admin_dashboard')

# Static Pages
def about_view(request):
    """About page"""
    return render(request, 'about.html')

def guidelines_view(request):
    """Community guidelines page"""
    return render(request, 'guidelines.html')

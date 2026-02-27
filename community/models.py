from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify
from PIL import Image
import os

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#800000')  # Maroon default
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=400)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    content = RichTextField()
    excerpt = models.TextField(max_length=500, blank=True, help_text="Short preview of the post")
    
    # Media files
    featured_image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    pdf_files = models.FileField(upload_to='post_pdfs/', blank=True, null=True)
    audio_file = models.FileField(upload_to='post_audio/', blank=True, null=True)
    external_links = models.TextField(blank=True, help_text="One link per line")
    
    # Metadata
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    
    # Engagement
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    # QR Code
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def total_likes(self):
        return self.likes.count()
    
    def comment_count(self):
        return self.comments.count()
    
    def generate_qr_code(self, request=None):
        """Generate QR code for the post using request for full URL"""
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        
        # Get the full URL using request if available
        if request:
            url = request.build_absolute_uri(self.get_absolute_url())
        else:
            # Fallback for when request isn't available (like in shell)
            url = f"http://127.0.0.1:8000{self.get_absolute_url()}"
        
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        # Save to model
        filename = f'qr_post_{self.id}.png'
        self.qr_code.save(filename, File(buffer), save=False)

    def get_absolute_url(self):
        if not self.slug:
            # If slug is empty for some reason, use ID as fallback
            return reverse('post_detail', args=[self.id])
        return reverse('post_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        # Extract request from kwargs if present
        request = kwargs.pop('request', None)
        
        # Generate slug if not exists or empty
        if not self.slug or self.slug == '':
            # Create base slug from title
            base_slug = slugify(self.title)
            if not base_slug:  # If title gave empty slug (unlikely but possible)
                import time
                base_slug = f"post-{int(time.time())}"
            self.slug = base_slug
        
        # Ensure uniqueness - THIS IS THE KEY PART
        original_slug = self.slug
        counter = 1
        
        # For new posts (no ID yet)
        if not self.pk:
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        else:
            # For existing posts being updated
            while Post.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Generate excerpt if not provided
        if not self.excerpt and self.content:
            import re
            plain_text = re.sub(r'<[^>]+>', '', self.content)
            self.excerpt = plain_text[:200] + '...'
        
        # Save the post
        super().save(*args, **kwargs)
        
        # Generate QR code after saving (so we have ID)
        if not self.qr_code:
            self.generate_qr_code(request=request)
            # Use update_fields to avoid recursion
            super().save(update_fields=['qr_code'])

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    def get_replies(self):
        return Comment.objects.filter(parent=self, is_active=True)

class Report(models.Model):
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Report by {self.reporter.username} - {self.report_type}'

class SyriacWord(models.Model):
    word = models.CharField(max_length=100)
    transliteration = models.CharField(max_length=100)
    meaning = models.TextField()
    pronunciation_guide = models.CharField(max_length=200, blank=True)
    etymology = models.TextField(blank=True, help_text="Origin and history of the word")
    notes = models.TextField(blank=True, help_text="Additional information")
    biblical_reference = models.CharField(max_length=200, blank=True, help_text="Where this word appears in the Bible")
    audio_file = models.FileField(upload_to='syriac_audio/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.word

class Partner(models.Model):
    PARTNER_TYPES = [
        ('church', 'Church'),
        ('organization', 'Organization'),
        ('academic', 'Academic Institution'),
        ('media', 'Media Partner'),
        ('individual', 'Individual Supporter'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES, default='organization')
    logo = models.ImageField(upload_to='partner_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=200, blank=True)
    
    # Contact info (optional)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    
    # Social media
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    
    # Metadata
    featured = models.BooleanField(default=False, help_text="Show on homepage")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('partner_detail', args=[self.slug])

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',  # ← Fixed: no 'media/'
        default='profile_pics/default_profile.png'  # ← Fixed: include the folder
    )
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    
    # Social links
    website = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def total_posts(self):
        return self.user.posts.count()
    
    def total_comments(self):
        return Comment.objects.filter(author=self.user).count()

class SyriacWord(models.Model):
    word = models.CharField(max_length=100)
    transliteration = models.CharField(max_length=100)
    meaning = models.TextField()
    pronunciation_guide = models.CharField(max_length=200, blank=True)
    audio_file = models.FileField(upload_to='syriac_audio/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.word

# Signal to create user profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

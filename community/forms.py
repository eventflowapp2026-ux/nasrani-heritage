from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Post, Comment, Report, UserProfile, SyriacWord
from ckeditor.widgets import CKEditorWidget
from django.utils.text import slugify
import re

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'excerpt', 'featured_image', 
                 'pdf_files', 'audio_file', 'external_links', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 
                                             'placeholder': 'Brief summary of your post'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'pdf_files': forms.FileInput(attrs={'class': 'form-control'}),
            'audio_file': forms.FileInput(attrs={'class': 'form-control'}),
            'external_links': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                    'placeholder': 'https://example.com\nhttps://another-link.com'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 
                                          'placeholder': 'Enter tags separated by commas'}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise forms.ValidationError("Title must be at least 10 characters long.")
        return title
    
    def clean_external_links(self):
        links = self.cleaned_data.get('external_links')
        if links:
            # Simple URL validation
            url_pattern = re.compile(r'^https?://\S+$')
            for line in links.split('\n'):
                line = line.strip()
                if line and not url_pattern.match(line):
                    raise forms.ValidationError(f"Invalid URL: {line}")
        return links

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 
                                            'placeholder': 'Write your comment here...'}),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 3:
            raise forms.ValidationError("Comment must be at least 3 characters long.")
        return content

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'description']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                                'placeholder': 'Please provide details about the issue...'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'location', 'birth_date', 'website', 'twitter']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
        }

class SyriacWordForm(forms.ModelForm):
    class Meta:
        model = SyriacWord
        fields = ['word', 'transliteration', 'meaning', 'pronunciation_guide', 'audio_file']
        widgets = {
            'word': forms.TextInput(attrs={'class': 'form-control'}),
            'transliteration': forms.TextInput(attrs={'class': 'form-control'}),
            'meaning': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pronunciation_guide': forms.TextInput(attrs={'class': 'form-control'}),
            'audio_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search posts...'
    }))
    category = forms.ChoiceField(choices=[('', 'All Categories')], required=False, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', [])
        super().__init__(*args, **kwargs)
        if categories:
            self.fields['category'].choices = [('', 'All Categories')] + [(c.slug, c.name) for c in categories]

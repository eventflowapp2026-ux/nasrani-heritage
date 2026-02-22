from django.urls import path, include
from . import views

urlpatterns = [
    # Remove the admin line from here - it belongs in main urls.py
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    path('post/<slug:slug>/download-pdf/', views.download_pdf, name='download_pdf'),
    path('like-post/', views.like_post, name='like_post'),
    path('report/', views.report_content, name='report_content'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/resolve-report/<int:report_id>/', views.resolve_report, name='resolve_report'),
    path('about/', views.about_view, name='about'),
    path('guidelines/', views.guidelines_view, name='guidelines'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('form/<uuid:form_id>/', views.form_handler, name='form_handler'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('contact/', views.contact_view, name='contact'),
    path('syriac-words/', views.syriac_words_view, name='syriac_words'),
]

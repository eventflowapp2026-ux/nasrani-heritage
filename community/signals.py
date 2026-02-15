from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Post, Comment, Report

@receiver(post_save, sender=Post)
def notify_followers_on_new_post(sender, instance, created, **kwargs):
    """Notify admin about new posts"""
    if created:
        # Wait a moment for the post to be fully saved with slug
        # Use a safer approach - check if slug exists
        if not instance.slug:
            # If no slug yet, don't send email now
            # The post will be saved again with QR code later
            return
        
        # Send email to admins
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            try:
                # Safely get URL
                post_url = instance.get_absolute_url() if instance.slug else '#'
                send_mail(
                    f'New Post: {instance.title}',
                    f'A new post has been created by {instance.author.username}.\n\n'
                    f'Title: {instance.title}\n'
                    f'Category: {instance.category}\n'
                    f'URL: https://yourdomain.com{post_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [admin.email],
                    fail_silently=True,
                )
            except Exception as e:
                # Log the error but don't crash
                print(f"Error sending email for post {instance.id}: {e}")

@receiver(post_save, sender=Comment)
def notify_post_author_on_comment(sender, instance, created, **kwargs):
    """Notify post author when someone comments"""
    if created and instance.author != instance.post.author:
        send_mail(
            f'New Comment on: {instance.post.title}',
            f'{instance.author.username} commented on your post:\n\n'
            f'"{instance.content}"\n\n'
            f'View comment: https://yourdomain.com{instance.post.get_absolute_url()}',
            settings.DEFAULT_FROM_EMAIL,
            [instance.post.author.email],
            fail_silently=True,
        )

@receiver(post_save, sender=Report)
def notify_admins_on_report(sender, instance, created, **kwargs):
    """Notify admins about new reports"""
    if created:
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            content_type = 'post' if instance.post else 'comment'
            content_url = ''
            if instance.post:
                content_url = f'https://yourdomain.com{instance.post.get_absolute_url()}'
            elif instance.comment:
                content_url = f'https://yourdomain.com{instance.comment.post.get_absolute_url()}'
            
            send_mail(
                f'New Report: {instance.get_report_type_display()}',
                f'A new report has been submitted by {instance.reporter.username}.\n\n'
                f'Type: {instance.get_report_type_display()}\n'
                f'Content Type: {content_type}\n'
                f'Description: {instance.description}\n'
                f'URL: {content_url}',
                settings.DEFAULT_FROM_EMAIL,
                [admin.email],
                fail_silently=True,
            )

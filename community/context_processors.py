from .models import Category

def categories_processor(request):
    """Make categories available to all templates"""
    return {
        'categories': Category.objects.all()
    }

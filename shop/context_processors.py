from .models import Category

def category_dropdown(request):
    categories = Category.objects.all()

    context = {
        'all_categories' : categories,
    }
    return context
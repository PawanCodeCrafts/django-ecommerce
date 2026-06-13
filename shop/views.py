from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Product, Cart, CartItem, Address
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required



def product_list(request, category_slug=None): 
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True).order_by('-id')
    
    if category_slug:
        # finds category 
        category = get_object_or_404(Category, slug=category_slug)
        # filter products related to that category
        products = products.filter(category=category)

     # *** Search logic ***
    query = request.GET.get('search')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains = query)
        )

    # *** Price filters ***
    max_price = request.GET.get('max_price')
    min_price = request.GET.get('min_price')
    if max_price and max_price.isdigit():
        products = products.filter(price__lte=max_price)
    if min_price and min_price.isdigit():
        products = products.filter(price__gte=min_price)

    # *** Sorting ****
    sort = request.GET.get('sort')
    if sort == 'low_to_high':
        products = products.order_by('price')
    elif sort == 'high_to_low':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created')

    # *** Paginator ***
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)


    data = {
        'categories' : categories,
        'category':category,
        'products':products,
    }
  
    return render(request, 'shop/product_list.html', data)
   

def product_detail(request, pk, slug): 
     product = get_object_or_404(Product , pk=pk, slug=slug, available=True)

     data2 = {
       'product' : product,
     }

     return render(request, 'shop/product_detail.html', data2)

@login_required(login_url='accounts:login')
def add_to_cart(request, pk):
    product_in_cart = get_object_or_404(Product , pk=pk, available=True)
    cart, created = Cart.objects.get_or_create(user = request.user)

    cart_item , created = CartItem.objects.get_or_create(cart=cart, product=product_in_cart)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('shop:cart_display')

@login_required(login_url='accounts:login')
def cart_display(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all() 
    data = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/cart_display.html', data)

def remove_product(request, pk):
    item = get_object_or_404( CartItem, pk=pk, cart__user=request.user)
    item.delete()    
    return redirect('shop:cart_display')

def update_cart(request, pk, action):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    if action == 'increase':
        item.quantity+=1
    elif action == "decrease":
        if item.quantity > 1:
            item.quantity -= 1
        else:
            item.quantity == 1
            return redirect('shop:cart_display')

    item.save()
    return redirect('shop:cart_display')

def checkout(request):
    user_address =  Address.objects.filter(user=request.user)
    if user_address.exists():
        return render(request, 'shop/checkout_summary.html',{'addresses':user_address})
    else :
        return redirect('shop:add_address')

def add_address(request):
    return render(request, 'shop/add_address.html')
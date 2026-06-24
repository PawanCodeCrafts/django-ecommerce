from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Product, Cart, CartItem, Address, Order, OrderItem
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages



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
    product_in_cart = get_object_or_404(Product, pk=pk, available=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product_in_cart)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    if request.GET.get('action') == 'buy_now':
        return redirect('shop:checkout') 

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
        if item.quantity + 1 > item.product.stock:
            messages.error(
                request, 
                f"Oops! Only {item.product.stock} units of '{item.product.name}' are available in stock."
            )
            return redirect('shop:cart_display')
        else:
            item.quantity += 1
    elif action == "decrease":
        if item.quantity > 1:
            item.quantity -= 1
        else:
            item.quantity = 1  
            return redirect('shop:cart_display')

    item.save()
    return redirect('shop:cart_display')

@login_required
def checkout(request):
    user_addresses = Address.objects.filter(user=request.user)
    if not user_addresses.exists():
        return redirect('shop:add_address')

    if request.method == 'POST':
        chosen_address_id = request.POST.get('selected_address')
        request.session['selected_address_id'] = chosen_address_id

        return redirect('shop:order_summary') 

    return render(request, 'shop/checkout_summary.html', {'addresses': user_addresses})

def add_address(request):
    if request.method == 'POST':
        user = request.user
        full_name = request.POST.get('full_name')  
        phone_number = request.POST.get('phone_number')  
        country = request.POST.get('country')  
        state = request.POST.get('state')  
        city = request.POST.get('city')  
        street = request.POST.get('street')  
        pincode = request.POST.get('pincode')  
        is_default = request.POST.get('is_default')=='on'
        gender = request.POST.get('gender')

        if is_default:
            Address.objects.filter(user=user, is_default=True).update(is_default=False)

        Address.objects.create(
            user = user,
            full_name = full_name,
            phone_number = phone_number,
            country = country,
            state = state,
            city = city,
            street = street,
            pincode = pincode,
            is_default = is_default,
            gender = gender,
        )

        return redirect("shop:checkout")

    return render(request, 'shop/add_address.html')

def order_summary(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    address_id = request.session.get('selected_address_id')
    
    address = None
    if address_id:
        address = get_object_or_404(Address, id=address_id)
    
    context = {
        'cart' : cart,
        'address' : address,
    }

    return render(request, 'shop/order_summary.html', context)

@login_required(login_url='accounts:login')
def place_order(request):
    address_id = request.session.get('selected_address_id')
    selected_address = Address.objects.filter(id=address_id, user=request.user).first()
    
    active_cart = Cart.objects.filter(user=request.user).first()

    if active_cart and selected_address:
        cart_items = CartItem.objects.filter(cart=active_cart)
        new_order = Order.objects.create(
            user = request.user,
            address = selected_address, 
            total_price = active_cart.get_grand_price(),
            order_status = "Out for Delivery"
        )

        for item in cart_items:
            OrderItem.objects.create(
                order = new_order,
                product = item.product,
                price = item.product.price,
                quantity = item.quantity, 
            )
        
        item.product.stock -= item.quantity
        item.product.save()

        active_cart.delete()

        return redirect('shop:order_success') 
    return redirect('shop:cart_display')
    
def order_success(request):
    return render(request, 'shop/order_success.html')

@login_required(login_url="accounts:login")
def order_history(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {'user_orders': user_orders}
    return render(request, 'shop/order_history.html', context )

# handles rating and review
@login_required(login_url='accounts:login')
def product_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        ProductReview.objects.create(
            user = request.user,
            rating = rating,
            comment = comment,
            product = product,
        )

        return redirect('shop/product_detail.html', id=product_id, slug=product.slug)
    return redirect('store:product_detail', id=product_id, slug=product.slug)


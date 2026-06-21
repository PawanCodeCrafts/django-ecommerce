from django.db import models
from django.contrib.auth.models import User

# category of products
class Category(models.Model):
    name =  models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        # for plural names
        verbose_name_plural = 'categories'
    
    def  __str__(self):
        return self.name


# Products information
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete = models.CASCADE, related_name = 'products')

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    description = models.TextField(default='Not specified', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    image = models.ImageField(upload_to='products/%y/%m/%d',blank=True )
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# user's cart 
class Cart(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart of {self.user.username}'
    
    def get_cart_total_quantity(self):
        total = 0
        for item in self.items.all():
            total+=item.quantity
        return total

    def get_grand_price(self):
        total_price = 0
        for item in self.items.all():
            total_price += item.get_sub_total()
        return total_price
            
# cart items information
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_add_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.quantity} of {self.product.name}'
    
    def get_sub_total(self):
        return self.quantity * self.product.price

# user's checkout address
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15)
    country = models.CharField(max_length=100, default="India")
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255) 
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    GENDER_CHOICES = {
        'M':'Male',
        'F':'Female',
        'O':'Other',
    }
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"

# order details
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address =  models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(default='Pending' , max_length=20)
    payment_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

# Order Item details
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order ID: {self.order.id})"
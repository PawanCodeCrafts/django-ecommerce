from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Address, Order, OrderItem, ProductReview

# customized Category Model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    # create slug from name field automatically
    prepopulated_fields = {'slug':('name',)}

# customized Product Model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['name', 'slug', 'price', 'stock', 'available','created','updated']
    list_filter=['category','created']
    prepopulated_fields = {'slug':('name',)}

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ProductReview)



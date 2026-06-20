from . import views
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

app_name = 'shop'

urlpatterns = [
    path('', views.product_list , name='product_list'),
     path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_display, name='cart_display'),
    path('remove-product/<int:pk>/', views.remove_product, name='remove_product'),
    path('update-cart/<int:pk>/<str:action>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add_address/', views.add_address, name='add_address'),
    path('order_summary/', views.order_summary, name='order_summary'),
    
    path('<slug:category_slug>/' , views.product_list, name='product_list_by_category'),
    path('<int:pk>/<slug:slug>/' , views.product_detail, name='product_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# ---------------------------------------------------------------------
# IMPORTANT: URL Sequence Rule
# ---------------------------------------------------------------------
# '<slug:category_slug>/' jaise dynamic paths ko hamesha list mein sabse 
# aakhiri (bottom) mein rakhna chahiye.
# Django routes ko top-to-bottom check karta hai. Agar slug upar hoga, 
# toh wo 'checkout/' ya 'cart/' jaise static URLs ko bhi intercept kar lega.
# as a slug url treat krega
# ---------------------------------------------------------------------
from django.urls import path
from . import views

app_name = 'stalls'

urlpatterns = [
    path('', views.stall_list, name='stall_list'),
    path('<slug:slug>', views.stall_page, name='stall_page'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path("cart/delete/<option_id>/", views.delete_cart_item, name="delete_cart_item"),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('history/', views.transaction_history, name='transaction_history'),
    path('owner/select-stall/', views.select_stall, name='select_stall'),
    path('owner/orders/<int:stall_id>/', views.owner_stall_orders, name='owner_stall_orders'),
    path('owner/orders/mark-completed/<int:order_id>/', views.mark_order_completed, name='mark_order_completed'),
    path('owner/orders/mark-incomplete/<int:order_id>/', views.mark_order_incomplete, name='mark_order_incomplete'),
]
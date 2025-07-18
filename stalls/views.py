from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import FoodStall, MenuItem, MenuOption, Order, OrderItem
from .cart import Cart
from .forms import ReceiptUploadForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Create your views here.
@login_required
def stall_list(request):
    stall = FoodStall.objects.all()
    return render(request, 'stalls/stall_list.html', {'stall': stall})

@login_required
def stall_page(request, slug):
    stall = FoodStall.objects.get(slug=slug)
    categories = stall.categories.prefetch_related('items')
    return render(request, 'stalls/stall_page.html', {
        'stall': stall,
        'categories': categories
    })

@login_required
def add_to_cart(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        option_id = request.POST.get("option_id", None)
        quantity = int(request.POST.get("quantity", 1))

        item = get_object_or_404(MenuItem, id=item_id)
        stall_id = item.category.stall.id if item.category else item.stall.id

        cart = Cart(request)

        try:
            if option_id:
                option = get_object_or_404(MenuOption, id=option_id)
                cart.add(
                    stall_id=stall_id,
                    item_id=item.id,
                    option_id=str(option.id),
                    item_name=item.name,
                    option_name=option.name,
                    quantity=quantity,
                    price=option.price,
                    description=None
                )
                messages.success(request, f"{item.name} ({option.name}) added to cart.")
            else:
                price = float(request.POST.get("price"))
                option_name = request.POST.get("option_name", "Regular")
                cart.add(
                    stall_id=stall_id,
                    item_id=item.id,
                    option_id=f"{item.id}-default",
                    item_name=item.name,
                    option_name=option_name,
                    quantity=quantity,
                    price=price,
                    description=item.description
                )
                messages.success(request, f"{item.name} added to cart.")
        except ValueError:
            messages.error(request, "Your cart already contains items from a different stall. Please clear your cart first.")
            
        return redirect(request.META.get("HTTP_REFERER", "stalls:stall_list"))

    return redirect("stalls:stall_list")

@login_required
def view_cart(request):
    cart = Cart(request)
    items = cart.get_items()
    for item in items:
        item["subtotal"] = item["quantity"] * item["price"]
    return render(request, "stalls/cart.html", {
        "cart_items": items,
        "total": cart.get_total(),
    })

@login_required
def delete_cart_item(request, option_id):
    cart = Cart(request)
    cart.delete(option_id)
    messages.success(request, "Item removed from cart.")
    return redirect("stalls:view_cart")

@login_required
def clear_cart(request):
    request.session["cart"] = []
    request.session["cart_stall_id"] = None
    request.session.modified = True
    return redirect("stalls:view_cart")

@login_required
def checkout(request):
    cart = Cart(request)
    items = cart.get_items()
    if not items:
        return redirect('stalls:view_cart')

    stall_id = request.session.get("cart_stall_id")
    stall = FoodStall.objects.get(id=stall_id) if stall_id else None
    total = cart.get_total()

    min_eta = (timezone.localtime(timezone.now()) + timezone.timedelta(minutes=10)).strftime('%H:%M')

    if request.method == "POST":
        form = ReceiptUploadForm(request.POST, request.FILES)
        if form.is_valid():
            receipt = form.cleaned_data['receipt']
            eta = form.cleaned_data['eta']
            customer_name = form.cleaned_data.get('customer_name', "")
            if request.user.is_authenticated:
                customer_name = f"{request.user.first_name} {request.user.last_name}".strip()
            else:
                customer_name = form.cleaned_data.get('customer_name', "")

            order = Order.objects.create(
                stall=stall,
                eta=eta,
                total=total,
                receipt=receipt,
                customer_name=customer_name,
                user=request.user,
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    item_name=item['item_name'],
                    option_name=item.get('option_name', ""),
                    quantity=item['quantity'],
                    price=item['price'],
                    subtotal=item['quantity'] * item['price'],
                )

            messages.success(request, "Your order has been placed! Please pick up your order at your estimated time of arrival.")
            cart.clear()
            return redirect('stalls:stall_list')
    else:
        form = ReceiptUploadForm(initial={'eta': min_eta})
        form.fields['eta'].widget.attrs['min'] = min_eta

    return render(request, 'stalls/checkout.html', {
        "cart_items": items,
        "stall": stall,
        "total": total,
        "form": form,
        "min_eta": min_eta,
    })

@login_required
def transaction_history(request):
    orders = request.user.orders.select_related('stall').order_by('-placed_at')
    return render(request, 'stalls/transaction_history.html', {'orders': orders})

@login_required
def select_stall(request):
    owned_stalls = request.user.owned_stalls.all()
    if owned_stalls.count() == 1:
        return redirect('owner_stall_orders', stall_id=owned_stalls.first().id)
    return render(request, 'stalls/owners/select_stall.html', {'stalls': owned_stalls})

@login_required
def owner_stall_orders(request, stall_id):
    stall = get_object_or_404(FoodStall, id=stall_id, owner=request.user)
    orders = Order.objects.filter(stall=stall).order_by('-placed_at')
    return render(request, 'stalls/owners/order_list.html', {'stall': stall, 'orders': orders})

@login_required
def mark_order_completed(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        order.status = "Completed"
        order.save()
    return redirect('stalls:owner_stall_orders', stall_id=order.stall.id)

def mark_order_incomplete(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        order.status = "Pending"
        order.save()
    return redirect('stalls:owner_stall_orders', stall_id=order.stall.id)
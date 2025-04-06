from django.shortcuts import render, redirect
from core.forms import CheckoutForm, ProductForm
from django.contrib import messages
from core.models import *
from django.utils import timezone

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from django.db.models import Q
from payment.models import eSewaTransaction, Invoice
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request, "core/index.html", {"products": products})


def orderlist(request):
    invoices = Invoice.objects.filter(user_id=request.user.id)
    print("Invoices:", invoices)
    if Order.objects.filter(user=request.user, ordered=False).exists():
        order = Order.objects.get(user=request.user, ordered=False)
        return render(request, "core/orderlist.html", {"order": order, "invoices": invoices})
    return render(request, "core/orderlist.html", {"message": "Your Cart is Empty", "invoices": invoices})


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            print("True")
            form.save()
            print("Data Saved Successfully")
            messages.success(request, "Product Added Successfully")
            return redirect("/")
        else:
            print("Not Working")
            messages.info("Product is not Added, Try Again")
    else:
        form = ProductForm()
    return render(request, "core/add_product.html", {"form": form})

def product_desc(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:8]  # limit to 4 for neat UI
    return render(request, "core/product_desc.html", {
        "product": product,
        "related_products": related_products,
    })


def add_to_cart(request, pk):
    # Get that Partiuclar Product of id = pk
    product = Product.objects.get(pk=pk)

    # Create Order item
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
    )
    # print(order_item.)
    # Get Query set of Order Object of Particular User
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Added Quantity Item")
            print(order.items.all(), order.user, order.order_id)
            # print(order_item.order_id)

            return redirect("product_desc", pk=pk)
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to Cart")
            print(order.items.all(), order.user, order.order_id)
            return redirect("product_desc", pk=pk)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to Cart")
        return redirect("product_desc", pk=pk)


def add_item(request, pk):
    # Get that Partiuclar Product of id = pk
    product = Product.objects.get(pk=pk)

    # Create Order item
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
    )

    # Get Query set of Order Object of Particular User
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            if order_item.quantity < product.product_available_count:
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "Added Quantity Item")
                return redirect("orderlist")
            else:
                messages.info(request, "Sorry! Product is out of Stock")
                return redirect("orderlist")
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to Cart")
            return redirect("product_desc", pk=pk)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to Cart")
        return redirect("product_desc", pk=pk)


def remove_item(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False,
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item = OrderItem.objects.filter(
                product=item,
                user=request.user,
                ordered=False,
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "Item quantity was updated")
            return redirect("orderlist")
        else:
            messages.info(request, "This item is not in your cart")
            return redirect("orderlist")
    else:
        messages.info(request, "You Do not have any Order")
        return redirect("orderlist")


def checkout_page(request):
    if CheckoutAddress.objects.filter(user=request.user).exists():
        return render(request, "core/checkout_address.html", {"payment_allow": "allow"})
    if request.method == "POST":
        print("Saving must start")
        form = CheckoutForm(request.POST)
        if form.is_valid():
            street_address = form.cleaned_data.get("street_address")
            apartment_address = form.cleaned_data.get("apartment_address")
            country = form.cleaned_data.get("country")
            zip_code = form.cleaned_data.get("zip")

            checkout_address = CheckoutAddress(
                user=request.user,
                street_address=street_address,
                apartment_address=apartment_address,
                country=country,
                zip_code=zip_code,
            )
            checkout_address.save()
            print("It should render the summary page")
            return render(
                request, "core/checkout_address.html", {"payment_allow": "allow"}
            )

    else:
        form = CheckoutForm()
        return render(request, "core/checkout_address.html", {"form": form})



def manageProducts(request):
    return render(request, "core/manage_products.html")

def delete_product(request, pk=None):
    # Check if the request is a POST (form submission)
    if request.method == "POST":
        # Get the product object using the provided pk
        product = get_object_or_404(Product, pk=pk)

        # Delete the product
        product.delete()

        # Show success message
        messages.success(request, "Product deleted successfully")

        # Redirect to the manage products page after deletion
        return redirect('/update_products')  # This will refresh the page with the updated product list

    else:
        # If not a POST request, just show the product data
        # product = get_object_or_404(Product, pk=pk)
        products = Product.objects.all()

        # Render the manage products page with the list of products and the selected product's data
        return render(request, 'core/delete_products.html', {'products': products})


# View to list all products
def update_product_list(request):
    products = Product.objects.all()
    return render(request, 'core/update_product.html', {'products': products})

# View to edit a product
def update_product_form(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        desc = request.POST.get('desc')
        price = request.POST.get('price')
        product_available_count = request.POST.get('product_available_count')
        img = request.FILES.get('img')

        # Update fields only if new values are provided
        if name:
            product.name = name
        if category_id:
            product.category = Category.objects.get(id=category_id)
        if desc:
            product.desc = desc
        if price:
            product.price = float(price)
        if product_available_count:
            product.product_available_count = int(product_available_count)
        if img:
            product.img = img
        else:
            # Keep the current image if no new image is uploaded
            pass

        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('update_product_list')  # Redirect after saving

    return render(request, 'core/edit_product.html', {'product': product, 'categories': categories})


def all_products(request):
    categories = Category.objects.filter(product__isnull=False).distinct()  # Get categories with products
    products = Product.objects.filter(category__in=categories)  # Get products that belong to the selected categories

    return render(request, 'core/products_by_category.html', {'categories': categories, 'products': products})

def all_product(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    product_list = Product.objects.all()

    # Filter by search query if provided
    if search_query:
        product_list = product_list.filter(
            Q(name__icontains=search_query) |
            Q(desc__icontains=search_query)
        )

    # Filter by category if provided
    if category_id:
        product_list = product_list.filter(category_id=category_id)

    paginator = Paginator(product_list, 24)  # Adjust per-page count if needed
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'core/all_products.html', context)
def all_products_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    print(products)
    return render(request, 'core/products_category.html', {'products': products, 'category': category})



def esewa_success(request):
    transaction = eSewaTransaction.objects.get(transaction_id=request.GET.get("transaction_id"))
    user=request.user
    try:
        address = CheckoutAddress.objects.get(user=user)
    except CheckoutAddress.DoesNotExist:
        address = None

    if transaction.status == 'completed':
        try:
            order = Order.objects.get(order_id=request.GET.get("order_id"), ordered=False)
            # another_order = Order.objects.get(order_id=request.order_id)
            # print(another_order)
            order.ordered = True  # Mark order as paid
            order.save()
            invoice = Invoice.objects.create(
                user=user,
                order_id=order.order_id,
                order_date=order.start_date,
                payment_date=order.datetime_ofpayment,
                transaction_id=transaction.transaction_id,
                transaction_status=transaction.status,
                transaction_amount=transaction.amount,
                payment_type="Credit Card",
                card_ending="**** 1234",
                billing_address = address.street_address or '',
                total_amount=order.get_total_price(),
            )
            invoice.save()

            return render(request, "invoice/invoice.html", {"order": order, "transaction": transaction ,"address":address})
        except Order.DoesNotExist:
            return HttpResponse("Order not found, but payment was successful!")
    else:
        return HttpResponse("Payment verification failed! Please contact support.")

def esewa_failure(request):
    return render(request, "core/payment_failed.html")

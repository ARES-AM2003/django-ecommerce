from django.shortcuts import render, redirect
from core.forms import CheckoutForm, ProductForm
from django.contrib import messages
from core.models import *
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET))

# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request, "core/index.html", {"products": products})


def orderlist(request):
    if Order.objects.filter(user=request.user, ordered=False).exists():
        order = Order.objects.get(user=request.user, ordered=False)
        return render(request, "core/orderlist.html", {"order": order})
    return render(request, "core/orderlist.html", {"message": "Your Cart is Empty"})


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
    product = Product.objects.get(pk=pk)
    return render(request, "core/product_desc.html", {"product": product})


def add_to_cart(request, pk):
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
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Added Quantity Item")
            return redirect("product_desc", pk=pk)
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


def payment(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        try:
            address = CheckoutAddress.objects.get(user=request.user)
            print(address)
        except:
            return redirect("checkout_page")
        order_amount = order.get_total_price()
        order_currency = "NRS"
        order_receipt = order.order_id
        notes = {
            "street_address": address.street_address,
            "apartment_address": address.apartment_address,
            "country": address.country.name,
            "zip": address.zip_code,
        }

        # The total amount is passed to eSewa in paise (1 NRS = 100 paise)
        total_amount_in_paise = int(order_amount * 100)  # Convert amount to paise

        # Send order details to the template
        return render(
            request,
            "core/paymentsummary.html",  # Update this to your eSewa summary page
            {
                "order": order,
                "order_id": order_receipt,  # Use the order receipt (unique identifier)
                "orderId": order.order_id,
                "final_price": order_amount,
                "total_amount": total_amount_in_paise,  # Total amount in paise
                # "success_url": settings.ESEWA_SUCCESS_URL,  # The success URL
                # "failure_url": settings.ESEWA_FAILURE_URL,  # The failure URL
            },
        )

    except Order.DoesNotExist:
        print("Order not found")
        return HttpResponse("404 Error")

def render_pdf_view(request):
    order_db = Order.objects.get(razorpay_order_id=order_id)
    checkout_address = CheckoutAddress.objects.get(user=request.user)
    amount = order_db.get_total_price()
    amount = amount * 100
    payment_id = order_db.razorpay_payment_id
    payment_status = razorpay_client.payment.capture(payment_id, amount)
    template_path = 'invoice/invoice.html'
    context = {
        "order":order_db,"payment_status":payment_status,"checkout_address":checkout_address
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# def render_pdf_view(request):
#     order_id = request.session["order_id"]
#     order_db = Order.objects.get(razorpay_order_id=order_id)
#     checkout_address = CheckoutAddress.objects.get(user=request.user)
#     amount = order_db.get_total_price()
#     amount = amount * 100
#     payment_id = order_db.razorpay_payment_id
#     payment_status = request.session["payment_status"]
#     template_path = 'invoice/invoice.html'
#     context = {
#         "order":order_db,"payment_status":payment_status,"checkout_address":checkout_address
#     }

#     # Create a Django response object, and specify content_type as pdf
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="report.pdf"'
#     # find the template and render it.
#     template = get_template(template_path)
#     html = template.render(context)

#     # create a pdf
#     pisa_status = pisa.CreatePDF(
#        html, dest=response)
#     # if error then show some funy view
#     if pisa_status.err:
#        return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response

@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get("razorpay_payment_id", "")
            order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            print(payment_id, order_id, signature)
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }

            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
                print("Order Found")
            except:
                print("Order Not found")
                return HttpResponse("505 Not Found")
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()
            print("Working............")
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result == None:
                print("Working Final Fine............")
                amount = order_db.get_total_price()
                amount = amount * 100  # we have to pass in paisa
                payment_status = razorpay_client.payment.capture(payment_id, amount)
                if payment_status is not None:
                    print(payment_status)
                    order_db.ordered = True
                    order_db.save()
                    print("Payment Success")
                    checkout_address = CheckoutAddress.objects.get(user=request.user)
                    request.session[
                        "order_complete"
                    ] = "Your Order is Successfully Placed, You will receive your order within 5-7 working days"
                    return render(request, "invoice/invoice.html",{"order":order_db,"payment_status":payment_status,"checkout_address":checkout_address})
                else:
                    print("Payment Failed")
                    order_db.ordered = False
                    order_db.save()
                    request.session[
                        "order_failed"
                    ] = "Unfortunately your order could not be placed, try again!"
                    return redirect("/")
            else:
                order_db.ordered = False
                order_db.save()
                return render(request, "core/paymentfailed.html")
        except:
            return HttpResponse("Error Occured")


def invoice(request):
    return render(request, "invoice/invoice.html")

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

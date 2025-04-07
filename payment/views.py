from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from core.models import Order, CheckoutAddress
from .models import eSewaTransaction, Invoice
import uuid  # To generate a unique transaction ID
# from env.lib.python3.11.site-packages.django.http.response import HttpResponseRedirect
from django.http import HttpResponseRedirect



def payment(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        print(request)

        try:
            print(order.items.all(),order.order_id)
            address = CheckoutAddress.objects.get(user=request.user)
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

        # Generate a unique transaction ID for this payment
        transaction_id = str(uuid.uuid4())  # Generates a random unique identifier
        # Send order details to the template
        print(order)

        order_payload = {
                'order': order,
                'order_id': order_receipt,  # Use the order receipt (unique identifier)
                'orderId': order.order_id,
                'final_price': order_amount,
                'total_amount': int(order_amount * 100),  # Total amount in paise
                'success_url': 'http://django-ecommerce-138p.onrender.com/esewa/success/',
                'failure_url': 'http://django-ecommerce-138p.onrender.com/esewa/failure/',
                'transaction_id': transaction_id,  # Pass the transaction ID to the form
            }

        print(order_payload)
        return render(
            request,
            "core/paymentsummary.html",  # Update this to your eSewa summary page
            order_payload,
        )
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)



def esewa_payment_process(request):
    if request.method == "POST":
        transaction_id = request.POST.get("transaction_id")
        amount = request.POST.get("amt")
        order_id = request.POST.get("pid")
        success_url = request.POST.get("su")
        failure_url = request.POST.get("fu")
        print("Transaction ID:", transaction_id)
        print("Amount:", amount)
        print("Order ID:", order_id)
        print("Success URL:", success_url)
        print("Failure URL:", failure_url)

        try:
            order = Order.objects.get(order_id=order_id)
            user = request.user

            # Create a new eSewaTransaction with status 'pending'
            transaction = eSewaTransaction.objects.create(
                order=order,
                user=user,
                amount=amount,
                transaction_id=transaction_id,
                status='pending'
            )

            print("Transaction created:", transaction)

            # Here, you would integrate eSewa API to confirm payment status
            # For now, assume payment is successful and update the transaction status
            transaction.status = 'completed'
            transaction.save()

            # Redirect to the success page
            success_url_with_params = f"{success_url}?transaction_id={transaction_id}&order_id={order_id}"
            return HttpResponseRedirect(success_url_with_params)
        except eSewaTransaction.DoesNotExist:
            return redirect(failure_url)

def invoiceById(request, transaction_id):
    invoice = get_object_or_404(Invoice, transaction_id=transaction_id)
    transaction = eSewaTransaction.objects.get(transaction_id=transaction_id)
    order = Order.objects.get(order_id=invoice.order_id)
    user=request.user
    try:
        address = CheckoutAddress.objects.get(user=user)
    except CheckoutAddress.DoesNotExist:
        address = None
    return render(request, 'invoice/invoice.html', { 'transaction': transaction, 'order': order, 'address': address})

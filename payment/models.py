from django.db import models
from core.models import Order, User
import uuid

# Create your models here.
class eSewaTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    created_at = models.DateTimeField(auto_now_add=True)


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # Invoice basic details
    order_id = models.CharField(max_length=100, unique=True)
    order_date = models.DateField()
    payment_date = models.DateTimeField()

    # Payment information
    transaction_id = models.CharField(max_length=100)
    transaction_status = models.CharField(max_length=50)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment method
    payment_type = models.CharField(max_length=50)
    card_ending = models.CharField(max_length=10)
    billing_address = models.TextField()

    # Total amount
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)



    def __str__(self):
        return f"Invoice {self.order_id}"

from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser
import random
from django.utils.timezone import now
import uuid
from django.conf import settings
from django.contrib.auth.models import Group
from pytz import all_timezones


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Tenant Name - {self.name}"


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)    
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in all_timezones],  # List of all available time zones
        default='UTC'
    )

    def generate_otp(self):
        """Generate a 6-digit OTP."""
        self.otp = f"{random.randint(100000, 999999)}"
        self.otp_created_at = now()
        self.save()    


    @property
    def roles(self):
        return self.groups.all()

    def add_role(self, role_name):
        group, created = Group.objects.get_or_create(name=role_name)
        self.groups.add(group)

    def remove_role(self, role_name):
        group = Group.objects.filter(name=role_name).first()
        if group:
            self.groups.remove(group)




class BankAccount(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('GBP', 'British Pound'),
        ('EUR', 'Euro'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts")
    account_number = models.CharField(max_length=16, unique=True, editable=False, db_index=True) #db_index to improve query performance
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = str(uuid.uuid4().int)[:16]  # Generate a unique 16-digit number
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Account {self.account_number} - User {self.user.username}"        



class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
    ]

    account = models.ForeignKey('BankAccount', on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    related_account = models.ForeignKey('BankAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name="related_transactions")

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.amount} ({self.account.account_number})"

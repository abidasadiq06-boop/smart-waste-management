from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('hks_team', 'HKS Team'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone = models.CharField(max_length=10)
    ward_no = models.CharField(max_length=10)
    address = models.TextField()

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


# scap
class ScrapCategory(models.Model):
    name = models.CharField(max_length=100)
    rate_per_kg = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ₹{self.rate_per_kg}/kg"


# risks
class WasteRequest(models.Model):
    REQUEST_TYPE = [
        ('normal', 'Normal Waste'),
        ('custom', 'Custom/Scrap'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted by HKS'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scrap_category = models.ForeignKey(ScrapCategory, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    scrap_image = models.ImageField(upload_to='scrap_images/', null=True, blank=True)
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    scheduled_date = models.DateField(null=True, blank=True)
    normal_waste_items = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.citizen.username} - {self.request_type} - {self.status}"


# paymnt
class CollectionPayment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]
    PAYMENT_METHOD = [
        ('cash', 'Cash on Pickup'),
        ('online', 'Online/UPI'),
    ]

    waste_request = models.OneToOneField(WasteRequest, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    receipt_no = models.CharField(max_length=50, unique=True)
    collected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt #{self.receipt_no} - {self.payment_status}"
def __str__(self):
        return f"Receipt #{self.receipt_no} - {self.payment_status}"


class MonthlyWasteSchedule(models.Model):
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]

    month = models.IntegerField(
        choices=MONTH_CHOICES,
        unique=True
    )

    waste_items = models.TextField(
        help_text="Enter waste items separated by commas"
    )

    def __str__(self):
        return dict(self.MONTH_CHOICES)[self.month]        
    
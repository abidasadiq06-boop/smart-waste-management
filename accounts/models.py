from django.db import models

class Citizen(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name

class WasteRequest(models.Model):
    WASTE_TYPES = [
        ('NORMAL', 'Normal Waste'),
        ('SCRAP', 'Custom/Scrap Material')
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted by HKS'),
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed')
    ]

    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    waste_type = models.CharField(max_length=10, choices=WASTE_TYPES, default='NORMAL')
    
    # Custom/Scrap-
    scrap_category = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.FloatField(default=0.0, blank=True, null=True)
    calculated_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # HKS Team 
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    pickup_date = models.DateField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.citizen.name} - {self.waste_type} ({self.status})"
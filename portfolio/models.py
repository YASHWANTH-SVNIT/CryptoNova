from django.db import models
from django.contrib.auth.models import User
import pytz
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin_id = models.CharField(max_length=100)
    coin_name = models.CharField(max_length=100)
    coin_symbol = models.CharField(max_length=20)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.FloatField()
    price_inr = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def created_at_ist(self):
        ist=pytz.timezone('Asia/Kolkata')
        return self.created_at.astimezone(ist)

    def __str__(self):
        return f"{self.user.username} {self.transaction_type} {self.coin_symbol} {self.quantity}"

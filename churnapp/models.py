from django.db import models

class ChurnPrediction(models.Model):
    customer_id = models.CharField(max_length=30, unique=True)

    credit_score = models.IntegerField()
    country = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    tenure = models.IntegerField()
    balance = models.FloatField()
    num_products = models.IntegerField()
    has_card = models.IntegerField()
    is_active = models.IntegerField()
    salary = models.FloatField()

    prediction = models.IntegerField()  # 1 = Churn, 0 = Stay
    probability = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


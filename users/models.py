from django.db import models
 
class UserProfile(models.Model):
    # Stores all registered users
    # is_active=False by default — admin must activate before user can login
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)   # no two users can have same email
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.name} ({self.email})"
 
 
class PredictionHistory(models.Model):
    # Stores every price prediction made by each user
    # user FK links each prediction to the UserProfile who made it
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    year = models.IntegerField()
    km_driven = models.IntegerField()
    fuel = models.CharField(max_length=50)
    transmission = models.CharField(max_length=50)
    predicted_price = models.FloatField()
    lower_bound = models.FloatField(default=0)
    upper_bound = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.user.name} - Rs.{self.predicted_price:.0f}"
  AFTERNOON  

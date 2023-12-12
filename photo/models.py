from django.db import models

# Create your models here.
class Images(models.Model):
    heading = models.CharField(max_length=64)
    image = models.ImageField(upload_to="images")

    def __str__(self):
        return f"{self.heading}"
    
class Sale(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
from django.db import models

# Create your models here.
from django.db import models

class URL(models.Model):
    url = models.URLField(max_length=500)

    def __str__(self):
        return self.url

# from django.db import models

# class URLModel(models.Model):
#     url = models.URLField()

#     def __str__(self):
#         return self.url
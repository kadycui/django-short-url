from django.db import models

# Create your models here.
from django.db import models

# Create your models here.

# 短url表
class ShortUrl(models.Model):
    id = models.AutoField(primary_key=True);
    short_url = models.CharField(max_length=255)
    ori_url = models.TextField()
    period = models.DateField()

    def __str__(self):
        return self.short_url

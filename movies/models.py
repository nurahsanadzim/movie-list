from django.db import models

from django.contrib.auth.models import User

class UserMovieList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_list = models.CharField(max_length=10000)


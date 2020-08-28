from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = "index"),
    path('addShortUrl',views.addShortUrl, name = "addShortUrl"),
    path('restoreUrl',views.restoreUrl, name = "restoreUrl")

]
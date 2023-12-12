from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("buy/<str:buy>", views.photo_buy, name="photo_buy"),
    path("purchase", views.purchase, name="purchase"),
    path("webkooks/stripe/", views.my_webhook, name='stripe-webkook'),
]
"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from adsinteraction import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('generate_refresh_token', views.generate_refresh_token, name='generate_refresh_token'),
    # Client customer id is an id of an account in a google ads manager account ex: 249-145-0448
    path('campaigns/<str:client_customer_id>', views.campaigns, name='client_campaigns')
]

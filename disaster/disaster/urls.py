"""disaster URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from core.views import TripListView, TripCreateView, TripDetailView, TripUpdateView, TripDeleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TripListView.as_view(), name='trip-list'),
    path('create/', TripCreateView.as_view(), name='trip-create'),
    path('<int:id>/', TripDetailView.as_view(), name='trip-detail'),
    path('<int:id>/update/', TripUpdateView.as_view(), name='trip-update'),
    path('<int:id>/delete/', TripDeleteView.as_view(), name='trip-delete'),

]

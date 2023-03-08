"""lisbona URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from stations import views
from users import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="home"),
    path('stops/<int:id>/', views.station_detail, name="station_detail"),
    path('stops/<int:parent>/add/', views.station_edit, name="station_add_child"),
    path('stops/<int:id>/edit/', views.station_edit, name="station_edit"),
    path('stops/add/', views.station_edit, name="station_add"),
    path('stops/lifts/<int:id>/', views.lift_detail, name="lift_detail"),
    path('stops/<int:parent>/lift/add', views.lift_edit, name="lift_add"),
    path('stops/lifts/<int:id>/edit', views.lift_edit, name="lift_edit"),
    path('stops/<int:platform>/services/add', views.services_edit, name="services_add"),
    path('stops/services/<int:id>/edit', views.services_edit, name="services_edit"),
    path('accounts/', include('users.urls')),
    path('download/', views.download_csv, name='download'),
    path('map/', views.stations_map, name='stations_map'),

    path('lines/add/', views.line_edit, name='line_add'),
    path('lines/', views.lines_index, name='lines'),
    path('lines/<int:id>/edit/', views.line_edit, name='line_edit'),

    path('lifts/', views.lifts_list, name='lifts'),

    path('ramps/<int:parent>/add/', views.ramps_edit, name='ramp_add'),
    path('ramps/<int:id>/edit/', views.ramps_edit, name='ramp_edit')
]

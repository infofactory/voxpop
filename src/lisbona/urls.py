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
    path('', views.choose_city, name="home"),

    path('accounts/', include('users.urls')),
 #   path('<slug:city>/download/', views.download_csv, name='download'),

    path('<slug:city>/', views.stops_list, name="stops_list"),
    path('<slug:city>/stops/', views.stops_list, name="stops_prefix"),

    path('<slug:city>/stops/<int:id>/', views.station_detail, name="station_detail"),
    path('<slug:city>/stops/<int:parent>/add/', views.station_edit, name="station_add_child"),
    path('<slug:city>/stops/<int:id>/edit/', views.station_edit, name="station_edit"),
    path('<slug:city>/stops/add/', views.station_edit, name="station_add"),
    path('<slug:city>/stops/lifts/<int:id>/', views.lift_detail, name="lift_detail"),
    path('<slug:city>/stops/<int:parent>/lift/add', views.lift_edit, name="lift_add"),
    path('<slug:city>/stops/lifts/<int:id>/edit', views.lift_edit, name="lift_edit"),
    path('<slug:city>/stops/<int:platform>/services/add', views.services_edit, name="services_add"),
    path('<slug:city>/stops/services/<int:id>/edit', views.services_edit, name="services_edit"),

    path('<slug:city>/map/', views.stations_map, name='stations_map'),

    path('<slug:city>/lines/add/', views.line_edit, name='line_add'),
    path('<slug:city>/lines/', views.lines_index, name='lines'),
    path('<slug:city>/lines/<int:id>/edit/', views.line_edit, name='line_edit'),

    path('<slug:city>/lifts/', views.lifts_list, name='lifts'),

    path('<slug:city>/ramps/<int:parent>/add/', views.ramps_edit, name='ramp_add'),
    path('<slug:city>/ramps/<int:id>/edit/', views.ramps_edit, name='ramp_edit'),

    path('<slug:city_slug>/gtfs/', views.download_gtfs, name='download_gtfs'),
    path('<slug:city_slug>/gtfs/<str:filename>/', views.download_gtfs, name='download_gtfs_file'),

    path('<slug:city_slug>/download/', views.download_custom, name='download_custom'),
    path('<slug:city_slug>/download/<str:filename>/', views.download_custom, name='download_custom_file'),

    path('<slug:city_slug>/realtime/', views.download_realtime, name='download_realtime'),


    path('lifts/<int:id>/thumbnail/', views.lift_thumbnail, name='lift_thumbnail'),
]

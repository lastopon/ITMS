from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'vendors', views.VendorViewSet)
router.register(r'assets', views.AssetViewSet)
router.register(r'maintenance-records', views.MaintenanceRecordViewSet)
router.register(r'software-licenses', views.SoftwareLicenseViewSet)
router.register(r'software-installations', views.SoftwareInstallationViewSet)
router.register(r'helpdesk-tickets', views.HelpDeskTicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
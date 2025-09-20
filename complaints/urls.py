from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rooms', views.RoomViewSet)
router.register(r'complaints', views.ComplaintViewSet)
router.register(r'report',views.ReportViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'issue-category', views.IssueCatViewset)
router.register(r'TATView', views.TATViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
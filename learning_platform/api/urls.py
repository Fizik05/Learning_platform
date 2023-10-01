from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()

router.register("product", ProductViewSet, "Product")
router.register("lesson", LessonViewSet, "lesson")

urlpatterns = [
    path("", include(router.urls)),
]

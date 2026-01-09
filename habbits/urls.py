from django.urls import path, include

from .apps import HabbitsConfig
from .views import PublicHabbitListAPIView, HabbitViewSet, PublicHabbitDetailAPIView

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"", HabbitViewSet, basename="habbit")

app_name = HabbitsConfig.name

urlpatterns = [
    path('public/', PublicHabbitListAPIView.as_view(), name='public-habbits-list'),
    path('public/<int:pk>/', PublicHabbitDetailAPIView.as_view(), name='public-habbit-detail'),
    path('', include(router.urls)),
]

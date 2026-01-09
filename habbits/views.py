from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Habbit
from .paginators import StandardResultsSetPagination
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from .serializers import HabbitSerializer
from users.permissions import IsOwner
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
# from django.shortcuts import get_object_or_404
# from rest_framework.response import Response
# from rest_framework import status


@method_decorator(cache_page(60 * 5), name="dispatch")
class PublicHabbitListAPIView(ListAPIView):
    queryset = Habbit.objects.filter(is_public=True).order_by("id")
    serializer_class = HabbitSerializer
    permission_classes = [AllowAny]


@method_decorator(cache_page(60 * 5), name="dispatch")
class PublicHabbitDetailAPIView(RetrieveAPIView):
    queryset = Habbit.objects.filter(is_public=True)
    serializer_class = HabbitSerializer
    permission_classes = [AllowAny]


@method_decorator(cache_page(60 * 5), name="dispatch")
class HabbitViewSet(ModelViewSet):
    queryset = Habbit.objects.all().order_by('id')
    pagination_class = StandardResultsSetPagination
    serializer_class = HabbitSerializer

    def get_queryset(self):
        return Habbit.objects.filter(user=self.request.user).order_by('id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            self.permission_denied(self.request, message="Habit not found")
        return obj

    def get_permissions(self):
        return [IsAuthenticated(), IsOwner()]

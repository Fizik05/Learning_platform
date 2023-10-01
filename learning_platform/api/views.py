from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product, Lesson, User, View
from .serializers import (
    LessonProductSerializer,
    ProductSerializer,
    ProductCreateSerializer,
    LessonSerializer,
    LessonCreateSerializer,
    StatisticksSerializer
)


class LessonViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для уроков.
    """
    serializer_class = LessonSerializer

    def get_queryset(self):
        if self.action in ["create", "partial_update"] or len(Lesson.objects.all()) == 0:
            return Lesson.objects.all()
        
        # Ниже представлен алгоритм поиска доступных lessons
        # Сначала я вытаскиваю все доступные для пользователя продукты
        # Потом достаю id всех lessons для каждого из объекта
        # Далее сортирую и вытаскиваю уже список доступных lessons
        # Решение конечно не из самых лучших, но именно на стажировке я планирую научится новому и полезному:)
        products = Product.objects.filter(access__id=self.request.user.id)
        lessons_list = [i.lessons.values("id") for i in products]
        lessons = []

        for query in lessons_list:
            for id in query:
                if id not in lessons:
                    lessons.append(id)
        indexes = [element["id"] for element in lessons]
        return Lesson.objects.filter(id__in=indexes)
    
    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return LessonCreateSerializer
        return LessonSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для продукта.
    """
    def retrieve(self, request, pk):
        """
        Функция возвращает подробную информацию об одном из продуктов.
        """
        current_product = get_object_or_404(
            Product,
            id=pk
        )
        serializer = LessonProductSerializer(
            current_product,
            context={
                "request": request
            }
        )
        return Response(serializer.data)

    @action(
        methods=["get",],
        detail=False,
        url_path="statisticks"
    )
    def get_statisticks(self, request):
        """
        Функция отвечает за получение статистики о продуктах.
        """
        products = Product.objects.all()
        serializer = StatisticksSerializer(products, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            print("This is anonymous user")
            return Product.objects.all()
        if self.action in ["create", "partial_update"] or len(Product.objects.all()) == 0:
            return Product.objects.all()
        return Product.objects.filter(access__id=self.request.user.id)

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return ProductCreateSerializer
        return ProductSerializer
    
    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

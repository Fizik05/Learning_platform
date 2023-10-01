import datetime
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Product, Lesson, User, Access, LessonProduct, View


class StatisticksSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения статистики о продуктах.
    """
    count_viewing = serializers.SerializerMethodField()
    all_time_viewings = serializers.SerializerMethodField()
    count_students = serializers.SerializerMethodField()
    buy_coefficient_product = serializers.SerializerMethodField()
    
    def get_count_viewing(self, obj):
        """
        Эта функция позволяет получить количество просмотренных уроков
        от всех учеников для каждого продукта.
        """
        views = 0
        lessons = obj.lessons.values("id")
        for lesson_ind in lessons:
            lesson = Lesson.objects.get(id=lesson_ind["id"])
            access_users = [user["id"] for user in obj.access.values("id")]
            for user_id in access_users:
                view = get_object_or_404(
                    View,
                    user__id=user_id,
                    lesson__id=lesson.id
                )
                if view.status:
                    views += 1
        return views
    
    def get_all_time_viewings(self, obj):
        """
        Получает время, которое ученики продукта потратили
        на просмотр его видеоуроков.
        """
        time = 0
        lessons = obj.lessons.values("id")
        for lesson_ind in lessons:
            lesson = Lesson.objects.get(id=lesson_ind["id"])
            access_users = [user["id"] for user in obj.access.values("id")]
            for user_id in access_users:
                view = get_object_or_404(
                    View,
                    user__id=user_id,
                    lesson__id=lesson.id
                )
                time += view.viewing_time.total_seconds()
        return time
    
    def get_count_students(self, obj):
        """
        Получает количество учеников, занимающихся на платформе.
        """
        return len(obj.access.values("id"))

    def get_buy_coefficient_product(self, obj):
        """
        Функция высчитывает процент приобретения продукта.
        """
        users = User.objects.all()
        count_students = self.get_count_students(obj)
        return count_students / len(users)

    class Meta:
        model = Product
        fields = (
            "title",
            "count_viewing",
            "all_time_viewings",
            "count_students",
            "buy_coefficient_product",
        )


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения всех уроков, к которым пользователь имеет доступ.
    Поля выводил, руководствуясь ТЗ. Как по мне, можно было и побольше информации вывести в данном пункте.
    Поэтому следующий сериализатор выводит более подробную информацию об уроках, но нигде не задействован.
    
    """
    status = serializers.SerializerMethodField()
    viewing_time = serializers.SerializerMethodField()
    last_viewing_time = serializers.SerializerMethodField()

    def get_status(self, obj):
        """
        Получение статуса.
        """
        print(self.context)
        user = self.context.get("request").user.id
        lesson = obj.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        if view.status:
            return "Просмотрено"
        return "Не просмотрено"
    
    def get_viewing_time(self, obj):
        """
        Функция получает время просмотра.
        """
        user = self.context.get("request").user.id
        lesson = obj.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        return view.viewing_time
    
    def get_last_viewing_time(self, obj):
        """
        Получение времени последнего просмотра.
        """
        user = self.context.get("request").user.id
        lesson = obj.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        return view.last_viewing_time

    class Meta:
        model = Lesson
        fields = (
            "title",
            "status",
            "viewing_time",
            "last_viewing_time"
        )


class LessonProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения подробной информации о продукте.
    """
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "title",
            "lessons"
        )


class DopLessonSerializer(serializers.ModelSerializer):
    """
    Дополнительный сериализатор об уроках, который выводит более подробную информацию.
    Нигде не задействован.
    """
    status = serializers.SerializerMethodField(read_only=True)
    duration = serializers.SerializerMethodField()
    viewing_time = serializers.SerializerMethodField()
    last_viewing_time = serializers.SerializerMethodField()

    def get_viewing_time(self, obj):
        user = self.context.get("request").user.id
        lesson = obj.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        return view.viewing_time

    def get_last_viewing_time(self, obj):
        user = self.context.get("request").user.id
        lesson = obj.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        return view.last_viewing_time

    def get_duration(self, obj):
        return obj.duration.total_seconds()

    def get_status(self, obj):
        user = self.context.get("request").user.id
        lesson = obj.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        return view.status

    
    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "video_link",
            "duration",
            "viewing_time",
            "last_viewing_time",
            "status"
        )

    
class LessonCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления видеоуроков.
    """
    viewing_time = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    last_viewing_time = serializers.SerializerMethodField()

    def get_last_viewing_time(self, obj):
        lesson = obj.id
        user = self.context.get("request").user.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        return view.last_viewing_time

    def get_viewing_time(self, obj):
        lesson = obj.id
        user = self.context.get("request").user.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        return view.viewing_time
    
    def get_status(self, obj):
        lesson = obj.id
        user = self.context.get("request").user.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        return view.status

    def create(self, validated_data):
        lesson = Lesson.objects.create(**validated_data)
        
        user = User.objects.get(id=self.context.get("request").user.id)
        View.objects.create(
            user=user,
            lesson=lesson,
            status=False,
            viewing_time=datetime.timedelta(seconds=0),
            #ЗДЕСЬ НУЖНО РАЗОБРАТЬСЯ С ТИПОМ DATETIME
            last_viewing_time=datetime.datetime.now().strftime("%d.%m.%y %H:%M")
        )
        return lesson
    
    def update(self, instance, validated_data):
        validated_data.pop("title")
        instance.video_link = validated_data["video_link"]
        instance.duration = validated_data["duration"]

        user = self.context.get("request").user.id
        lesson = instance.id
        view = get_object_or_404(
            View,
            user__id=user,
            lesson__id=lesson
        )
        view.viewing_time = datetime.timedelta(seconds=self.initial_data["viewing_time"])
        view.last_viewing_time = datetime.datetime.now().strftime("%d.%m.%y %H:%M")
        duration_coef = view.viewing_time.total_seconds() / instance.duration.total_seconds()
        if duration_coef >= 0.8:
            view.status = True
        else:
            view.status = False
        view.save()

        instance.save()
        return instance

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "video_link",
            "duration",
            "viewing_time",
            "last_viewing_time",
            "status"
        )


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения списка всех доступных продуктов.
    """
    owner = serializers.StringRelatedField(read_only=True)
    access = serializers.StringRelatedField(
        read_only=True,
        many=True
    )
    lessons = serializers.StringRelatedField(
        read_only=True,
        many=True
    )
    link_to_product = serializers.SerializerMethodField()

    def get_link_to_product(self, obj):
        return self.context.get("request").path + str(obj.id) + "/"
    
    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "owner",
            "access",
            "lessons",
            "link_to_product"
        )


class AccessCreateSerializer(serializers.Serializer):
    username = serializers.CharField()


class LessonProductCreateSerializer(serializers.Serializer):
    title = serializers.CharField()


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания продукта.
    """
    access = AccessCreateSerializer(many=True)
    lessons = LessonProductCreateSerializer(many=True)

    def create(self, validated_data):
        """
        Создание продукта, а также связи юзера и доступных ему кроков
        """
        usernames = validated_data.pop("access")
        lessons_titles = validated_data.pop("lessons")
        product = Product.objects.create(**validated_data)
        usernames = [username["username"] for username in usernames]
        lessons_titles = [title["title"] for title in lessons_titles]

        for lesson_title in lessons_titles:
            current_lesson = get_object_or_404(
                Lesson,
                title=lesson_title
            )
            LessonProduct.objects.create(
                lesson = current_lesson,
                product = product
            )
            for username in usernames:
                current_user = get_object_or_404(
                    User,
                    username=username
                )
                Access.objects.get_or_create(
                    user = current_user,
                    product = product
                )
                if not View.objects.filter(
                    user=current_user,
                    lesson=current_lesson,
                ).exists():
                    View.objects.create(
                        user=current_user,
                        lesson=current_lesson,
                        status=False,
                        viewing_time=datetime.timedelta(seconds=0),
                        last_viewing_time=datetime.datetime.utcnow().strftime("%d.%m.%y %H:%M")
                    )
    
    class Meta:
        model = Product
        fields = (
            "title",
            "access",
            "lessons"
        )

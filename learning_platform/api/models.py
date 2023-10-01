from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Lesson(models.Model):
    title = models.CharField(max_length=100, unique=True)
    video_link = models.URLField()
    duration = models.DurationField()
    views = models.ManyToManyField(
        User,
        related_name="lessons",
        through="View"
    )

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    access = models.ManyToManyField(
        User,
        related_name="products",
        through="Access"
    )
    lessons = models.ManyToManyField(
        Lesson,
        through="LessonProduct"
    )

    def __str__(self):
        return self.title
    

class Access(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="acs"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="acs"
    )


class LessonProduct(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="lesson_product"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="lesson_product"
    )
    
    def __str__(self):
        return f"{self.product.title} and {self.lesson.title}"


class View(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="view"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="view"
    )
    status = models.BooleanField(default=False)
    viewing_time = models.DurationField()
    last_viewing_time = models.DateTimeField(auto_now=True)

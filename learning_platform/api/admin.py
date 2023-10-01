from django.contrib import admin
from .models import Product, Lesson, Access, LessonProduct, View


admin.site.register(Product)
admin.site.register(Lesson)
admin.site.register(Access)
admin.site.register(LessonProduct)
admin.site.register(View)

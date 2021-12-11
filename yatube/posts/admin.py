from django.contrib import admin

from yatube.settings import EMPTY_VALUE_DISPLAY

from .models import Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('pk', 'text', 'created', 'author', 'group')
    list_editable = ('group',)
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('created',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title')
    search_fields = ('title',)
    empty_value_display = EMPTY_VALUE_DISPLAY

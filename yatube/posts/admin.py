from django.contrib import admin

from .models import Comment, Group, Post


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'description',
    )
    search_fields = ('text', 'description',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created', 'group',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'post',
        'created',
        'author',
    )
    search_fields = ('text',)
    list_filter = ('created', 'post',)
    empty_value_display = '-пусто-'


admin.site.register(Comment, CommentAdmin)

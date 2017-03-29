from django.contrib import admin

# Register your models here.

from models import *


class ArticleAdmin(admin.ModelAdmin):
	list_display = ('title','category','date_publish','desc','click_count')
	list_display_links = ('category','title')
	list_editable = ('click_count',)


	class Media:
		js = (
			'/static/js/kindeditor-4.1.10/kindeditor-min.js',
			'/static/js/kindeditor-4.1.10/lang/zh_CN.js',
			'/static/js/kindeditor-4.1.10/config.js',
		)
	

admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Article,ArticleAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Links)
admin.site.register(Ad)


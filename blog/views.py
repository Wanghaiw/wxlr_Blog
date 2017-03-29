# -*- coding:utf-8 -*-
import logging
from django.shortcuts import render,redirect,HttpResponse
from django.core.urlresolvers import reverse
from models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout,login,authenticate
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.db import connection
from django.db.models import Count
from forms import *
import json

# Create your views here.

#logger = logging.getLogger('blog.views')



def global_settings(request):
	#分类信息获取(导航栏)
	category_list = Category.objects.all()
	#文章归档
	archive_list = Article.objects.distinct_date()  ##自定义的文章管理
	
	#评论排行
	comment_count_list = Comment.objects.values('article').annotate(comment_count = Count('article')).order_by('-comment_count')
	article_comment_list = [Article.objects.get(pk=comment['article']) for comment in comment_count_list]
	
	#浏览排行
	click_count_list = Article.objects.values('click_count').order_by('-click_count')
	
	article_click_list = [Article.objects.filter(click_count=click['click_count']) for click in click_count_list]
	#article_click_list2 = [Article.objects.get(click_count=click['click_count']) for click in click_count_list]
	
	article_content_list = []
	for article in article_click_list:
		article_content_list.append(article[0])
	
	#标签云

	tags_list = []
	tags = Tag.objects.all()
	
	for tag in tags:
		if tag not in tags_list:
			tags_list.append(tag)

	#友情链接
	links_list = Links.objects.all()

	#站长推荐
	wx_list = Article.objects.filter(is_recommend=1)
	wx_list = [wx_content for wx_content in wx_list]
	
	
	return locals()



	

def index(request):
	try:
		#最新文章的数据
		article_list = Article.objects.all()
		article_list = getPage(request,article_list)

	except Exception as e:
		logger.error(e)
	return render(request,'index1.html',locals())



def archive(request):
	try:
		#先获取客户端提交的信息
		year = request.GET.get('year',None)
		month = request.GET.get('month',None)
		article_list = Article.objects.filter(date_publish__icontains=year+'-'+month)
		
		article_list = getPage(request,article_list)
		
	except Exception as e:
		logger.error(e)

	return render(request,'archive.html',locals())


#分页代码
def getPage(request,article_list):
	paginator = Paginator(article_list,2)
	try:
		page = int(request.GET.get('page',1))
		article_list = paginator.page(page)
	except (EmptyPage,InvalidPage,PageNotAnInteger):
		article_list = paginator.page(1)
	return article_list


#标签查询
def search_tag(request,tag):
	try:
		article_list = Article.objects.filter(tag__name__contains=tag)
		article_list = getPage(request,article_list)
	except Article.DoesNotExist as e:
		logger.error(e)
		
	return render(request,'tag.html',locals())

#文章详情页
def article(request):
    try:
        # 获取文章id
        id = request.GET.get('id', None)
        try:
            # 获取文章信息
            article = Article.objects.get(pk=id)
            
            click_count = article.click_count+1
            
            #article = Article(id=id)
            article.click_count = click_count
            article.save()
        except Article.DoesNotExist:
            return render(request, 'failure.html', {'reason': '没有找到对应的文章'})

        # 评论表单
        comment_form = CommentForm({'author': request.user.username,
                                    'email': request.user.email,
                                    'article': id} if request.user.is_authenticated() else{'article': id})
        # 获取评论信息
        comments = Comment.objects.filter(article=article).order_by('id')
        
        comment_list = []
        for comment in comments:
            for item in comment_list:
                if not hasattr(item, 'children_comment'):
                    setattr(item, 'children_comment', [])
                if comment.pid == item:
                    item.children_comment.append(comment)

                    break
            if comment.pid is None:
                comment_list.append(comment)
    except Exception as e:
        print e,'--------------'
        logger.error(e)
    #评论数量

    comment_count = len(comments)
    return render(request, 'article.html', locals())
    

# 提交评论
def comment_post(request):
    try:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            #获取表单信息
            comment = Comment.objects.create(username=comment_form.cleaned_data["author"],
                                             email=comment_form.cleaned_data["email"],
                                             content=comment_form.cleaned_data["comment"],
                                             article_id=comment_form.cleaned_data["article"],
                                             user=request.user if request.user.is_authenticated() else None)
            comment.save()
        else:
            return render(request, 'failure.html', {'reason': comment_form.errors})
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

# 注销
def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        print e
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

# 注册
def do_reg(request):
    try:
        if request.method == 'POST':
            reg_form = RegForm(request.POST)
            print '-------------------'
            if reg_form.is_valid():
                # 注册
                user = User.objects.create(username=reg_form.cleaned_data["username"],
                                    email=reg_form.cleaned_data["email"],
                                    #url=reg_form.cleaned_data["url"],
                                    password=make_password(reg_form.cleaned_data["password"]),)
                user.save()

                # 登录
                print '------------------'
                user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                login(request, user)

                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form = RegForm()
    except Exception as e:
    	print e
        ##logger.error(e)
    return render(request, 'reg.html', locals())

# 登录
def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'login.html', locals())

def category(request):
    try:
        # 先获取客户端提交的信息
        cid = request.GET.get('cid', None)
        try:
            category = Category.objects.get(pk=cid)
        except Category.DoesNotExist:
            return render(request, 'failure.html', {'reason': '分类不存在'})
        article_list = Article.objects.filter(category=category)
        article_list = getPage(request, article_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'category.html', locals())


#关于我
def about_me(request):
    return render(request,'about_me.html')

#照片墙

def get_lr(request):
    return render(request,'lr.html')


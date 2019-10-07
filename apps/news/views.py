

import  logging

from django.conf import settings
from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import F
from django.http import HttpResponseNotFound
from . import constants
from utils import res_code
from utils.res_code import Code,error_map,json_response
from .models import Tag, News, HotNews,Banner,Comments
from haystack.generic_views import SearchView
logger = logging.getLogger('django')



# Create your views here.

def index(request):
    """
    新闻首页视图
    :param request:
    :return:
    """

    tags = Tag.objects.only('id', 'name').filter(is_delete=False)
    #hot_news返回的是一个字符串。然后切片
    #select_related是重点，查询的时候插询了与news的相关字段
    hot_news=HotNews.objects.select_related('news').only('news__title','news__image_url', 'news_id').\
        filter(is_delete=False).order_by('priority','-news__clicks')[:constants.SHOW_HOTNEWS_COUNT]
    return render(request, 'news/index.html',
                  context={
                      'tags': tags,
                      'hot_news':hot_news
                  })
class NewslistView(View):
    """
    新闻列表视图
    url: /news/
    args: tag, page
    """
#1获取参数
    def get(self,request):
        try:
            tag_id=int(request.GET.get('tag',0))
        except Exception as e:
            logger.error('标签错误：\n{}'.format(e))
            tag_id = 0
        #page的获取

        try:
            page = int(request.GET.get('page', 0))
        except Exception as e:
            logger.error('页码错误：\n{}'.format(e))
            page = 1

        #3.获取查询集
        # 使用only返回的是对象，所以传递到前端时需要迭代处理
        # news_queryset = News.objects.select_related('tag', 'author').only(
        #     'title', 'digest', 'image_url', 'update_time', 'tag__name', 'author__username')
        # values 返回字典
        news_queryset=News.objects.values('id','title','digest','image_url','update_time').annotate(tag_name=F('tag__name'),author=F('author__username'))
        #4过滤
        # if tag_id:
        #     news=news_queryset.filter(is_delete=False,tag_id=tag_id)
        # else:
        #     news=news_queryset.filter(is_delete=False)
        news=news_queryset.filter(is_delete=False,tag_id=tag_id) or news_queryset.filter(is_delete=False)
        #3分页
        pageinator=Paginator(news,constants.PER_PAGE_NEWS_COUNT)

            # 获取页面数据 get_page可以容错
        news_info=pageinator.get_page(page)
        #4返回数据
        data={
            'total_page':pageinator.num_pages,
            'news':list(news_info)
        }
        return res_code.json_response(data=data)

class NewsBannerView(View):
    def get(self,request):
        #返回字典用values
        banners=Banner.objects.values('image_url','news_id').annotate(news_title=F('news__title')).filter(is_delete=False)[:constants.SHOW_BANNER_COUNT]#切片取6个
        data={
            'banners':list(banners)
        }
        return res_code.json_response(data=data)

class NewsDetailView(View):
    def get(self,request,news_id):
        # 1检验是否存在
        # 2获取数据
        news=News.objects.select_related('tag','author').\
            only('title','content','update_time','tag__name','author__username').filter(is_delete=False,id=news_id).first()
        if news:

        # 快捷方式
        # 1. 去数据库获取新闻数据
        # news_queryset = News.objects.select_related('tag', 'author').only('title', 'content', 'update_time', 'tag__name', 'author__username').filter(is_delete=False, id=news_id)
        # news = get_object_or_404(news_queryset, is_delete=False, id=news_id)

        # 2. 返回渲染页面
        # return render(request, 'news/news_detail.html', context={'news': news})
        #加载评论
            comments=Comments.objects.select_related('author','parent').\
            only( 'content', 'author__username', 'update_time', 'parent__author__username', 'parent__content',
                'parent__update_time').filter(is_delete=False, news_id=news_id)
            return render(request, 'news/news_detail.html', context={
            'news': news,
            'comments': comments
        })
        else:
            return HttpResponseNotFound('<h1>Page not found</h1>')

class NewsCommentsViews(View):
    """
     添加评论视图
     url: /news/<int:news_id>/comment/
     """

    def post(self, request, news_id):
        # 是否登录
        if not request.user.is_authenticated:
            return json_response(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])
        # 新闻是否存在
        if not News.objects.only('id').filter(is_delete=False, id=news_id).exists():
            return json_response(errno=Code.PARAMERR, errmsg='新闻不存在！')

        content = request.POST.get('content')
        # 内容是否为空
        if not content:
            return json_response(errno=Code.PARAMERR, errmsg='评论内容不能为空！')

        # 父id是否正常
        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                parent_id = int(parent_id)
                if not Comments.objects.only('id').filter(is_delete=False, id=parent_id, news_id=news_id).exists():
                    return json_response(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            except Exception as e:
                logger.info('前端传递过来的parent_id异常\n{}'.format(e))
                return json_response(errno=Code.PARAMERR, errmsg='未知异常')

        # 保存到数据库
        new_comment = Comments()
        new_comment.content = content
        new_comment.news_id = news_id
        new_comment.author = request.user
        new_comment.parent_id = parent_id if parent_id else None
        new_comment.save()

        return json_response(data=new_comment.to_dict_data())

class NewsSearchView(SearchView):
    """
    新闻搜索视图
    """
    # 设置搜索模板文件
    template_name = 'news/search.html'

    # 重写get请求，如果请求参数q为空，返回模型News的热门新闻数据
    # 否则根据参数q搜索相关数据
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        if not query:
            # 显示热门新闻
            hot_news = HotNews.objects.select_related('news__tag').only('news__title', 'news__image_url', 'news_id',
                                                                        'news__tag__name').filter(
                is_delete=False).order_by('priority', '-news__clicks')
            paginator = Paginator(hot_news, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
            try:
                page = paginator.get_page(int(request.GET.get('page')))
            except Exception as e:
                page = paginator.get_page(1)

            return render(request, 'news/search.html', context={
                'page': page,
                'paginator': paginator,
                'query': query
            })
        else:
            # 搜索
            return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """
        在context中添加page变量
        :param args:
        :param kwargs:
        :return:
        """
        context = super().get_context_data(*args, **kwargs)
        if context['page_obj']:
            context['page'] = context['page_obj']
        return context
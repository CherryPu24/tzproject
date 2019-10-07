from django.shortcuts import render
from django.views import View
from django.http import Http404
from .models import Course
# Create your views here.
def course_list(request):
    """
    在线课程列表
    url:/course/
    :param request:
    :return:
    """
    courses =Course.objects.only('title', 'cover_url', 'teacher__title', 'teacher__name').filter(
        is_delete=False).select_related(
        'teacher')
    return render(request, 'course/course.html', context={'courses': courses})
class CourseDetailView(View):
    def get(self,request,course_id):
        # 1.拿到数据
        course=Course.objects.only('title','cover_url','video_url','profile','outline','teacher__name',
                                           'teacher__photo','teacher__title','teacher__profile').\
            select_related('teacher').filter(is_delete=False,id=course_id).first()
        # 2.渲染
        if course:
            return render(request,'course/course_detail.html',context={'course':course})
        else:
            return Http404('课程不存在')
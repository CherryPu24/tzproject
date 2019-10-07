from django.http import FileResponse, Http404
from django.shortcuts import render
from django.utils.encoding import escape_uri_path
from django.views import View


from .models import Doc
from .constans import PER_PAGE_DOC_COUNT
from django.core.paginator import Paginator
from utils.res_code import json_response
import logging
logger=logging.Logger('django')


# Create your views here.
def indexView(request):
    return render(request,'doc/docDownload.html')

class DocListView(View):
    def get(selfr,request):
        # 1.拿到所有文档
        # 2.分页
        # 1.拿到所有文档
        docs = Doc.objects.values('file_url', 'file_name', 'title', 'desc', 'image_url').filter(is_delete=False)
        # 2.分页
        paginator = Paginator(docs, PER_PAGE_DOC_COUNT)
        try:
            page=paginator.get_page(int(request.GET.get('page')))
        except Exception as e:
            page = paginator.get_page(1)

        data = {
            'total_page': paginator.num_pages,
            'docs': list(page)
        }
        return json_response(data=data)

class DocDownloadView(View):
    def get(self,request):
        file_fb = makefile()  # 生成文件流
        try:
            res = FileResponse(file_fb)
        except Exception as e:
            logger.info("获取文档内容出现异常：\n{}".format(e))
            raise Http404("文档下载异常！")

        ex_name = 'xls'  # 文件后缀，表明文件类型
        # https://stackoverflow.com/questions/23714383/what-are-all-the-possible-values-for-http-content-type-header
        # http://www.iana.org/assignments/media-types/media-types.xhtml#image
        if not ex_name:
            raise Http404("文档url异常！")
        else:
            ex_name = ex_name.lower()

        if ex_name == "pdf":
            res["Content-type"] = "application/pdf"
        elif ex_name == "zip":
            res["Content-type"] = "application/zip"
        elif ex_name == "doc":
            res["Content-type"] = "application/msword"
        elif ex_name == "xls":
            res["Content-type"] = "application/vnd.ms-excel"
        elif ex_name == "docx":
            res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ex_name == "ppt":
            res["Content-type"] = "application/vnd.ms-powerpoint"
        elif ex_name == "pptx":
            res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        else:
            raise Http404("文档格式不正确！")

        doc_filename = escape_uri_path('某表格.xls')

        res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)
        return res
        file_fb = makefile()  # 生成文件流
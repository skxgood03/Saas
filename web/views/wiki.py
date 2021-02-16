from django.shortcuts import *
from django.http import *
from web.models import *
from web.forms.wiki import WikiModelFrom
from django.views.decorators.csrf import csrf_exempt
from utils.encrypt import uid
from utils.tencent.cos import upload_file

def wiki(request, project_id):
    """wiki首页展示"""
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')

    wiki_object = WiKi.objects.filter(id=wiki_id, project_id=project_id).first()
    print(wiki_object)

    return render(request, 'wiki.html', {'wiki_object': wiki_object})


def wiki_add(request, project_id):
    """wiki添加"""
    if request.method == 'GET':
        form = WikiModelFrom(request)
        return render(request, 'wiki_form.html', {'form': form})
    form = WikiModelFrom(request, data=request.POST)
    if form.is_valid():
        # 判断用户是否选择副文章
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1

        form.instance.project = request.saas.project
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)

    return render(request, 'wiki_form.html', {'form': form})


def wiki_catalog(request, project_id):
    '''获取wiki目录'''
    # 获取当前项目的所有目录:data = QuerySet类行
    data = WiKi.objects.filter(project=request.saas.project).values('id', 'title', 'parent_id').order_by('depth', 'id')
    # data = WiKi.objects.filter(project=request.saas.project).values('id', 'title','parent_id')
    # print(data)
    return JsonResponse({'status': True, 'data': list(data)})


def wiki_delete(request, project_id, wiki_id):
    '''删除文章'''
    WiKi.objects.filter(project_id=project_id, id=wiki_id).delete()

    url = reverse('wiki', kwargs={'project_id': project_id})
    return redirect(url)


def wiki_edit(request, project_id, wiki_id):
    '''编辑文章'''
    wiki_object = WiKi.objects.filter(project_id=project_id, id=wiki_id).first()
    if not wiki_object:
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)
    if request.method == 'GET':
        form = WikiModelFrom(request, instance=wiki_object)
        return render(request, 'wiki_form.html', {'form': form})
    form = WikiModelFrom(request, data=request.POST, instance=wiki_object)
    if form.is_valid():
        # 判断用户是否选择副文章
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1

        form.instance.project = request.saas.project
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        preview_url = "{0}?wiki_id={1}".format(url, wiki_id)
        return redirect(preview_url)
    return render(request, 'wiki_form.html', {'form': form})


@csrf_exempt
def wiki_upload(request, project_id):
    '''markdown插件上传图片'''
    result = {
        'success':0,
        'message':None,
        'url':None
    }

    image_object = request.FILES.get('editormd-image-file')
    if not image_object:
        result['message'] = '文件不存在'
        return JsonResponse(result)
    # 将文件对象上传到项目桶中
    ext = image_object.name.split('.')[-1]
    key = '{}.{}'.format(uid(request.saas.user.phone),ext)
    image_url = upload_file(
        request.saas.project.bucket,
        request.saas.project.region,
        image_object,
        key
    )

    result['success'] = 1
    result['url'] = image_url
    return JsonResponse(result)

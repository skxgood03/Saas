from django.shortcuts import render
from web.forms.file import FileFolderModelForm
from django.http import JsonResponse
from web.models import *

def file(request, project_id):
    '''文件列表'''
    # 区分父级目录
    parent_object = None
    folder_id = request.GET.get('folder', "")
    if folder_id.isdecimal():
        parent_object = FileRepository.objects.filter(id=int(folder_id), file_type=2,
                                                      project=request.saas.project).first()
    # 查看页面`
    if request.method == 'GET':
        #导航条
        breadcrumb_list = []
        parent = parent_object
        while parent:
            breadcrumb_list.insert(0,{'id':parent.id,'name':parent.name})
            parent = parent.parent

        # 当前目录下的所有文件 $ 文件夹获取到即可
        queryset = FileRepository.objects.filter(project=request.saas.project)
        if parent_object:
            # 进入了某个目录
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')  # 倒序,文件夹在上文件在下
        else:
            # 根目录
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')
        form = FileFolderModelForm(request, parent_object)
        return render(request, 'file.html', {'form': form,'file_object_list':file_object_list,'breadcrumb_list':breadcrumb_list})

    # 文件夹添加 & 修改
    fid = request.POST.get('fid','')
    edit_object = None
    if fid.isdecimal():
        #修改
        edit_object = FileRepository.objects.filter(id=int(fid), file_type=2,
                                                      project=request.saas.project).first()
    if edit_object:
        form = FileFolderModelForm(request, parent_object, data=request.POST,instance = edit_object)
    else:
        form = FileFolderModelForm(request, parent_object, data=request.POST)
    if form.is_valid():
        form.instance.project = request.saas.project
        form.instance.file_type = 2
        form.instance.update_user = request.saas.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})

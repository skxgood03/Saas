import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from web.forms.file import FileFolderModelForm, FileModelForm
from django.http import JsonResponse
from web.models import *
from utils.tencent.cos import *


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
        # 导航条
        breadcrumb_list = []
        parent = parent_object
        while parent:
            breadcrumb_list.insert(0, {'id': parent.id, 'name': parent.name})
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
        context = {
            'form': form,
            "file_object_list": file_object_list,
            "breadcrumb_list": breadcrumb_list,
            'folder_object': parent_object
        }
        return render(request, 'file.html', context)
    # 文件夹添加 & 修改
    fid = request.POST.get('fid', '')
    edit_object = None
    if fid.isdecimal():
        # 修改
        edit_object = FileRepository.objects.filter(id=int(fid), file_type=2,
                                                    project=request.saas.project).first()
    if edit_object:
        form = FileFolderModelForm(request, parent_object, data=request.POST, instance=edit_object)
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


def file_delete(request, project_id):
    """删除文件"""
    fid = request.GET.get('fid')
    # 删除数据库文件和文件夹(级联删除)
    delete_object = FileRepository.objects.filter(id=fid, project=request.saas.project).first()
    if delete_object.file_type == 1:
        # 删除文件(数据库文件/cos文件),并且把空间还回去
        # 删除文件,将容量还回去
        request.saas.project.use_space -= delete_object.file_size
        request.saas.project.save()
        # 去cos中删除文件
        delete_file(request.saas.project.bucket, request.saas.project.region, delete_object.key)
        delete_object.delete()
        return JsonResponse({'status': True})
    else:
        # 删除文件夹(找到文件夹下面的所有文件,删除并且把空间还回去)
        total_size = 0
        key_list = []
        folder_list = [delete_object, ]
        for folder in folder_list:
            child_list = FileRepository.objects.filter(project=request.saas.project, parent=folder).order_by(
                '-file_type')
            for child in child_list:
                if child.file_type == 2:
                    folder_list.append(child)
                else:
                    # 文件大小汇总
                    total_size += child.file_type

                    # 删除文件
                    key_list.append({"Key": child.key})

        # cos 批量删除文件
        if key_list:
            delete_file_list(request.saas.project.bucket, request.saas.project.region, key_list)
        # 归还容量
        if total_size:
            request.saas.project.use_space -= total_size
            request.saas.project.save()

        delete_object.delete()
        return JsonResponse({'status': True})


@csrf_exempt
def cos_credential(request, project_id):
    '''获取上传临时凭证'''
    per_file_limit = request.saas.price_policy.per_file_size * 1024 * 1024  # 限制 单个文件
    total_file_limit = request.saas.price_policy.per_file_size * 1024 * 1024 * 1024  # 限制   单个项目
    file_list = json.loads(request.body.decode('utf-8'))
    total_size = 0
    # 单个容量限制
    for item in file_list:
        # 文件字节大小 item['size]=B  单文件限制大小 M
        if item['size'] > per_file_limit:
            # 超出限制
            msg = '单文件超出限制(最大{}M),文件:{},请升级套餐'.format(request.saas.price_policy.per_file_size, item['name'])
            return JsonResponse({'status': False, 'error': msg})
    # 总容量限制
    # request.saas.price_policy.project_space #项目允许使用的空间
    # request.saas.project.use_space #项目已使用的空间
    if request.saas.project.use_space + total_size > total_file_limit:
        # 超出限制
        return JsonResponse({'status': False, 'error': '容量超过限制,请升级套餐'})
    data_dict = credential(request.saas.project.bucket, request.saas.project.region)

    return JsonResponse({'status': True, 'data': data_dict})


@csrf_exempt
def file_post(request, project_id):
    """ 已上传成功的文件写入到数据 """
    """
    name: fileName,
    key: key,
    file_size: fileSize,
    parent: CURRENT_FOLDER_ID,
    # etag: data.ETag,
    file_path: data.Location
    """

    # 根据key再去cos获取文件Etag和"db7c0d83e50474f934fd4ddf059406e5"

    print(request.POST)
    # 把获取到的数据写入数据库即可
    form = FileModelForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过,写入数据库
        # form.instance.file_type = 1
        # form._update_user = request.saas.user
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict.update({'project': request.saas.project, 'file_type': 1, 'update_user': request.saas.user})
        instance = FileRepository.objects.create(**data_dict)
        #项目的已使用空间
        request.saas.project.use_space += data_dict['file_size']
        request.saas.project.save()


        result = {
            'id': instance.id,
            'name': instance.name,
            'file_size': instance.file_size,
            'username': instance.update_user.name,
            'datetime': instance.update_datetime.strftime('%Y年-%m月-%d日 %H:%M'),
            # 'file_type':instance.get_file_type_display()
        }
        return JsonResponse({'status': True, 'data': result})
    return JsonResponse({'status': False, 'data': '文件错误'})

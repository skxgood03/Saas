from django.urls import path, include
from web.views import account
from web.views import home
from web.views import project
from web.views import manage
from web.views import wiki
from web.views import file

urlpatterns = [
    path('register/', account.register, name='register'),
    path('send/sms/', account.send_sms, name='send_sms'),
    path('login/sms/', account.login_sms, name='login_sms'),
    path('login/', account.login, name='login'),
    path('loginout/', account.loginout, name='loginout'),
    path('image_code/', account.image_code, name='image_code'),
    path('index/', home.index, name='index'),
    # 项目列表
    path('project/list/', project.project_list, name='project_list'),
    # project/star/my/1
    # project/star/join/1
    path('project/star/<str:project_type>/<int:project_id>/', project.project_star, name='project_star'),
    path('project/unstar/<str:project_type>/<int:project_id>/', project.project_unstar, name='project_unstar'),
    # 项目管理(路由分发)
    path('manage/<int:project_id>/', include([
        path('dashboard/', manage.dashboard, name='dashboard'),
        path('issues/', manage.issues, name='issues'),

        path('wiki/', wiki.wiki, name='wiki'),
        path('wiki/add/', wiki.wiki_add, name='wiki_add'),
        path('wiki/catalog/', wiki.wiki_catalog, name='wiki_catalog'),
        path('wiki/delete/<int:wiki_id>', wiki.wiki_delete, name='wiki_delete'),
        path('wiki/edit/<int:wiki_id>', wiki.wiki_edit, name='wiki_edit'),
        path('wiki/upload/', wiki.wiki_upload, name='wiki_upload'),

        path('statistics/', manage.statistics, name='statistics'),
        path('setting/', manage.setting, name='setting'),
        path('file/', file.file, name='file'),

    ], None))

]
"""
    #项目管理
    path('manage/<int:project_id>/dashboard',project.dashboard,name = 'dashboard'),
    path('manage/<int:project_id>/dashboard',project.issues,name = 'dashboard'),
    path('manage/<int:project_id>/dashboard',project.file,name = 'dashboard'),
    path('manage/<int:project_id>/dashboard',project.wiki,name = 'dashboard'),
    path('manage/<int:project_id>/dashboard',project.setting,name = 'dashboard'),
"""

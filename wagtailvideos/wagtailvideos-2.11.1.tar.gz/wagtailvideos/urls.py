from django.urls import path, re_path

from wagtailvideos.views import chooser, multiple, videos

app_name = 'wagtailvideos'
urlpatterns = [
    path('add/', videos.add, name='add'),
    re_path(r'^usage/(\d+)/$', videos.usage, name='video_usage'),

    path('multiple/add/', multiple.add, name='add_multiple'),
    re_path(r'^multiple/(\d+)/delete/$', multiple.delete, name='delete_multiple'),
    re_path(r'^multiple/(\d+)/$', multiple.edit, name='edit_multiple'),

    path('chooser/upload/', chooser.chooser_upload, name='chooser_upload'),
    re_path(r'^chooser/(\d+)/$', chooser.video_chosen, name='video_chosen'),
    path('chooser/', chooser.chooser, name='chooser'),

    re_path(r'^(\d+)/delete/$', videos.delete, name='delete'),
    re_path(r'^(\d+)/create_transcode/$', videos.create_transcode, name='create_transcode'),
    re_path(r'^(\d+)/$', videos.edit, name='edit'),
    path('', videos.index, name='index'),
]

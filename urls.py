"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from .views import *


urlpatterns = [
	url(r'^admin/', admin.site.urls),

	url(r'^(\d+)/(\d+)/$', task_update_view),
	url(r'^(\d+)/$',      task_create_view),
	url(r'^(\d+)/(\d+)/add-tag/$', add_tag),
	url(r'^(\d+)/(\d+)/del-tag/(\d+)/$', del_tag),

	url(r'^(\d+)/\d+/share/$', share),
	url(r'^\d+/(\d+)/unshare/(\d+)/$', unshare),

	url(r'^(\d+)/share/$', share),
	url(r'^(\d+)/unshare/(\d+)/$', unshare),

	url(r'^$', view),
	url(r'^create_list/$', list_create_view),
	url(r'^(\d+)/create_list/$', list_update_view),
	url(r'^(\d+)/\d+/create_list/$', list_update_view),

	url(r'^del-list/(\d+)/$', del_list),
	url(r'^\d+/del-list/(\d+)/$', del_list),
	url(r'^\d+/\d+/del-list/(\d+)/$', del_list),

	url(r'^(\d+)/\d+/del-task/(\d+)$', del_task),
	url(r'^(\d+)/del-task/(\d+)$', del_task),

	url(r'^logout/$', logout),
	url(r'^login/$', login)
]

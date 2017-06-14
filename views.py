from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
import requests
from django.core.mail import send_mail
#объявляем глобальные переменные
adress			= 'http://localhost:8000'
url_tasklists	= 'todolists'
url_tasks		= 'tasks'
url_tags		= 'tags'
url_share		= 'shared'
url_register	= 'register'
url_login		= 'token-login'
token = ''
username=''
auth = ('max', 'pswd')
#Отдаём наш токен в удобной форме
def headers():
	return {'Authorization' : 'Token ' + token}


def make_url(*args):
	return '/'.join(args) + '/'

#Получаем json объект с данными по адресу
def get_data(*pieces_of_address):
	res = requests.get(make_url(*pieces_of_address), headers=headers()).json()
	return res

#Выполняем функцию по каждому эл-ту списка
def get_elem_by_func(lst, func):
	for i in lst:
		if func(i):
			return i
	raise LookupError('no such element')

#Проверяем можем ли мы редактировать
def is_editable(tasklist, username):
	if tasklist.get('owner') == username:
		return True
	try:
		share = get_elem_by_func(tasklist['shared'], lambda x: x['username'] == username)
	except LookupError:
		return False
	return share.get('access') == 'e'


def add_ediable_field(tasklists, username):
	for index, value in enumerate(tasklists):
		tasklists[index]['editable'] = is_editable(value, username)

#Декоратор, еренаправлющий на страницу авторизации, если нет токена
def is_logged_in(func):
	def wrapper(*args, **kwargs):
		if not token:
			return HttpResponseRedirect('/login/')
		return func(*args, **kwargs)
	return wrapper


def list_create_view(request):
	requests.post(make_url(adress, url_tasklists), data=request.GET, headers=headers())
	return redirect(make_url(request.build_absolute_uri('/')[:-1]))


@is_logged_in
def view(request):
	tasklists = get_data(adress, url_tasklists)
	add_ediable_field(tasklists, username)
	return render(request, 'page.html',
	{
		'tasklists': tasklists,
		'editable':True
	})


@is_logged_in
def list_update_view(request, list_id):
	requests.put(make_url(adress, url_tasklists, list_id), data=request.GET, headers=headers())
	return redirect(make_url(request.build_absolute_uri('/')[:-1], list_id))


def del_list(request, list_id):
	requests.delete(make_url(adress, url_tasklists, list_id), headers=headers())
	return redirect(make_url(request.build_absolute_uri('/')[:-1]))


def del_task(request, list_id, task_id):
	resp = requests.delete(make_url(adress, url_tasklists, list_id, url_tasks, task_id), headers=headers())
	return redirect(make_url(request.build_absolute_uri('/')[:-1], list_id))

@is_logged_in
def task_update_view(request, list_id, task_id):

	if request.GET:
		requests.put(make_url(adress, url_tasklists, list_id, url_tasks, task_id),
		data=request.GET, headers=headers())

	tasklists = get_data(adress, url_tasklists)
	tasklist  = get_elem_by_func(tasklists, lambda x: x['id'] == int(list_id))
	tasks	  = get_data(adress, url_tasklists, list_id, url_tasks)
	task	  = get_data(adress, url_tasklists, list_id, url_tasks, task_id)
	tags 	  = get_data(adress, url_tasklists, list_id, url_tasks, task_id, url_tags)

	add_ediable_field(tasklists, username)

	return render(request, 'page.html',
		{
			'tasklists': tasklists,
			'tasks': tasks,
			'list':tasklist,
			'task':task,
			'tags':tags,
			'editable':is_editable(tasklist, username)
		})

@is_logged_in
def task_create_view(request, list_id):

	if request.GET:
		requests.post(make_url(adress, url_tasklists, list_id, url_tasks),
		data=request.GET, headers=headers())

	tasklists	= get_data(adress, url_tasklists)
	tasklist 	= get_elem_by_func(tasklists, lambda x: x['id'] == int(list_id))
	tasks	  	= get_data(adress, url_tasklists, list_id, url_tasks)

	add_ediable_field(tasklists, username)

	task = {
		"name": "",
		"description": "",
		"completed": False,
		"due_date": None,
		"priority": "h",
		"tags": []
	}

	return render(request, 'page.html',
		{
			'tasklists': tasklists,
			'tasks': tasks,
			'list':tasklist,
			# 'task':task,
			'editable':is_editable(tasklist, username)
		})



def add_tag(request, list_id, task_id):
	resp = requests.post(make_url(adress, url_tasklists, list_id, url_tasks, task_id, url_tags),
	data=request.GET, headers=headers())
	return redirect(make_url(request.build_absolute_uri('/')[:-1], list_id, task_id))


def del_tag(request, list_id, task_id, tag_id):
	resp = requests.delete(make_url(adress, url_tasklists, list_id, url_tasks, task_id, url_tags,
	tag_id), headers=headers())
	return redirect(make_url(request.build_absolute_uri('/')[:-1], list_id, task_id))

#Делимся  задачами
def share(request, list_id):
	resp = requests.post(make_url(adress, url_tasklists, list_id, url_share),
	data=request.GET, headers=headers())
	return redirect(make_url(request.build_absolute_uri('/')[:-1], list_id))

#Больше не делимся задачами с этим id
def unshare(request, list_id, share_id):
	resp = requests.delete(make_url(adress, url_tasklists, list_id, url_share, share_id),
	headers=headers())
	return redirect(make_url(request.build_absolute_uri('/')[:-1], list_id))

#Регистрируемся или авторизируемся, в зависимости от выбранного в списке значения
def login(request):
	data = request.GET.dict()
	if data:
		global token
		global username
		act = data.pop('act', 'login')
		if act == 'login':
			data.pop('email')
			resp = requests.post(make_url(adress, url_login), data=data)
			token = resp.json().get('token')
			username = data.get('username')
			return HttpResponseRedirect('/')
		if act == 'register':
			token = ''
			username = ''
			resp = requests.post(make_url(adress, url_register), data=data)
			if data.get('email', None):
				send_mail("Registration", "You've registrated username: %s\npassword %s" % (data['username'], data['password']), 'vasilisk0071@yandex.ru', recipient_list=(data['email'],), fail_silently=False)
			return HttpResponseRedirect('/')

	if token:
		username = data.get('username')
		return HttpResponseRedirect('/')

	return render(request, 'login.html')

#Разлогиниваемся
def logout(request):
	global token
	token = ''
	username = ''
	resp = requests.get(adress + '/api-auth/logout/')
	return redirect(make_url(request.build_absolute_uri('/')[:-1]))

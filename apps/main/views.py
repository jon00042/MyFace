import apps.main.models as m
import django

from django.contrib import messages
from django.shortcuts import redirect, render

def index(request):
    if ('user_id' in request.session):
        return redirect('main:wall', wall_user_id=request.session['user_id'])
    if (request.method != 'GET'):
        return redirect('main:index')
    context = {}
    if ('registered' in request.session):
        context['registered'] = request.session['registered']
        del(request.session['registered'])
    return render(request, 'main/index.html', context)

def register(request):
    if ('user_id' not in request.session):
        if (request.method == 'GET'):
            return render(request, 'main/register.html')
        if (request.method == 'POST'):
            for field in ('email', 'username', 'password'):
                if (len(request.POST[field]) < 1):
                    messages.error(request, 'registration fields cannot be empty!')
                    return redirect('main:register')
            if (request.POST['password'] != request.POST['confirm']):
                messages.error(request, 'passwords mismatch!')
                return redirect('main:register')
        try:
            m.User.objects.create(email=request.POST['email'], username=request.POST['username'], password=request.POST['password'])
            request.session['registered'] = request.POST['email']
            return redirect('main:index')
        except django.db.utils.IntegrityError:
            messages.error(request, 'email already in use!')
        except Exception as ex:
            messages.error(request, ex)
    return redirect('main:register')

def login(request):
    if ('user_id' in request.session):
        return redirect('main:wall', wall_user_id=request.session['user_id'])
    if (request.method == 'GET'):
        return render(request, 'main/login.html')
    if (request.method == 'POST'):
        try:
            user = m.User.objects.get(email=request.POST['email'])
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return redirect('main:wall', wall_user_id=request.session['user_id'])
        except m.User.DoesNotExist:
            pass
        except Exception as ex:
            messages.error(request, ex)
        messages.error(request, 'login attempt failed!')
    return redirect('main:login')

def logout(request):
    if ('user_id' in request.session and request.method == 'GET'):
        request.session.clear()
    return redirect('main:index')

def search(request):
    if ('user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    context = {}
    context['results'] = m.User.objects.filter(username__icontains=request.GET['text']).order_by('username')
    return render(request, 'main/search.html', context)

def settings(request):
    if ('user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    return render(request, 'main/settings.html')

def wall(request, wall_user_id):
    if ('user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    context = {}
    wall_user = m.User.objects.get(id=wall_user_id)
    context['wall_user_id'] = wall_user_id
    context['wall_username'] = wall_user.username
    context['posts'] = m.Post.objects.filter(wall_user_id=wall_user_id).order_by('-id')
    return render(request, 'main/wall.html', context)

def post(request):
    if ('user_id' not in request.session or request.method != 'POST'):
        return redirect('main:index')
    wall_user_id = request.POST['wall_user_id']
    if (len(request.POST['text']) > 0):
        m.Post.objects.create(text=request.POST['text'], post_user_id=request.session['user_id'], wall_user_id=wall_user_id)
    return redirect('main:wall', wall_user_id=wall_user_id)

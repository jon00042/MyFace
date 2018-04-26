import apps.main.models as m
import django

from django.contrib import messages
from django.shortcuts import redirect, render

def index(request):
    if (request.method != 'GET'):
        return redirect('main:index')
    context = {}
    if ('registered' in request.session):
        if ('user_id' not in request.session):
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
        return redirect('main:index')
    if (request.method == 'GET'):
        return render(request, 'main/login.html')
    if (request.method == 'POST'):
        try:
            user = m.User.objects.get(email=request.POST['email'])
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return redirect('main:index')
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


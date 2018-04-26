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

def get_followings(session_user_id):
    followings = {}
    results = m.Followings.objects.filter(doing_the_following_user_id=session_user_id)
    for result in results:
        followings[str(result.being_followed_user_id)] = 1
    return followings

def search(request):
    if ('user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    context = {}
    context['sidebar'] = 'Search Results'
    context['users'] = m.User.objects.filter(username__icontains=request.GET['text']).order_by('username')
    context['followings'] = get_followings(request.session['user_id'])
    request.session['last_url'] = request.get_full_path()
    return render(request, 'main/results.html', context)

def followers_of(request, follow_user_id):
    if ('user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    followed_user = m.User.objects.get(id=follow_user_id)
    following_users = []
    results = followed_user.follows_me.all()
    for result in results:
        following_users.append(result.doing_the_following_user)
    context = {}
    context['sidebar'] = 'Followers of {}'.format(followed_user.username)
    context['users'] = following_users
    context['followings'] = get_followings(request.session['user_id'])
    request.session['last_url'] = request.get_full_path()
    return render(request, 'main/results.html', context)

def followings_of(request, follow_user_id):
    if ('user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    user_doing_the_following = m.User.objects.get(id=follow_user_id)
    user_followings = []
    results = user_doing_the_following.i_follow.all()
    for result in results:
        user_followings.append(result.being_followed_user)
    context = {}
    context['sidebar'] = '{} follows'.format(user_doing_the_following.username)
    context['users'] = user_followings
    context['followings'] = get_followings(request.session['user_id'])
    request.session['last_url'] = request.get_full_path()
    return render(request, 'main/results.html', context)

def follow(request, follow_user_id):
    if ('user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    if ('last_url' not in request.session):
        return redirect('main:index')
    if (follow_user_id == request.session['user_id']):
        return redirect('main:index')
    last_url = request.session['last_url']
    del(request.session['last_url'])
    existing = None
    try:
        existing = m.Followings.objects.get(being_followed_user_id=follow_user_id, doing_the_following_user_id=request.session['user_id'])
    except m.Followings.DoesNotExist:
        pass
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    if (not existing):
        m.Followings.objects.create(being_followed_user_id=follow_user_id, doing_the_following_user_id=request.session['user_id'])
    return redirect(last_url)

def unfollow(request, unfollow_user_id):
    if ('user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    if ('last_url' not in request.session):
        return redirect('main:index')
    last_url = request.session['last_url']
    del(request.session['last_url'])
    existing = None
    try:
        existing = m.Followings.objects.get(being_followed_user_id=unfollow_user_id, doing_the_following_user_id=request.session['user_id'])
    except m.Followings.DoesNotExist:
        pass
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    if (existing):
        existing.delete()
    return redirect(last_url)

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

def settings(request):
    if ('user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    return render(request, 'main/settings.html')


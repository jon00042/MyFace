import apps.main.models as m
import django

from django.contrib import messages
from django.db.models.functions import Lower
from django.shortcuts import redirect, render

def index(request):
    if ('logged_in_user_id' in request.session):
        return redirect('main:wall', wall_user_id=request.session['logged_in_user_id'])
    if (request.method != 'GET'):
        return redirect('main:index')
    context = {}
    if ('just_registered_email' in request.session):
        context['just_registered_email'] = request.session['just_registered_email']
        del(request.session['just_registered_email'])
    return render(request, 'main/index.html', context)

def register(request):
    if ('logged_in_user_id' in request.session):
        return redirect('main:index')
    if (request.method == 'GET'):
        return render(request, 'main/register.html')
    if (request.method != 'POST'):
        return redirect('main:index')
    for field in ('email', 'username', 'password'):
        if (len(request.POST[field]) < 1):
            messages.error(request, 'registration fields cannot be empty!')
            return redirect('main:register')
    if (request.POST['password'] != request.POST['confirm']):
        messages.error(request, 'passwords mismatch!')
        return redirect('main:register')
    try:
        m.User.objects.create(email=request.POST['email'], username=request.POST['username'], password=request.POST['password'])
        request.session['just_registered_email'] = request.POST['email']
        return redirect('main:index')
    except django.db.utils.IntegrityError:
        messages.error(request, 'email already in use!')
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    return redirect('main:register')

def login(request):
    if ('logged_in_user_id' in request.session):
        return redirect('main:index')
    if (request.method == 'GET'):
        return render(request, 'main/login.html')
    if (request.method != 'POST'):
        return redirect('main:index')
    try:
        user = m.User.objects.get(email=request.POST['email'])
        request.session['logged_in_user_id'] = user.id
        request.session['logged_in_username'] = user.username
        return redirect('main:wall', wall_user_id=user.id)
    except m.User.DoesNotExist:
        pass
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    messages.error(request, 'login attempt failed!')
    return redirect('main:login')

def logout(request):
    request.session.clear()
    return redirect('main:index')

def get_followings_dict(of_user_id):
    followings_dict = {}
    results = None
    try:
        results = m.Followings.objects.filter(doing_the_following_user_id=of_user_id)
    except:
        raise
    for result in results:
        followings_dict[str(result.being_followed_user_id)] = 1
    return followings_dict

def search(request):
    if ('logged_in_user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    context = {}
    context['sidebar_text'] = 'Search Results'
    try:
        context['users_list'] = m.User.objects.filter(username__icontains=request.GET['text']).order_by(Lower('username'))
        context['logged_in_followings_dict'] = get_followings_dict(request.session['logged_in_user_id'])
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    request.session['last_url'] = request.get_full_path()
    return render(request, 'main/results.html', context)

def followers_of(request, followed_user_id):
    if ('logged_in_user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    context = {}
    try:
        followed_user = m.User.objects.get(id=followed_user_id)
        context['sidebar_text'] = 'Followers of {}'.format(followed_user.username)
        doing_the_following_user_ids = followed_user.follows_me.all().values_list('doing_the_following_user_id', flat=True)
        context['users_list'] = m.User.objects.filter(id__in=doing_the_following_user_ids).order_by(Lower('username'))
        context['logged_in_followings_dict'] = get_followings_dict(request.session['logged_in_user_id'])
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    request.session['last_url'] = request.get_full_path()
    return render(request, 'main/results.html', context)

def followings_of(request, following_user_id):
    if ('logged_in_user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    try:
        user_doing_the_following = m.User.objects.get(id=following_user_id)
        being_followed_user_ids = user_doing_the_following.i_follow.all().values_list('being_followed_user_id', flat=True)
        context = {}
        context['sidebar_text'] = '{} follows'.format(user_doing_the_following.username)
        context['users_list'] = m.User.objects.filter(id__in=being_followed_user_ids).order_by(Lower('username'))
        context['logged_in_followings_dict'] = get_followings_dict(request.session['logged_in_user_id'])
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    request.session['last_url'] = request.get_full_path()
    return render(request, 'main/results.html', context)

def follow(request, follow_user_id):
    if ('logged_in_user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    if ('last_url' not in request.session):
        return redirect('main:index')
    if (follow_user_id == request.session['logged_in_user_id']):
        return redirect('main:index')
    last_url = request.session['last_url']
    del(request.session['last_url'])
    existing = None
    try:
        existing = m.Followings.objects.get(being_followed_user_id=follow_user_id, doing_the_following_user_id=request.session['logged_in_user_id'])
    except m.Followings.DoesNotExist:
        pass
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    if (not existing):
        try:
            m.Followings.objects.create(being_followed_user_id=follow_user_id, doing_the_following_user_id=request.session['logged_in_user_id'])
        except Exception as ex:
            print(ex)
            return redirect('main:index')
    return redirect(last_url)

def unfollow(request, unfollow_user_id):
    if ('logged_in_user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    if ('last_url' not in request.session):
        return redirect('main:index')
    last_url = request.session['last_url']
    del(request.session['last_url'])
    existing = None
    try:
        existing = m.Followings.objects.get(being_followed_user_id=unfollow_user_id, doing_the_following_user_id=request.session['logged_in_user_id'])
    except m.Followings.DoesNotExist:
        pass
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    if (existing):
        try:
            existing.delete()
        except Exception as ex:
            print(ex)
            return redirect('main:index')
    return redirect(last_url)

def wall(request, wall_user_id):
    if ('logged_in_user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    context = {}
    try:
        wall_user = m.User.objects.get(id=wall_user_id)
        context['wall_user_id'] = wall_user_id
        context['wall_username'] = wall_user.username
        context['posts'] = m.Post.objects.filter(wall_user_id=wall_user_id).order_by('-id')
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    return render(request, 'main/wall.html', context)

def add_post(request):
    if ('logged_in_user_id' not in request.session or request.method != 'POST'):
        return redirect('main:index')
    wall_user_id = request.POST['wall_user_id']
    if (len(request.POST['text']) > 0):
        try:
            m.Post.objects.create(text=request.POST['text'], post_user_id=request.session['logged_in_user_id'], wall_user_id=wall_user_id)
        except Exception as ex:
            print(ex)
            return redirect('main:index')
    return redirect('main:wall', wall_user_id=wall_user_id)

def del_post(request, post_id):
    if ('logged_in_user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    try:
        post = m.Post.objects.get(id=post_id)
        if (post.wall_user_id == request.session['logged_in_user_id'] or post.post_user_id == request.session['logged_in_user_id']):
            post.delete()
        return redirect('main:wall', wall_user_id=post.wall_user_id)
    except m.Post.DoesNotExist:
        return redirect('main:index')
    except Exception as ex:
        print(ex)
        return redirect('main:index')

def settings(request):
    if ('logged_in_user_id' not in request.session or request.method != 'GET'):
        return redirect('main:index')
    return render(request, 'main/settings.html')


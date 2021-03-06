import apps.main.models as m
import django

from django.contrib import messages
from django.db.models.functions import Lower
from django.shortcuts import redirect, render

def get_logged_in_user(request):
    if ('logged_in_user_id' not in request.session):
        return None
    try:
        return m.User.objects.get(id=request.session['logged_in_user_id'])
    except Exception as ex:
        print(ex)
    request.session.clear()
    return None

def index(request):
    logged_in_user = get_logged_in_user(request)
    if (logged_in_user):
        return redirect('main:wall', wall_user_id=logged_in_user.id)
    if (request.method != 'GET'):
        return redirect('main:index')
    context = {}
    if ('just_registered_email' in request.session):
        context['just_registered_email'] = request.session['just_registered_email']
        del(request.session['just_registered_email'])
    return render(request, 'main/index.html', context)

def register(request):
    logged_in_user = get_logged_in_user(request)
    if (logged_in_user):
        return redirect('main:index')
    if (request.method == 'GET'):
        return render(request, 'main/register.html')
    if (request.method != 'POST'):
        return redirect('main:index')
    for field in ('email', 'username', 'password', 'confirm'):
        if (field not in request.POST):
            return redirect('main:index')
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
    logged_in_user = get_logged_in_user(request)
    if (logged_in_user):
        return redirect('main:index')
    if (request.method == 'GET'):
        return render(request, 'main/login.html')
    if (request.method != 'POST'):
        return redirect('main:index')
    if ('email' not in request.POST):
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
        results = m.Following.objects.filter(doing_the_following_user_id=of_user_id)
    except:
        raise
    for result in results:
        followings_dict[str(result.being_followed_user_id)] = 1
    return followings_dict

def search(request):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'GET'):
        return redirect('main:index')
    context = {}
    context['sidebar_text'] = 'Search Results'
    try:
        context['users_list'] = m.User.objects.filter(username__icontains=request.GET['text']).order_by(Lower('username'))
        context['logged_in_followings_dict'] = get_followings_dict(logged_in_user.id)
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    request.session['last_url'] = request.get_full_path()
    return render(request, 'main/results.html', context)

def followers_of(request, followed_user_id):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'GET'):
        return redirect('main:index')
    context = {}
    try:
        followed_user = m.User.objects.get(id=followed_user_id)
        context['sidebar_text'] = 'Followers of {}'.format(followed_user.username)
        doing_the_following_user_ids = followed_user.follows_me.all().values_list('doing_the_following_user_id', flat=True)
        context['users_list'] = m.User.objects.filter(id__in=doing_the_following_user_ids).order_by(Lower('username'))
        context['logged_in_followings_dict'] = get_followings_dict(logged_in_user.id)
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    request.session['last_url'] = request.get_full_path()
    return render(request, 'main/results.html', context)

def followings_of(request, following_user_id):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'GET'):
        return redirect('main:index')
    try:
        user_doing_the_following = m.User.objects.get(id=following_user_id)
        being_followed_user_ids = user_doing_the_following.i_follow.all().values_list('being_followed_user_id', flat=True)
        context = {}
        context['sidebar_text'] = '{} follows'.format(user_doing_the_following.username)
        context['users_list'] = m.User.objects.filter(id__in=being_followed_user_ids).order_by(Lower('username'))
        context['logged_in_followings_dict'] = get_followings_dict(logged_in_user.id)
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    request.session['last_url'] = request.get_full_path()
    return render(request, 'main/results.html', context)

def follow(request, follow_user_id):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'GET'):
        return redirect('main:index')
    if ('last_url' not in request.session):
        return redirect('main:index')
    if (follow_user_id == logged_in_user.id):
        return redirect('main:index')
    last_url = request.session['last_url']
    del(request.session['last_url'])
    existing = None
    try:
        existing = m.Following.objects.get(being_followed_user_id=follow_user_id, doing_the_following_user_id=logged_in_user.id)
    except m.Following.DoesNotExist:
        pass
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    if (not existing):
        try:
            m.Following.objects.create(being_followed_user_id=follow_user_id, doing_the_following_user_id=logged_in_user.id)
        except Exception as ex:
            print(ex)
            return redirect('main:index')
    return redirect(last_url)

def unfollow(request, unfollow_user_id):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'GET'):
        return redirect('main:index')
    if ('last_url' not in request.session):
        return redirect('main:index')
    last_url = request.session['last_url']
    del(request.session['last_url'])
    existing = None
    try:
        existing = m.Following.objects.get(being_followed_user_id=unfollow_user_id, doing_the_following_user_id=logged_in_user.id)
    except m.Following.DoesNotExist:
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
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'GET'):
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
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'POST'):
        return redirect('main:index')
    if ('text' not in request.POST or 'wall_user_id' not in request.POST):
        return redirect('main:index')
    if (len(request.POST['text']) > 0):
        try:
            m.Post.objects.create(text=request.POST['text'], post_user_id=logged_in_user.id, wall_user_id=request.POST['wall_user_id'])
        except Exception as ex:
            print(ex)
            return redirect('main:index')
    return redirect('main:wall', wall_user_id=request.POST['wall_user_id'])

def del_post(request, post_id):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'GET'):
        return redirect('main:index')
    try:
        post = m.Post.objects.get(id=post_id)
        if (post.wall_user_id == logged_in_user.id or post.post_user_id == logged_in_user.id):
            post.delete()
        return redirect('main:wall', wall_user_id=post.wall_user_id)
    except m.Post.DoesNotExist:
        return redirect('main:index')
    except Exception as ex:
        print(ex)
        return redirect('main:index')

def add_comment(request):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'POST'):
        return redirect('main:index')
    if ('post_id' not in request.POST or 'text' not in request.POST):
        return redirect('main:index')
    post = None
    try:
        post = m.Post.objects.get(id=request.POST['post_id'])
    except m.Post.DoesNotExist:
        return redirect('main:index')
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    try:
        m.Comment.objects.create(post_id=post.id, text=request.POST['text'], user_id=logged_in_user.id)
        return redirect('main:wall', wall_user_id=post.wall_user_id)
    except Exception as ex:
        print(ex)
        return redirect('main:index')

def del_comment(request, comment_id):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'GET'):
        return redirect('main:index')
    comment = None
    try:
        comment = m.Comment.objects.get(id=comment_id)
        post = comment.post
        if (comment.user_id == logged_in_user.id or post.wall_user_id == logged_in_user.id):
            comment.delete()
        return redirect('main:wall', wall_user_id=post.wall_user_id)
    except m.Comment.DoesNotExist:
        return redirect('main:index')
    except Exception as ex:
        print(ex)
        return redirect('main:index')
    return None

def settings(request):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method != 'GET'):
        return redirect('main:index')
    return render(request, 'main/settings.html')

def photo(request):
    logged_in_user = get_logged_in_user(request)
    if (not logged_in_user):
        return redirect('main:index')
    if (request.method == 'GET'):
        return render(request, 'main/photo.html')
    if (request.method != 'POST'):
        return redirect('main:index')
    if ('file' not in request.FILES):
        messages.error(request, 'Must choose a file!')
        return redirect('main:photo')
    f = request.FILES['file']
    if (f.content_type != 'image/jpeg'):
        messages.error(request, 'Can only accept a jpeg!')
        return redirect('main:photo')
    if (f.size > 512 * 1024 * 1024):
        messages.error(request, 'File cannot be larger than 512MB!')
        return redirect('main:photo')
    of = open('media/user-photos/{}.jpg'.format(logged_in_user.id), 'wb')
    for chunk in f.chunks():
        of.write(chunk)
    of.close
    return redirect('main:index')


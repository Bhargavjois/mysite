from django.core.mail import send_mail, BadHeaderError
from django.http.response import BadHeaderError
from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView
from .models import Post, Comment
from .forms import CommentForm, ContactForm, PostForm, UpdateForm 
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect 
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def PostList(request):

    search_post = request.GET.get('search')
    if search_post:
        object_list = Post.objects.filter(Q(title__icontains=search_post) & Q(content__icontains=search_post))
        ol_count = object_list.count()
    else:
        object_list = Post.objects.filter(status=1).order_by('-created_on')
        ol_count = -1
    paginator = Paginator(object_list, 6)  # 6 posts in each page
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        post_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        post_list = paginator.page(paginator.num_pages)
    return render(request,
                  'index.html',
                  {'page': page,
                   'post_list': post_list,
                   'ol_count':ol_count})

@login_required(login_url='/members/login/')
def UserPostsView(request, usr):
    user_posts_active = Post.objects.filter(author=usr,status=1).order_by('-created_on')
    user_posts_draft = Post.objects.filter(author=usr,status=0).order_by('-created_on')
    draft_count = user_posts_draft.count()
    active_count = user_posts_active.count()
    usr_id = int(usr)
    return render(request, 'post-creation.html',{   'user_posts_active':user_posts_active,
                                                    'user_posts_draft':user_posts_draft,
                                                    'usr_id':usr_id,
                                                    'draft_count':draft_count,
                                                    'active_count':active_count,
    })

def post_detail(request, slug):
    model = Post
    template_name = 'post_detail.html'
    post = get_object_or_404(Post, slug=slug)
    if not post.status:
        if not request.user == post.author:
            return redirect('home')
    likes = post.total_likes()
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        liked = True
    comments = post.comments.filter(active=True,parent__isnull=True)
    new_comment = None
    reply_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            parent_obj = None
            try:
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                if parent_obj:
                    reply_comment = comment_form.save(commit=False)
                    reply_comment.parent = parent_obj
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return HttpResponseRedirect(post.get_absolute_url(),{'iscmt': True})
    else:
        comment_form = CommentForm()

    return render(request, template_name, { 'post': post,
                                            'comments': comments,
                                            'reply_comment': reply_comment,
                                            'new_comment': new_comment,
                                            'comment_form': comment_form,
                                            'total_likes':likes,
                                            'liked':liked,
    })

@login_required(login_url='/members/login/')
def AddPostView(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            slug = form.cleaned_data['slug']
            return HttpResponseRedirect(reverse('post_detail', args=[str(slug)]))
        else:
            return render(request, 'add_post.html',{'form':form,'msg':'Some error occured, Maybe post with TITLE already exists!'})
    form = PostForm()
    return render(request, 'add_post.html',{'form':form})



class AboutView(TemplateView):
    template_name = 'about.html'

class PaLandView(LoginRequiredMixin,TemplateView):
    login_url = 'login'
    template_name = 'pa-land.html'

class PolicyView(TemplateView):
    template_name = 'policy.html'

def ContactUs(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            subject = "Website Mail"
            msg_name = contact_form.cleaned_data['first_name'] 
            email_address = contact_form.cleaned_data['email_address']
            body = {
                'first_name' : 'Name: ' + msg_name + ' ' +contact_form.cleaned_data['last_name'],
                'email_address' : 'Email: ' + email_address,
                'message' : 'Message: ' + contact_form.cleaned_data['message'],
            }
            message = "\n".join(body.values())

            try:
                send_mail(subject, message, 'mailsenderforbv@gmail.com',['imbhargavjois@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
        contact_form = ContactForm()
        return render(request, "contact.html", {'contact_form': contact_form, 'msg_name':msg_name})
    contact_form = ContactForm()
    return render(request, "contact.html", {'contact_form': contact_form})

class UpdatePostView(LoginRequiredMixin,UpdateView):
    login_url = 'login'
    model = Post
    template_name = 'update_post.html'
    form_class = UpdateForm


def profileView(request, usr):
    duser = User.objects.get(id=usr)
    posts = Post.objects.filter(author=duser.id, status=1).order_by('-created_on')
    return render(request, 'profile_view.html',{'usr':duser,'posts':posts})

@login_required(login_url='/members/login/')
def deletePost(request,slug):
    if request.method == 'DELETE':
        Post.objects.get(slug=slug).delete()
        usr=request.user.id
        user_posts_active = Post.objects.filter(author=usr,status=1).order_by('-created_on')
        user_posts_draft = Post.objects.filter(author=usr,status=0).order_by('-created_on')
        draft_count = user_posts_draft.count()
        active_count = user_posts_active.count()
        return render(request, 'post-creation-model.html',{'user_posts_active':user_posts_active,
                                                            'user_posts_draft':user_posts_draft,
                                                            'usr_id':usr,
                                                            'draft_count':draft_count,
                                                            'active_count':active_count,
        })
    if request.method == 'POST':
        Post.objects.get(slug=slug).delete()
        usr=request.user.id
        user_posts_active = Post.objects.filter(status=1).order_by('-created_on')
        user_posts_draft = Post.objects.filter(status=0).order_by('-created_on')
        draft_count = user_posts_draft.count()
        active_count = user_posts_active.count()
        return render(request, 'editor.html',{'active_posts':user_posts_active,
                                                'draft_posts':user_posts_draft,
                                                'draft_count':draft_count,
                                                'active_count':active_count,
        })
    return redirect('pa-land')


def LikeView(request, slug):
    if request.method == "POST":
        instance = Post.objects.get(slug=slug)
        if not instance.likes.filter(id=request.user.id).exists():
            instance.likes.add(request.user)
            instance.save() 
            liked = True
            likes = instance.total_likes()
            return render( request, 'likes.html', context={'post':instance,'liked':liked,'total_likes':likes})
        else:
            instance.likes.remove(request.user)
            instance.save()
            liked = False 
            likes = instance.total_likes()
            return render( request, 'likes.html', context={'post':instance,'liked':liked,'total_likes':likes})


@login_required(login_url='/members/login/')
def Publish(request,slug):
    if request.method == 'POST':
        pst = Post.objects.get(slug=slug)
        pst.status = 1 if pst.status == 0 else 0
        pst.save()
        
        if pst.status:
            email_list = list(User.objects.values_list("email", flat=True))
            d = {'slug':slug}
            htmly = get_template('Notif-Email.html')
            subject, from_email, to = 'Welcome to Dhi Darpan', 'mailsenderforbv@gmail.com', email_list
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        draft_posts = Post.objects.filter(status=0).order_by('-created_on')
        active_posts = Post.objects.filter(status=1).order_by('-created_on')
        draft_count = draft_posts.count()
        active_count = active_posts.count()
        return render(request, 'editor.html',{'active_posts':active_posts,'draft_posts':draft_posts,'draft_count':draft_count,
                                                'active_count':active_count,})
    return redirect('pa-land')


@login_required(login_url='/members/login/')
@permission_required('blog.change_post', login_url='/members/login/')
def PublishView(request):
    if request.user.has_perm('blog.change_post'):
        draft_posts = Post.objects.filter(status=0).order_by('-created_on')
        active_posts = Post.objects.filter(status=1).order_by('-created_on')
        draft_count = draft_posts.count()
        active_count = active_posts.count()
        return render(request, 'editor-main.html',{'active_posts':active_posts,'draft_posts':draft_posts,'draft_count':draft_count,
                                                'active_count':active_count,}) 
    return redirect('pa-land')

@login_required(login_url='/members/login/')
@permission_required('auth.change_user', login_url='/members/login/')
def ManageUsersView(request):
    users = User.objects.all().exclude(groups__id=1).exclude(groups__id=2)
    authors = User.objects.filter(groups__id=1)
    editors = User.objects.filter(groups__id=2)
    return render(request, 'manage_users.html',{'authors':authors,'editors':editors,'users':users,'users_count':users.count(),
    'authors_count':authors.count(),'editors_count':editors.count(),})

def MakeAuthor(request,usr):
    if request.method == 'POST':
        myuser = User.objects.get(id=usr)
        users = User.objects.all().exclude(groups__id=1).exclude(groups__id=2).order_by('date_joined')
        authors = User.objects.filter(groups__id=1).order_by('date_joined')
        editors = User.objects.filter(groups__id=2).order_by('date_joined')
        if myuser.groups.filter(id=1).exists():
            myuser.groups.remove(1)
            myuser.save()
        else:
            myuser.groups.add(1)
            myuser.save()
        return render( request, 'manage_user_model.html',{'authors':authors,'editors':editors,'users':users,'users_count':users.count(),
                                'authors_count':authors.count(),'editors_count':editors.count(),})
    return redirect('home')

def MakeEditor(request,usr):
    if request.method == 'POST':
        myuser = User.objects.get(id=usr)
        users = User.objects.all().exclude(groups__id=1).exclude(groups__id=2).order_by('date_joined')
        authors = User.objects.filter(groups__id=1).order_by('date_joined')
        editors = User.objects.filter(groups__id=2).order_by('date_joined')
        if myuser.groups.filter(id=2).exists():
            myuser.groups.remove(2)
            myuser.save()
        else:
            myuser.groups.add(2)
            myuser.save()
        return render( request, 'manage_user_model.html',{'authors':authors,'editors':editors,'users':users,'users_count':users.count(),
                                'authors_count':authors.count(),'editors_count':editors.count(),})
    return redirect('home')


def AuthorsView(request):
    authors = User.objects.filter(groups__id=1)
    return render(request, 'our_authors.html',{'authors':authors,'users_count':authors.count(),})
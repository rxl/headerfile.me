from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView

from flask.ext.mongoengine.wtf import model_form

from headerfile.auth import requires_auth
from headerfile.models import *

from flask import flash

#------------------------
# admin
#------------------------

admin = Blueprint('admin', __name__, template_folder='templates')

#------------------------
# users
#------------------------

class UserAdminListView(MethodView):
    decorators = [requires_auth]
    cls = User

    def get(self):
        users = self.cls.objects.all()
        return render_template('admin/user_list.html', users=users)

class UserAdminDeleteView(MethodView):
    decorators = [requires_auth]

    def get(self, username):
        user = None
        if username:
            user = User.objects.get_or_404(username=username)
        else:
            user = None
        return render_template('admin/user_delete.html', user=user)

    def post(self, username):
        user = User.objects.get_or_404(username=username)
        user.delete()
        return redirect(url_for('admin.user_index'))

class UserAdminDetailsView(MethodView):
    decorators = [requires_auth]

    def get_context(self, username=None):
        form_cls = model_form(User, exclude=('created_at', 'websites', 'github', 'blog','facebook','twitter','linkedin','stackoverflow','topcoder','work'))

        if username:
            user = User.objects.get_or_404(username=username)
            if request.method == 'POST':
                form = form_cls(request.form, inital=user._data)
            else:
                form = form_cls(obj=user)
        else:
            user = User()
            form = form_cls(request.form)

        context = {
            "user": user,
            "form": form,
            "create": username is None
        }
        return context

    def get(self, username):
        context = self.get_context(username)
        return render_template('admin/user_details.html', **context)

    def post(self, username):
        context = self.get_context(username)
        form = context.get('form')

        error = None
        if form.validate():
            user = context.get('user')
            form.populate_obj(user)

            user_with_email = User.objects(email=user.email)
            user_with_username = User.objects(username=user.username)

            if len(user_with_email) != 0:
                error = 'Sorry! A user with that email already exists! Try another one.'
            elif len(user_with_username) != 0:
                error = 'Sorry! A user with that username already exists! Try another one.'
            else:
                user.save()
                return redirect(url_for('admin.user_index'))
        return render_template('admin/user_details.html', error=error, **context)

# Register the urls
admin.add_url_rule('/admin/', view_func=UserAdminListView.as_view('user_index'))
admin.add_url_rule('/admin/users/', view_func=UserAdminListView.as_view('user_index'))
admin.add_url_rule('/admin/users/create/', defaults={'username': None}, view_func=UserAdminDetailsView.as_view('user_create'))
admin.add_url_rule('/admin/users/<username>/', view_func=UserAdminDetailsView.as_view('user_edit'))
admin.add_url_rule('/admin/users/<username>/delete/', view_func=UserAdminDeleteView.as_view('user_delete'))

#------------------------
# posts
#------------------------

class PostAdminListView(MethodView):
    decorators = [requires_auth]
    cls = Post

    def get(self):
        posts = self.cls.objects.all()
        return render_template('admin/post_list.html', posts=posts)

class PostAdminDeleteView(MethodView):
    decorators = [requires_auth]

    def get(self, slug):
        post = None
        if slug:
            post = Post.objects.get_or_404(slug=slug)
        else:
            post = None
        return render_template('admin/post_delete.html', post=post)

    def post(self, slug):
        post = Post.objects.get_or_404(slug=slug)
        post.delete()
        return redirect(url_for('admin.index'))

class PostAdminDetailsView(MethodView):

    decorators = [requires_auth]
    # Map post types to models
    class_map = {
        'post': BlogPost,
        'video': Video,
        'image': Image,
        'quote': Quote,
    }

    def get_context(self, slug=None):

        if slug:
            post = Post.objects.get_or_404(slug=slug)
            # Handle old posts types as well
            cls = post.__class__ if post.__class__ != Post else BlogPost
            form_cls = model_form(cls,  exclude=('created_at', 'comments'))
            if request.method == 'POST':
                form = form_cls(request.form, inital=post._data)
            else:
                form = form_cls(obj=post)
        else:
            # Determine which post type we need
            cls = self.class_map.get(request.args.get('type', 'post'))
            post = cls()
            form_cls = model_form(cls,  exclude=('created_at', 'comments'))
            form = form_cls(request.form)
        context = {
            "post": post,
            "form": form,
            "create": slug is None
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('admin/post_details.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            post = context.get('post')
            form.populate_obj(post)
            post.save()

            return redirect(url_for('admin.index'))
        return render_template('admin/post_details.html', **context)

# Register the urls
admin.add_url_rule('/admin/posts/', view_func=PostAdminListView.as_view('index'))
admin.add_url_rule('/admin/posts/create/', defaults={'slug': None}, view_func=PostAdminDetailsView.as_view('create'))
admin.add_url_rule('/admin/posts/<slug>/', view_func=PostAdminDetailsView.as_view('edit'))
admin.add_url_rule('/admin/posts/<slug>/delete/', view_func=PostAdminDeleteView.as_view('delete'))


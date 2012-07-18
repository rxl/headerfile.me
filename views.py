from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from headerfile.models import *
from flask.ext.mongoengine.wtf import model_form

import json

#------------------------
# filters
#------------------------


import re
from jinja2 import evalcontextfilter, Markup, escape, filters

def nl2br(value):
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                          for p in _paragraph_re.split(escape(value)))
    result = Markup(result)
    return result

def contains_choice(this, choice):
    if this:
        this_list = json.loads(this)
        if choice in this_list:
            return True
    return False

filters.FILTERS['contains_choice'] = contains_choice
filters.FILTERS['nl2br'] = nl2br

#------------------------
# users
#------------------------

users = Blueprint('users', __name__, template_folder='templates')

class HomeView(MethodView):
    def get(self):
        return render_template('index.html')

class UserListView(MethodView):
    def get(self):
        users = User.objects.all()
        return render_template('users/list.html', users=users)

class UserDetailsView(MethodView):
    def get(self, username):
        user = User.objects.get_or_404(username=username)

        if hasattr(user, 'industries'):
            try:
                user.industries = json.loads(user.industries)
            except:
                user.industries = None
        if hasattr(user, 'technologies'):
            try:
                user.technologies = json.loads(user.technologies)
            except:
                user.technologies = None

        return render_template('users/details.html', user=user)

class UserEditView(MethodView):
    #decorators = [requires_auth] # only profile's owner can edit profile

    def get_context(self, username=None):
        form_cls = model_form(User, exclude=('created_at', 'websites'))

        if username:
            user = User.objects.get_or_404(username=username)
            if request.method == 'POST':
                form = form_cls(request.form, inital=user._data)
            else:
                form = form_cls(obj=user)
        else:
            user = None
            form = form_cls(request.form)

        context = {
            "user": user,
            "form": form,
            "create": username is None,
            "industry_choices": INDUSTRIES,
            "technology_choices": TECHNOLOGIES
        }
        return context

    def get(self, username):
        context = self.get_context(username)
        if context.get('user') is not None:
            return render_template('users/edit.html', **context)
        return render_template('404.html'), 404

    def post(self, username):
        context = self.get_context(username)
        form = context.get('form')

        if form.validate():
            user = context.get('user')
            form.populate_obj(user)

            if 'industries' in form:
                industries = request.form.getlist('industries[]')
                user.industries = json.dumps(industries)
            if 'technologies' in form:
                technologies = request.form.getlist('technologies[]')
                user.technologies = json.dumps(technologies)

            user.save()

            return redirect(url_for('users.details', username=username))
        return render_template('users/edit.html', **context)

# Register the urls
users.add_url_rule('/', view_func=HomeView.as_view('index'))
users.add_url_rule('/users/', view_func=UserListView.as_view('list'))
users.add_url_rule('/users/<username>/', view_func=UserDetailsView.as_view('details'))
users.add_url_rule('/users/<username>/edit', view_func=UserEditView.as_view('edit'))

#------------------------
# login
#------------------------

from flaskext.oauth import OAuth
from flask import session, flash

TWITTER_APP_ID = 'PXpp9Ny0qj02sCvNfhCOg'
TWITTER_APP_SECRET = '7t7AOFecOjrlQlUP4QNLy9u8YBxzmSA13YyukobLo'
FACEBOOK_APP_ID = '399792966735734'
FACEBOOK_APP_SECRET = 'cf0cf8b405be6255c9f0fbe54133de7b'

oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='http://api.twitter.com/1/',
    request_token_url='http://api.twitter.com/oauth/request_token',
    access_token_url='http://api.twitter.com/oauth/access_token',
    authorize_url='http://api.twitter.com/oauth/authorize',
    consumer_key=TWITTER_APP_ID,
    consumer_secret=TWITTER_APP_SECRET
)
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

@twitter.tokengetter
def get_twitter_token():
    return session.get('twitter_token')

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

class LoginView(MethodView):
    def get(self):
        return render_template('users/login.html')

def pop_session_login():
    session.pop('logged_in', None)
    # logout of twitter
    session.pop('twitter_token', None)
    session.pop('twitter_user', None)
    # logout of facebook
    session.pop('facebook_token', None)

class FacebookLoginView(MethodView):
    def get(self):
        #pop_session_login()
        return facebook.authorize(callback=url_for('users.facebook-authorized',
            next=request.args.get('next'),
            _external=True))

class TwitterLoginView(MethodView):
    def get(self):
        pop_session_login()
        return twitter.authorize(callback=url_for('users.oauth-authorized',
            next=request.args.get('next')))

class LogoutView(MethodView):
    def get(self):
        pop_session_login()
        return redirect(url_for('users.index'))

class FacebookAuthorizedView(MethodView):
    @facebook.authorized_handler
    def get(resp, self):
        next_url = request.args.get('next') or url_for('users.index')
        if resp is None or 'access_token' not in resp:
            flash(u'You could not be signed in.')
            return redirect(next_url)

        session['logged_in'] = True
        session['facebook_token'] = (resp['access_token'], '')
        
        me = facebook.get('/me')
        print me.data
        print me.data['id']
        flash('You were signed in as %s' % me.data['name'])

        return redirect(next_url)

class OAuthAuthorizedView(MethodView):
    @twitter.authorized_handler
    def get(resp, self):
        next_url = request.args.get('next') or url_for('users.index')
        if resp is None or 'oauth_token' not in resp or 'oauth_token_secret' not in resp or 'screen_name' not in resp:
            flash(u'You could not be signed in.')
            return redirect(next_url)

        session['logged_in'] = True
        session['twitter_token'] = (resp['oauth_token'], resp['oauth_token_secret'])
        session['twitter_user'] = resp['screen_name']
        flash('You were signed in as %s' % resp['screen_name'])
        return redirect(next_url)

users.add_url_rule('/login', view_func=LoginView.as_view('login'))
users.add_url_rule('/twitter-login', view_func=TwitterLoginView.as_view('twitter-login'))
users.add_url_rule('/facebook-login', view_func=FacebookLoginView.as_view('facebook-login'))
users.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
users.add_url_rule('/oauth-authorized', view_func=OAuthAuthorizedView.as_view('oauth-authorized'))
users.add_url_rule('/facebook-authorized', view_func=FacebookAuthorizedView.as_view('facebook-authorized'))


#------------------------
# posts
#------------------------

posts = Blueprint('posts', __name__, template_folder='templates')

class ListView(MethodView):

    def get(self):
        posts = Post.objects.all()
        return render_template('posts/list.html', posts=posts)

class DetailView(MethodView):

    form = model_form(Comment, exclude=['created_at'])

    def get_context(self, slug):
        post = Post.objects.get_or_404(slug=slug)
        form = self.form(request.form)

        context = {
            "post": post,
            "form": form
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('posts/details.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            comment = Comment()
            form.populate_obj(comment)

            post = context.get('post')
            post.comments.append(comment)
            post.save()

            return redirect(url_for('posts.details', slug=slug))

        return render_template('posts/details.html', **context)

# Register the urls
posts.add_url_rule('/posts/', view_func=ListView.as_view('list'))
posts.add_url_rule('/posts/<slug>/', view_func=DetailView.as_view('details'))


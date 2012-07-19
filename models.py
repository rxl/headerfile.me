import datetime
from flask import url_for
from headerfile import db

#------------------------
# users
#------------------------

TECHNOLOGIES=(
('python','python'),
('javascript','javascript'),
('ruby','ruby'),
('c','c'),
('c#','c#'),
('php','php'),
('java','java'),
('c++','c++'),
('haskell','haskell'),
('clojure','clojure'),
('coffeescript','coffeescript'),
('objective-c','objective-c'),
('lisp','lisp'),
('perl','perl'),
('scala','scala'),
('scheme','scheme'),
('erlang','erlang'),
('matlab','matlab')
)

INDUSTRIES = (
('advertising', 'advertising'), 
('biotech-life-sciences', 'biotech-life-sciences'),
('ecommerce-retail', 'ecommerce-retail'),
('emerging-markets', 'emerging-markets'), 
('energy-cleantech', 'energy-cleantech'), 
('hardware', 'hardware'),  
('education', 'education'), 
('enterprise-software', 'enterprise-software'),
('finance', 'finance'), 
('gaming-entertainment', 'gaming-entertainment'),
('health-wellness', 'health-wellness'), 
('media-communications', 'media-communications'),
('mobile', 'mobile'), 
('saas', 'saas'),
('search', 'search'), 
('security', 'security'),
('semiconductor', 'semiconductor'),
('social-media', 'social-media')
)

UNIVERSITIES = (('Other', 'Other'),
    ('Princeton University', 'Princeton'),
    ('University of Pennsylvania', 'Penn'),
    ('Cornell University', 'Cornell'),
    ('Columbia University', 'Columbia'),
    ('Harvard University', 'Harvard'),
    ('Stanford University', 'Stanford'),
)

class User(db.DynamicDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    email = db.EmailField(max_length=255, required=True, unique=True)
    password = db.StringField(max_length=255, required=True)
    name = db.StringField(max_length=255, required=True)
    username = db.StringField(max_length=255, required=True, unique=True)
    
    university = db.StringField(max_length=255, required=False, choices=UNIVERSITIES)
    industries = db.StringField(required=False)
    technologies = db.StringField(required=False)

    bio = db.StringField(required=False)

    github = db.URLField(max_length=255, required=False, verify_exists=False)
    blog = db.URLField(max_length=255, required=False, verify_exists=False)
    facebook = db.URLField(max_length=255, required=False, verify_exists=False) 
    twitter = db.URLField(max_length=255, required=False, verify_exists=False)
    linkedin = db.URLField(max_length=255, required=False, verify_exists=False)
    stackoverflow = db.URLField(max_length=255, required=False, verify_exists=False)
    topcoder = db.URLField(max_length=255, required=False, verify_exists=False)

    work = db.StringField(required=False)

    websites = db.ListField(db.EmbeddedDocumentField('Website'))

    image = db.ImageField(size=(800, 600, True), thumbnail_size=(160, 160, True))

    def get_absolute_url(self):
        return url_for('user', kwargs={"username": self.username})

    def __unicode__(self):
        return self.name

    @property
    def post_type(self):
        return self.__class__.__name__

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'username'],
        'ordering': ['-created_at']
    }

class Website(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=255, required=True)
    url = db.URLField(verify_exists=False, required=True)

#------------------------
# posts
#------------------------

class Post(db.DynamicDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))

    def get_absolute_url(self):
        return url_for('post', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.title

    @property
    def post_type(self):
        return self.__class__.__name__

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }

class BlogPost(Post):
    body = db.StringField(required=True)


class Video(Post):
    embed_code = db.StringField(required=True)


class Image(Post):
    image_url = db.StringField(required=True, max_length=255)


class Quote(Post):
    body = db.StringField(required=True)
    author = db.StringField(verbose_name="Author Name", required=True, max_length=255)


class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    body = db.StringField(verbose_name="Comment", required=True)
    author = db.StringField(verbose_name="Name", max_length=255, required=True)


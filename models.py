import datetime
from flask import url_for
from headerfile import db

#------------------------
# users
#------------------------

TECHNOLOGIES=(
('c','c'),
('java','java'),
('objective-c','objective-c'),
('c++','c++'),
('c#','c#'),
('vb.net','vb.net'),
('php','php'),
('python','python'),
('perl','perl'),
('ruby','ruby'),
('javascript','javascript'),
('delphi','delphi'),
('lisp','lisp'),
('pascal','pascal'),
('ada','ada'),
('lua','lua'),
('matlab','matlab'),
('haskell','haskell'),
('erlang','erlang'),
('scala','scala'),
('ocaml','ocaml'),
('scheme','scheme'),
('assembly','assembly'),
('actionscript','actionscript'),
('sql','sql'),
('coffeescript','coffeescript'),
('node.js','node.js'),
('ios','ios'),
('android','android'),
('windows-phone','windows-phone'),
)

INDUSTRIES = (
('Agriculture', 'Agriculture'), 
('Computing & Storage Infrastructure', 'Computing & Storage Infrastructure'), 
('Consumer Internet & Media', 'Consumer Internet & Media'),
('Education', 'Education'),
('Emerging Markets', 'Emerging Markets'),
('Energy/Cleantech', 'Energy/Cleantech'),
('Enterprise Software & SaaS', 'Enterprise Software & SaaS'),
('Financial Technology', 'Financial Technology'),
('Hardware', 'Hardware'),
('Healthcare & Biotech', 'Healthcare & Biotech'),
('Mobile', 'Mobile'),
('Networking Systems', 'Networking Systems'),
('Retail Consumer', 'Retail Consumer'),
('Security', 'Security'),
('Semiconductors', 'Semiconductors'),
('Technology Enabled Services', 'Technology Enabled Services')
)

UNIVERSITIES = (('', ''),
    ('Princeton University', 'Princeton'),
    ('University of Pennsylvania', 'Penn'),
    ('Cornell University', 'Cornell'),
    ('Columbia University', 'Columbia'),
    ('Harvard University', 'Harvard')
)

class User(db.DynamicDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    email = db.EmailField(max_length=255, required=True)
    password = db.StringField(max_length=255, required=True)
    name = db.StringField(max_length=255, required=True)
    username = db.StringField(max_length=255, required=True)
    
    university = db.StringField(max_length=255, required=False, choices=UNIVERSITIES)
    industries = db.StringField(required=False)
    technologies = db.StringField(required=False)

    github = db.StringField(max_length=255, required=False)
    blog = db.StringField(max_length=255, required=False)
    facebook = db.StringField(max_length=255, required=False) 
    twitter = db.StringField(max_length=255, required=False)
    linkedin = db.StringField(max_length=255, required=False)
    stackoverflow = db.StringField(max_length=255, required=False)
    topcoder = db.StringField(max_length=255, required=False)

    bio = db.StringField(required=False)
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


from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config["MONGODB_DB"] = "my_tumble_log"
app.config["SECRET_KEY"] = "KeepThisS3cr3t"

db = MongoEngine(app)

def register_blueprints(app):
    # Prevents circular imports
    from headerfile.views import posts
    from headerfile.admin import admin
    from headerfile.views import users
    app.register_blueprint(posts)
    app.register_blueprint(admin)
    app.register_blueprint(users)

register_blueprints(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
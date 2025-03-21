import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from src.models import db, User, People, Planet, Favorite

class UserAdmin(ModelView):
    column_display_pk = True
    form_columns = ["username", "email"]

class PlanetAdmin(ModelView):
    column_display_pk = True
    form_columns = ["name", "climate", "terrain", "population"]

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(PlanetAdmin(Planet, db.session))

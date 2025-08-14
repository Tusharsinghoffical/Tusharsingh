# home/resources.py

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth.models import User
from .models import Profile

class UserResource(resources.ModelResource):
    first_name = fields.Field(attribute='first_name', column_name='First Name')
    last_name = fields.Field(attribute='last_name', column_name='Last Name')
    email = fields.Field(attribute='email', column_name='Email')
    username = fields.Field(attribute='username', column_name='Username')

    class Meta:
        model = User
        import_id_fields = ['username']
        fields = ('username', 'first_name', 'last_name', 'email')
        export_order = ('username', 'first_name', 'last_name', 'email')


class ProfileResource(resources.ModelResource):
    user = fields.Field(
        column_name='Username',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')
    )
    phone = fields.Field(attribute='phone', column_name='Phone')
    position = fields.Field(attribute='position', column_name='Position')
    address = fields.Field(attribute='address', column_name='Address')

    class Meta:
        model = Profile
        import_id_fields = ['user']
        fields = ('user', 'phone', 'position', 'address')
        export_order = ('user', 'phone', 'position', 'address')

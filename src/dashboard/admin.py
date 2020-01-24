from django.contrib import admin
from users.models import User, UserAdmin
from labs.models import LabEnvironment
from labs.forms import LabEnvironmentAdmin

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(LabEnvironment, LabEnvironmentAdmin)

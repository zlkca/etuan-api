from __future__ import unicode_literals

from django.contrib import admin
# from django.contrib.admin import ModelAdmin
# from django.contrib.auth.admin import UserAdmin

from .models import User
# , Address, Profile, Feedback
# from .forms import AddressAdminForm


# class UserModelAdmin(UserAdmin):
#     model = User

#     fieldsets = UserAdmin.fieldsets + (
#             (None, {'fields': ('type',)}),
#     )

# class AddressModelAdmin(ModelAdmin):
#     model = Address
#     form = AddressAdminForm

admin.site.register(User)
#admin.site.register(Profile)
#admin.site.register(Address)
#admin.site.register(Feedback)

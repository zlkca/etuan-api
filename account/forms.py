from django.forms import Form, ModelChoiceField, CharField
from .models import Province, City

class AddressAdminForm(Form):
    name = CharField(label="Agreement Name", max_length=150, required=True)
    province = ModelChoiceField(label='Addr', queryset=Province.objects.filter(country_code="CN"), required=False)
    city = ModelChoiceField(label='City', queryset=City.objects.filter(province_id=2), required=False)
    def __init__(self, *args, **kwargs):
        super(AddressAdminForm, self).__init__(*args, **kwargs)

from django.forms import ModelForm

from core.models import Trip


class TripModelForm(ModelForm):
    class Meta:
        model = Trip
        fields = '__all__'

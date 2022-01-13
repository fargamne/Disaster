from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView, ListView

from core.forms import TripModelForm
from core.models import Trip


class TripCreateView(CreateView):
    template_name = 'core/trip_create.html'
    form_class = TripModelForm
    queryset = Trip.objects.all()  # <blog>/<modelname>_list.html

    # success_url = '/'

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    # def get_success_url(self):
    #    return '/'


class TripListView(ListView):
    template_name = 'core/Trip_list.html'
    queryset = Trip.objects.all()  # <blog>/<modelname>_list.html


class TripDetailView(DetailView):
    template_name = 'core/Trip_detail.html'

    # queryset = Trip.objects.all()

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Trip, id=id_)


class TripUpdateView(UpdateView):
    template_name = 'core/trip_create.html'
    form_class = TripModelForm

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Trip, id=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


class TripDeleteView(DeleteView):
    template_name = 'core/trip_delete.html'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Trip, id=id_)

    def get_success_url(self):
        return reverse('core:Trip-list')

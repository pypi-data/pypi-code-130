from django.views.generic import DetailView, ListView

from .models import Event


class EventIndex(ListView):
    """
    Index view for events queryset
    """

    model = Event
    context_object_name = "event_index"
    template_name = "events/index.html"
    paginate_by = 8

    def get_queryset(self):
        """
        Override get method here to allow us to filter using tags
        """
        return Event.objects.published(user=self.request.user).order_by("-publish_at")

    def get_context_data(self, **kwargs):
        """
        Update the context with extra args
        """
        context = super().get_context_data(**kwargs)
        context["future_events"] = Event.objects.future(user=self.request.user)
        # We want the most recent past event first here so we reverse the default order
        context["past_events"] = Event.objects.past(user=self.request.user).reverse()
        return context


class EventDetail(DetailView):
    """
    Detail view for an events object
    """

    template_name = "events/detail.html"

    def get_queryset(self):
        """
        Override the default queryset method so that we can access the request.user
        """
        if self.queryset is None:
            return Event.objects.published(user=self.request.user)
        return self.queryset

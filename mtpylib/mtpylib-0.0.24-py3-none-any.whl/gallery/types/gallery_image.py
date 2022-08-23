from attr import fields
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from ..models import GalleryImage
from graphene import relay
User = get_user_model()

class GalleryImageNode(DjangoObjectType):
    class Meta:
        model = GalleryImage
        # fields = ("id", "username", "ingredients")
        # exclude = ("password",)
        # fields=["__all__"]
        filter_fields = {}
        interfaces = (relay.Node, )
        
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            # return queryset.filter(live=True)
            return None
        queryset.filter(uploaded_by_user=info.context.user)
        return queryset

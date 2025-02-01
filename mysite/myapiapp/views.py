from django.contrib.auth.models import Group
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin

from .serializers import GroupSerializer

# Create your views here.
@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({'message': "Hello World!"})

class GroupListView(ListCreateAPIView): #ListModelMixin, GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    # def get(self, request: Request) -> Response:
    #     # groups = Group.objects.all()
    #     # serialized = GroupSerializer(groups, many=True)
    #     # return Response({"group": serialized.data})
    #     return self.list(request)
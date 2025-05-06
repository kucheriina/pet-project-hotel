from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class CatalogIndexView(APIView):
    def get(self, request):
        return Response({"message": "Страница приложения catalog"})
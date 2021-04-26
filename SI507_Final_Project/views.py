from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.html import escape
from django.views import View
from django.shortcuts import render, redirect



class HomeView(View):
    def get(self, request):
        return redirect(reverse_lazy("data:all"))
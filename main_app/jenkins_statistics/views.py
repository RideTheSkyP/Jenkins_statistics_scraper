import os
import json
import datetime
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect, reverse


def index(request):
    return render(request, 'index.html', {})


def test_results(request):
    return render(request, 'test_results.html', {})


def test_failures(request):
    return render(request, 'test_failures.html', {})

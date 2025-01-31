from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from marketplace.models import prodProduct
from django.core.cache import cache
from basket.models import Basket
from .models import Person
from django.shortcuts import render
from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404
# from LOGIN.models import Person as FarmingPerson
# from LOGIN.models import Feed, Booking, Workshop, Group, Member 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
# from .forms import CreateInDiscussion, PersonForm, UserUpdateForm
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.fernet import Fernet
from django.conf import settings
from member.models import Person
# from sharing.models import Feed
from marketplace.models import prodProduct
from basket.models import Basket
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from topic.models import Topic, ApprovedTopic, SuggestedTopic

import json
import os

# Create your views here.

def selectTopic(request):
    person = Person.objects.filter(Email = request.POST.get('Email')).first()
    if request.method == 'POST':
        Topiclist = request.POST.getlist('topic')
        for topic in Topiclist:
            Topic.objects.create(TopicName=topic, Person_fk=person)
        return redirect('Login')
    else:
        return render(request, 'Topic.html', {'person': person})
    
def viewSelectedTopic(request):
    person = Person.objects.filter(Email=request.session['Email'])
    personlist = Person.objects.filter(Email=request.session['Email'])[0]
    topics = Topic.objects.filter(Person_fk=personlist).values('TopicName').distinct()
    topic_list = ApprovedTopic.objects.values('TopicName').distinct()
    return render(request, 'viewTopic.html', {'person': person, 'topics': topics, 'topic_list': topic_list})

def updateSelectedTopic(request):
    person = Person.objects.filter(Email=request.session['Email'])
    if request.method == 'POST':
        personlist = Person.objects.filter(Email=request.session['Email'])[0]
        Topic.objects.filter(Person_fk=personlist).delete()
        Topiclist = request.POST.getlist('topic')
        for topic in Topiclist:
            Topic.objects.create(TopicName=topic, Person_fk=personlist)
        return redirect('ViewProfile')
    else:
        return render(request, 'Topic.html',{'person': person})

def suggestNewTopic(request):
    person = Person.objects.get(Email=request.session['Email'])
    personlist = Person.objects.get(Email=request.session['Email'])
    topics = Topic.objects.filter(Person_fk=personlist).values('TopicName').distinct()
    topic_list = ApprovedTopic.objects.values('TopicName').distinct()
    
    if request.method == 'POST':
        topicName = request.POST.get('topicsuggest')

        # Check if the topic already exists in the TopicList model
        topic_exists = ApprovedTopic.objects.filter(TopicName=topicName).exists()
        if topic_exists:
            messages.error(request, 'Topic already exists..!')
            return render(request, 'viewTopic.html', {'person': person, 'topics': topics, 'topic_list': topic_list})
        else:
            # Check if the topic already exists in the SuggestedTopic model
            topic_exists = SuggestedTopic.objects.filter(TopicName=topicName).exists()
            if topic_exists:
                messages.error(request, 'Topic already suggested..!')
                return render(request, 'viewTopic.html', {'person': person, 'topics': topics, 'topic_list': topic_list})
            else:
                # Create a new topic suggestion
                SuggestedTopic.objects.create(TopicName=topicName, Person_fk=personlist)
                messages.success(request, topicName + ' has been suggested successfully..!')
                return render(request, 'viewTopic.html', {'person': person, 'topics': topics, 'topic_list': topic_list})
    else:
        return render(request, 'Topic.html', {'person': person})
    
def managetopic(request):
    person = Person.objects.get(Email=request.session['Email'])
    suggestT = SuggestedTopic.objects.all()
    topics = ApprovedTopic.objects.all()

    if request.method == 'POST':
        stat = request.POST.get('status')
        topicName = request.POST.get('topicName')

        if stat == 'Approve':
            topic_exists = ApprovedTopic.objects.filter(TopicName=topicName).exists()
            if topic_exists:
                SuggestedTopic.objects.filter(TopicName=topicName).delete()
                messages.success(request, 'Topic is already approved and exists in the Topic Database!')
            else:
                ApprovedTopic.objects.create(TopicName=topicName)
                SuggestedTopic.objects.filter(TopicName=topicName).delete()
                messages.success(request, 'Topic approved successfully!')
        
        elif stat == 'Reject':
            SuggestedTopic.objects.filter(TopicName=topicName).delete()
            messages.success(request, 'Topic rejected successfully!')
        
        elif stat == 'Delete':
            ApprovedTopic.objects.filter(TopicName=topicName).delete()
            Topic.objects.filter(TopicName=topicName).delete()
            messages.success(request, 'Topic deleted successfully!')

        elif stat == 'Add':
            topic_exists = ApprovedTopic.objects.filter(TopicName=topicName).exists()
            if topic_exists:
                messages.error(request, 'Topic name already exists in Approved Topics table!')
            else:
                ApprovedTopic.objects.create(TopicName=topicName)
                messages.success(request, 'New topic added successfully!')

        # Redirect to the same page after processing the form submission
        return redirect('topic:Managetopic')

    return render(request, 'ManageTopicAdmin.html', {'person': person, 'suggestT': suggestT, 'topics': topics})
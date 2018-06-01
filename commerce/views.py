import logging

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
#from django.core.urlresolvers import reverse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# from .forms import ItemForm

logger = logging.getLogger(__name__)


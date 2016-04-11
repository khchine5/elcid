import json
import logging

from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden
from django.conf import settings
from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response
from elcid.gloss_api import bulk_create_from_gloss_response
from opal.core.api import OPALRouter


class GlossEndpointApi(viewsets.ViewSet):
    base_name = 'glossapi'

    def create(self, request):
        request_data = json.loads(request.data)
        bulk_create_from_gloss_response(request_data)
        return Response("ok")


router = OPALRouter()
router.register('glossapi', GlossEndpointApi)

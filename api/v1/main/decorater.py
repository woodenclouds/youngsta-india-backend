from rest_framework.permissions import BasePermission
from django.http.response import HttpResponseRedirect, HttpResponse
import json
from rest_framework.response import Response
from rest_framework import status


def group_required(group_names):
    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                if not bool(request.user.groups.filter(name__in=group_names)) or request.user.is_superuser:
                    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                        response_data = {
                            'status': 'false',
                            'stable': 'true',
                            'title': 'Permission Denied',
                            'message': 'You have no permission to do this action.',
                        }
                        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
                    else:
                        context = {
                            'title': 'Permission Denied',
                        }
                        response_data  = {
                            "StatusCode":6001,
                            "data":{
                                "message":"you dont have access to this api"
                            }
                        }
                        return Response({'app_data': response_data}, status=status.HTTP_200_OK)
            return view_method(request, *args, **kwargs)

        return _arguments_wrapper

    return _method_wrapper
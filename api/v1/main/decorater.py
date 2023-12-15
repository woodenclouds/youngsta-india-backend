from rest_framework.permissions import BasePermission
from django.http.response import HttpResponseRedirect, HttpResponse
import json



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
                        return HttpResponse('<h1>Permission Denied</h1>')
            return view_method(request, *args, **kwargs)

        return _arguments_wrapper

    return _method_wrapper
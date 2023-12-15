from rest_framework import permissions
import requests
from django.conf import settings
from django.shortcuts import render

import json
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from rest_framework.exceptions import PermissionDenied
from firebase_admin import messaging,credentials
import firebase_admin


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        # message += "%s : %s | " %(key,error_message)
        message += f"{key} - {error_message} | "
    return message[:-3]


class Permissions(permissions.BasePermission):

    def is_plant(self, request, view):
        user = request.user
        is_plant = user.groups.filter(name='Plant')
        return is_plant


def get_auto_id(model):
    # auto_id = 1
    # latest_auto_id =  model.objects.all().order_by("-created_at")[:1]
    # if latest_auto_id:
    #     for auto in latest_auto_id:
    #         auto_id = auto.auto_id + 1
    auto_id = model.objects.all().count()+1
    return auto_id


# class GroupRequiredMixin(UserPassesTestMixin):
#     group_required = None
#     # print(UserPassesTestMixin,"------------------------------------------------------------------")

#     def test_func(self):
#         user = self.request.user
#         if not user.is_authenticated:
#             return False
#         if self.group_required is None:
#             return True
#         if isinstance(self.group_required, str):
#             groups = [self.group_required]
#             print(groups,"====================================================")
#         elif isinstance(self.group_required, (list, tuple)):
#             groups = self.group_required
#         else:
#             raise ValueError("Invalid group_required attribute")
#         return user.groups.filter(name__in=groups).exists()

#     # def handle_no_permission(self):
#     #     raise PermissionDenied()

def get_first_letters(string):
    words = string.split()

    if len(words) == 1:
        code = words[0][0].upper() + words[0][-1].upper()
    else:
        code = "".join(word[0] for word in string.split()).upper()

    return code



def send_notification(token,title,message,device_type):
    # token = "ffBIYT4tzUREh7-NputjPh:APA91bFAjm5y_jUg1e_kDDZYfOiXhsc_suEWNmNV8CZDCwK1L2aoEB4LY0mhDIun2K8C43-0fhk5HIXHGDviPOgthAs8WkyJO_a0Q-MdmZQLYARI0cRT-oVtkNJVaOuLAIGpCEuDyl-Z"
    print(settings.FIREBASE_CREDENTIALS)
    if not firebase_admin._apps:
        credentials = firebase_admin.credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(credentials,options={'projectId': 'jeeva-77175'})
        firebase_admin.get_app()
    else:
         firebase_admin.get_app()
    multicast_message = messaging.MulticastMessage(
    tokens=[token],
    notification=messaging.Notification(title, message) if device_type.lower() == "android" else None,
        data={
            "title": title,
            "body": message,
            "type": "DATA",
        },
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    content_available=1
                )
            )
        )
    )
    message_res = messaging.send_multicast(
            multicast_message)
    return message_res
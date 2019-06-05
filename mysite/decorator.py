from study.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
import pdb
def login_require(func):
    def wrappped_func(request, *args, **kwargs):
        headers = request.headers
        Authorization = headers.get('Authorization')
        user = User.objects.filter(id=Authorization).first()
        if user:
            request.user = user
            return func(request, *args, **kwargs)
        return JsonResponse({'error': '未登录'}, safe=False)
    return wrappped_func


def login_check(func):
    def wrappped_func(request, *args, **kwargs):
        headers = request.headers
        Authorization = headers.get('Authorization')
        request.user = User.objects.filter(id=Authorization).first()
        return func(request, *args, **kwargs)
    return wrappped_func
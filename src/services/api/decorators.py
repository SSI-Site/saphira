import datetime
import json
from functools import wraps

import firebase_admin
import jwt
from django.conf import settings
from django.http import JsonResponse
from firebase_admin import auth
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

if not firebase_admin._apps:
    firebase_admin.initialize_app()

def firebase_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                decoded_token = auth.verify_id_token(token)
                user_id = decoded_token.get('uid')
                token_email = decoded_token.get('email')
                name = decoded_token.get('name')

                body = json.loads(request.body)
                email = body.get('email')
                
                if str(token_email) != str(email):
                    return JsonResponse({'error': 'Unauthorized access.'}, status=403)

                jwt_token = AccessToken()
                jwt_token['user_id'] = user_id
                jwt_token['email'] = token_email
                jwt_token['name'] = name
                jwt_token.set_exp(lifetime=datetime.timedelta(minutes=5))

                request.META['HTTP_AUTHORIZATION'] = f'Bearer {str(jwt_token)}'

            except Exception as e:
                return JsonResponse({'error': 'Invalid Firebase token.'}, status=401)

            return view_func(request, *args, **kwargs)

        return JsonResponse({'error': 'Authorization header missing or invalid.'}, status=401)

    return _wrapped_view


def student_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                request.user = decoded_token
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired.'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token.'}, status=401)

            student_id = kwargs.get('student_id')
            user_id = request.user.get('user_id')

            if student_id and user_id:
                if str(student_id) == str(user_id):
                    return view_func(request, *args, **kwargs)
                else:
                    return JsonResponse({'error': 'Unauthorized access.'}, status=403)

            return JsonResponse({'error': 'Invalid ID or token.'}, status=400)

        return JsonResponse({'error': 'Authorization header missing or invalid.'}, status=401)

    return _wrapped_view


def admin_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return JsonResponse({'detail': 'Acesso exclusivo da CO-SSI.'}, status=403)
    return _wrapped_view
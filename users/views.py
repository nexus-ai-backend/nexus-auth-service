from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate




class UserRegistrationView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        msg = "This API Endpoint is for registering new user."
        User = get_user_model()
        uers = User.objects.all()
        serializers = UserRegistrationSerializers(uers, many=True)
        resp = {
            "message" : msg,
            "users" : serializers.data
        }

        return Response(
            resp,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        data = UserRegistrationSerializers(data=request.data)
        data.is_valid(raise_exception=True)
        user = data.save()

        return Response(
            UserRegistrationSerializers(user).data,
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail" : "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh_token = RefreshToken.for_user(user)

        return Response(
            {
                "access_token": str(refresh_token.access_token),
                "refresh_token": str(refresh_token)
            },
            status=status.HTTP_200_OK,
        )


class CurrentUserView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            }
        )

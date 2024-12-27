from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from accounts.serializers import BankAccountSerializer, BatchAccountCreationSerializer
from rest_framework.permissions import AllowAny
from accounts.utils import send_otp_via_email
from accounts.models import CustomUser, BankAccount
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model
from pytz import all_timezones

User = get_user_model()



class BankAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BankAccountSerializer

    def get(self, request):
        """Retrieve all accounts of the logged-in user."""
        accounts = BankAccount.objects.filter(user=request.user)
        #accounts =BankAccount.objects.prefetch_related('transactions').filter(user=request.user)

        serializer = BankAccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new bank account for the logged-in user."""
        serializer = BankAccountSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BatchAccountCreationView(APIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = BatchAccountCreationSerializer

    def post(self, request):
        """Admin batch account creation."""
        serializer = BatchAccountCreationSerializer(data=request.data)
        if serializer.is_valid():
            accounts_data = serializer.validated_data['accounts']
            created_accounts = []
            for account_data in accounts_data:
                user = User.objects.filter(username=account_data.get('username')).first()
                if user:
                    account = BankAccount.objects.create(user=user)
                    created_accounts.append(BankAccountSerializer(account).data)
            return Response({'created_accounts': created_accounts}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

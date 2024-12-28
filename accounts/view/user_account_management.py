from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from accounts.serializers import RegisterSerializer, LoginSerializer, BankAccountSerializer, BatchAccountCreationSerializer, UpdateTimeZoneSerializer, VerifyOTPSerializer
from rest_framework.permissions import AllowAny
from accounts.utils import send_otp_via_email
from accounts.models import CustomUser, BankAccount
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model
from pytz import all_timezones

User = get_user_model()




class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginViewWithKeys(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            # Generate OTP
            user.generate_otp()
            send_otp_via_email(user.email, user.otp)
            return Response({'message': 'OTP sent to your email'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)




class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        username = request.data.get('username')
        otp = request.data.get('otp')

        try:
            user = CustomUser.objects.get(username=username)
            print(user)
            if user.otp == otp and user.otp_created_at > now() - timedelta(minutes=5):
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



class UpdateTimezoneView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateTimeZoneSerializer

    def post(self, request):
        timezone = request.data.get('timezone')
        print(timezone)
        print(type(timezone))
        if timezone not in all_timezones:
            return Response({'error': 'Invalid time zone'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.timezone = timezone
        request.user.save()
        return Response({'message': 'Time zone updated successfully'}, status=status.HTTP_200_OK)




class BankAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retrieve all accounts of the logged-in user."""
        accounts = BankAccount.objects.filter(user=request.user)
        #accounts =BankAccount.objects.prefetch_related('transactions').filter(user=request.user)

        serializer = BankAccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new bank account for the logged-in user."""
        serializer = BankAccountSerializer(data=request.data)
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

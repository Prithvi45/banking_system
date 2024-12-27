from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import BankAccount, Transaction, Tenant
from django.contrib.auth.models import Group, Permission

from pytz import timezone
from django.utils.timezone import localtime

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        #print("cccc")
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields=['name']

class BankAccountSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(required=False)

    class Meta:
        model = BankAccount
        fields = ['id', 'account_number', 'balance', 'created_at','tenant']
        read_only_fields = ['account_number', 'created_at','tenant']

    def create(self, validated_data):
        tenant_data = validated_data.pop('tenant', None)  # Extract tenant data if provided
        user = self.context['request'].user  # Get the user from the request context
        validated_data.pop('user', None)

        # Create the bank account
        bank_account = BankAccount.objects.create(user=user, **validated_data)

        # If tenant data is provided, handle it
        if tenant_data:
            print(tenant_data)
            tenant,created = Tenant.objects.get_or_create(**tenant_data)
            print(tenant)
            print(type(tenant))
            bank_account.tenant = tenant
            bank_account.save()

        return bank_account


class BatchAccountCreationSerializer(serializers.Serializer):
    accounts = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=255)
        )
    )


class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['account','amount']


class TransferTransactionSerializer(serializers.Serializer):
    from_account = serializers.CharField()
    to_account = serializers.CharField()
    amount = serializers.CharField()

class UpdateTimeZoneSerializer(serializers.Serializer):
    timezone = serializers.CharField()

class VerifyOTPSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField()

class CreateDeleteRoleSerializer(serializers.Serializer):
    name = serializers.CharField()



class TransactionSerializer(serializers.ModelSerializer):
    related_account_number = serializers.SerializerMethodField()
    local_created_at = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'account', 'transaction_type', 'amount', 'created_at', 'related_account', 'related_account_number','local_created_at'
        ]
        read_only_fields = ['created_at']

    def get_related_account_number(self, obj):
        """Get the account number of the related account (for transfers)."""
        return obj.related_account.account_number if obj.related_account else None

    def get_local_created_at(self, obj):
        user_timezone = timezone(self.context['request'].user.timezone)
        return localtime(obj.created_at, user_timezone)    



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

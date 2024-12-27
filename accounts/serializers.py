from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import BankAccount, Transaction, Tenant
from django.contrib.auth.models import Group, Permission

from pytz import timezone
from django.utils.timezone import localtime

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name','timezone']

    def create(self, validated_data):
        print("cccc")
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            timezone=validated_data.get('timezone', 'UTC'),
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
        read_only_fields = ['account_number', 'created_at']



class BatchAccountCreationSerializer(serializers.Serializer):
    accounts = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=255)
        )
    )



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

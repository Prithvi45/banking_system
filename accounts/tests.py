from django.test import TestCase

# Create your tests here.

from accounts.models import CustomUser, BankAccount
from unittest.mock import patch
from decimal import Decimal
from accounts.utils import convert_currency
from accounts.serializers import RegisterSerializer
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken



#Section 1 - Unit Testing  - Bank Account and Currency Conversion

class BankAccountModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password123")

    def test_account_number_is_unique(self):
        account1 = BankAccount.objects.create(user=self.user, balance=100.00)
        account2 = BankAccount.objects.create(user=self.user, balance=200.00)
        self.assertNotEqual(account1.account_number, account2.account_number)
        print("Test Case 1 Passed")

    def test_balance_updates_correctly(self):
        account = BankAccount.objects.create(user=self.user, balance=100.00)
        account.balance += 50.00
        account.save()
        self.assertEqual(account.balance, 150.00)
        print("Test Case 2 Passed")



class CurrencyConversionTest(TestCase):
    @patch('accounts.utils.requests.get')
    def test_currency_conversion(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'rates': {'EUR': 0.9, 'GBP': 0.8}
        }

        converted = convert_currency(Decimal('100'), 'USD', 'EUR')
        self.assertAlmostEqual(converted, Decimal('90.00') * Decimal('1.01'))  # Includes 1% spread
        print("Test Case 3 Passed")

    def test_same_currency_conversion(self):
        converted = convert_currency(Decimal('100'), 'USD', 'USD')
        self.assertEqual(converted, Decimal('100'))
        print("Test Case 4 Passed")



# Section - Serializer and Validation testing

class RegisterSerializerTest(TestCase):
    def test_valid_data(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'timezone': 'UTC'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        print("Test Case 5 Passed")

    def test_invalid_data(self):
        data = {'username': '', 'email': 'invalid-email'}
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('email', serializer.errors)
        print("Test Case 6 Passed")




# Section3 - Integration Testing to deposit, withdraw and transfer

class TransactionIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")
        self.account = BankAccount.objects.create(user=self.user, balance=100.00)
        # Obtain JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        # Include the token in the Authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')


    def test_deposit_money(self):
        url = reverse('deposit') 
        response = self.client.post(url, {
            'account': self.account.id,
            'amount': 50.00
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 150.00)
        print("Test Case 7 Passed")

    def test_withdraw_money(self):
        url = reverse('withdraw')
        response = self.client.post(url, {
            'account': self.account.id,
            'amount': 50.00
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 50.00)
        print("Test Case 8 Passed")

    def test_invalid_transfer(self):
        url = reverse('transfer')
        response = self.client.post(url, {
            'from_account': self.account.id,
            'to_account': 999,  # Invalid account
            'amount': 50.00
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("Test Case 9 Passed")


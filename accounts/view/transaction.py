from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts.models import BankAccount, Transaction
from accounts.serializers import TransactionSerializer, CreateTransactionSerializer, TransferTransactionSerializer
from decimal import Decimal
from django.utils.dateparse import parse_date
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from accounts.utils import convert_currency
from django.core.cache import cache
from accounts.pagination import TransactionPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter

import logging
logger = logging.getLogger(__name__)


class DepositView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateTransactionSerializer

    def post(self, request):
        account_id = request.data.get('account')
        amount = Decimal(request.data.get('amount'))  # Convert to Decimal
        try:
            account = BankAccount.objects.get(id=account_id, user=request.user)
            if amount <= 0:
                return Response({'error': 'Amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update account balance
            account.balance += amount
            account.save()

            # Create transaction record
            Transaction.objects.create(account=account, transaction_type='deposit', amount=amount)

            return Response({'message': 'Deposit successful'}, status=status.HTTP_200_OK)
        except BankAccount.DoesNotExist:
            return Response({'error': 'Account not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)



class WithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateTransactionSerializer

    def post(self, request):
        account_id = request.data.get('account')
        amount = Decimal(request.data.get('amount'))  # Convert to Decimal
        try:
            account = BankAccount.objects.get(id=account_id, user=request.user)
            if amount <= 0 or amount > account.balance:
                return Response({'error': 'Invalid withdrawal amount'}, status=status.HTTP_400_BAD_REQUEST)

            # Update account balance
            account.balance -= amount
            account.save()

            # Create transaction record
            Transaction.objects.create(account=account, transaction_type='withdraw', amount=amount)

            return Response({'message': 'Withdrawal successful'}, status=status.HTTP_200_OK)
        except BankAccount.DoesNotExist:
            return Response({'error': 'Account not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)



class TransferView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransferTransactionSerializer

    def post(self, request):
        from_account_id = request.data.get('from_account')
        to_account_id = request.data.get('to_account')
        amount = Decimal(request.data.get('amount'))  # Convert to Decimal
        try:
            from_account = BankAccount.objects.get(id=from_account_id, user=request.user)
            to_account = BankAccount.objects.get(id=to_account_id)

            if from_account == to_account:
                return Response({'error': 'Cannot transfer to the same account'}, status=status.HTTP_400_BAD_REQUEST)
            if amount <= 0 or amount > from_account.balance:
                return Response({'error': 'Invalid transfer amount'}, status=status.HTTP_400_BAD_REQUEST)

            # Update balances
            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()

            # Create transaction records
            Transaction.objects.create(account=from_account, transaction_type='transfer', amount=amount, related_account=to_account)
            Transaction.objects.create(account=to_account, transaction_type='transfer', amount=amount, related_account=from_account)

            return Response({'message': 'Transfer successful'}, status=status.HTTP_200_OK)
        except BankAccount.DoesNotExist:
            return Response({'error': 'Account not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)




class TransactionHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination

    def get_queryset(self):
        account_id = self.request.query_params.get('account')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        transaction_type = self.request.query_params.get('type')

        # Get all transactions for the specified account
        queryset = Transaction.objects.filter(account__user=self.request.user)

        #Task 9.4 - we can select relevant columns to display incase we have 100s of cloumns as below
        #queryset = Transaction.objects.only('id','amount','transaction_type','created_at')


        if account_id:
            queryset = queryset.filter(account_id=account_id)

        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        if start_date:
            start_date = parse_date(start_date)
            queryset = queryset.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset



class ExternalTransferView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransferTransactionSerializer


    def post(self, request):
        from_account_id = request.data.get('from_account')
        to_account_id = request.data.get('to_account')
        amount = Decimal(request.data.get('amount'))  # Convert to Decimal

        try:
            from_account = BankAccount.objects.get(id=from_account_id, user=request.user)
            to_account = BankAccount.objects.get(id=to_account_id)

            if from_account == to_account:
                return Response({'error': 'Cannot transfer to the same account'}, status=status.HTTP_400_BAD_REQUEST)
            if amount <= 0 or amount > from_account.balance:
                return Response({'error': 'Invalid transfer amount'}, status=status.HTTP_400_BAD_REQUEST)

            # Convert currency if necessary
            converted_amount = convert_currency(amount, from_account.currency, to_account.currency)

            # Update balances
            from_account.balance -= amount
            to_account.balance += converted_amount
            from_account.save()
            to_account.save()

            # Create transaction records
            Transaction.objects.create(account=from_account, transaction_type='transfer', amount=amount, related_account=to_account)
            Transaction.objects.create(account=to_account, transaction_type='transfer', amount=converted_amount, related_account=from_account)

            return Response({'message': 'Transfer successful'}, status=status.HTTP_200_OK)
        except BankAccount.DoesNotExist:
            return Response({'error': 'Account not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




class TransactionHistoryCachedView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer


    @extend_schema(
        summary="Retrieve transaction history",
        description="Retrieve transaction history filtered by account ID.",
        parameters=[
            OpenApiParameter(
                name="account",
                description="Account ID for filtering transactions",
                required=True,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: "Transaction History Retrieved", 400: "Invalid Request"}
    )
    def get_queryset(self):
        account_id = self.request.query_params.get('account')
        if not account_id:
            return Transaction.objects.none()  # No account specified, return empty queryset

        cache_key = f'transactions_{account_id}'

        # Check cache for transaction IDs
        transaction_ids = cache.get(cache_key)
        if not transaction_ids:
            # Cache miss: Fetch data from the database
            transactions = Transaction.objects.filter(account_id=account_id).select_related('account')
            transaction_ids = list(transactions.values_list('id', flat=True))  # Store IDs in the cache
            cache.set(cache_key, transaction_ids, timeout=300)
        else:
            logger.info(f"Cache hit for {cache_key}")

        # Return QuerySet using IDs
        return Transaction.objects.filter(id__in=transaction_ids)



#Test Redis connection
#from django.core.cache import cache
#cache.set('test_key', 'test_value', timeout=30)
#print(cache.get('test_key'))  # Should print 'test_value'

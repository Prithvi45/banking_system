from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts.models import CustomUser, BankAccount, Transaction
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date


class AdminReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Enable this for custom date range filtering
        #start_date = request.query_params.get('start_date')
        #end_date = request.query_params.get('end_date')
        #transactions = Transaction.objects.filter(created_at__date__gte=parse_date(start_date), created_at__date__lte=parse_date(end_date))


        # Total users
        total_users = CustomUser.objects.count()

        # Total accounts
        total_accounts = BankAccount.objects.count()

        # Total balance across all accounts
        total_balance = BankAccount.objects.aggregate(total=Sum('balance'))['total'] or 0.00

        # Total transactions
        total_transactions = Transaction.objects.count()

        # Transactions breakdown by type
        transaction_breakdown = Transaction.objects.values('transaction_type').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )

        # Top 5 users by balance
        top_users = BankAccount.objects.values('user__username').annotate(total_balance=Sum('balance')).order_by('-total_balance')[:5]

        inactive_accounts = BankAccount.objects.filter(balance=0).count()


        return Response({
            'total_users': total_users,
            'total_accounts': total_accounts,
            'total_balance': total_balance,
            'total_transactions': total_transactions,
            'transaction_breakdown': list(transaction_breakdown), 
            'top_users': top_users,
            'inactive_accounts':inactive_accounts}, status=status.HTTP_200_OK)


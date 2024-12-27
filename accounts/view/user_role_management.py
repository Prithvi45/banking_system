from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import Group
from accounts.serializers import GroupSerializer
from accounts.models import CustomUser

class RoleView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """List all roles"""
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new role"""
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Delete a role"""
        role_name = request.data.get('name')
        group = Group.objects.filter(name=role_name).first()
        if group:
            group.delete()
            return Response({'message': f'Role "{role_name}" deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'error': f'Role "{role_name}" not found'}, status=status.HTTP_404_NOT_FOUND)



class UserRoleView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """Assign a role to a user"""
        username = request.data.get('username')
        role_name = request.data.get('role')
        try:
            user = CustomUser.objects.get(username=username)
            user.add_role(role_name)
            return Response({'message': f'Role "{role_name}" assigned to user "{username}"'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': f'User "{username}" not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """Remove a role from a user"""
        username = request.data.get('username')
        role_name = request.data.get('role')
        try:
            user = CustomUser.objects.get(username=username)
            user.remove_role(role_name)
            return Response({'message': f'Role "{role_name}" removed from user "{username}"'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': f'User "{username}" not found'}, status=status.HTTP_404_NOT_FOUND)



class PermissionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """List all permissions"""
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        


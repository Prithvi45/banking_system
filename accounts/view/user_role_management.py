from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import Group, Permission
from accounts.serializers import GroupSerializer, RoleDeleteSerializer, RoleAssignSerializer, PermissionSerializer, PermissionAssignSerializer
from accounts.models import CustomUser
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view

class RoleView(APIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = GroupSerializer

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
        return Response(serializer.errors, status=status.HTTP_401_BAD_REQUEST)

    def delete(self, request):
        """Delete a role"""
        serializer = RoleDeleteSerializer(data=request.data)
        if serializer.is_valid():
            role_name = serializer.validated_data['name']
            group = Group.objects.filter(name=role_name).first()
            group.delete()
            return Response({'message': f'Role "{role_name}" deleted successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserRoleView(APIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = RoleAssignSerializer

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
        



# Assign or remove permissions for a user or group
class AssignPermissionView(APIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = PermissionAssignSerializer

    def post(self, request):
        """Assign a permission to a user or group"""
        serializer = PermissionAssignSerializer(data=request.data)
        if serializer.is_valid():
            target_type = serializer.validated_data['target_type']
            target_name = serializer.validated_data['target_name']
            permission_codename = serializer.validated_data['permission_codename']

            try:
                permission = Permission.objects.get(codename=permission_codename)
            except Permission.DoesNotExist:
                return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)

            if target_type == 'user':
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(username=target_name)
                    user.user_permissions.add(permission)
                    return Response({'message': f'Permission "{permission_codename}" assigned to user "{target_name}"'}, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({'error': f'User "{target_name}" not found'}, status=status.HTTP_404_NOT_FOUND)

            elif target_type == 'group':
                try:
                    group = Group.objects.get(name=target_name)
                    group.permissions.add(permission)
                    return Response({'message': f'Permission "{permission_codename}" assigned to group "{target_name}"'}, status=status.HTTP_200_OK)
                except Group.DoesNotExist:
                    return Response({'error': f'Group "{target_name}" not found'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'error': 'Invalid target type'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Remove a permission from a user or group"""
        serializer = PermissionAssignSerializer(data=request.data)
        if serializer.is_valid():
            target_type = serializer.validated_data['target_type']
            target_name = serializer.validated_data['target_name']
            permission_codename = serializer.validated_data['permission_codename']

            try:
                permission = Permission.objects.get(codename=permission_codename)
            except Permission.DoesNotExist:
                return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)

            if target_type == 'user':
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(username=target_name)
                    user.user_permissions.remove(permission)
                    return Response({'message': f'Permission "{permission_codename}" removed from user "{target_name}"'}, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({'error': f'User "{target_name}" not found'}, status=status.HTTP_404_NOT_FOUND)

            elif target_type == 'group':
                try:
                    group = Group.objects.get(name=target_name)
                    group.permissions.remove(permission)
                    return Response({'message': f'Permission "{permission_codename}" removed from group "{target_name}"'}, status=status.HTTP_200_OK)
                except Group.DoesNotExist:
                    return Response({'error': f'Group "{target_name}" not found'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'error': 'Invalid target type'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

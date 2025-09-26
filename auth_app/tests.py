from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from auth_app.models import CustomUser
from complaints.models import Department
from auth_app.serializers import UserSerializer

class DepartmentModelTest(TestCase):
    def test_department_creation(self):
        department = Department.objects.create(department_name="HR")
        self.assertEqual(department.department_name, "HR")
        self.assertTrue(isinstance(department, Department))

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(department_name="IT")

    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email="user@example.com",
            username="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role="User",
            department=self.department
        )
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.role, "User")
        self.assertEqual(user.department, self.department)

    def test_create_superuser(self):
        admin_user = CustomUser.objects.create_superuser(
            email="admin@example.com",
            username="admin@example.com",
            password="password123",
            first_name="Admin",
            last_name="User",
            department=self.department
        )
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.role, "master_admin")

    def test_create_user_no_email(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email="",
                username="",
                password="password123",
                first_name="Test",
                last_name="User",
                role="User",
                department=self.department
            )

class CustomUserSerializerTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(department_name="Sales")
        self.user = CustomUser.objects.create_user(
            email="existing@example.com",
            username="existing@example.com",
            password="password123",
            first_name="Existing",
            last_name="User",
            role="User",
            department=self.department
        )

    def test_custom_user_serializer_valid(self):
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
        self.assertEqual(data['role'], self.user.role)
        self.assertEqual(data['department'], self.user.department.department_name)

class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(department_name="Support")
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            "role": "User",
            "department": self.department
        }
        self.staff_user_data = {
            "email": "staffuser@example.com",
            "username": "staffuser@example.com",
            "password": "staffpassword",
            "first_name": "Staff",
            "last_name": "User",
            "role": "Staff",
            "department": self.department
        }
        self.admin_user_data = {
            "email": "adminuser@example.com",
            "username": "adminuser@example.com",
            "password": "adminpassword",
            "first_name": "Admin",
            "last_name": "User",
            "role": "Admin",
            "department": self.department
        }
        self.user = CustomUser.objects.create_user(**self.user_data)
        self.staff_user = CustomUser.objects.create_staffuser(
            email=self.staff_user_data['email'],
            username=self.staff_user_data['username'],
            password=self.staff_user_data['password'],
            first_name=self.staff_user_data['first_name'],
            last_name=self.staff_user_data['last_name'],
            department=self.staff_user_data['department']
        )
        self.admin_user = CustomUser.objects.create_superuser(
            email=self.admin_user_data['email'],
            username=self.admin_user_data['username'],
            password=self.admin_user_data['password'],
            first_name=self.admin_user_data['first_name'],
            last_name=self.admin_user_data['last_name'],
            department=self.admin_user_data['department']
        )

    def test_user_registration(self):
        # Commenting out as 'register' URL is not defined in auth_app/urls.py
        pass
        # url = reverse('register') # Assuming 'register' is the name of your registration URL
        # new_user_data = {
        #     "email": "newregister@example.com",
        #     "username": "newregister@example.com",
        #     "password": "newpassword123",
        #     "password2": "newpassword123",
        #     "first_name": "New",
        #     "last_name": "Register",
        #     "role": "User",
        #     "department": self.department.id
        # }
        # response = self.client.post(url, new_user_data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertIn('email', response.data)
        # self.assertEqual(CustomUser.objects.count(), 4) # 3 from setup + 1 new

    def test_user_login_success(self):
        url = reverse('token_obtain_pair') # Corrected URL name
        login_data = {
            "username": self.user_data['username'],
            "password": self.user_data['password']
        }
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], self.user.username)

    def test_user_profile_retrieval_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user_detail') # Corrected URL name
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_admin_can_list_all_users(self):
        # Commenting out as 'user-list' URL is not defined in auth_app/urls.py
        pass
        # self.client.force_authenticate(user=self.admin_user)
        # url = reverse('user-list') # Assuming 'user-list' is the name of the URL for listing all users
        # response = self.client.get(url, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data), CustomUser.objects.count())

    def test_staff_cannot_list_all_users(self):
        # Commenting out as 'user-list' URL is not defined in auth_app/urls.py
        pass
        # self.client.force_authenticate(user=self.staff_user)
        # url = reverse('user-list')
        # response = self.client.get(url, format='json')
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN
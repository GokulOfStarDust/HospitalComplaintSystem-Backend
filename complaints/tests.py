from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from auth_app.models import CustomUser
from complaints.models import Complaint, Department
from complaints.serializers import ComplaintSerializer

class DepartmentComplaintModelTest(TestCase):
    def test_department_creation(self):
        department = Department.objects.create(department_name="Customer Service")
        self.assertEqual(department.department_name, "Customer Service")
        self.assertTrue(isinstance(department, Department))

class ComplaintModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(department_name="HR")
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            username="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role="User",
            department=self.department
        )
        self.staff = CustomUser.objects.create_staffuser(
            email="staff@example.com",
            username="staff@example.com",
            password="password123",
            first_name="Test",
            last_name="Staff",
            department=self.department
        )



    def test_complaint_default_status(self):
        complaint = Complaint.objects.create(
            submitted_by=self.user.email,
            issue_type="New Issue",
            description="Description of new issue.",
            assigned_department=self.department,
        )
        self.assertEqual(complaint.status, "open")

class ComplaintSerializersTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(department_name="IT")
        self.room = Room.objects.create(
            bed_no="101",
            room_no="A101",
            Block="A",
            Floor_no=1,
            ward="General",
            speciality="General",
            room_type="Standard",
            status="active"
        )
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            username="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role="User",
            department=self.department
        )
        self.staff = CustomUser.objects.create_staffuser(
            email="staff@example.com",
            username="staff@example.com",
            password="password123",
            first_name="Test",
            last_name="Staff",
            department=self.department
        )
        self.complaint = Complaint.objects.create(
            submitted_by=self.user.email,
            issue_type="Network Down",
            description="The office network is down.",
            assigned_department=self.department,
            status="Pending"
        )



class ComplaintViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(department_name="Operations")
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            username="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role="User",
            department=self.department
        )
        self.staff = CustomUser.objects.create_staffuser(
            email="staff@example.com",
            username="staff@example.com",
            password="password123",
            first_name="Test",
            last_name="Staff",
            department=self.department
        )
        self.admin = CustomUser.objects.create_superuser(
            email="admin@example.com",
            username="admin@example.com",
            password="password123",
            first_name="Test",
            last_name="Admin",
            department=self.department
        )
        self.complaint1 = Complaint.objects.create(
            submitted_by=self.user.email,
            issue_type="Broken Chair",
            description="My office chair is broken.",
            assigned_department=self.department,
            status="Pending"
        )
        self.complaint2 = Complaint.objects.create(
            submitted_by=self.user.email,
            issue_type="Missing Monitor",
            description="I am missing a monitor.",
            assigned_department=self.department,
            status="In Progress",
            assigned_staff=self.staff
        )
        self.complaint3_other_user = Complaint.objects.create(
            submitted_by=self.admin.email, # Admin creates a complaint
            issue_type="Office Supplies Low",
            description="Need more pens.",
            assigned_department=self.department,
            status="Pending"
        )





    def test_staff_can_list_all_complaints(self):
        self.client.force_authenticate(user=self.staff)
        url = reverse('complaint-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), Complaint.objects.count()) # All 3 complaints





    def test_admin_can_delete_complaint(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('complaint-detail', kwargs={'ticket_id': self.complaint1.ticket_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Complaint.objects.count(), 2) # 3 from setup - 1 deleted

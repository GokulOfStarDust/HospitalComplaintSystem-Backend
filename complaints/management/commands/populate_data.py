import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from complaints.models import Department, Issue_Category, Room, Complaint

class Command(BaseCommand):
    help = 'Populates the database with sample data for Department, Issue_Category, Room, and CustomUser models.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))

        # Create Departments
        departments_data = [
            {'department_code': 'DEP001', 'department_name': 'Housekeeping', 'status': 'active'},
            {'department_code': 'DEP002', 'department_name': 'Maintenance', 'status': 'active'},
            {'department_code': 'DEP003', 'department_name': 'IT Support', 'status': 'active'},
        ]
        for data in departments_data:
            department, created = Department.objects.get_or_create(department_code=data['department_code'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Department: {department.department_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Department already exists: {department.department_name}'))

        # Create Issue Categories
        housekeeping_dept = Department.objects.get(department_code='DEP001')
        maintenance_dept = Department.objects.get(department_code='DEP002')
        it_dept = Department.objects.get(department_code='DEP003')

        issue_categories_data = [
            {'issue_category_code': 'ISC001', 'department': housekeeping_dept, 'issue_category_name': 'Cleaning', 'status': 'active'},
            {'issue_category_code': 'ISC002', 'department': housekeeping_dept, 'issue_category_name': 'Pest Control', 'status': 'active'},
            {'issue_category_code': 'ISC003', 'department': maintenance_dept, 'issue_category_name': 'Plumbing', 'status': 'active'},
            {'issue_category_code': 'ISC004', 'department': maintenance_dept, 'issue_category_name': 'Electrical', 'status': 'active'},
            {'issue_category_code': 'ISC005', 'department': it_dept, 'issue_category_name': 'Network Issue', 'status': 'active'},
        ]
        for data in issue_categories_data:
            issue_category, created = Issue_Category.objects.get_or_create(issue_category_code=data['issue_category_code'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Issue Category: {issue_category.issue_category_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Issue Category already exists: {issue_category.issue_category_name}'))

        # Create Rooms
        rooms_data = [
            {
                'bed_no': 'B1', 'room_no': '101', 'Block': 'A', 'Floor_no': 1, 'ward': 'General', 
                'speciality': 'None', 'room_type': 'Single', 'status': 'active'
            },
            {
                'bed_no': 'B2', 'room_no': '101', 'Block': 'A', 'Floor_no': 1, 'ward': 'General', 
                'speciality': 'None', 'room_type': 'Single', 'status': 'active'
            },
            {
                'bed_no': 'B1', 'room_no': '205', 'Block': 'B', 'Floor_no': 2, 'ward': 'ICU', 
                'speciality': 'Critical Care', 'room_type': 'Double', 'status': 'active'
            },
        ]
        for data in rooms_data:
            room, created = Room.objects.get_or_create(room_no=data['room_no'], bed_no=data['bed_no'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Room: {room.room_no}-{room.bed_no}'))
            else:
                self.stdout.write(self.style.WARNING(f'Room already exists: {room.room_no}-{room.bed_no}'))

        # Create Custom Users
        User = get_user_model()
        users_data = [
            {'username': 'admin', 'email': 'admin@example.com', 'role': 'master_admin', 'is_staff': True, 'is_superuser': True},
            {'username': 'housekeeping_admin', 'email': 'hk@example.com', 'role': 'dept_admin'},
            {'username': 'maintenance_admin', 'email': 'mt@example.com', 'role': 'dept_admin'},
        ]
        for data in users_data:
            try:
                user, created = User.objects.get_or_create(username=data['username'], defaults=data)
                if created:
                    user.set_password('password123')  # Set a default password
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Created User: {user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'User already exists: {user.username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating user {data['username']}: {e}"))

        self.stdout.write(self.style.SUCCESS('Database population complete.'))
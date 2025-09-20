import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from complaints.models import Department, Issue_Category, Room, Complaint, ComplaintImage
from faker import Faker
import random
from django.core.files.base import ContentFile
import base64

class Command(BaseCommand):
    help = 'Populates the database with realistic and high-volume sample data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting realistic database population for hospital environment...'))
        fake = Faker()
        User = get_user_model()

        # Clear existing data
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        ComplaintImage.objects.all().delete()
        Complaint.objects.all().delete()
        Room.objects.all().delete()
        Issue_Category.objects.all().delete()
        Department.objects.all().delete()
        User.objects.filter(is_superuser=False).delete() # Keep superuser
        self.stdout.write(self.style.WARNING('Existing data cleared.'))

        # 1. Create Departments (approx. 5-7 records)
        self.stdout.write(self.style.SUCCESS('Creating Departments...'))
        departments_data = [
            {'code': 'NUR', 'name': 'Nursing Department'},
            {'code': 'MAI', 'name': 'Maintenance'},
            {'code': 'HOU', 'name': 'Housekeeping'},
            {'code': 'IT', 'name': 'IT Support'},
            {'code': 'PHA', 'name': 'Pharmacy'},
            {'code': 'LAB', 'name': 'Laboratory'},
        ]
        departments = []
        for data in departments_data:
            department, created = Department.objects.get_or_create(
                department_code=data['code'],
                defaults={'department_name': data['name'], 'status': 'active'}
            )
            departments.append(department)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Department: {department.department_name}'))

        # 2. Create Issue Categories (approx. 20 records)
        self.stdout.write(self.style.SUCCESS('Creating Issue Categories...'))
        issue_categories = []
        hospital_issue_names = [
            "Broken Bed", "Leaky Faucet", "Clogged Toilet", "HVAC Malfunction",
            "Light Out", "Power Outage", "Network Down", "Software Glitch",
            "Printer Jam", "Dirty Room", "Biohazard Spill", "Trash Overflow",
            "Pest Sighting", "Missing Supplies", "Equipment Malfunction", "Patient Fall Hazard",
            "Noise Complaint", "Temperature Issue", "Water Leak", "Security Concern"
        ]
        for i in range(min(20, len(hospital_issue_names))):
            department = random.choice(departments)
            issue_code = f'ISC{i+1:03d}'
            issue_name = hospital_issue_names[i]
            issue_category, created = Issue_Category.objects.get_or_create(
                issue_category_code=issue_code,
                defaults={'department': department, 'issue_category_name': issue_name, 'status': 'active'}
            )
            issue_categories.append(issue_category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Issue Category: {issue_category.issue_category_name}'))

        # 3. Create Rooms (approx. 20 records)
        self.stdout.write(self.style.SUCCESS('Creating Rooms...'))
        rooms = []
        room_types = ['Single', 'Double', 'ICU', 'ER', 'OR']
        wards = ['General Ward', 'Pediatrics', 'Cardiology', 'Oncology', 'Maternity']
        blocks = ['A', 'B', 'C']

        for i in range(20):
            room_no = str(random.randint(100, 500))
            bed_no = random.choice([f'B{j}' for j in range(1, 3)]) # 1 or 2 beds per room
            block = random.choice(blocks)
            floor_no = random.randint(1, 5)
            ward = random.choice(wards)
            room_type = random.choice(room_types)
            speciality = fake.word().capitalize() + ' Speciality' if room_type not in ['ICU', 'ER', 'OR'] else room_type

            room, created = Room.objects.get_or_create(
                room_no=room_no, bed_no=bed_no,
                defaults={
                    'Block': block,
                    'Floor_no': floor_no,
                    'ward': ward,
                    'speciality': speciality,
                    'room_type': room_type,
                    'status': 'active',
                }
            )
            rooms.append(room)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Room: {room.room_no}-{room.bed_no}'))

        # 4. Create Custom Users (approx. 10-15 records, including admin)
        self.stdout.write(self.style.SUCCESS('Creating Custom Users...'))
        users = []
        # Ensure an admin user exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@hospital.com', 'role': 'master_admin', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('password123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created Admin User: {admin_user.username}'))
        users.append(admin_user)

        for i in range(15):
            username = fake.unique.user_name()
            email = fake.unique.email()
            role = random.choice(['master_admin', 'dept_admin', 'staff'])
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'role': role, 'is_staff': (role == 'dept_admin' or role == 'staff'), 'is_superuser': (role == 'master_admin')}
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created User: {user.username}'))
            users.append(user)

        # Get all staff users
        staff_users = User.objects.filter(role='staff')

        # 5. Create Complaints (approx. 20 records)
        self.stdout.write(self.style.SUCCESS('Creating Complaints...'))
        for i in range(20):
            room = random.choice(rooms)
            issue_category = random.choice(issue_categories)
            priority = random.choice(['low', 'medium', 'high'])
            status = random.choice(['open', 'in_progress', 'resolved', 'closed', 'on_hold'])
            submitted_at = fake.date_time_between(start_date='-6m', end_date='now')
            resolved_at = None
            if status in ['resolved', 'closed']:
                resolved_at = fake.date_time_between(start_date=submitted_at, end_date='now')

            assigned_department_obj = issue_category.department # Assign department based on issue category
            assigned_staff_obj = random.choice(staff_users) if staff_users and random.random() > 0.5 else None

            complaint, created = Complaint.objects.get_or_create(
                ticket_id=f'HOS{fake.unique.random_number(digits=5)}',
                defaults={
                    'room': room,
                    'issue_type': issue_category.issue_category_name,
                    'description': fake.paragraph(nb_sentences=3),
                    'priority': priority,
                    'submitted_by': fake.name(),
                    'status': status,
                    'assigned_department': assigned_department_obj,
                    'assigned_staff': assigned_staff_obj, # Assign the staff object
                    'resolved_by': fake.name() if resolved_at else None,
                    'resolved_at': resolved_at,
                    'remarks': fake.sentence() if resolved_at else None,
                    'submitted_at': submitted_at,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Complaint: {complaint.ticket_id}'))

                # Add Complaint Images (optional)
                if random.random() < 0.5: # 50% chance to add images
                    for _ in range(random.randint(1, 2)):
                        img_data = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
                        image_file = ContentFile(img_data, name=f'{fake.uuid4()}.gif')
                        ComplaintImage.objects.create(complaint=complaint, image=image_file)
                        self.stdout.write(self.style.SUCCESS(f'  Added image to Complaint {complaint.ticket_id}'))

        self.stdout.write(self.style.SUCCESS('Realistic database population complete.'))

import hmac
import hashlib
from django.conf import settings
from rest_framework import serializers
from .models import Room, Complaint, ComplaintImage, Department,Issue_Category
from django.db import models
from datetime import timedelta
from django.utils import timezone

class ComplaintImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintImage
        fields = ['image']  # you can also include 'id' if needed

    def to_internal_value(self, data):
        return super().to_internal_value(data)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ('qr_code', 'dataenc')

    def validate(self, data):
        # Get all fields except status
        bed_no = data.get('bed_no')
        room_no = data.get('room_no')
        Block = data.get('Block')
        Floor_no = data.get('Floor_no')
        ward = data.get('ward')
        speciality = data.get('speciality')
        room_type = data.get('room_type')

        # Check if all required fields are present
        if all([bed_no, room_no, Block, Floor_no, ward, speciality, room_type]):
            # Check if a room with these exact fields already exists
            existing_room = Room.objects.filter(
                bed_no=bed_no,
                room_no=room_no,
                Block=Block,
                Floor_no=Floor_no,
                ward=ward,
                speciality=speciality,
                room_type=room_type
            )

            # If updating, exclude the current instance from the check
            if self.instance:
                existing_room = existing_room.exclude(pk=self.instance.pk)

            if existing_room.exists():
                raise serializers.ValidationError(
                    "A room with these exact details already exists. All fields (except status) must be unique together."
                )

        return data


class DepartmentSerializer(serializers.ModelSerializer):
    department_code = serializers.CharField(required=False)  # Make it optional for updates

    class Meta:
        model = Department
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        # Make department_code read-only if we're updating an existing instance
        if self.instance is not None:
            fields['department_code'].read_only = True
        return fields

    def validate_department_name(self, value):
        # Ensure department name is unique (case-insensitive)
        if self.instance:  # If updating
            if Department.objects.exclude(pk=self.instance.pk).filter(department_name__iexact=value).exists():
                raise serializers.ValidationError("A department with this name already exists.")
        else:  # If creating
            if Department.objects.filter(department_name__iexact=value).exists():
                raise serializers.ValidationError("A department with this name already exists.")
        return value

    def validate_status(self, value):
        if value not in dict(Department.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status value")
        return value


class IssueCatSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    issue_category_code = serializers.CharField(required=False)  # Updated field name

    class Meta:
        model = Issue_Category
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        # Make issue_category_code read-only if we're updating an existing instance
        if self.instance is not None:
            fields['issue_category_code'].read_only = True
        return fields

    def validate_issue_category_name(self, value):  # Updated field name
        # Ensure category name is unique (case-insensitive)
        if self.instance:  # If updating
            if Issue_Category.objects.exclude(pk=self.instance.pk).filter(
                department=self.initial_data.get('department', self.instance.department),
                issue_category_name__iexact=value  # Updated field name
            ).exists():
                raise serializers.ValidationError("An issue category with this name already exists in this department.")
        else:  # If creating
            if Issue_Category.objects.filter(
                department=self.initial_data.get('department'),
                issue_category_name__iexact=value  # Updated field name
            ).exists():
                raise serializers.ValidationError("An issue category with this name already exists in this department.")
        return value

    def validate_status(self, value):
        if value not in dict(Issue_Category.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status value")
        return value

    def validate_department(self, value):
        if value.status != 'active':
            raise serializers.ValidationError("Cannot assign issue category to an inactive department")
        return value

class ComplaintCreateSerializer(serializers.ModelSerializer):
    images = ComplaintImageSerializer(many=True,write_only=True,required=False)
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())

    def create(self, validated_data):
        print("--- ComplaintCreateSerializer: create method ---")
        print("Validated data:", validated_data)
        images_data = self.context['request'].FILES.getlist('images')
        print("Images data:", images_data)
        validated_data.pop('images', None)

        complaint = Complaint.objects.create(**validated_data)

        for image_file in images_data:
            ComplaintImage.objects.create(complaint=complaint, image=image_file)

        return complaint

    def validate(self, data):
        print("--- ComplaintCreateSerializer: validate method ---")
        print("Initial data:", data)
        issue_type = data.get('issue_type')
        room = data.get('room')

        try:
            issue_category = Issue_Category.objects.get(issue_category_name=issue_type, status='active')
            data['assigned_department'] = issue_category.department
            print("Assigned department:", data['assigned_department'])
        except Issue_Category.DoesNotExist:
            raise serializers.ValidationError({
                'issue_type': 'Invalid or inactive issue category. Please select a valid issue category.'
            })

        if room.status != 'active':
            raise serializers.ValidationError("The specified room is not active")

        if issue_type and room:
            existing_complaint = Complaint.objects.filter(
                issue_type=issue_type,
                room=room,
                status__in=['open', 'in_progress']
            ).exists()

            if existing_complaint:
                raise serializers.ValidationError(
                    'A complaint with the same issue type is already open or in progress for this room.'
                )
        print("Final data before return:", data)
        return data

    class Meta:
        model = Complaint
        fields = ['room', 'issue_type', 'description', 'priority', 'images']


from auth_app.models import CustomUser

class ComplaintSerializer(serializers.ModelSerializer):
    images = ComplaintImageSerializer(many=True, read_only=True)
    room = RoomSerializer(read_only=True)
    assigned_department = serializers.CharField(source='assigned_department.department_name', read_only=True, allow_null=True)
    assigned_staff = serializers.CharField(source='assigned_staff.username', read_only=True, allow_null=True)

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ('ticket_id',)


class ComplaintUpdateSerializer(serializers.ModelSerializer):
    images = ComplaintImageSerializer(many=True, write_only=True, required=False)
    assigned_department = serializers.SlugRelatedField(
        queryset=Department.objects.all(),
        slug_field='department_name',
        required=False, # Allow null if department is optional
        allow_null=True # Allow null if department is optional
    )
    assigned_staff = serializers.SlugRelatedField(
        queryset=CustomUser.objects.filter(role='staff'), # Only allow assigning staff role users
        slug_field='username',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ('ticket_id', 'room')

    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        validated_data.pop('images', None)

        # If status is being updated
        if 'status' in validated_data:
            new_status = validated_data['status']

            if new_status == 'closed' and instance.status != 'resolved':
                raise serializers.ValidationError("A ticket can only be closed if it is already resolved.")
            
            if new_status == 'resolved':
                assigned_staff = validated_data.get('assigned_staff', instance.assigned_staff)

                if assigned_staff:
                    validated_data['resolved_by'] = assigned_staff.username
                else:
                    validated_data['resolved_by'] = None
                
                validated_data['resolved_at'] = timezone.now()
            
            elif new_status in ['open', 'in_progress', 'on_hold']:
                validated_data['resolved_by'] = None
                validated_data['resolved_at'] = None

        complaint = super().update(instance, validated_data)

        for image_file in images_data:
            ComplaintImage.objects.create(complaint=complaint, image=image_file)

        return complaint

class ComplaintImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintImage
        fields = ['image']

class ReportDepartment(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Complaint
        fields = ['ticket_id', 'assigned_department', 'priority', 'status', 'submitted_at', 'issue_type', 'room']
class TATserializer(serializers.ModelSerializer):
    tat = serializers.SerializerMethodField()
    assigned_department = serializers.CharField(source='assigned_department.department_code', read_only=True, allow_null=True)
    department_name = serializers.CharField(source='assigned_department.department_name', read_only=True, allow_null=True)

    class Meta:
        model = Complaint
        fields = ['ticket_id', 'submitted_at', 'resolved_at', 'priority', 'status', 'tat', 'assigned_department', 'department_name']

    def get_tat(self, obj):
        if (obj.status == 'resolved' or obj.status == 'closed') and obj.resolved_at:
            tat_duration = obj.resolved_at - obj.submitted_at
            return self.format_timedelta(tat_duration)
        return '-'  # Or None if you prefer null
    
    def format_timedelta(self, delta):
        total_seconds = int(delta.total_seconds())
        days = delta.days
        hours = total_seconds // 3600 % 24
        minutes = total_seconds // 60 % 60
        seconds = total_seconds % 60

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

        return ', '.join(parts) or "0 seconds"
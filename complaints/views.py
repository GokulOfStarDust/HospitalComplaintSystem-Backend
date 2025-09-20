from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,DestroyModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from .models import Room, Complaint, Department, Issue_Category
from .serializers import RoomSerializer, ComplaintSerializer, ComplaintCreateSerializer, ComplaintUpdateSerializer, DepartmentSerializer,IssueCatSerializer,ReportDepartment,TATserializer
from .pagination import CustomLimitOffsetPagination
from django.db.models import Count, Q
from django.db.models import Avg, F, ExpressionWrapper, DurationField
from datetime import timedelta, time
from dateutil.parser import parse
from django.db.models import DurationField, ExpressionWrapper
from rest_framework.permissions import IsAuthenticated, AllowAny
from auth_app.permissions import IsMasterAdmin, IsMasterAdminOrDeptAdmin

# Create your views here.
class RoomViewSet(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,DestroyModelMixin):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'ward', 'speciality', 'room_type']
    search_fields = ['room_no', 'bed_no', 'Block']

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated, IsMasterAdmin]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        room = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Room.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        room.status = new_status
        room.save()
        return Response(RoomSerializer(room).data)


class DepartmentViewSet(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    pagination_class = CustomLimitOffsetPagination
    lookup_field = 'department_code'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department_name','status']
    search_fields = ['department_code', 'department_name']

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated, IsMasterAdmin]
        return super().get_permissions()

class IssueCatViewset(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    queryset = Issue_Category.objects.all()
    serializer_class = IssueCatSerializer
    pagination_class = CustomLimitOffsetPagination
    lookup_field = 'issue_category_code'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['issue_category_code', 'department', 'issue_category_name', 'status']
    search_fields = ['issue_category_code', 'department__department_name', 'issue_category_name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, IsMasterAdmin]
        return super().get_permissions()

from .filters import ComplaintFilter

class ComplaintViewSet(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    queryset = Complaint.objects.all().order_by('-submitted_at')
    lookup_field = 'ticket_id'
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ComplaintFilter
    search_fields = ['ticket_id', 'room__room_no', 'room__bed_no', 'description']
    ordering_fields = ['submitted_at', 'priority', 'status']
    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'dept_admin' or user.role == 'staff':
                return self.queryset.filter(assigned_department=user.department)
        return self.queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ComplaintCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ComplaintUpdateSerializer
        return ComplaintSerializer

    def create(self, request, *args, **kwargs):
        print("--- ComplaintViewSet: create method ---")
        print("Incoming request data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        print("--- ComplaintViewSet: perform_create method ---")
        print("Serializer validated data:", serializer.validated_data)
        serializer.save(submitted_by=self.request.user.username if self.request.user.is_authenticated else "Anonymous")

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        status_filter = request.query_params.get('status')
        if status_filter not in dict(Complaint.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        complaints = self.queryset.filter(status=status_filter)
        serializer = self.get_serializer(complaints, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_priority(self, request):
        priority_filter = request.query_params.get('priority')
        if priority_filter not in dict(Complaint.PRIORITY_CHOICES):
            return Response(
                {'error': 'Invalid priority'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        complaints = self.queryset.filter(priority=priority_filter)
        serializer = self.get_serializer(complaints, many=True)
        return Response(serializer.data)

class ReportViewSet(GenericViewSet, ListModelMixin):
    queryset = Complaint.objects.all()
    serializer_class = ReportDepartment
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assigned_department', 'priority', 'status', 'submitted_at']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Complaint.objects.select_related('assigned_department').all()
        if user.is_authenticated:
            if user.role == 'dept_admin' or user.role == 'staff':
                return queryset.filter(assigned_department=user.department)
        return queryset

    @action(detail=False, methods=['get'])
    def department_priority_stats(self, request):
        # Get department and priority from query params
        department = request.query_params.get('department')
        priority = request.query_params.get('priority')

        if not department or not priority:
            return Response(
                {'error': 'Both department and priority parameters are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate priority
        if priority not in dict(Complaint.PRIORITY_CHOICES):
            return Response(
                {'error': 'Invalid priority value'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get counts for the specific department and priority
        stats = self.queryset.filter(
            assigned_department=department,
            priority=priority
        ).aggregate(
            resolved_tickets=Count('ticket_id', filter=Q(status__in=['resolved', 'closed'])),
            pending_tickets=Count('ticket_id', filter=~Q(status__in=['resolved', 'closed'])),
            total_tickets=Count('ticket_id')
        )

        # Add department and priority to the response
        stats['department'] = department
        stats['priority'] = priority

        return Response(stats)

    @action(detail=False, methods=['get'])
    def all_department_stats(self, request):
        # Get filter parameters
        priority = request.query_params.get('priority')
        department = request.query_params.get('department')
        status_filter = request.query_params.get('status')  # Renamed to avoid conflict
        submitted_at = request.query_params.get('submitted_at')

        # Start with base queryset
        queryset = self.get_queryset() # Use get_queryset to apply role-based filtering

        # Apply filters if provided
        if priority:
            if priority not in dict(Complaint.PRIORITY_CHOICES):
                return Response(
                    {'error': 'Invalid priority value'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            queryset = queryset.filter(priority=priority)

        if department:
            queryset = queryset.filter(assigned_department=department)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if submitted_at:
            queryset = queryset.filter(submitted_at__date=submitted_at)

        # Get all combinations of department and priority with their counts
        stats = queryset.annotate(
            department_name=F('assigned_department__department_name')
        ).values(
            'assigned_department', 
            'department_name', 
            'priority'
        ).annotate(
            resolved_tickets=Count('ticket_id', filter=Q(status__in=['resolved', 'closed'])),
            pending_tickets=Count('ticket_id', filter=~Q(status__in=['resolved', 'closed'])),
            total_tickets=Count('ticket_id')
        ).order_by('assigned_department', 'priority')

        # If no results found before pagination, return empty response with message
        if not stats.exists():
            return Response({
                'message': 'No data found for the specified filters',
                'filters_applied': {
                    'priority': priority,
                    'department': department,
                    'status': status_filter,
                    'submitted_at': submitted_at
                }
            }, status=status.HTTP_200_OK)

        # Paginate the results
        page = self.paginate_queryset(stats)
        if page is not None:
            return self.get_paginated_response(list(page))

        return Response(stats)

    
class TATViewSet(GenericViewSet, ListModelMixin):
    queryset = Complaint.objects.all()
    serializer_class = TATserializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['priority', 'status']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Complaint.objects.select_related('assigned_department').all()
        if user.is_authenticated:
            if user.role == 'dept_admin' or user.role == 'staff':
                return queryset.filter(assigned_department=user.department)
        return queryset

    def format_timedelta(self, delta):
        if not delta:
            return "-"

        total_seconds = int(delta.total_seconds())
        total_hours = total_seconds // 3600
        days = total_hours // 24
        hours = total_hours % 24
        minutes = (total_seconds % 3600) // 60
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

        return ', '.join(parts) or "0 minutes"


    @action(detail=False, methods=['get'])
    def all_department_TATS(self, request):
        # Get filter parameters
        priority = request.query_params.get('priority')
        date = request.query_params.get('date')  # Format: YYYY-MM-DD
        start_time = request.query_params.get('start_time')  # Format: HH:MM (24-hour)
        end_time = request.query_params.get('end_time')  # Format: HH:MM (24-hour)

        # Start with base queryset
        queryset = self.get_queryset() # Use get_queryset to apply role-based filtering

        # Apply priority filter if provided
        if priority:
            if priority not in dict(Complaint.PRIORITY_CHOICES):
                return Response(
                    {'error': 'Invalid priority value'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            queryset = queryset.filter(priority=priority)

        # Handle date and time filtering
        try:
            if date:
                # Parse the date
                parsed_date = parse(date)
                if not parsed_date:
                    raise ValueError("Invalid date format")

                # If time range is provided
                if start_time or end_time:
                    # Validate time format
                    if start_time:
                        try:
                            # Parse start time
                            start_hour, start_minute = map(int, start_time.split(':'))
                            if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59):
                                raise ValueError("Invalid time format")
                            start_datetime = parsed_date.replace(hour=start_hour, minute=start_minute)
                        except ValueError:
                            raise ValueError("Invalid start time format. Use HH:MM (24-hour)")
                    else:
                        # If no start time, use start of day
                        start_datetime = parsed_date.replace(hour=0, minute=0)

                    if end_time:
                        try:
                            # Parse end time
                            end_hour, end_minute = map(int, end_time.split(':'))
                            if not (0 <= end_hour <= 23 and 0 <= end_minute <= 59):
                                raise ValueError("Invalid time format")
                            end_datetime = parsed_date.replace(hour=end_hour, minute=end_minute)
                        except ValueError:
                            raise ValueError("Invalid end time format. Use HH:MM (24-hour)")
                    else:
                        # If no end time, use end of day
                        end_datetime = parsed_date.replace(hour=23, minute=59)

                    # Apply datetime range filter
                    queryset = queryset.filter(
                        submitted_at__gte=start_datetime,
                        submitted_at__lte=end_datetime
                    )
                else:
                    # If no time range, filter for the entire day
                    queryset = queryset.filter(submitted_at__date=parsed_date)
            elif start_time or end_time:
                # Only time filtering, across all dates
                if start_time:
                    start_hour, start_minute = map(int, start_time.split(':'))
                    start_time_obj = time(start_hour, start_minute)
                else:
                    start_time_obj = time(0, 0)
                if end_time:
                    end_hour, end_minute = map(int, end_time.split(':'))
                    end_time_obj = time(end_hour, end_minute)
                else:
                    end_time_obj = time(23, 59)
                queryset = queryset.filter(
                    submitted_at__time__gte=start_time_obj,
                    submitted_at__time__lte=end_time_obj
                )
        except ValueError as e:
            return Response({
                'error': str(e),
                'message': 'Please use the following formats:',
                'example': {
                    'date_only': '/api/tat/all_department_TATS/?date=2025-06-16',
                    'with_time_range': '/api/tat/all_department_TATS/?date=2025-06-16&start_time=09:00&end_time=17:00'
                },
                'format_guide': {
                    'date': 'YYYY-MM-DD (e.g., 2025-06-16)',
                    'time': 'HH:MM in 24-hour format (e.g., 09:00, 17:30)'
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        resolved_tickets = queryset.filter(
            status__in=['resolved', 'closed'],
            resolved_at__isnull=False
        )

        # Calculate average explicitly
        avg_tat = resolved_tickets.aggregate(
            avg_tat=Avg(
                ExpressionWrapper(
                    F('resolved_at') - F('submitted_at'),
                    output_field=DurationField()
                )
            )
        )['avg_tat']

        # Get total tickets count
        total_tickets = queryset.count()
        
        # Calculate average TAT for resolved tickets
        # avg_tat = resolved_tickets.aggregate(
        #     avg_tat=Avg('tat')
        # )['avg_tat']

        # Add individual ticket TATs
        # for ticket in queryset:
        #     ticket_data = {
        #         'ticket_id': ticket.ticket_id,
        #         'submitted_at': ticket.submitted_at,
        #         'resolved_at': ticket.resolved_at,
        #         'priority': ticket.priority,
        #         'status': ticket.status,
        #         'tat': str(ticket.resolved_at - ticket.submitted_at) if ticket.status == 'resolved' and ticket.resolved_at else '-'
        #     }
        #     response_data['tickets'].append(ticket_data)

        # Paginate the queryset for the 'tickets' list
        page = self.paginate_queryset(queryset)

        if page is not None:
            # Serialize the paginated data
            serializer = self.get_serializer(page, many=True)
            paginated_tickets_data = serializer.data

            # Get pagination links and count from self.paginator
            paginator = self.paginator
            count = paginator.count
            next_link = paginator.get_next_link()
            previous_link = paginator.get_previous_link()

            response_data = {
                'total_tickets': total_tickets,
                'average_tat': self.format_timedelta(avg_tat) if avg_tat else '-',
                'filters_applied': {
                    'priority': priority,
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time
                },
                'count': count,
                'next': next_link,
                'previous': previous_link,
                'results': paginated_tickets_data
            }
            return Response(response_data)
        else:
            # Fallback if pagination is not applied (should ideally not be reached if pagination_class is set).
            # In this case, just return the unpaginated results along with aggregations.
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'total_tickets': total_tickets,
                'average_tat': self.format_timedelta(avg_tat) if avg_tat else '-',
                'filters_applied': {
                    'priority': priority,
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time
                },
                'results': serializer.data  # Unpaginated results
            }
            return Response(response_data)
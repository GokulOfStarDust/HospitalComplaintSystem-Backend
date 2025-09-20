from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from complaints.models import Department, Issue_Category, Room, Complaint, ComplaintImage

class Command(BaseCommand):
    help = 'Clears all sample data from the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Clearing all existing data...'))

        # Delete data in reverse order of dependency
        ComplaintImage.objects.all().delete()
        Complaint.objects.all().delete()
        Room.objects.all().delete()
        Issue_Category.objects.all().delete()
        Department.objects.all().delete()
        
        # Delete CustomUser data, but keep superusers
        User = get_user_model()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('All sample data cleared successfully.'))

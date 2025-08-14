from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import EmailVerification
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Create test data for admin dashboard'

    def handle(self, *args, **options):
        # Create test users
        test_users = [
            {'username': 'testuser1', 'email': 'test1@example.com', 'first_name': 'Test', 'last_name': 'User1'},
            {'username': 'testuser2', 'email': 'test2@example.com', 'first_name': 'Test', 'last_name': 'User2'},
            {'username': 'testuser3', 'email': 'test3@example.com', 'first_name': 'Test', 'last_name': 'User3'},
            {'username': 'testuser4', 'email': 'test4@example.com', 'first_name': 'Test', 'last_name': 'User4'},
            {'username': 'testuser5', 'email': 'test5@example.com', 'first_name': 'Test', 'last_name': 'User5'},
        ]
        
        created_users = []
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True
                }
            )
            if created:
                created_users.append(user)
                self.stdout.write(f'Created user: {user.username}')
        
        # Create test email verifications
        statuses = ['pending', 'approved', 'rejected']
        for user in created_users:
            verification, created = EmailVerification.objects.get_or_create(
                user=user,
                defaults={
                    'email': user.email,
                    'verification_key': f'test_key_{user.id}_{random.randint(1000, 9999)}',
                    'status': random.choice(statuses),
                    'created_at': timezone.now() - timezone.timedelta(days=random.randint(1, 7))
                }
            )
            if created:
                self.stdout.write(f'Created verification for: {user.username} - {verification.status}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_users)} test users and verifications')
        ) 
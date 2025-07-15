from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from vendor.models import Vendor, OpeningHour
from django.urls import reverse
from django.test import Client
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Test opening hours functionality'

    def handle(self, *args, **options):
        self.stdout.write("🧪 TESTING OPENING HOURS FUNCTIONALITY")
        self.stdout.write("=" * 50)
        
        # Check if vendor users exist
        vendors = User.objects.filter(role=User.VENDOR)
        if not vendors.exists():
            self.stdout.write(self.style.ERROR("❌ No vendor users found!"))
            self.stdout.write("Create a vendor user first:")
            self.stdout.write("python manage.py createsuperuser")
            return
        
        vendor_user = vendors.first()
        self.stdout.write(f"✅ Found vendor user: {vendor_user.username}")
        
        # Check if vendor profile exists
        try:
            vendor = vendor_user.vendor
            self.stdout.write(f"✅ Vendor profile: {vendor.vendor_name}")
        except:
            self.stdout.write(self.style.ERROR("❌ Vendor profile not found!"))
            return
        
        # Test URLs
        self.stdout.write("\n🔗 TESTING URLS:")
        try:
            opening_hours_url = reverse('opening_hours')
            add_opening_hours_url = reverse('add_opening_hours')
            self.stdout.write(f"✅ Opening hours URL: {opening_hours_url}")
            self.stdout.write(f"✅ Add opening hours URL: {add_opening_hours_url}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ URL error: {e}"))
            return
        
        # Test with Django test client
        self.stdout.write("\n📡 TESTING AJAX ENDPOINT:")
        client = Client()
        client.force_login(vendor_user)
        
        # Test POST request
        response = client.post(add_opening_hours_url, {
            'day': '1',
            'from_hour': '09:00 AM',
            'to_hour': '05:00 PM',
            'is_closed': 'False',
        })
        
        self.stdout.write(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                if data.get('status') == 'success':
                    self.stdout.write("✅ AJAX endpoint working!")
                    self.stdout.write(f"Created opening hour ID: {data.get('id')}")
                    
                    # Clean up - remove the test opening hour
                    if data.get('id'):
                        OpeningHour.objects.filter(id=data.get('id')).delete()
                        self.stdout.write("🧹 Cleaned up test data")
                else:
                    self.stdout.write(self.style.ERROR(f"❌ AJAX error: {data.get('message')}"))
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f"❌ Invalid JSON response: {response.content}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ HTTP error {response.status_code}"))
            self.stdout.write(f"Response: {response.content}")
        
        # Check existing opening hours
        self.stdout.write("\n📅 EXISTING OPENING HOURS:")
        existing_hours = OpeningHour.objects.filter(vendor=vendor)
        if existing_hours.exists():
            for hour in existing_hours:
                self.stdout.write(f"  • {hour}")
        else:
            self.stdout.write("  No opening hours found")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("🎯 DEBUGGING STEPS:")
        self.stdout.write("1. If URLs are missing: Check vendor/urls.py")
        self.stdout.write("2. If AJAX fails: Check vendor/views.py add_opening_hours function")
        self.stdout.write("3. If vendor missing: Create vendor profile")
        self.stdout.write("4. For frontend issues: Use browser console test")
        self.stdout.write("=" * 50)

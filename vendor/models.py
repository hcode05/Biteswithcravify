from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import time, date, datetime
import math

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='vendor', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='vendor_profile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    
    # Location fields for distance calculation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def get_opening_hours(self):
        """
        Returns a list of opening hours for each day.
        Example:
        [
            {'day': 'Monday', 'periods': [{'from': '09:00 AM', 'to': '05:00 PM'}, ...], 'closed': False},
            ...
        ]
        """
        opening_hours = []
        for day_num, day_name in DAYS:
            periods = []
            closed = False
            hours = self.openinghour_set.filter(day=day_num)
            for hour in hours:
                if hour.is_closed:
                    closed = True
                elif hour.from_hour and hour.to_hour:
                    periods.append({'from': hour.from_hour, 'to': hour.to_hour})
            opening_hours.append({
                'day': day_name,
                'periods': periods,
                'closed': closed and not periods,
            })
        return opening_hours
    
    def calculate_distance(self, customer_lat, customer_lng):
        """Calculate distance between vendor and customer using Haversine formula"""
        if not self.latitude or not self.longitude:
            return None
            
        try:
            # Convert to float for calculation
            vendor_lat = float(self.latitude)
            vendor_lng = float(self.longitude)
            customer_lat = float(customer_lat)
            customer_lng = float(customer_lng)
            
            # Haversine formula
            R = 6371  # Earth's radius in kilometers
            
            dlat = math.radians(customer_lat - vendor_lat)
            dlng = math.radians(customer_lng - vendor_lng)
            
            a = (math.sin(dlat/2) * math.sin(dlat/2) + 
                 math.cos(math.radians(vendor_lat)) * math.cos(math.radians(customer_lat)) * 
                 math.sin(dlng/2) * math.sin(dlng/2))
            
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            return round(distance, 2)
        except (ValueError, TypeError):
            return None
    
    @property
    def is_open(self):
        """Check if vendor is currently open based on opening hours"""
        if not self.is_approved:
            return False
        
        now = datetime.now()
        # Python's weekday(): Monday is 0, Sunday is 6. We want Monday=1, Sunday=7.
        current_day = now.weekday() + 1
        if current_day > 7:
            current_day = 1
        current_time = now.time()
        
        try:
            today_hours = self.openinghour_set.filter(day=current_day, is_closed=False)
            for hour in today_hours:
                if hour.from_hour and hour.to_hour:
                    try:
                        from_time = datetime.strptime(hour.from_hour, '%I:%M %p').time()
                        to_time = datetime.strptime(hour.to_hour, '%I:%M %p').time()
                        # Handle overnight hours (e.g., 10:00 PM to 2:00 AM)
                        if from_time <= to_time:
                            if from_time <= current_time <= to_time:
                                return True
                        else:
                            if current_time >= from_time or current_time <= to_time:
                                return True
                    except ValueError:
                        continue
            return False
        except Exception:
            return False

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Update
            try:
                orig = Vendor.objects.get(pk=self.pk)
                if orig.is_approved != self.is_approved:
                    mail_template = 'accounts/emails/admin_approval_email.html'
                    context = {
                        'user': self.user,
                        'is_approved': self.is_approved,
                        'to_email': self.user.email,
                    }
                    if self.is_approved == True:
                        # Send notification email
                        mail_subject = "Congratulations! Your restaurant has been approved."
                        send_notification(mail_subject, mail_template, context)
                    else:
                        # Send notification email
                        mail_subject = "We're sorry! You are not eligible for publishing your food menu on our marketplace."
                        send_notification(mail_subject, mail_template, context)
            except Vendor.DoesNotExist:
                pass
        return super(Vendor, self).save(*args, **kwargs)

DAYS = [
    (1, "Monday"),
    (2, "Tuesday"),
    (3, "Wednesday"),
    (4, "Thursday"),
    (5, "Friday"),
    (6, "Saturday"),
    (7, "Sunday"),
]

# Fixed time choices - using proper time format
HOUR_OF_DAY_24 = [
    (time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) 
    for h in range(0, 24) for m in (0, 30)
]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True, null=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True, null=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', 'from_hour')
        # Allow multiple opening periods per day for a vendor
        constraints = [
            models.UniqueConstraint(fields=['vendor', 'day', 'from_hour', 'to_hour'], name='unique_vendor_day_period')
        ]

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_display()} - Closed"
        return f"{self.get_day_display()} - {self.from_hour} to {self.to_hour}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if not self.is_closed:
            if not self.from_hour or not self.to_hour:
                raise ValidationError("From hour and To hour are required when not closed.")
            
            # Convert to time objects for validation
            try:
                from_time = datetime.strptime(self.from_hour, '%I:%M %p').time()
                to_time = datetime.strptime(self.to_hour, '%I:%M %p').time()
                # Allow overnight hours (e.g., 10:00 PM to 2:00 AM)
                if from_time == to_time:
                    raise ValidationError("From hour and To hour cannot be the same.")
            except ValueError:
                raise ValidationError("Invalid time format.")
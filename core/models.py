from django.db import models


class Advertisement(models.Model):
    """Promotional banner/ad shown on the homepage. Managed by admin/staff."""
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class MapLocation(models.Model):
    """A point on the island map (hotel, ferry dock, activity, beach, etc.)."""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    pin_x = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50,
        help_text='Horizontal pin position on the map image, from 0 to 100 percent.',
    )
    pin_y = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50,
        help_text='Vertical pin position on the map image, from 0 to 100 percent.',
    )

    def __str__(self):
        return self.name


class MapImage(models.Model):
    """Main visitor map image uploaded by the system admin."""
    title = models.CharField(max_length=200, default='Maavaharu Visitor Map')
    image = models.ImageField(upload_to='island_maps/')
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SystemIssue(models.Model):
    """Admin-tracked issue or content task for the booking system."""
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

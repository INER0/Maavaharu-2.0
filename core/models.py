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
    """A point on the island map (hotel, ferry dock, ride, beach, etc.)."""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name

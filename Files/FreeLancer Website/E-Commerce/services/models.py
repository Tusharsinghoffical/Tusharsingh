from django.db import models

class ServiceFeature(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Development'),
        ('mobile', 'Mobile Development'),
        ('design', 'UI/UX Design'),
        ('seo', 'SEO Optimization'),
        ('consultation', 'Consultation'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_type = models.CharField(max_length=20, choices=[
        ('hourly', 'Per Hour'),
        ('fixed', 'Fixed Price'),
        ('monthly', 'Per Month'),
    ])
    icon = models.CharField(max_length=50, default='fas fa-cog')
    duration = models.CharField(max_length=50, blank=True)
    team_size = models.CharField(max_length=50, blank=True)
    delivery_time = models.CharField(max_length=50, blank=True)
    additional_info = models.TextField(blank=True)
    features = models.ManyToManyField(ServiceFeature, blank=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-is_popular', '-created_at']
    
    def __str__(self):
        return self.title 
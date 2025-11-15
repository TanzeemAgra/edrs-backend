# Generated migration for ContactInquiry model

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactInquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('company', models.CharField(blank=True, max_length=255)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('inquiry_type', models.CharField(choices=[
                    ('general', 'General Inquiry'),
                    ('technical', 'Technical Support'),
                    ('sales', 'Sales & Licensing'),
                    ('partnership', 'Partnership Opportunities'),
                    ('training', 'Training & Certification'),
                    ('enterprise', 'Enterprise Solutions'),
                ], default='general', max_length=20)),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[
                    ('new', 'New'),
                    ('in_progress', 'In Progress'),
                    ('resolved', 'Resolved'),
                    ('closed', 'Closed'),
                ], default='new', max_length=20)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contact_inquiries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contact Inquiry',
                'verbose_name_plural': 'Contact Inquiries',
                'ordering': ['-submitted_at'],
            },
        ),
    ]
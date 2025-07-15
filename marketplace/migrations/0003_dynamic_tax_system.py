# Generated manually for dynamic tax system implementation

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_tax'),
    ]

    operations = [
        # First, create the new TaxCategory model
        migrations.CreateModel(
            name='TaxCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Tax Categories',
            },
        ),

        # Create TaxExemption model
        migrations.CreateModel(
            name='TaxExemption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('exemption_type', models.CharField(choices=[('user', 'User Based'), ('item', 'Item Based'), ('location', 'Location Based'), ('amount', 'Amount Based')], max_length=20)),
                ('conditions', models.JSONField(default=dict, help_text='JSON field to store exemption conditions')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),

        # Backup existing tax data by renaming the table
        migrations.RenameModel(
            old_name='Tax',
            new_name='TaxOld',
        ),

        # Create the new enhanced Tax model
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('rate', models.DecimalField(decimal_places=4, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('calculation_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], default='percentage', max_length=20)),
                ('applicable_on', models.CharField(choices=[('subtotal', 'Subtotal'), ('total', 'Total including other taxes')], default='subtotal', max_length=20)),
                ('location_type', models.CharField(blank=True, choices=[('country', 'Country'), ('state', 'State/Province'), ('city', 'City'), ('postal_code', 'Postal Code')], max_length=20)),
                ('location_value', models.CharField(blank=True, max_length=100)),
                ('minimum_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('maximum_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('priority', models.IntegerField(default=1, help_text='Lower numbers have higher priority')),
                ('is_included_in_price', models.BooleanField(default=False, help_text='Whether this tax is already included in the item price')),
                ('valid_from', models.DateTimeField(blank=True, null=True)),
                ('valid_until', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.taxcategory')),
            ],
            options={
                'ordering': ['priority', 'name'],
            },
        ),

        # Add many-to-many relationship for exemptions
        migrations.AddField(
            model_name='tax',
            name='exemptions',
            field=models.ManyToManyField(blank=True, to='marketplace.taxexemption'),
        ),
    ]

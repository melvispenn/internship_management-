from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_otp_updated_at_user_first_name_user_last_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="phone",
            field=models.CharField(
                blank=True,
                max_length=30,
                verbose_name="phone number",
            ),
        ),
    ]

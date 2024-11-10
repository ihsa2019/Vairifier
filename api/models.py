from django.db import models


class Document(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    document_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    document_file = models.FileField(upload_to='documents/')


class PersonalInformation(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, primary_key=True)

    class Meta:
        db_table = 'personal_information'
        managed = False  # Prevent Django from managing this table

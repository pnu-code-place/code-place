from django.db import models


class College(models.Model):
    college_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'college'


class Department(models.Model):
    college = models.ForeignKey(College, null=True, on_delete=models.SET_NULL)
    department_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'department'
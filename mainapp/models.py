from django.db import models

# Create your models here.


class TemplateDetails(models.Model):
    id = models.AutoField(primary_key=True)
    template_name = models.TextField(max_length=255, default="", unique=True)
    title = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return f'{self.id}, {self.template_name}'


class FieldDetails(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.TextField(max_length=255, default="", null=False)
    type = models.TextField(max_length=255, default="", null=False)
    maxValue = models.IntegerField(null=True)
    pickList = models.JSONField(null=True)
    decimalPoint = models.CharField(max_length=255, null=True)
    templateid = models.ForeignKey(TemplateDetails, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return f'{self.id}, {self.label}'

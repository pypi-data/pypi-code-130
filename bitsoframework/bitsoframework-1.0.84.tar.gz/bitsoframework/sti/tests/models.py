from django.db import models
from django.db.models import SET_NULL

from bitsoframework.sti.models import STIModel


class Party(STIModel):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = "sti_party"


class Person(Party):
    cpf = models.CharField(max_length=20, null=False)

    class Meta(Party.Meta):
        pass


class Organization(Party):
    cnpj = models.CharField(max_length=20)


class Address(models.Model):
    name = models.CharField(max_length=20)
    party = models.ForeignKey(Party, null=True, blank=True, on_delete=SET_NULL)

    class Meta:
        db_table = "address"

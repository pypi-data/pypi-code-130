from django.test import TestCase

from django.test import TestCase

from bitsoframework.sti.tests.models import Person, Address, Organization, Party


class STITestCase(TestCase):

    def test_crud(self):
        """Make sure images are attached, retrieved and deleted"""

        person = Person.objects.create(cpf="123")
        organization = Organization.objects.create(cnpj="456")

        home_address = Address.objects.create(name="Home Address", party=person)
        corporate_address = Address.objects.create(name="Corporate Address", party=organization)

        home_address.refresh_from_db()
        corporate_address.refresh_from_db()

        self.assertIsNotNone(home_address.party)
        self.assertEqual(home_address.party.__class__, Person)
        self.assertEqual(home_address.party, person)
        self.assertIsNotNone(home_address.party.cpf)
        self.assertEqual(home_address.party.cpf, person.cpf)

        self.assertIsNotNone(corporate_address.party)
        self.assertEqual(corporate_address.party.__class__, Organization)
        self.assertEqual(corporate_address.party, organization)
        self.assertIsNotNone(corporate_address.party.cnpj)
        self.assertEqual(corporate_address.party.cnpj, organization.cnpj)

        person_queryset = Person.objects.all()
        organization_queryset = Organization.objects.all()
        party_queryset = Party.objects.all()

        self.assertEqual(1, person_queryset.count())
        self.assertEqual(person, person_queryset.first())

        self.assertEqual(1, organization_queryset.count())
        self.assertEqual(organization, organization_queryset.first())

        self.assertEqual(2, party_queryset.count())
        self.assertEqual(person, party_queryset.first())
        self.assertEqual(Person, party_queryset.first().__class__)
        self.assertEqual(Organization, party_queryset.last().__class__)

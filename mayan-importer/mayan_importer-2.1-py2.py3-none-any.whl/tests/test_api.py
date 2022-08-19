from rest_framework import status

from credentials.tests.mixins import StoredCredentialTestMixin
from mayan.apps.documents.events import (
    event_document_created, event_document_file_created,
    event_document_file_edited, event_document_version_created,
    event_document_version_page_created
)
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..events import (
    event_import_setup_created, event_import_setup_edited,
    event_import_setup_item_completed, event_import_setup_populate_ended,
    event_import_setup_populate_started, event_import_setup_process_ended,
    event_import_setup_process_started
)
from ..models import ImportSetup
from ..permissions import (
    permission_import_setup_create, permission_import_setup_delete,
    permission_import_setup_edit, permission_import_setup_process,
    permission_import_setup_view
)
from .mixins import (
    EventTestCaseMixin, ImportSetupAPIViewTestMixin,
    ImportSetupItemAPIViewTestMixin, ImportSetupItemTestMixin,
    ImportSetupTestMixin
)


class ImportSetupAPIViewTestCase(
    DocumentTestMixin, EventTestCaseMixin, ImportSetupAPIViewTestMixin,
    ImportSetupTestMixin, BaseAPITestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    def test_import_setup_create_api_view_no_permission(self):
        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_create_api_view_with_access(self):
        import_setup_count = ImportSetup.objects.count()

        self.grant_permission(permission=permission_import_setup_create)

        self._clear_events()

        response = self._request_test_import_setup_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self.test_import_setup)
        self.assertEqual(events[0].target, self.test_import_setup)
        self.assertEqual(events[0].verb, event_import_setup_created.id)

    def test_import_setup_delete_api_view_no_permission(self):
        self._create_test_import_setup()

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_delete_api_view_with_access(self):
        self._create_test_import_setup()

        import_setup_count = ImportSetup.objects.count()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_delete
        )

        self._clear_events()

        response = self._request_test_import_setup_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_detail_api_view_no_permission(self):
        self._create_test_import_setup()

        self._clear_events()

        response = self._request_test_import_setup_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('id' not in response.data)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_detail_api_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_view
        )

        self._clear_events()

        response = self._request_test_import_setup_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['id'], self.test_import_setup.pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_edit_via_patch_api_view_no_permssion(self):
        self._create_test_import_setup()

        import_setup_label = self.test_import_setup.label

        self._clear_events()

        response = self._request_test_import_setup_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_import_setup.refresh_from_db()
        self.assertEqual(
            self.test_import_setup.label, import_setup_label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_edit_via_patch_api_view_with_access(self):
        self._create_test_import_setup()

        import_setup_label = self.test_import_setup.label

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )

        self._clear_events()

        response = self._request_test_import_setup_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_import_setup.refresh_from_db()
        self.assertNotEqual(
            self.test_import_setup.label, import_setup_label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self.test_import_setup)
        self.assertEqual(events[0].target, self.test_import_setup)
        self.assertEqual(events[0].verb, event_import_setup_edited.id)

    def test_import_setup_list_api_view_no_permission(self):
        self._create_test_import_setup()

        self._clear_events()

        response = self._request_test_import_setup_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_list_api_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_view
        )

        self._clear_events()

        response = self._request_test_import_setup_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['id'], self.test_import_setup.pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class ImportSetupActionAPIViewTestCase(
    DocumentTestMixin, EventTestCaseMixin, ImportSetupItemAPIViewTestMixin,
    ImportSetupTestMixin, ImportSetupItemTestMixin,
    StoredCredentialTestMixin, BaseAPITestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_stored_credential()
        self._create_test_import_setup()

    def test_import_setup_clear_api_view_no_perimssion(self):
        self._create_test_import_setup_item()

        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_clear_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_clear_api_view_with_access(self):
        self._create_test_import_setup_item()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )

        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_clear_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_populate_api_view_no_permission(self):
        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_populate_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_populate_api_view_with_access(self):
        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )

        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_populate_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 2)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self.test_import_setup)
        self.assertEqual(events[0].target, self.test_import_setup)
        self.assertEqual(
            events[0].verb, event_import_setup_populate_started.id
        )

        self.assertEqual(events[1].action_object, None)
        self.assertEqual(events[1].actor, self.test_import_setup)
        self.assertEqual(events[1].target, self.test_import_setup)
        self.assertEqual(
            events[1].verb, event_import_setup_populate_ended.id
        )

    def test_import_setup_process_api_view_no_access(self):
        self._create_test_import_setup_item()

        document_count = self.test_document_type.documents.count()

        self._clear_events()

        response = self._request_test_import_setup_process_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self.test_document_type.documents.count(), document_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_process_api_view_with_access(self):
        self._create_test_import_setup_item()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )
        document_count = self.test_document_type.documents.count()

        self._clear_events()

        response = self._request_test_import_setup_process_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            self.test_document_type.documents.count(), document_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 8)

        test_document = Document.objects.last()
        test_document_file = test_document.file_latest
        test_document_version = test_document.versions.last()
        test_document_version_page = test_document_version.pages.first()

        self.assertEqual(events[0].actor, self.test_import_setup)
        self.assertEqual(events[0].target, self.test_import_setup)
        self.assertEqual(
            events[0].verb, event_import_setup_process_started.id
        )

        self.assertEqual(events[1].action_object, self.test_document_type)
        self.assertEqual(events[1].actor, test_document)
        self.assertEqual(events[1].target, test_document)
        self.assertEqual(events[1].verb, event_document_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_file)
        self.assertEqual(events[2].target, test_document_file)
        self.assertEqual(events[2].verb, event_document_file_created.id)

        self.assertEqual(events[3].action_object, test_document)
        self.assertEqual(events[3].actor, test_document_file)
        self.assertEqual(events[3].target, test_document_file)
        self.assertEqual(events[3].verb, event_document_file_edited.id)

        self.assertEqual(events[4].action_object, test_document)
        self.assertEqual(events[4].actor, test_document_version)
        self.assertEqual(events[4].target, test_document_version)
        self.assertEqual(events[4].verb, event_document_version_created.id)

        self.assertEqual(events[5].action_object, test_document_version)
        self.assertEqual(events[5].actor, test_document_version_page)
        self.assertEqual(events[5].target, test_document_version_page)
        self.assertEqual(
            events[5].verb, event_document_version_page_created.id
        )

        self.assertEqual(events[6].action_object, self.test_import_setup)
        self.assertEqual(events[6].actor, self.test_import_setup_item)
        self.assertEqual(events[6].target, self.test_import_setup_item)
        self.assertEqual(
            events[6].verb, event_import_setup_item_completed.id
        )

        self.assertEqual(events[7].action_object, None)
        self.assertEqual(events[7].actor, self.test_import_setup)
        self.assertEqual(events[7].target, self.test_import_setup)
        self.assertEqual(events[7].verb, event_import_setup_process_ended.id)

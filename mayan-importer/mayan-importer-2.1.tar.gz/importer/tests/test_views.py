from mayan.apps.documents.events import (
    event_document_created, event_document_file_created,
    event_document_file_edited, event_document_version_created,
    event_document_version_page_created
)
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.testing.tests.base import GenericViewTestCase

from credentials.tests.mixins import StoredCredentialTestMixin

from ..events import (
    event_import_setup_created, event_import_setup_edited,
    event_import_setup_item_completed, event_import_setup_populate_ended,
    event_import_setup_populate_started, event_import_setup_process_ended,
    event_import_setup_process_started
)
from ..models import ImportSetup, ImportSetupAction
from ..permissions import (
    permission_import_setup_create, permission_import_setup_delete,
    permission_import_setup_edit, permission_import_setup_process,
    permission_import_setup_view
)

from .mixins import (
    EventTestCaseMixin, ImportSetupActionTestMixin,
    ImportSetupActionViewTestMixin, ImportSetupTestMixin,
    ImportSetupItemTestMixin, ImportSetupViewTestMixin,
    ImportSetupItemViewTestMixin
)


class ImportSetupActionViewTestCase(
    StoredCredentialTestMixin, DocumentTestMixin, EventTestCaseMixin,
    ImportSetupActionTestMixin, ImportSetupActionViewTestMixin,
    ImportSetupTestMixin, GenericViewTestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_stored_credential()
        self._create_test_import_setup()

    def test_import_setup_action_backend_selection_view_no_permissions(self):
        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_backend_selection_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_action_backend_selection_view_with_permissions(self):
        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )
        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_backend_selection_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_action_create_view_no_permissions(self):
        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_create_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_action_create_view_with_permissions(self):
        self.grant_access(
            obj=self.test_import_setup, permission=permission_import_setup_edit
        )
        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_action_delete_view_no_permissions(self):
        self._create_test_import_setup_action()

        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_action_delete_view_with_access(self):
        self._create_test_import_setup_action()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )

        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_action_edit_view_no_permissions(self):
        self._create_test_import_setup_action()

        import_setup_action_label = self.test_import_setup_action.label

        self._clear_events()

        response = self._request_test_import_setup_action_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_import_setup_action.refresh_from_db()
        self.assertEqual(
            self.test_import_setup_action.label, import_setup_action_label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_action_edit_view_with_access(self):
        self._create_test_import_setup_action()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )

        self._clear_events()

        import_setup_action_label = self.test_import_setup_action.label

        response = self._request_test_import_setup_action_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_import_setup_action.refresh_from_db()
        self.assertNotEqual(
            self.test_import_setup_action.label, import_setup_action_label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_action_list_view_with_no_permission(self):
        self._create_test_import_setup_action()

        self._clear_events()

        response = self._request_test_import_setup_action_list_view()
        self.assertNotContains(
            response=response, text=self.test_import_setup_action.label,
            status_code=404
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_action_list_view_with_access(self):
        self._create_test_import_setup_action()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_view
        )

        self._clear_events()

        response = self._request_test_import_setup_action_list_view()
        self.assertContains(
            response=response, text=self.test_import_setup_action.label,
            status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class ImportSetupViewTestCase(
    StoredCredentialTestMixin, DocumentTestMixin, EventTestCaseMixin,
    ImportSetupTestMixin, ImportSetupViewTestMixin, GenericViewTestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_stored_credential()

    def test_import_setup_backend_selection_view_no_permissions(self):
        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_backend_selection_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_backend_selection_view_with_permissions(self):
        self.grant_permission(permission=permission_import_setup_create)

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_backend_selection_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_create_view_no_permissions(self):
        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_create_view_with_permissions(self):
        self.grant_permission(permission=permission_import_setup_create)

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self.test_import_setup)
        self.assertEqual(events[0].verb, event_import_setup_created.id)

    def test_import_setup_delete_view_no_permissions(self):
        self._create_test_import_setup()

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_delete_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_delete
        )

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_edit_view_no_permissions(self):
        self._create_test_import_setup()

        import_setup_label = self.test_import_setup.label

        self._clear_events()

        response = self._request_test_import_setup_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_import_setup.refresh_from_db()
        self.assertEqual(self.test_import_setup.label, import_setup_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_edit_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )

        import_setup_label = self.test_import_setup.label

        self._clear_events()

        response = self._request_test_import_setup_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_import_setup.refresh_from_db()
        self.assertNotEqual(self.test_import_setup.label, import_setup_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self.test_import_setup)
        self.assertEqual(events[0].verb, event_import_setup_edited.id)

    def test_import_setup_list_view_with_no_permission(self):
        self._create_test_import_setup()

        self._clear_events()

        response = self._request_test_import_setup_list_view()
        self.assertNotContains(
            response=response, text=self.test_import_setup.label,
            status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_list_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_view
        )

        self._clear_events()

        response = self._request_test_import_setup_list_view()
        self.assertContains(
            response=response, text=self.test_import_setup.label,
            status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class ImportSetupItemViewTestCase(
    StoredCredentialTestMixin, DocumentTestMixin, EventTestCaseMixin,
    ImportSetupTestMixin, ImportSetupItemTestMixin,
    ImportSetupItemViewTestMixin, GenericViewTestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_stored_credential()
        self._create_test_import_setup()

    def test_import_setup_clear_view_no_permission(self):
        self._create_test_import_setup_item()

        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_clear_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_clear_view_with_access(self):
        self._create_test_import_setup_item()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )

        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_clear_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_populate_view_no_permission(self):
        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_populate_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_populate_view_with_access(self):
        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )

        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_populate_view()
        self.assertEqual(response.status_code, 302)

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

    def test_import_setup_process_view_no_permission(self):
        self._create_test_import_setup_item()

        document_count = self.test_document_type.documents.count()

        self._clear_events()

        response = self._request_test_import_setup_process_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_document_type.documents.count(), document_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_process_view_with_access(self):
        self._create_test_import_setup_item()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )
        document_count = self.test_document_type.documents.count()

        self._clear_events()

        response = self._request_test_import_setup_process_view()
        self.assertEqual(response.status_code, 302)

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

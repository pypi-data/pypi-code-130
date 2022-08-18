from django.utils.translation import gettext_lazy as _

MENUS = {
    "NAV_MENU_CORE": [
        {
            "name": _("Class register"),
            "url": "#",
            "svg_icon": "mdi:book-open-outline",
            "vuetify_icon": "mdi-book-open-outline",
            "root": True,
            "validators": [
                "menu_generator.validators.is_authenticated",
                "aleksis.core.util.core_helpers.has_person",
            ],
            "submenu": [
                {
                    "name": _("Coursebook"),
                    "url": "select_coursebook",
                    "svg_icon": "mdi:book-education-outline",
                    "vuetify_icon": "mdi-book-education-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_coursebook_rule",
                        ),
                    ],
                },
                {
                    "name": _("Current lesson"),
                    "url": "lesson_period",
                    "svg_icon": "mdi:alarm",
                    "vuetify_icon": "mdi-alarm",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_lesson_menu_rule",
                        ),
                    ],
                },
                {
                    "name": _("Current week"),
                    "url": "week_view",
                    "svg_icon": "mdi:view-week-outline",
                    "vuetify_icon": "mdi-view-week-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_week_menu_rule",
                        ),
                    ],
                },
                {
                    "name": _("My groups"),
                    "url": "my_groups",
                    "svg_icon": "mdi:account-multiple-outline",
                    "vuetify_icon": "mdi-account-multiple-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_my_groups_rule",
                        ),
                    ],
                },
                {
                    "name": _("My overview"),
                    "url": "overview_me",
                    "svg_icon": "mdi:chart-box-outline",
                    "vuetify_icon": "mdi-chart-box-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_person_overview_menu_rule",
                        ),
                    ],
                },
                {
                    "name": _("My students"),
                    "url": "my_students",
                    "svg_icon": "mdi:account-school-outline",
                    "vuetify_icon": "mdi-account-school-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_my_students_rule",
                        ),
                    ],
                },
                {
                    "name": _("Assign group role"),
                    "url": "assign_group_role_multiple",
                    "svg_icon": "mdi:clipboard-account-outline",
                    "vuetify_icon": "mdi-clipboard-account-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.assign_grouprole_for_multiple_rule",
                        ),
                    ],
                },
                {
                    "name": _("All lessons"),
                    "url": "all_register_objects",
                    "svg_icon": "mdi:format-list-text",
                    "vuetify_icon": "mdi-format-list-text",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_register_objects_list_rule",
                        ),
                    ],
                },
                {
                    "name": _("Excuse types"),
                    "url": "excuse_types",
                    "svg_icon": "mdi:label-outline",
                    "vuetify_icon": "mdi-label-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_excusetypes_rule",
                        ),
                    ],
                },
                {
                    "name": _("Extra marks"),
                    "url": "extra_marks",
                    "svg_icon": "mdi:label-variant-outline",
                    "vuetify_icon": "mdi-label-variant-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_extramarks_rule",
                        ),
                    ],
                },
                {
                    "name": _("Manage group roles"),
                    "url": "group_roles",
                    "svg_icon": "mdi:clipboard-plus-outline",
                    "vuetify_icon": "mdi-clipboard-plus-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "alsijil.view_grouproles_rule",
                        ),
                    ],
                },
            ],
        }
    ]
}

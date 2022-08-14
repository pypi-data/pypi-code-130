from swapper import load_model

from notifications.base.admin import (
    AbstractCategoryAdmin,
    AbstractTemplateAdmin,
    AbstractNotificationAdmin,
)

from django.contrib import admin

Category = load_model("notifications", "Category")
Template = load_model("notifications", "Template")
Notification = load_model("notifications", "Notification")


@admin.register(Category)
class CategoryAdmin(AbstractCategoryAdmin):
    pass


@admin.register(Template)
class TempalteAdmin(AbstractTemplateAdmin):
    pass


@admin.register(Notification)
class NotificationAdmin(AbstractNotificationAdmin):
    pass

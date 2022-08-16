from swapper import swappable_setting

from notifications.base.models import (
    AbstractCategory,
    AbstractTemplate,
    AbstractNotification,
    AbstractUserHandlerSettings,
    AbstractUserCategorySettings,
)


class Category(AbstractCategory):
    class Meta(AbstractCategory.Meta):
        swappable = swappable_setting("notifications", "Category")
        abstract = False


class Template(AbstractTemplate):
    class Meta(AbstractTemplate.Meta):
        swappable = swappable_setting("notifications", "Template")
        abstract = False


class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        swappable = swappable_setting("notifications", "Notification")
        abstract = False


class UserCategorySettings(AbstractUserCategorySettings):
    class Meta(AbstractUserCategorySettings.Meta):
        swappable = swappable_setting("notifications", "UserCategorySettings")
        abstract = False


class UserHandlerSettings(AbstractUserHandlerSettings):
    class Meta(AbstractUserHandlerSettings.Meta):
        swappable = swappable_setting("notifications", "UserHandlerSettings")
        abstract = False

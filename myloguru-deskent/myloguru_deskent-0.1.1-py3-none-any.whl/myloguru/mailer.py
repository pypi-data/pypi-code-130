from myloguru.my_loguru import MyLogger


class MailerLogger(MyLogger):
    """Add new methods for default loguru.logger"""

    def admin(self, text, *args, **kwargs):
        self.logger.log("ADMIN", text, *args, **kwargs)

    def token(self, text, *args, **kwargs):
        self.logger.log("TOKEN", text, *args, **kwargs)

    def openai(self, text, *args, **kwargs):
        self.logger.log("OPENAI", text, *args, **kwargs)

    def get_mailer(self) -> 'MailerLogger':
        default: MyLogger = self.get_default()
        self.levels = default.levels
        self.add_level("ADMIN", "<fg #d787ff>", no=100)
        self.add_level("TOKEN", "<white>", no=90)
        self.add_level("OPENAI", "<fg #d787ff>", no=80)
        self.add_logger(enqueue=True, level='ADMIN', rotation="100 MB")
        self.add_logger(enqueue=True, level='TOKEN', rotation="50 MB")
        self.add_logger(enqueue=True, level='OPENAI', rotation="50 MB")

        return self


def get_mailer_logger(
        level: int = 20,
        parent_dir: str = '',
        logs_dir: str = 'logs',
        add_date_dir: bool = True,
        serialize_errors: bool = False
) -> MailerLogger:
    return MailerLogger(
        level=level,
        parent_dir=parent_dir,
        logs_dir=logs_dir,
        date_dir=add_date_dir,
        serialize=serialize_errors
    ).get_mailer()

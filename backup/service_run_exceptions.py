class BaseServiceRunException(Exception):
    pass


class NotAServiceRunItem(BaseServiceRunException):
    pass


class TimestampMissing(BaseServiceRunException):
    pass

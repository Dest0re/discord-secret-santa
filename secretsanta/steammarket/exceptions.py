class SteamStoreException(Exception):
    pass


class LoginRequired(SteamStoreException):
    pass


class ApiError(SteamStoreException):
    pass


class PackageDoesNotExist(SteamStoreException):
    pass


class AppDoesNotExist(SteamStoreException):
    pass


class LoginError(SteamStoreException):
    pass


class PaymentError(SteamStoreException):
    pass


class FriendInviteError(SteamStoreException):
    pass

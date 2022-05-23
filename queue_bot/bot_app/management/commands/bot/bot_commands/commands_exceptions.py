class CommandNotExistError(Exception):
    pass


class ChatAlreadySavedError(Exception):
    pass


class MemberNotSavedError(Exception):
    pass


class QueueAlreadySaved(Exception):
    pass


class ChatDoesNotExistError(Exception):
    pass


class QueueDoesNotExistError(Exception):
    pass

class BaseInfoException(Exception):
    def __init__(self, info):
        self.info = info


class ObjectNotFoundException(BaseInfoException):
    def __init__(self, info):
        super(ObjectNotFoundException, self).__init__(info)


class ObjectAlreadyAddedException(BaseInfoException):
    def __init__(self, info):
        super(ObjectAlreadyAddedException, self).__init__(info)


class ArgMismatchException(BaseInfoException):
    def __init__(self, info):
        super(ArgMismatchException, self).__init__(info)


class SubprocessFailedException(BaseInfoException):
    def __init__(self, info):
        super(SubprocessFailedException, self).__init__(info)


class SubprocessTimeoutException(BaseInfoException):
    def __init__(self, info):
        super(SubprocessTimeoutException, self).__init__(info)


class ExitCleanException(BaseInfoException):
    def __init__(self):
        super(ExitCleanException, self).__init__('')


class SocketException(BaseInfoException):
    def __init__(self, info):
        super(SocketException, self).__init__(info)


class InvalidConfigurationException(BaseInfoException):
    def __init__(self, config, reason):
        super(InvalidConfigurationException, self).__init__(
            reason + " in config <" + str(config) + ">")


class PacketParsingException(BaseInfoException):
    def __init__(self, info, fatal=True):
        super(PacketParsingException, self).__init__(info)
        self.fatal = fatal


class FileNotFoundException(BaseInfoException):
    def __init__(self, info):
        super(FileNotFoundException, self).__init__(info)

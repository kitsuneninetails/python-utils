class ObjectNotFoundException(Exception):
    def __init__(self, info):
        super(ObjectNotFoundException, self).__init__(info)


class ObjectAlreadyAddedException(Exception):
    def __init__(self, info):
        super(ObjectAlreadyAddedException, self).__init__(info)


class ArgMismatchException(Exception):
    def __init__(self, info):
        super(ArgMismatchException, self).__init__(info)


class SubprocessFailedException(Exception):
    def __init__(self, info):
        super(SubprocessFailedException, self).__init__(info)


class SubprocessTimeoutException(Exception):
    def __init__(self, info):
        super(SubprocessTimeoutException, self).__init__(info)


class ExitCleanException(Exception):
    def __init__(self):
        super(ExitCleanException, self).__init__('')


class SocketException(Exception):
    def __init__(self, info):
        super(SocketException, self).__init__(info)


class InvalidConfigurationException(Exception):
    def __init__(self, config, reason):
        super(InvalidConfigurationException, self).__init__(
            reason + " in config <" + str(config) + ">")


class PacketParsingException(Exception):
    def __init__(self, info, fatal=True):
        super(PacketParsingException, self).__init__(info)
        self.fatal = fatal


class FileNotFoundException(Exception):
    def __init__(self, info):
        super(FileNotFoundException, self).__init__(info)

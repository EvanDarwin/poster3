def register_openers():
    """
    DEPRECATED - This function will be removed in version 1.0.0

    This function is now a placeholder for backwards compatibility
    """

    class DummyOpener(object):
        def add_handler(self, *args, **kwargs):
            pass

    return DummyOpener()

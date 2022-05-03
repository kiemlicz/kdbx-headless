import kdbx_headless.kdbx


class SecretProvider:
    def __init__(self, config) -> None:
        klass = getattr(kdbx_headless.kdbx, config['kdbx_class'])
        kdbx_config = config['kdbx']
        self.service = klass(**kdbx_config)

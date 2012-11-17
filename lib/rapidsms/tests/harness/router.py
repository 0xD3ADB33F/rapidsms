from django.conf import settings

from rapidsms.tests.harness.base import CreateDataTest
from rapidsms.tests.harness import backend
from rapidsms.router import lookup_connections


__all__ = ('CustomRouter', 'MockBackendRouter')


class CustomRouter(CreateDataTest):
    """
    Inheritable TestCase-like object that allows Router customization
    """
    router_class = 'rapidsms.router.blocking.BlockingRouter'
    backends = {}

    def _pre_rapidsms_setup(self):
        self._INSTALLED_BACKENDS = getattr(settings, 'INSTALLED_BACKENDS', {})
        setattr(settings, 'INSTALLED_BACKENDS', self.backends)
        self._RAPIDSMS_ROUTER = getattr(settings, 'RAPIDSMS_ROUTER', None)
        setattr(settings, 'RAPIDSMS_ROUTER', self.router_class)

    def _post_rapidsms_teardown(self):
        setattr(settings, 'INSTALLED_BACKENDS', self._INSTALLED_BACKENDS)
        setattr(settings, 'RAPIDSMS_ROUTER', self._RAPIDSMS_ROUTER)

    def __call__(self, result=None):
        self._pre_rapidsms_setup()
        super(CustomRouter, self).__call__(result)
        self._post_rapidsms_teardown()


class MockBackendRouter(CustomRouter):
    """
    Test exentions with BlockingRouter and MockBackend, and utility functions
    to examine outgoing messages
    """
    backends = {'mockbackend': {'ENGINE': backend.MockBackend}}

    def _post_rapidsms_teardown(self):
        super(MockBackendRouter, self)._post_rapidsms_teardown()
        self.clear()

    @property
    def outbox(self):
        return backend.outbox

    def clear(self):
        if hasattr(backend, 'outbox'):
            backend.outbox = []

    def lookup_connections(self, backend='mockbackend', identities=None):
        """loopup_connections wrapper to use mockbackend by default"""
        if not identities:
            identities = []
        return lookup_connections(backend, identities)

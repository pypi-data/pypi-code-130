from abc import ABC, abstractmethod

from .. import services


# -------------------
## Abstract base class for storage functions
class Storage(ABC):
    # -------------------
    ## factory to generate the child class given the storage type
    #
    # @return a storage object
    @classmethod
    def factory(cls):
        if services.cfg.storage_type == 'dev':
            from .storage_dev import StorageDev
            return StorageDev()

        services.logger.err(f'unknown storage type: {services.cfg.storage_type}')
        services.harness.abort()

    # -------------------
    ## (abstract) terminate
    #
    # @return None
    @abstractmethod
    def term(self):
        pass  # pragma: no cover

    # -------------------
    ## (abstract) save the protocol information
    #
    # @param protocols  the protocol information to save
    # @return None
    @abstractmethod
    def save_protocol(self, protocols):
        pass  # pragma: no cover

    # -------------------
    ## (abstract) get saved protocol information
    #
    # @return None
    @abstractmethod
    def get_protocols(self):
        pass  # pragma: no cover

    # -------------------
    ## (abstract) save the trace matrix information
    #
    # @param trace   the trace matrix information to save
    # @return None
    @abstractmethod
    def save_trace(self, trace):
        pass  # pragma: no cover

    # -------------------
    ## (abstract) get saved trace matrix information
    #
    # @return None
    @abstractmethod
    def get_trace(self):
        pass  # pragma: no cover

    # -------------------
    ## (abstract) save the summary information
    #
    # @param summary   the summary information to save
    # @return None
    @abstractmethod
    def save_summary(self, summary):
        pass  # pragma: no cover

    # -------------------
    ## (abstract) get saved summary information
    #
    # @return None
    @abstractmethod
    def get_summary(self):
        pass  # pragma: no cover

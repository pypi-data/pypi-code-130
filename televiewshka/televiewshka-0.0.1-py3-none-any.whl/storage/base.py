from abc import ABC, abstractmethod


class AbstractUserOperations(ABC):
	@abstractmethod
	def __enter__(self, *args, **kwargs):
		pass

	@abstractmethod
	def get_current_view(self) -> str:
		""" Get current view of user with `user_id` """
		pass

	@abstractmethod
	def set_current_view(self, view_name: str) -> None:
		""" At minimum, this one and `get_current_view` are
			the only operations that must be implemented for all storages.
			It is used by adaptors to update `current_view` flag 
			when the new view is rendered
			It is then used e.g. in dispatching text messages to 
			investigate whether text input is acceptable 
			on this view or not """
		pass

	@abstractmethod
	def __exit__(self, ext_type, ext_val, ext_tb):
		pass


class AbstractAsyncUserOperations(ABC):
	@abstractmethod
	async def __aenter__(self, *args, **kwargs):
		pass

	@abstractmethod
	async def get_current_view(self) -> str:
		pass

	@abstractmethod
	async def set_current_view(self, view_name: str) -> None:
		pass

	@abstractmethod
	async def __aexit__(self, ext_type, ext_val, ext_tb):
		pass


class AbstractStorage(ABC):
	@abstractmethod
	def select_user(self, user_id: int) -> AbstractUserOperations:
		""" Must return an instance that implements contextmanager
			methods: `__enter__` and `__exit__` 
			
			`__exit__` supposed to roll back all changes in
			case of exception occures while in `with` block

			Builtin adaptors only use it to get and update `current_view` flag 
			for a particular user, so basic storage classes 
			returns contextmanager that handles only these operations. 
			This behaviour can be extended though """
		pass


class AbstractAsyncStorage(ABC):
	@abstractmethod
	def select_user(self, user_id: int) -> AbstractAsyncUserOperations:
		""" An async version of `AbstractStorage` """
		pass

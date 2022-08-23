import time
import inspect
from typing import Dict, Optional, Literal, Union, Type, List, TYPE_CHECKING, TypedDict
from pydantic import BaseModel, Field
import datetime
from croniter import croniter
from logging import getLogger

log = getLogger(__name__)
if TYPE_CHECKING:
    from buffy.buffyserver.api.v1.models import Request, Response
    from buffy.buffyserver.backend.storage.interface import StorageInterface


class BaseReCachingStrategy(BaseModel):
    strategy_name: str = None

    def __eq__(self, other):
        if inspect.isclass(other):
            return other.__name__ == self.__class__.__name__
        elif isinstance(other, str):
            return other == self.__class__.__name__
        return isinstance(other, self.__class__)

    def request_needs_recache(
        self,
        request: "Request",
        latest_response: "Response",
        strategy_state: dict,
        storage: "StorageInterface",
    ) -> bool:
        pass


class ReCachingStrategy:
    """
    Wrapper class to contain all possible ReCachingStrategies.
    A ReCachingStrategy defines how an when a remote resource should be updated
    """

    @classmethod
    def list(cls) -> List[Type[BaseReCachingStrategy]]:
        """List all available strategies"""
        return [
            cls_attribute
            for cls_attribute in cls.__dict__.values()
            if inspect.isclass(cls_attribute)
        ]

    class never(BaseReCachingStrategy):
        """never -
        Once downlaoded we will serve only this cached file. no matter how often it is requested.
        This is usefull for files that will be 100% static.
        """

        strategy_name: Literal["never"] = Field(default="never", const=True)

        def request_needs_recache(
            self,
            request: "Request",
            latest_response: "Response",
            strategy_state: dict,
            storage: "StorageInterface",
        ) -> bool:
            return False

    class age(BaseReCachingStrategy):
        """Age Strategy
        
        Buffy will redownload when the cached version has a certain age in seconds.  
        The default age is 3600sec.  
        This is usefull for dynamic remote resources, where the webserver wont provide any informations about the \
            state of the resource like "etag", "last_modified_datetime" or "size_in_bytes"

        Args:
            seconds (int): \
                default:3600 - The duration a resource will be cached until it gets a redownload from the source \
                
        """

        strategy_name: Literal["age"] = Field(default="age", const=True)
        seconds: int = 3600

        def request_needs_recache(
            self,
            request: "Request",
            latest_response: "Response",
            strategy_state: dict,
            storage: "StorageInterface",
        ) -> bool:
            if request.latest_requests and latest_response.cached_datetime_utc is None:
                return True
            if (
                latest_response.cached_datetime_utc is not None
                and (
                    datetime.datetime.utcnow() - latest_response.cached_datetime_utc
                ).total_seconds()
                > request.cache_configuration.recaching_strategy.seconds
            ):
                return True
            return False

    class cron(BaseReCachingStrategy):
        """cron - Strategy
        Buffy will redownload the remote resource in an certain interval. Defined in the Linux cron format.
        Similar to the "age"-Strategy, but allows more flexibility for more complex situations.
        This is usefull for dynamic remote resources, where the webserver wont provide any informations about the state of the resource like "etag", "last_modified_datetime" or "size_in_bytes"

        params:
            cron - str - a standard cron definition https://en.wikipedia.org/wiki/Cron

            run_at_start - bool - regardless of the cron schedule, Buffy will redownload the resource once when Buffy just started
        """

        strategy_name: Literal["cron"] = Field(default="cron", const=True)
        cron: str = "0 0 * * *"
        run_at_start: bool = True

        def request_needs_recache(
            self,
            request: "Request",
            latest_response: "Response",
            strategy_state: dict,
            storage: "StorageInterface",
        ) -> bool:
            if TYPE_CHECKING:
                request.cache_configuration.recaching_strategy: ReCachingStrategy.cron = (
                    request.cache_configuration.recaching_strategy
                )

            if request.id not in strategy_state:
                #  init cron
                start_time: datetime.datetime = datetime.datetime.utcnow()
                strategy_state[request.id]: Dict[
                    str, Union[croniter, datetime.datetime]
                ] = {}
                new_cron_job = croniter(
                    request.cache_configuration.recaching_strategy.cron, start_time
                )
                strategy_state[request.id]["cron_job"] = new_cron_job
                strategy_state[request.id]["start_time"] = start_time
                strategy_state[request.id]["next"] = new_cron_job.get_next(
                    datetime.datetime
                )
                if request.cache_configuration.recaching_strategy.run_at_start:
                    return True
            next_cron_time: datetime.datetime = strategy_state[request.id]["next"]
            cron_job: croniter = strategy_state[request.id]["cron_job"]
            if next_cron_time <= datetime.datetime.utcnow():
                strategy_state[request.id]["next"] = cron_job.get_next(
                    datetime.datetime
                )
                return True
            return False

    class when_requested(BaseReCachingStrategy):
        """when_requested  - Strategy
        Default Strategy!
        Buffy will redownload the resource when the client requests the resource.
        This is the most simple scenario which is closest to a classic just-download case but with a fallback safeguard;
        If the remote resource fails to download, buffy can fallback to an older cached version of the resource, if available.

        **HINT**: Multiple request during one server tick (default 0.3s), will be bundled and share one response. \
            Example: If you simultaneously request 5 numbers from a REST API that generates random numbers, you will most likely just get same number for every request.
            In cases like this you maybe better off, bypassing a caching middleware like Buffy.
        """

        strategy_name: Literal["when_requested"] = Field(
            default="when_requested", const=True
        )

        def request_needs_recache(
            self,
            request: "Request",
            latest_response: "Response",
            strategy_state: dict,
            storage: "StorageInterface",
        ) -> bool:
            if request.latest_requests:
                return True
            return False

    class when_remote_changed(BaseReCachingStrategy):
        """when_remote_changed  - Strategy
        Buffy will ask the webserver of the remote resource about the state of the resource.
        Via "etag", "last_modified_datetime" or "size_in_bytes" Buffy can determine if the resource changed.
        If it has changed Buffy will download and cache the newer version.
        This is usefull for scenarios where the client need to have the newest version instant and reliable available.

        params:
            check_interval_sec
        """

        strategy_name: Literal["when_remote_changed"] = Field(
            default="when_remote_changed", const=True
        )
        check_interval_sec: int = 43200

        def request_needs_recache(
            self,
            request: "Request",
            latest_response: "Response",
            strategy_state: dict,
            storage: "StorageInterface",
        ) -> bool:
            if TYPE_CHECKING:
                request.cache_configuration.recaching_strategy: ReCachingStrategy.when_remote_changed = (
                    request.cache_configuration.recaching_strategy
                )
            from buffy.tools.stuborn_downloader import StubornDownloader

            if not request.id in strategy_state:
                strategy_state[request.id] = 0
            remote_file_change_last_check_time_unix_epoch: float = strategy_state[
                request.id
            ]
            if (
                remote_file_change_last_check_time_unix_epoch
                + request.cache_configuration.recaching_strategy.check_interval_sec
                > time.time()
            ):
                return False
            remote_file_change_last_check_time_unix_epoch = time.time()
            strategy_state[request.id] = remote_file_change_last_check_time_unix_epoch
            potential_next_response_header = StubornDownloader(
                request=request
            ).get_response_content_attrs()
            if (
                not potential_next_response_header
                and not potential_next_response_header.etag
                and not potential_next_response_header.last_modified_datetime_utc
                and not potential_next_response_header.size_in_bytes
            ):
                err_msg = f"The file can not be recached with strategy 'ReCachingStrategy.{ReCachingStrategy.when_remote_changed.__name__}'! Can not determine if target file of request (id:'{request.id}',url:'{request.url}' changed. The server at '{request.url}' does not provide any informations. Please use another caching strategy than {ReCachingStrategy.when_remote_changed}."
                log.error(err_msg)
                latest_response.download_stats.error = err_msg
                storage.update_response(latest_response)
                return False

            attr_comparison_sequence: List[str] = [
                "etag",
                "last_modified_datetime",
                "size_in_bytes",
            ]
            for attr in attr_comparison_sequence:
                if (
                    hasattr(potential_next_response_header, attr)
                    and hasattr(latest_response, attr)
                ) and (
                    getattr(potential_next_response_header, attr)
                    != getattr(latest_response, attr)
                ):
                    return True
            return False

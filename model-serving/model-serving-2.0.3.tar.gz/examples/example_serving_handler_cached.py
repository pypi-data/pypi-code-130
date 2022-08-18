from aylien_model_serving.cached_app_factory import CachedFlaskWrapper
from .example_serving_handler import process_request


def run_app():
    routes = [{"endpoint": "/",
               "callable": process_request,
               "methods": ["POST"]}]
    return CachedFlaskWrapper.create_app(routes)

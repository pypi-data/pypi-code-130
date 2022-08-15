from . import BookService_pb2_grpc as importStub

class BookServiceService(object):

    def __init__(self, router):
        self.connector = router.get_connection(BookServiceService, importStub.BookServiceStub)

    def checkBookPresence(self, request, timeout=None):
        return self.connector.create_request('checkBookPresence', request, timeout)
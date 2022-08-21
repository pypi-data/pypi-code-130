"""Some utilities"""


def is_first_visit(request):
    """Assumes that requests without any cookies are first-time requests (to be used for inlining critical css later)"""
    return len(request.COOKIES) == 0

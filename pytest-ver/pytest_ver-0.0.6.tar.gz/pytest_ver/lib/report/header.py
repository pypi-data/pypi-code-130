from .. import services


# -------------------
## holds Header information
class Header:
    # -------------------
    ## constructor
    def __init__(self):
        ## holds content for left side of header
        self.left = ''

        ## holds content for center section of header
        self.middle = ''

        ## holds content for right side of header
        self.right = ''

    # -------------------
    ## save a header item
    #
    # @param item    the name of the item to set: left, middle or right
    # @param value   the value to set
    # @return None
    def __setitem__(self, item, value):
        if item == 'left':
            self.left = value
            return

        if item == 'middle':
            self.middle = value
            return

        if item == 'right':  # pragma: no cover
            self.right = value
            return

        services.logger.err(f'ERR bad item name: {item}')  # pragma: no cover
        services.harness.abort()  # pragma: no cover

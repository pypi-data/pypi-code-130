import curses
from pytermwindows.Window import Window

class ScrollWindow( Window ):
    """
    A window to handle writing data to the terminal using the `curses` library. This window is specifically designed to write content that is too long to be shown in full
    and instead should be presented scrollably.

    Attributes
    ----------
    window : curses.window
        The main curses window object.
    width : int
        The width of the window in characters per line.
    height : int
        The height of the window as maximal number of lines.
    children : dict
        A dictionary of sub-windows and panes that may be stored inside the main window.
        These can be added to using `add_child`, and accessed directly or via `get_child`.
    name : str
        The name of this window.
    parent : Window
        The parent window of this window. This will be automatically set in case a window is added via `add_child`.

    Setting Updates
    
        set_update_interval
            Set the update interval. The Window supports a second time interval (measured in seconds rather than milliseconds)
            in which periodic updates may be performed such as reading external data files to update the window content, while
            allowing the window itself to render at a much faster rate.
        can_update
            Check if the window can update. If the update interval has been reached, this will return 
            `True` and reset the internal update counter.
        update_counter
            Increment the update counter. This should be called each time the window is refreshed.


    Parameters
    ----------
    width : int
        Width of the window in characters per line.
    height : int
        Height of the window as maximal number of lines.
    start_line : int
        Start line of the window.
    refresh : int
        Refresh rate of the window in milliseconds.
    waitkey : int
        Wait time between each refresh in milliseconds.
    use_color : bool
        Use colors if available. This will slow down the rendering a bit...
    """

    up = -1
    down = 1

    def __init__( self, name : str = None, width : int = None, height : int = None, start_line = 0, refresh : int = 50, waitkey : int = 50, use_color : bool = False ):
        super().__init__( name, width, height, start_line, refresh, waitkey, use_color )
        
        # initialize data indices for an 
        # iterable to print to the scroll window
        self.top = 0
        self.bottom = self.height 
        
        self.up_key = curses.KEY_UP
        self.down_key = curses.KEY_DOWN

    def set_scroll_range( self, bottom : int ):
        """
        Set the number of lines to print after the top line within the scroll window.
        This will be used to subset any iterable data to write to the scroll window.

        Parameters
        ----------
        bottom : int
            The number of lines to print after the top line.
        """
        self.bottom = bottom

    def _init( self ):
        super()._init()
        self.window.scrollok(True)
        self.window.idlok(True)

    def scroll_range( self, as_slice : bool = False ):
        """
        Get the top and bottom index of the data to display in the scroll window.

        Parameters
        ----------
        as_slice : bool
            If True then return a slice object instead of a tuple of the top and bottom indices.
        """
        if as_slice:
            return slice( self.top, self._bottom_index() )
        return self.top, self._bottom_index()


    def crop_data_to_scroll_range( self, data ):
        """
        Crop the data to the scroll range.

        Parameters
        ----------
        data : iterable
            The data to crop. 
        """
        if self.top < 0: 
            self.top = 0
        elif self._bottom_index() >= len(data):
            self.top = len(data) - self.bottom
        return data[ self.top : self._bottom_index() ]

    def contents( self, **kwargs ):
        
        # self.window.erase()

        self.write( self.to_first_line, 0, "-" * 50 )
        self.write( self.to_next_line, 0, "This is a ScrollWindow"  )
        self.write( self.to_next_line, 0, "-" * 50 )

        maxval = 200
        _data = [ str(i) + "\ttest" * 5 for i in range( maxval ) ]
        self.resize( len(_data) + 5, 200 )

        self.auto_scroll( restrict = len(_data) )
       
        data = _data[ self.scroll_range( as_slice = True ) ]
        for idx, line in enumerate(data):
            self.write( self.to_next_line, 0, line )

        
        self.write( self.to_next_line, 0, "-" * 50 )
        self.write( self.to_next_line, 0, "End of ScrollWindow" )
        self.write( self.to_next_line, 0, "-" * 50 )

        self.quit_on( keystring = "q" )
        self.refresh()

    def crop_data_to_scroll_range( self, data ):
        """
        Return a subset of the data to display in the scroll window.
        """
        return data[ self.top : self._bottom_index() ]

    def set_scroll_keys( self, up_key : int, down_key : int ):
        """
        Set the keys to scroll the window.

        Parameters
        ----------
        up_key : int
            The key to scroll up at.
        down_key : int
            The key to scroll down at.
        """
        self.up_key = up_key
        self.down_key = down_key

    def auto_scroll( self, restrict : int = None ):
        """
        Automatically checks for the key input as either up or down arrow keys and scrolls accordingly.

        Parameters
        ----------
        restrict : int
            The maximum number of entries to scroll.
            This can be for instance the length of the data to ensure it 
            does not scroll out of the window. By default the window height is used.

        Returns
        -------
        bool
            True if the current top index has been changed, False otherwise.
        """
        cmd = self.keycode
        if cmd == self.up_key:
            self.scroll_up()
            return True

        elif cmd == self.down_key:
            # set the maximal value to which to adjust the current line
            # either based on the window size or some externally provided max value 
            # such as the data length.
            self.scroll_down( restrict = restrict )
            return True
        return False

    def scroll( self, direction ):
        """
        Scroll the dataa by n entries either up or down.

        Parameters
        ----------
        direction : int
            The direction to scroll in numbers of entries. 
            If this is negative then the direction is upward. 
            If this is positive then the direction is downward.
        """
        # self.window.scroll( direction )
        self.top = self.top + direction

    def scroll_up( self, n : int = 1 ):
        """
        Scroll up n data entries.
        
        Parameters
        ----------
        n : int
            The number of entries to scroll up.
        
        """
        # self.window.scroll( -n )
        self.top = max( self.top - n, 0 )

    def scroll_down( self, n : int = 1, restrict : int = None ):
        """
        Scroll down n data entries.
        
        Parameters
        ----------
        n : int
            The number of entries to scroll down.
        restrict : int
            The maximum number of entries to scroll. By default this will be the number of lines in the window,
            but this can be set to a different value such as the length of the currently displayed data.
        """
        # self.window.scroll( n )
        restrict = self.height - 1 if restrict is None else restrict
        value = min( self.top + n, restrict - self.bottom )
        self.top = min( self.top + n, value )

    def _bottom_index( self ):
        """
        Get the bottom index of the scroll window.
        """
        return self.top + self.bottom #min( self.top + self.bottom, self.height )         

if __name__ == '__main__':

    win = ScrollWindow( height = 100, width = 50 )
    win.set_scroll_range( 10 )
    win.run()

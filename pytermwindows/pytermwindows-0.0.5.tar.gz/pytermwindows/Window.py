import curses
from collections.abc import Iterable
import logging

logger = logging.getLogger("pytermwindows")

class Window:
    """
    A window to handle writing python data to the terminal using the `curses` library.
    It offers a number of features to make it easier to write to the terminal in specific settings.

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
    def __init__(
                    self,
                    name : str = None,
                    width : int = None, 
                    height : int = None,
                    start_line : int = 0,
                    refresh : int = 100,
                    waitkey : int = 50,
                    use_color : bool = False,
                ):
        """
        Set up a new curses main window.

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
        self.children = {} # a dictionary of sub-windows and panes that may be stored inside the main window...
        self.name = name # the name of this window...
        self.parent = None # the parent window of this window...
        self.colors = {}

        self.setup( width, height, start_line, refresh, waitkey, use_color )

        # define some attributes in case we wish to periodically get refreshed content to write...
        self.__update_counter__ = 0 
        self.__update_performance__ = 0.9
        self.__update_due__ = 5 # just use 5 seconds interval by default
        self.__update_refs__ = self.__update_performance__ * 1000 / ( self._refresh_delay + self.waitkey )

    
    def setup( self, 
                width : int = None, 
                height : int = None,
                start_line : int = 0,
                refresh : int = 100,
                waitkey : int = 50,
                use_color : bool = False,
            ):
        """
        Settings for the window.

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
        self.width = width if width else 1
        self.height = height if height else 1
        self._lines = start_line
        self._first_line = start_line
        self._max_lines = start_line
        self._refresh_delay = refresh
        self.waitkey = waitkey
        self._use_color = use_color


    def contents( self, **kwargs ):
        """
        The actual content of the window. 
        This will be the method called by `run`.
        """
        self.write( 0, 0, "-" * 50 )
        self.write( 1, 0, "This is a MainWindow" )
        self.write( 2, 0, "-" * 50 )
        self.write( 3, 0, "Press q to exit" )

        # other stuff here...
        cmd = self.keystring
        self.quit_on( keystring = "q" )

        if cmd:
            self.write( 4, 0, f"You pressed {cmd}" )

        self.auto_adjust_size()
        self.reload()
    
    def run(self, **kwargs):
        """
        Run the main window.
        """
        try:

            self._init()
            
            while True:
            
                self.contents(**kwargs)
                self.auto_adjust_size()

        except KeyboardInterrupt:
            print( "Exiting..." )

        finally:
            self._destroy()

    def quit_on( self, keycode : int = None, keystring : str = None ):
        """
        Quit the window when the given keycode or keystring is pressed.

        Parameters
        ----------
        keycode : int
            The keycode of the key that will quit the window.
        keystring : str
            The keystring of the key that will quit the window.
        """
        if not keystring and not keycode:
            raise ValueError( "Either keycode or keystring must be given." )
        if keystring:
            if self.keystring == keystring:
                self.exit()
        elif keycode:
            if self.keycode == keycode:
                self.exit()
    
    def exit( self ):
        """
        Exit the window via keyboard interrupt.
        """
        raise KeyboardInterrupt()

    def reload( self ):
        """
        Reload the window.
        This will erase, refresh, and reset the line counter.
        """
        self.erase()
        self.reset_lines()
    
    def erase( self ):
        """
        Erase the window contents and refresh.
        """
        self.window.erase()

    def refresh( self ):
        """
        Refresh the window.
        """
        self.window.refresh()
    
    def add_child( self, child ):
        """
        Add a child window or pane to the main window.

        Parameters
        ----------
        child
            The child window or pane to add.
        """
        self.children[child.name] = child
        child.parent = self
        child.window.refresh()

    def get_child( self, name ):
        """
        Get a child window or pane from the main window.

        Parameters
        ----------
        name : str
            The name of the child window or pane to get.
        """
        return self.children.get( name, None )

    def write( self, line : int, pos : int, string : str, refresh : bool = False, clear : bool = False ):
        """
        Write a string to the window.

        Parameters
        ----------
        line : int
            The line to write to.
        pos : int
            The position within the line to start writing at.
        string : str
            The string to write.
        refresh : bool
            Whether to refresh the window after writing.
        clear : bool
            Whether to clear the line before writing.
        """
        self.write_to( self.window, line, pos, string, refresh, clear )
    
    def write_to( self, window_or_pane, line : int, pos : int, string : str, refresh : bool = False, clear : bool = False ):
        """
        Write a string to a specific (sub)window or pane.

        Parameters
        ----------
        window_or_pane 
            The window or pane to write to.
        line : int
            The line to write to.
        pos : int
            The position within the line to start writing at.
        string : str
            The string to write.
        refresh : bool
            Whether to refresh the window after writing.
        clear : bool
            Whether to clear the line before writing.
        """

        if self.is_linewise_iterable( line, string ):
            for l,s in zip( line, string ):
                if clear: 
                    window_or_pane.move( l, 0 )
                    window_or_pane.clrtoeol()

                self._write_to( window_or_pane, l, pos, s, refresh )
                self._modify_line( self.line_diff( l ) )

        elif self.is_columwise_iterable( pos, string ):
            if clear: 
                window_or_pane.move( line, 0 )
                window_or_pane.clrtoeol()
                
            for p,s in zip( pos, string ):
                self._write_to( window_or_pane, line, p, s, refresh )

        else:
            if clear:
                window_or_pane.move( line, 0 )
                window_or_pane.clrtoeol()
            self._write_to( window_or_pane, line, pos, string, refresh )

    def auto_adjust_size( self ):
        """
        Automatically adjust the size of the window in case of terminal resize.
        """
        if self.keycode == curses.KEY_RESIZE:
            self.adjust_size()

    def resize( self, height : int , width : int ):
        """
        Resize the window.

        Parameters
        ----------
        height : int
            The new height of the window (in numbers of lines).
        width : int
            The new width of the window (in numbers of characters per line).
        """
        curses.resizeterm( height, width )
        # self.window.resize( height, width )
        self.window.clear()
        self._upack_size()
        self.window.refresh()

    def adjust_size(self):
        """
        Resizes the window to terminal size.
        """
        curses.resizeterm( *self.size )
        self.height, self.width = self.size
        self.window.clear()
        self.window.refresh()

    def colored( self, text : str, color : str ):
        """
        Turn a string to a tuple with a color.

        Parameters
        ----------
        text : str
            The string to turn to a colored tuple.
        color : str
            The color to use.
        """
        if not self._use_color:
            logger.warning( "Color is not enabled." )
            return text
        col = self.colors.get( color, None )
        if col:
            return ( text, col )
        else:
            raise ValueError( f"Color {color} not found. Use one of these colors: { list( self.colors.keys() ) }." )
    
    def clear_line( self, line : int or Iterable ):
        """
        Clear a line.

        Note
        ----
        This will not refresh the window. And not affect the positioning of the current_line.

        Parameters
        ----------
        line : int or Iterable
            The line(s) to clear. 
        """
        # current = self._lines

        if isinstance( line, int):
            self.window.move( line, 0 )
            self.window.clrtoeol()

        elif isinstance( line, Iterable ):
            for l in line:
                self.window.move( l, 0 )
                self.window.clrtoeol()
                
        # self._lines = current

    @staticmethod
    def key_to_int( key ) -> int:
        """
        Convert a keypress to an integer.
        """
        return ord( key )

    @staticmethod
    def int_to_key( key ) -> str:
        """
        Convert an integer to a keypress.
        """
        return chr( key )

    def reset_lines( self ):
        """
        Reset the line counter to the first line.
        """
        self._lines = self._first_line


    def line_diff( self, line ):
        """
        Get the difference between the current line and the given line.

        Parameters
        ----------
        line : int
            The line to get the difference to.
        """
        return line - self._lines

    def set_line( self, line ):
        """
        Set the current line.
        """
        self._lines = line
        # self.window.move( line, 0 )
    
    def is_linewise_iterable( self, line, string ) -> bool:
        """
        Check if a string is linewise iterable.
        
        Note
        ----
        Line-wise iterable means the data is interpreted as a column!

        Parameters
        ----------
        line : int or list or tuple
            The line(s) to write to.
        string : str or list or tuple
            The string(s) to write.
        
        Returns
        -------
        bool
        """
        return self._is_ab_iterable( line, string )

    def is_columwise_iterable( self, pos, string ) -> bool:
        """
        Check if a string is columnwise iterable.

        Note
        ----
        Column-wise iterable means the data is interpreted as a row!

        Parameters
        ----------
        pos : int or list or tuple
            The position(s) to write to.
        string : str or list or tuple
            The string(s) to write.
        
        Returns
        -------
        bool
        """
        return self._is_ab_iterable( pos, string )

    def update_counter( self ):
        """
        Increment the counter value.
        """
        self.__update_counter__ += 1
    
    def set_update_interval( self, value : int ):
        """
        Set the interval after which the window should be "updatable".
        In this case the method `can_update` will return True if a number of refreshes have 
        been performed that corresponded approximately to the provided time interval.

        Parameters
        ----------
        value : int
            The new update interval in seconds.
        """
        self.__update_due__ = value

    def can_update( self ):
        """
        Check if the window can be updated and reset the counter if so.
        """
        if self.__update_counter__ > self.__update_due__ * self.__update_refs__ : 
            self.__update_counter__ = 0
            return True
        return False

    @property
    def size( self ) -> tuple:
        """
        Get the size of the window in as (height, width).
        Height is given in number of lines in the window, 
        and width in number of characters per line.
        """
        return self.window.getmaxyx()

    @property
    def keystring( self ) -> str:
        """
        Get the last keypress event from the window as a string or None (if no keys were pressed).
        """
        code = self.window.getch()
        if code == -1:
            return None
        return chr( code )

    @property
    def keycode( self ) -> int:
        """
        Get the last keypress event from the window as an integer code or None (if no keys were pressed).
        """
        code = self.window.getch()
        if code == -1:
            return None
        return code

    @property
    def first_line( self ) -> int:
        """
        Get the first line of the window.
        """
        return self._first_line

    @property
    def to_first_line( self ) -> int:
        """
        Go to the top line of the window.
        """
        self._lines = self._first_line
        return self._lines

    @property
    def bottom_line( self ) -> int:
        """
        Get the bottom line of the window.
        """
        return self.height - 1
    
    @property
    def to_bottom_line( self ) -> int:
        """
        Go to the bottom line of the window.
        """
        self._lines = self.bottom_line
        return self._lines

    @property
    def last_line( self ) -> int:
        """
        Get the down-most line that was written to.
        """
        return self._max_lines

    @property
    def to_last_line( self ) -> int:
        """
        Go to the down-most line that was written to.
        """
        self._lines = self._max_lines
        return self._lines

    @property
    def current_line( self ) -> int:
        """
        Get the current line (by default the bottom-most line)
        """
        return self._lines

    @current_line.setter
    def current_line( self, line ):
        """
        Set the current line.
        """
        self.set_line( line )

    @property
    def next_line( self ) -> int:
        """
        Get the one-next line.
        """
        return self._lines + 1
    
    @property
    def to_next_line( self ) -> int:
        """
        Go to the one-next line and update the current line.
        """
        self._modify_line( 1 )
        return self._lines

    @property
    def to_previous_line( self ) -> int:
        """
        Go to the one-previous line and update the current line.
        """
        self._modify_line( -1 )
        return self._lines

    @property
    def previous_line( self ) -> int:
        """
        Get the one-previous line.
        """
        return self._lines - 1
    
    def _init( self ):
        """
        Initialize curses
        """
        self.window = curses.initscr()
        if self._use_color:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair( 1, curses.COLOR_WHITE, -1 )
            curses.init_pair( 2, curses.COLOR_BLACK, -1 )
            curses.init_pair( 3, curses.COLOR_RED, -1 )
            curses.init_pair( 4, curses.COLOR_GREEN, -1 )
            curses.init_pair( 5, curses.COLOR_BLUE, -1 )
            curses.init_pair( 6, curses.COLOR_YELLOW, -1 )
            curses.init_pair( 7, curses.COLOR_CYAN, -1 )
            self.colors = {
                    "white" : curses.color_pair( 1 ),
                    "black" : curses.color_pair( 2 ),
                    "red"   : curses.color_pair( 3 ),
                    "green" : curses.color_pair( 4 ),
                    "blue"  : curses.color_pair( 5 ),
                    "yellow": curses.color_pair( 6 ),
                    "cyan"  : curses.color_pair( 7 ),
                }

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.napms( self._refresh_delay )


        self.window.keypad(1)
        self.window.nodelay(1)
        self.window.timeout( self.waitkey )
        self.window.clear()
        self.window.refresh()

        if self.height and self.width:
            self.resize( self.height, self.width )
        else:
            self.adjust_size()

    def _destroy( self ):
        """
        Destroy curses
        """
        curses.nocbreak()
        self.window.keypad(0)
        curses.echo()
        curses.endwin()

    def _modify_line( self, value ):
        """
        Update the current line index.
        """
        if self.height is None or self._lines + value < self.height:
            self._lines += value

        if self._lines > self._max_lines:
            self._max_lines = self._lines

        if self._lines + value < self._first_line: 
            self._lines = self._first_line

    def _upack_size( self ):
        """
        Unpack the size of the window into height and width attributes.
        """
        self.height, self.width = self.size
        self._max_lines = self.height - 1
 

    def _write_to( self, window_or_pane, line : int, pos : int, string : str, refresh : bool = False ):
        """
        The core of write_to()
        
        Write a string to a specific (sub)window or pane.

        Parameters
        ----------
        window_or_pane 
            The window or pane to write to.
        line : int
            The line to write to.
        pos : int
            The position within the line to start writing at.
        string : str
            The string to write.
        refresh : bool
            Whether to refresh the window after writing.
        """
        # if we have a tuple with colors then unpack it
        if isinstance( string, tuple):
            window_or_pane.addstr( line, pos, *string )
        else:
            window_or_pane.addstr( line, pos, string )
        if refresh:
            self.refresh()
            
    def _is_ab_iterable( self, a, b ):
        """
        Checks if two arguments are both iterable and have the same lengths.
        This is the core of the linewise and columnwise iterable methods.
        """
        both_iterable = isinstance( a, Iterable ) and isinstance( b, Iterable )
        if not both_iterable:
            return False
        same_length = len( a ) == len( b )
        return both_iterable and same_length

import os
import sys
import types


# -------------------
## holds various utility functions
class Utils:

    # -------------------
    ## gets the location of the caller
    #
    # @param levels   default 3; used to go back further in the trace back
    # @return a string showing the filename and line number of the caller
    @staticmethod
    def get_location(levels=3):
        # get a full stackframe
        try:
            raise AssertionError
        except AssertionError:
            tb = sys.exc_info()[2]

        # go levels callers back
        frame = tb.tb_frame
        while levels > 0:
            frame = frame.f_back
            levels -= 1

        tb = types.TracebackType(tb_next=None,
                                 tb_frame=frame,
                                 tb_lasti=frame.f_lasti,
                                 tb_lineno=frame.f_lineno)

        # uncomment to debug
        # print(f"\nDBG: {frame.f_code.co_name}")
        # print(f"DBG: {frame.f_code.co_filename}")
        # print(f"DBG: {frame.f_lineno}")

        fname = os.path.basename(frame.f_code.co_filename)
        location = f'{fname}({frame.f_lineno})'
        return location

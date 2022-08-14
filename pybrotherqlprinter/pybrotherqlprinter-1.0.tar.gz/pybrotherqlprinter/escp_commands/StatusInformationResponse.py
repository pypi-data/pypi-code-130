#!/usr/bin/env python3

class StatusInformationResponse:

    def __init__(self, raw):
        assert type(raw) == bytes and len(raw) == 32
        assert raw[0] == 0x80
        assert raw[1] == 0x20

        self._printer_type_code = raw[3:5].decode("ascii")
        self._error1 = raw[8]
        self._error2 = raw[9]
        self._media_width = raw[10]
        self._media_type = raw[11]
        self._media_length = raw[17]
        self._status_type = raw[18]

    @property
    def printer_code(self):
        return self._printer_type_code

    @property
    def media_width(self): # millimeter
        return self._media_width

    @property
    def media_length(self):
        return self._media_length

    @property
    def media_present(self):
        return self._media_type != 0x00

    @property
    def is_continous_media(self):
        return self._media_type == 0x0A

    @property
    def is_label_media(self):
        return self._media_type == 0x0B

    @property
    def error1_code(self):
        return self._error1

    @property
    def error2_code(self):
        return self._error2

    @property
    def errors(self):
        output = []
        def add(cond, error):
            if cond: output.append(error)
        add(self._error1 & 0x01, "No media when printing.")
        add(self._error1 & 0x02, "End of media (labels).")
        add(self._error1 & 0x04, "Tape cutter jam.")
        add(self._error1 & 0x10, "Main unit in use.")
        add(self._error1 & 0x80, "Fan failure.")
        add(self._error2 & 0x04, "Transmission error.")
        add(self._error2 & 0x10, "Cover opened while printing.")
        add(self._error2 & 0x40, "Cannot feed paper.")
        add(self._error2 & 0x80, "System error.")
        return output



    def __repr__(self):
        yn = lambda i: "Yes" if i else "No"
        ret = [
            "Printer status:",
            " - printer type code: %s" % self.printer_code,
            " - media present: %s" % yn(self.media_present),
            " - media size: %dmm x %s" % (
                self.media_width,
                self.is_continous_media and "Continous" or (
                    "%dmm" % self.media_length
                )
            ),
            " - errors:\n%s" % ("  * ".join(self.errors) or "   None")
        ]
        return "\n".join(ret)

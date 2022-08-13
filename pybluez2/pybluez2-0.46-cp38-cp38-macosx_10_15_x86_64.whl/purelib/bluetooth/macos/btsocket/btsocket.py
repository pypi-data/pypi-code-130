import logging
import time
import socket
import threading
import os
import errno

import objc
import Foundation

import bluetooth.address
from bluetooth.btcommon import BluetoothError, Protocols
from bluetooth.macos.loop import Loop
from bluetooth.macos import IOBluetooth
from bluetooth.macos import util
from bluetooth.macos.btsocket.connection import _L2CAPConnection, _RFCOMMConnection
from bluetooth.macos.btsocket.delegate import BluezBluetoothChannelDelegate

logger = logging.getLogger(__name__)

try:
    SHUT_RD, SHUT_WR, SHUT_RDWR = \
        socket.SHUT_RD, socket.SHUT_WR, socket.SHUT_RDWR
except AttributeError:
    # python 2.3
    SHUT_RD, SHUT_WR, SHUT_RDWR = (0, 1, 2)


def _getavailableport(proto: Protocols):
    # Just advertise a service and see what channel it was assigned, then
    # stop advertising the service and return the channel.
    # It's a hacky way of doing it, but IOBluetooth doesn't seem to provide
    # functionality for just getting an available channel.
    from lightblue._LightAquaBlue import BBServiceAdvertiser
    if proto == Protocols.RFCOMM:
        try:
            result, channelID, servicerecord = BBServiceAdvertiser.addRFCOMMServiceDictionary_withName_UUID_channelID_serviceRecord_(BBServiceAdvertiser.serialPortProfileDictionary(), "DummyService", None, None, None)
        except:
            result, channelID, servicerecord = BBServiceAdvertiser.addRFCOMMServiceDictionary_withName_UUID_channelID_serviceRecord_(BBServiceAdvertiser.serialPortProfileDictionary(), "DummyService", None)
        
        if result != util.kIOReturnSuccess:
            raise BluetoothError(f"Could not retrieve an available service channel ({result})")
        
        result = BBServiceAdvertiser.removeService_(servicerecord)
        
        if result != util.kIOReturnSuccess:
            raise BluetoothError(f"Could not retrieve an available service channel ({result})")
        
        return channelID

    else:
        raise NotImplementedError("L2CAP server sockets not currently supported")


def _checkaddrpair(address, checkbtaddr=True):
    # will want checkbtaddr=False if the address might be empty string
    # (for binding to a server address)

    if not isinstance(address, tuple):
        raise TypeError(f"address must be (address, port) tuple, was {type(address)}")

    if len(address) != 2:
        raise TypeError(f"address tuple must have 2 items (has {len(address)})")

    if not isinstance(address[0], str):
        raise TypeError(f"address host value must be string, was {type(address[0])}")

    if checkbtaddr:
        if not bluetooth.address.validate(address[0]):
            raise TypeError(f"invalid address: {address[0]}")

    if not isinstance(address[1], int):
        raise TypeError(f"address port value must be int, was {type(address[1])}")


# from std lib socket module
class _closedsocket:
    __slots__ = []
    def _dummy(*args):
        raise socket.error(errno.EBADF, 'Bad file descriptor')
    send = recv = sendto = recvfrom = __getattr__ = _dummy


# TODO: replace with BytesIO if minimum supported version is python3?
# or just get rid of wrapper class altogether & use bytearray directly if
# multi-threaded usage isn't support (it's not currently).
class _ByteQueue:
    def __init__(self):
        self.buffered = bytearray()
        self.lock = threading.Lock()

    def empty(self):
        return len(self.buffered) == 0

    def write(self, data):
        with self.lock:
          self.buffered.extend(data)

    def __len__(self):
        #calculate length without needing to _build_str
        return len(self.buffered)

    def read(self, count):
        with self.lock:
            #get data requested by caller
            result = self.buffered[:count]
            #remove requested data from buffer
            del self.buffered[:count]
        return result


#class socketWrapper(socket.socketobject):
class socketWrapper:
    """
    A Bluetooth socket object has the same interface as a socket object from
    the Python standard library <socket> module. It also uses the same
    exceptions, raising socket.error for general errors and socket.timeout for
    timeout errors.

    Note that L2CAP sockets are not available on Python For Series 60, and
    only L2CAP client sockets are supported on Mac OS X and Linux.

    A simple client socket example:
        >>> from lightblue import *
        >>> s = socket()        # or socket(L2CAP) to create an L2CAP socket
        >>> s.connect(("00:12:2c:45:8a:7b", 5))
        >>> s.send("hello")
        5
        >>> s.close()

    A simple server socket example:
        >>> from lightblue import *
        >>> s = socket()
        >>> s.bind(("", 0))
        >>> s.listen(1)
        >>> advertise("My RFCOMM Service", s, RFCOMM)
        >>> conn, addr = s.accept()
        >>> print("Connected by", addr)
        Connected by ('00:0D:93:19:C8:68', 5)
        >>> conn.recv(1024)
        "hello"
        >>> conn.close()
        >>> s.close()
    """

    def __init__(self, sock):
        self._sock = sock

    def accept(self):
        sock, addr = self._sock.accept()
        return socketWrapper(sock), addr

    def dup(self):
        return socketWrapper(self._sock)

    def close(self):
        self._sock.close()

        self._sock = _closedsocket()
        self.send = self.recv = self.sendto = self.recvfrom = self._sock._dummy

        try:
            import lightblue
            lightblue.stopadvertise(self)
        except:
            pass

    def makefile(self, mode='r', bufsize=-1):
        # use std lib socket's _fileobject
        return socket._fileobject(self._sock, mode, bufsize)

    # delegate all other method calls to internal sock obj
    def __getattr__(self, attr):
        return getattr(self._sock, attr)


# internal _sock object for RFCOMM and L2CAP sockets
class _BluetoothSocket:
    _boundports = { Protocols.L2CAP: set(),
                    Protocols.RFCOMM: set() }

    # conn is the associated _RFCOMMConnection or _L2CAPConnection
    def __init__(self, conn):
        self.__conn = conn

        if conn is not None and conn.channel is not None:
            self.__remotedevice = conn.channel.getDevice()
        else:
            self.__remotedevice = None

        # timeout=None cos sockets default to blocking mode
        self.__timeout = None

        #self.__isserverspawned = (conn.channel is not None)
        self.__port = 0
        self.__eventlistener = None
        self.__closed = False
        self.__maxqueuedconns = 0
        self.__incomingdata = _ByteQueue()
        self.__queuedchannels = []
        self.__queuedchannels_lock = threading.RLock()

        # whether send or recv has been shut down
        # set initial value to be other than SHUT_WR/SHUT_RD/SHUT_RDWR
        self.__commstate = -1

    def accept(self):
        if not self.__isbound():
            raise socket.error('Socket not bound')
        if not self.__islistening():
            raise socket.error('Socket must be listening first')

        def clientconnected():
            return len(self.__queuedchannels) > 0


        Loop().wait_until(clientconnected)
        if not clientconnected():
            self.__waituntil(clientconnected, "accept timed out")

        self.__queuedchannels_lock.acquire()
        try:
            newchannel = self.__queuedchannels.pop(0)
        finally:
            self.__queuedchannels_lock.release()

        # return (new-socket, addr) pair using the new channel
        newconn = socket_CLASSES[self.__conn.proto](newchannel)
        sock = socketWrapper(_BluetoothSocket(newconn))
        sock.__startevents()
        return (sock, sock.getpeername())

    def bind(self, address):
        _checkaddrpair(address, False)
        if self.__isbound():
            raise socket.error('Socket is already bound')
        elif self.__isconnected():
            raise socket.error("Socket is already connected, cannot be bound")

        if self.__conn.proto == Protocols.L2CAP:
            raise NotImplementedError("L2CAP server sockets not currently supported")

        if address[1] != 0:
            raise socket.error("must bind to port 0, other ports not supported on Mac OS X")
        address = (address[0], _getavailableport(self.__conn.proto))

        # address must be either empty string or local device address
        if address[0] != "":
            try:
                import lightblue
                localaddr = lightblue.gethostaddr()
            except:
                localaddr = None
            if localaddr is None or address[0] != localaddr:
                raise socket.error(
                    errno.EADDRNOTAVAIL, os.strerror(errno.EADDRNOTAVAIL))

        # is this port already in use?
        if address[1] in self._boundports[self.__conn.proto]:
            raise socket.error(errno.EADDRINUSE, os.strerror(errno.EADDRINUSE))

        self._boundports[self.__conn.proto].add(address[1])
        self.__port = address[1]

    def close(self):
        wasconnected = self.__isconnected() or self.__isbound()
        self.__stopevents()

        if self.__conn is not None:
            if self.__isbound():
                self._boundports[self.__conn.proto].discard(self.__port)
            else:
                if self.__conn.channel is not None:
                    self.__conn.channel.setDelegate_(None)
                    self.__conn.channel.closeChannel()

        # disconnect the baseband connection.
        # This will fail if other RFCOMM channels to the remote device are
        # still open (which is what we want, cos we don't know if another
        # process is talking to the device)
        if self.__remotedevice is not None:
            self.__remotedevice.closeConnection()   # returns err code

        # if you don't run the event loop a little here, it's likely you won't
        # be able to reconnect to the same remote device later
        if wasconnected:
            Loop().wait_blocking(0.5)


    def connect(self, address):
        if self.__isbound():
            raise socket.error("Can't connect, socket has been bound")
        elif self.__isconnected():
            raise socket.error("Socket is already connected")
        _checkaddrpair(address)

        # open a connection to device
        self.__remotedevice = IOBluetooth.IOBluetoothDevice.withAddressString_(address[0])

        if not self.__remotedevice.isConnected():
            if self.__timeout is None:
                result = self.__remotedevice.openConnection()
            else:
                result = self.__remotedevice.openConnection_withPageTimeout_authenticationRequired_(
                    None, self.__timeout*1000, False)

            if result != util.kIOReturnSuccess:
                if result == util.kBluetoothHCIErrorPageTimeout:
                    if self.__timeout == 0:
                        raise socket.error(errno.EAGAIN,
                            "Resource temporarily unavailable")
                    else:
                        raise socket.timeout("connect timed out")
                else:
                    raise socket.error(result,
                        "Cannot connect to %s, can't open connection." \
                                                            % str(address[0]))

        # open RFCOMM or L2CAP channel
        self.__eventlistener = self.__createlistener()
        result = self.__conn.connect(self.__remotedevice, address[1],
                self.__eventlistener)   # pass listener as cocoa delegate

        if result != util.kIOReturnSuccess:
            self.__remotedevice.closeConnection()
            self.__stopevents()
            self.__eventlistener = None
            raise socket.error(result,
                    "Cannot connect to %d on %s" % (address[1], address[0]))
            return

        # if you don't run the event loop a little here, it's likely you won't
        # be able to reconnect to the same remote device later
        Loop().wait_blocking(0.5)

    def connect_ex(self, address):
        try:
            self.connect(address)
        except socket.error as err:
            if len(err.args) > 1:
                return err.args[0]
            else:
                # there's no error code, just a message, so this error wasn't
                # from a system call -- so re-raise the exception
                raise socket.error(err)
        return 0

    def getpeername(self):
        self.__checkconnected()
        addr = util.formatdevaddr(self.__remotedevice.getAddressString())
        return (addr, self._getport())

    def getsockname(self):
        if self.__isbound() or self.__isconnected():
            import lightblue
            return (lightblue.gethostaddr(), self._getport())
        else:
            return ("00:00:00:00:00:00", 0)

    def listen(self, backlog):
        if self.__islistening():
            return

        if not self.__isbound():
            raise socket.error('Socket not bound')
        if not isinstance(backlog, int):
            raise TypeError("backlog must be int, was %s" % type(backlog))
        if backlog < 0:
            raise ValueError("backlog cannot be negative, was %d" % backlog)

        self.__maxqueuedconns = backlog

        # start listening for client connections
        self.__startevents()


    def _isclosed(self):
        # isOpen() check doesn't work for incoming (server-spawned) channels
        if (self.__conn.proto == Protocols.RFCOMM and
                self.__conn.channel is not None and
                not self.__conn.channel.isIncoming()):
            return not self.__conn.channel.isOpen()
        return self.__closed


    def recv(self, bufsize, flags=0):
        if self.__commstate in (SHUT_RD, SHUT_RDWR):
            return ""
        self.__checkconnected()

        if not isinstance(bufsize, int):
            raise TypeError("buffer size must be int, was %s" % type(bufsize))
        if bufsize < 0:
            raise ValueError("negative buffersize in recv") # as for tcp
        if bufsize == 0:
            return ""

        # need this to ensure the _isclosed() check is up-to-date
        #_macutil.looponce()
        Loop().wait_blocking(0.02)
        Loop().wait_blocking(0.02)


        if self._isclosed():
            if len(self.__incomingdata) == 0:
                raise socket.error(errno.ECONNRESET,
                                    os.strerror(errno.ECONNRESET))
            return self.__incomingdata.read(bufsize)

        # if incoming data buffer is empty, wait until data is available or
        # channel is closed
        def gotdata():
            return not self.__incomingdata.empty() or self._isclosed()
        if not gotdata():
            self.__waituntil(gotdata, "recv timed out")

        # other side closed connection while waiting?
        if self._isclosed() and len(self.__incomingdata) == 0:
            raise socket.error(errno.ECONNRESET, os.strerror(errno.ECONNRESET))

        return self.__incomingdata.read(bufsize)


    # recvfrom() is really for datagram sockets not stream sockets but it
    # can be implemented anyway.
    def recvfrom(self, bufsize, flags=0):
        # stream sockets return None, instead of address
        return (self.recv(bufsize, flags), None)

    def sendall(self, data, flags=0):
        sentbytescount = self.send(data, flags)
        while sentbytescount < len(data):
            sentbytescount += self.send(data[sentbytescount:], flags)
        return None

    def send(self, data, flags=0):
        # On python 2 this should be OK for backwards compatability as "bytes"
        # is an alias for "str".
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("data must be bytes, was %s" % type(data))
        if self.__commstate in (SHUT_WR, SHUT_RDWR):
            raise socket.error(errno.EPIPE, os.strerror(errno.EPIPE))
        self.__checkconnected()

        # do setup for if sock is in non-blocking mode
        if self.__timeout is not None:
            if self.__timeout == 0:
                # in non-blocking mode
                # isTransmissionPaused() is not available for L2CAP sockets,
                # what to do for that?
                if self.__conn.proto == Protocols.RFCOMM and \
                        self.__conn.channel.isTransmissionPaused():
                    # sending data now will block
                    raise socket.error(errno.EAGAIN,
                        "Resource temporarily unavailable")
            elif self.__timeout > 0:
                # non-blocking with timeout
                starttime = time.time()

        # loop until all data is sent
        writebuf = data
        bytesleft = len(data)
        mtu = self.__conn.getwritemtu()
        while bytesleft > 0:
            if self.__timeout is not None and self.__timeout > 0:
                if time.time() - starttime > self.__timeout:
                    raise socket.timeout("send timed out")

            # write the data to the channel (only the allowed amount)
            # the method/selector is the same for L2CAP and RFCOMM channels
            if bytesleft > mtu:
                sendbytecount = mtu
            else:
                sendbytecount = bytesleft
            #result = self.__conn.channel.writeSync_length_(
            #        writebuf[:sendbytecount], sendbytecount)
            result = self.__conn.write(writebuf[:sendbytecount])

            # normal tcp sockets don't seem to actually error on the first
            # send() after a connection has broken; if you try a second time,
            # then you get the (32, 'Broken pipe') socket.error
            if result != util.kIOReturnSuccess:
                raise socket.error(result, "Error sending data")

            bytesleft -= sendbytecount
            writebuf = writebuf[sendbytecount:] # remove the data just sent

        return len(data) - bytesleft

    # sendto args may be one of:
    # - data, address
    # - data, flags, address
    #
    # The standard behaviour seems to be to ignore the given address if already
    # connected.
    # sendto() is really for datagram sockets not stream sockets but it
    # can be implemented anyway.
    def sendto(self, data, *args):
        if len(args) == 1:
            address = args[0]
            flags = 0
        elif len(args) == 2:
            flags, address = args
        else:
            raise TypeError("sendto takes at most 3 arguments (%d given)" % \
                (len(args) + 1))
        _checkaddrpair(address)

        # must already be connected, cos this is stream socket
        self.__checkconnected()
        return self.send(data, flags)

    def fileno(self):
        raise NotImplementedError

    def getsockopt(self, level, optname, buflen=0):
        # see what options on Linux+s60
        # possibly have socket security option.
        raise socket.error(
            errno.ENOPROTOOPT, os.strerror(errno.ENOPROTOOPT))

    def setsockopt(self, level, optname, value):
        # see what options on Linux+s60
        # possibly have socket security option.
        raise socket.error(
            errno.ENOPROTOOPT, os.strerror(errno.ENOPROTOOPT))

    def setblocking(self, flag):
        if flag == 0:
            self.__timeout = 0      # non-blocking
        else:
            self.__timeout = None   # blocking

    def gettimeout(self):
        return self.__timeout

    def settimeout(self, value):
        if value is not None and not isinstance(value, (float, int)):
            msg = "timeout value must be a number or None, was %s" % \
                type(value)
            raise TypeError(msg)
        if value < 0:
            msg = "timeout value cannot be negative, was %d" % value
            raise ValueError(msg)
        self.__timeout = value

    def shutdown(self, how):
        if how not in (SHUT_RD, SHUT_WR, SHUT_RDWR):
            raise socket.error(22, "Invalid argument")
        self.__commstate = how

    # This method is called from outside this file.
    def _getport(self):
        if self.__isconnected():
            return self.__conn.getport()
        if self.__isbound():
            return self.__port
        raise BluetoothError("socket is neither connected nor bound")

    # This method is called from outside this file.
    def _getchannel(self):
        if self.__conn is None:
            return None
        return self.__conn.channel

    # Called by the event listener when data is available
    # 'channel' is IOBluetoothRFCOMMChannel or IOBluetoothL2CAPChannel object
    def _handle_channeldata(self, channel, data):
        self.__incomingdata.write(data)
        #_macutil.interruptwait()

    # Called by the event listener when a client connects to a server socket
    def _handle_channelopened(self, channel):
        # put new channels into a queue, which 'accept' can then pull out
        self.__queuedchannels_lock.acquire()
        try:
            # need to implement max connections
            #if len(self.__queuedchannels) < self.__maxqueuedconns:
            self.__queuedchannels.append(channel)
            #_macutil.interruptwait()
        finally:
            self.__queuedchannels_lock.release()

    # Called by the event listener when the channel is closed.
    def _handle_channelclosed(self, channel):
        # beware that this value won't actually be set until the event loop
        # has been driven so that this method is actually called
        self.__closed = True
        #_macutil.interruptwait()

    def __waituntil(self, stopwaiting, timeoutmsg):
        """
        Waits until stopwaiting() returns True, or until the wait times out
        (according to the self.__timeout value).

        This is to make a function wait until a buffer has been filled. i.e.
        stopwaiting() should return True when the buffer is no longer empty.
        """
        if not stopwaiting():
            if self.__timeout == 0:
                # in non-blocking mode (immediate timeout)
                # push event loop to really be sure there is no data available
                Loop().wait_blocking(0.02)
                if not stopwaiting():
                    # trying to perform operation now would block
                    raise socket.error(errno.EAGAIN, os.strerror(errno.EAGAIN))
            else:
                # block and wait until we get data, or time out
                if not Loop().wait_until(stopwaiting, self.__timeout):
                    raise socket.timeout(timeoutmsg)

    def __createlistener(self):
        if self.__isbound():
            return ChannelServerEventListener.alloc().initWithDelegate_port_protocol_(self,
                    self._getport(), self.__conn.proto)
        else:
            listener = ChannelEventListener.alloc().initWithDelegate_(self)
            if self.__conn.channel is not None:
                self.__conn.channel.setDelegate_(listener.delegate())
                listener.registerclosenotif(self.__conn.channel)
            return listener

    # should not call this if connect() has been called to connect this socket
    def __startevents(self):
        if self.__eventlistener is not None:
            raise BluetoothError("socket already listening")
        self.__eventlistener = self.__createlistener()

    def __stopevents(self):
        if self.__eventlistener is not None:
            self.__eventlistener.close()

    def __islistening(self):
        return self.__eventlistener is not None

    def __checkconnected(self):
        if not self._sock.isconnected():  # i.e. is connected, non-server socket
            # not connected, raise "socket not connected"
            raise socket.error(errno.ENOTCONN, os.strerror(errno.ENOTCONN))

    # returns whether socket is a bound server socket
    def __isbound(self):
        return self.__port != 0

    def __isconnected(self):
        return self.__conn.channel is not None

    def __checkconnected(self):
        if not self.__isconnected():
            # not connected, raise "socket not connected"
            raise socket.error(errno.ENOTCONN, os.strerror(errno.ENOTCONN))



class ChannelEventListener(Foundation.NSObject):
    """
    Uses a BluezBluetoothChannelDelegate to listen for events on an
    IOBluetoothRFCOMMChannel or IOBluetoothL2CAPChannel, and makes callbacks to
    a specified object when events occur.
    """

    # note this is a NSObject "init", not a python object "__init__"

    @objc.typedSelector(b"@@:@")
    def initWithDelegate_(self, cb_obj):
        """
        Arguments:
        - cb_obj: An object that receives callbacks when events occur. This
          object should have:
            - a method '_handle_channeldata' which takes the related channel (a
              IOBluetoothRFCOMMChannel or IOBluetoothL2CAPChannel) and the new
              data (a string) as the arguments.
            - a method '_handle_channelclosed' which takes the related channel
              as the argument.

        If this listener's delegate is passed to the openRFCOMMChannel... or
        openL2CAPChannel... selectors as the delegate, the delegate (and
        therefore this listener) will automatically start receiving events.

        Otherwise, call setDelegate_() on the channel with this listener's
        delegate as the argument to allow this listener to start receiving
        channel events. (This is the only option for server-spawned sockets.)
        """
        self = super().init()
        if cb_obj is None:
            raise TypeError("callback object is None")
        self.__cb_obj = cb_obj
        self.__closenotif = None
        self.__channelDelegate = BluezBluetoothChannelDelegate.alloc().initWithDelegate_(self)
        return self

    def delegate(self):
        return self.__channelDelegate

    @objc.python_method
    def registerclosenotif(self, channel):
        # oddly enough, sometimes the channelClosed: selector doesn't get called
        # (maybe if there's a lot of data being passed?) but this seems to work
        notif = channel.registerForChannelCloseNotification_selector_(self,
                "channelClosedEvent:channel:")
        if notif is not None:
            self.__closenotif = notif

    def close(self):
        if self.__closenotif is not None:
            self.__closenotif.unregister()

    @objc.typedSelector(b"v@:@@")
    def channelClosedEvent_channel_(self, notif, channel):
        if hasattr(self.__cb_obj, '_handle_channelclosed'):
            self.__cb_obj._handle_channelclosed(channel)

    # implement method from BluezBluetoothChannelDelegateObserver protocol:
    # - (void)channelData:(id)channel data:(NSData *)data;
    @objc.typedSelector(b"v@:@@")
    def channelData_data_(self, channel, data):
        if hasattr(self.__cb_obj, '_handle_channeldata'):
            self.__cb_obj._handle_channeldata(channel, data[:])

    # implement method from BluezBluetoothChannelDelegateObserver protocol:
    # - (void)channelClosed:(id)channel;
    @objc.typedSelector(b"v@:@")
    def channelClosed_(self, channel):
        if hasattr(self.__cb_obj, '_handle_channelclosed'):
            self.__cb_obj._handle_channelclosed(channel)


class ChannelServerEventListener(Foundation.NSObject):
    """
    Listens for server-specific events on a RFCOMM or L2CAP channel (i.e. when a
    client connects) and makes callbacks to a specified object when events
    occur.
    """
    @objc.typedSelector(b"@@:@ii")
    def initWithDelegate_port_protocol_(self, cb_obj, port, proto):
        """
        Arguments:
        - cb_obj: to receive callbacks when a client connects to
          to the channel, the callback object should have a method
          '_handle_channelopened' which takes the newly opened
          IOBluetoothRFCOMMChannel or IOBluetoothL2CAPChannel as its argument.
        - port: the channel or PSM that the server is listening on
        - proto: L2CAP or RFCOMM.
        """
        self = super().init()
        if cb_obj is None:
            raise TypeError("callback object is None")
        self.__cb_obj = cb_obj
        self.__usernotif = None

        if proto == Protocols.RFCOMM:
            usernotif = IOBluetooth.IOBluetoothRFCOMMChannel.registerForChannelOpenNotifications_selector_withChannelID_direction_(self, "newChannelOpened:channel:", port, util.kIOBluetoothUserNotificationChannelDirectionIncoming)
        elif proto == Protocols.L2CAP:
            usernotif = IOBluetooth.IOBluetoothL2CAPChannel.registerForChannelOpenNotifications_selector_withPSM_direction_(self, "newChannelOpened:channel:", port, util.kIOBluetoothUserNotificationChannelDirectionIncoming)

        if usernotif is None:
            raise socket.error("Unable to register for channel-" + \
                "opened notifications on server socket on channel/PSM %d" % \
                port)
        self.__usernotif = usernotif
        return self

    def close(self):
        if self.__usernotif is not None:
            self.__usernotif.unregister()

    @objc.typedSelector(b"v@:@@")
    def newChannelOpened_channel_(self, notif, newChannel):
        """
        Handle when a client connects to the server channel.
        (This method is called for both RFCOMM and L2CAP channels.)
        """
        if newChannel is not None and newChannel.isIncoming():
            # not sure if delegate really needs to be set
            newChannel.setDelegate_(self)

            if hasattr(self.__cb_obj, '_handle_channelopened'):
                self.__cb_obj._handle_channelopened(newChannel)


# -----------------------------------------------------------

# protocol-specific classes
socket_CLASSES = { Protocols.RFCOMM: _RFCOMMConnection,
                    Protocols.L2CAP:  _L2CAPConnection }

def _getsocketobject(proto):
    if proto not in list(socket_CLASSES.keys()):
        raise ValueError("Unknown socket protocol, must be L2CAP or RFCOMM")
    return socketWrapper(_BluetoothSocket(socket_CLASSES[proto]()))

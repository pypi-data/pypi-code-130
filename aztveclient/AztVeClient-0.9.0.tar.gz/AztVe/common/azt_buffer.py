#  =============================================================================
#  GNU Lesser General Public License (LGPL)
#
#  Copyright (c) 2022 Qujamlee from www.aztquant.com
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  =============================================================================
import struct


class BufferQueue:
    def __init__(self):
        self._buf = bytearray()

    def enqueue(self, msg: bytes):
        self._buf.extend(msg)

    def dequeue(self, n=1):
        ret = self._buf[:n]
        self._buf = self._buf[n:]
        return ret

    def dequeue_all(self):
        ret = self._buf
        self.clear()
        return ret

    def drop(self, n=1):
        self._buf = self._buf[n:]

    def read(self, n=1):
        return self._buf[:n]

    def size(self):
        return len(self._buf)

    def clear(self):
        self._buf.clear()


class DefalutRecvPolicy:
    def __call__(self, buffer: BufferQueue):
        return buffer.dequeue_all()


class DefaultSendPolicy:
    def __call__(self, data: bytes):
        return data


class HeaderRecvPolicy(DefalutRecvPolicy):
    def __init__(self, header_size=4, max_recv_size=4096):
        self.m_header_size = header_size
        self.m_max_recv_size = max_recv_size

    def __call__(self, buffer: BufferQueue):
        msgs = []
        while True:
            header_size = self._get_header_size(buffer)
            if header_size is None:
                break
            msgs.append(buffer.dequeue(header_size))
        return msgs if msgs else None

    def _get_header_size(self, buffer):
        while buffer.size() > self.m_header_size:
            header_size = struct.unpack("I", buffer.read(self.m_header_size))[0]
            if header_size > self.m_max_recv_size:
                buffer.drop(self.m_header_size)
                continue

            if buffer.size() >= (header_size + self.m_header_size):
                buffer.drop(self.m_header_size)
                return header_size
            return None


class HeaderSendPolicy(DefaultSendPolicy):
    def __call__(self, data: bytes):
        return struct.pack("I", len(data)) + data

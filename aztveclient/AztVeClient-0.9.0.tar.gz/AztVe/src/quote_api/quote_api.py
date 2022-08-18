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
from typing import List, Union

from ._quote_api_base import *


class AztQuoteApi(QuoteApiBase):
    def Subscribe(self, codes: Union[str, List[str]]):
        return self._subscribe(codes)

    def Unsubscribe(self, codes: Union[str, List[str]]):
        return self._unsubscribe(codes)

    def Start(self, ip: str, port: int, spi=None, timeout=None, set_heart_beat=False):
        if spi:
            if isinstance(spi, type):
                spi = spi()
            if not getattr(spi, "api", None):
                setattr(spi, "api", self)
        return self._start(ip, port, spi, timeout, set_heart_beat)

    def Stop(self):
        return self._stop()  # 正常stop返回None

    def Join(self, timeout: int = None):
        self._join(timeout=timeout)

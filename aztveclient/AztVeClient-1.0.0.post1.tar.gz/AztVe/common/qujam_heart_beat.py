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

class QujamHeartBeat:
    def __init__(self, hb_data, hb_times=3):
        self.m_hb_data = hb_data
        self.m_hb_times = hb_times if hb_times > 0 else 3
        self.m_hb_cout = self.m_hb_times

    def data(self):
        return self.m_hb_data

    def alive(self):
        return self.m_hb_cout > 0

    def keep(self):
        self.m_hb_cout = self.m_hb_times

    def cost(self):
        self.m_hb_cout -= 1

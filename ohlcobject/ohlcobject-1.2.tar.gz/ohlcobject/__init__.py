#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# 去 pandas 化，性能优化用
# 内部存储为 { "low": [], "high": [] }
# 可将 ohlc_object[num]['key'] 的调用转化为 ohlc_object['key'][num] 的调用
# 从而避免大量的 pandas 内存拷贝，达到性能优化的效果

import abc
from typing import Union


class _OHLCIndexProtocol(object):

    @abc.abstractmethod
    def keys(self) -> list:
        pass

    @abc.abstractmethod
    def move_to_next(self) -> None:
        pass

    @abc.abstractmethod
    def current_idx(self) -> int:
        pass

    @abc.abstractmethod
    def reset_idx(self) -> None:
        pass

    @abc.abstractmethod
    def is_ended(self) -> bool:
        pass

    @abc.abstractmethod
    def current_bars(self):  # -> 可以通过[str|int]语法取下标的二维map/list对象
        pass

    @abc.abstractmethod
    def __getitem__(self, item):
        pass

    @abc.abstractmethod
    def __setitem__(self, key, value):
        pass

    @abc.abstractmethod
    def __len__(self):
        pass

    def current_ohlc(self):
        idx = self.current_idx()
        ohlc = self[idx]
        return ohlc


class _OHLCAbstractObject(_OHLCIndexProtocol):

    """
    结构：
    {
        'timestamp' = {list: 5349} [1498924800000, 1498939200000, ...],
        'open' = {list: 5349} [1.2, 1.33, 1.1235, 1.0595, 1.1501, ...],
        'high' = {list: 5349} [1.4, 1.6479, 1.3999, 1.2496, 1.548, ...],
        'low' = {list: 5349} [0.5, 1.0201, 0.9406, 1.0004, 1.14, ...],
        'close' = {list: 5349} [1.33, 1.135, 1.0743, 1.1709, ...],
        'vol' = {list: 5349} [662085.3021313506, 380645.72278805973, ...]
    }
    """

    def __init__(self):
        self.__current_idx: int = 0
        self.reset_idx()
        self.all_keys = list()

    @abc.abstractmethod
    def _operation_stack(self) -> list:
        pass

    @abc.abstractmethod
    def _root_object(self):  # return a OHLCEvaluateInterface
        pass

    @abc.abstractmethod
    def _evaluate(self, operation_list: list = None, key: str = ''):
        pass

    @abc.abstractmethod
    def merge(self, ohlc_obj: _OHLCIndexProtocol, concat: bool = False) -> None:
        """
        将 ohlc_obj 合入到 self 中。
        1. self 的最后一个 candle 将使用 ohlc_obj 中对应时间点的替代;
        2. ohlc_obj 尾部有而 self 中没有的 candle，将被拼接到 self 的尾部;
        3. self 中有 key 而 ohlc_obj 中无 key 的，会随 candle 往前移动（缩短），不会自动用 None 或 0 或 nan 填充。
        :param ohlc_obj 等待被合入的 ohlc_obj
        :param concat False 时，合并过程将保持 self 长度不变，合入时最早的记录将被移除。为 True 时，将持续拼接。
        :return 被更新的第一个 candle (最早的 candle) 的 timestamp
        """
        pass

    def keys(self) -> list:
        return self.all_keys

    def move_to_next(self) -> None:
        self.__current_idx = self.__current_idx + 1

    def current_idx(self) -> int:
        return self.__current_idx

    def reset_idx(self) -> None:
        self.__current_idx = 0

    def is_ended(self) -> bool:
        length: int = len(self)
        ended: bool = self.current_idx() >= length
        return ended

    def current_bars(self):
        # 举例：当current index 为 10 时，希望取到的是 0 到 10 ，总共11根k线
        # 所以这里传 11，也就是 self.current_id() + 1
        bars = self[0: self.current_idx() + 1]
        return bars

    def to_string(self) -> str:
        result = ''
        for key in self.all_keys:
            result += key + ':\n'
            result += str(self[key]) + '\n'
        return result


class OHLCEvaluateObject(_OHLCAbstractObject):

    def __init__(self,
                 original_object: _OHLCAbstractObject,
                 operation: Union[slice, int, str]):
        super().__init__()
        self.operation = operation
        self.original_object = original_object
        self.all_keys = self.original_object.all_keys

    def __getitem__(self, key):
        if isinstance(key, slice):
            return OHLCEvaluateObject(self, key)
        elif isinstance(key, int):
            return OHLCEvaluateObject(self, key)
        elif isinstance(key, str):
            return self._root_object()._evaluate(self._operation_stack(), key)
        else:
            return None

    def __setitem__(self, key, value):
        print('Performance warning!')
        raise

    def __len__(self):
        evaluated_list = self._root_object()._evaluate(self._operation_stack(), 'timestamp')
        return len(evaluated_list)

    def merge(self, ohlc_obj: _OHLCIndexProtocol, concat: bool = False) -> None:
        """
        将 ohlc_obj 合入到 self 中。
        1. self 的最后一个 candle 将使用 ohlc_obj 中对应时间点的替代;
        2. ohlc_obj 尾部有而 self 中没有的 candle，将被拼接到 self 的尾部;
        3. self 中有 key 而 ohlc_obj 中无 key 的，会随 candle 往前移动（缩短），不会自动用 None 或 0 或 nan 填充。
        :param ohlc_obj 等待被合入的 ohlc_obj
        :param concat False 时，合并过程将保持 self 长度不变，合入时最早的记录将被移除。为 True 时，将持续拼接。
        :return 被更新的第一个 candle (最早的 candle) 的 timestamp
        """
        self.original_object.merge(ohlc_obj, concat)
        return

    def _operation_stack(self) -> list:
        operation_list = self.original_object._operation_stack()
        operation_list.append(self.operation)
        return operation_list

    def _root_object(self) -> _OHLCAbstractObject:
        return self.original_object._root_object()

    def _evaluate(self, operation_list: list = None, key: str = ''):
        return None


class OHLCObject(_OHLCAbstractObject):

    """
    结构：
    {
        'timestamp' = {list: 5349} [1498924800000, 1498939200000, ...],
        'open' = {list: 5349} [1.2, 1.33, 1.1235, 1.0595, 1.1501, ...],
        'high' = {list: 5349} [1.4, 1.6479, 1.3999, 1.2496, 1.548, ...],
        'low' = {list: 5349} [0.5, 1.0201, 0.9406, 1.0004, 1.14, ...],
        'close' = {list: 5349} [1.33, 1.135, 1.0743, 1.1709, ...],
        'vol' = {list: 5349} [662085.3021313506, 380645.72278805973, ...]
    }

    初始化：
    ohlc_obj = OHLCObject()
    ohlc_obj['timestamp'] = [1498924800000, 1498939200000, ...]
    ohlc_obj['open'] = [1.2, 1.33, 1.1235, 1.0595, 1.1501, ...]
    ...
    """

    def __init__(self,
                 using_lazy_evaluate: bool = True,
                 using_slice_int_hack: bool = False):
        """
        OHLCObject 初始化。需注意，using_slice_int_hack 为 True 仅当 using_lazy_evaluate 为 True 时生效
        :param using_lazy_evaluate: 是否使表达式执行延迟到取第一个 str key 为止（性能正优化，正比于 len(self.all_keys)）
        :param using_slice_int_hack: 是否使用 index 计算替换 [slice][int] 执行，少部分场景会快一点，大部分会慢
        """
        super().__init__()
        self.using_lazy_evaluate = using_lazy_evaluate
        self.using_slice_int_hack = using_slice_int_hack  # 花了两天性能优化，结果大部分情况是负优化
        self.all_keys = list()
        self.__data = dict()
        self.__data['timestamp'] = []
        self.__data['open'] = []
        self.__data['high'] = []
        self.__data['low'] = []
        self.__data['close'] = []
        self.__data['vol'] = []

    def __del__(self):
        pass

    def __getitem__(self, key):
        if isinstance(key, slice) or isinstance(key, int):
            if self.using_lazy_evaluate:
                return OHLCEvaluateObject(self, key)
            else:
                new_ohlc_obj = OHLCObject(using_lazy_evaluate=self.using_lazy_evaluate,
                                          using_slice_int_hack=self.using_slice_int_hack)
                for each_key in self.all_keys:
                    data_list = self[each_key]
                    evaluated_expr = data_list[key]
                    new_ohlc_obj[each_key] = evaluated_expr
                return new_ohlc_obj
        elif isinstance(key, str):
            return self.__data.get(key)
        else:
            return None

    def __setitem__(self, key, value):
        if isinstance(key, str):
            self.__data[key] = value
            if key not in self.all_keys:
                self.all_keys.append(key)
        return

    def __len__(self):
        return len(self['timestamp'])

    def merge(self, ohlc_obj: _OHLCIndexProtocol, concat: bool = False) -> None:
        """
        将 ohlc_obj 合入到 self 中。
        1. self 的最后一个 candle 将使用 ohlc_obj 中对应时间点的替代;
        2. ohlc_obj 尾部有而 self 中没有的 candle，将被拼接到 self 的尾部;
        3. self 中有 key 而 ohlc_obj 中无 key 的，会随 candle 往前移动（缩短），不会自动用 None 或 0 或 nan 填充。
        :param ohlc_obj 等待被合入的 ohlc_obj
        :param concat False 时，合并过程将保持 self 长度不变，合入时最早的记录将被移除。为 True 时，将持续拼接。
        :return 被更新的第一个 candle (最早的 candle) 的 timestamp
        """
        if self['timestamp'] is None or len(self['timestamp']) == 0:
            for key in ohlc_obj.keys():
                self[key] = ohlc_obj[key]
            return
        last_ts = self['timestamp'][-1]
        updating_idx = -1
        for i in range(len(ohlc_obj) - 1, -1, -1):
            ts = ohlc_obj[i]['timestamp']
            if ts == last_ts:
                updating_idx = i
                break
        if updating_idx != -1:  # 如果 self 和 objc_obj 中有重叠的时间
            # self 的最后一个元素用 ohlc_obj 替换
            for key in self.all_keys:
                l1 = self[key]
                if ohlc_obj[key] is None:
                    # ohlc_obj 没有 key（后计算的技术指标会有这种情况），移除 self 中的最后一个元素
                    del l1[-1]
                else:
                    # ohlc_obj 有 key，替换
                    l1[-1] = ohlc_obj[key][updating_idx]
        # ohlc_obj 的游标 i 继续后移，每次移除 self 第一个元素，再追加 ohlc_obj 游标元素
        for i in range(updating_idx + 1, len(ohlc_obj)):
            for key in self.all_keys:
                l2 = self[key]
                if concat is False:
                    del l2[0]
                if ohlc_obj[key] is not None and len(ohlc_obj[key]) > i:
                    # ohlc_obj 没有 key（后计算的技术指标会有这种情况），就不用拼接了，保持不变就完事
                    # ohlc_obj 有 key，拼接
                    l2.append(ohlc_obj[key][i])
        return

    def _operation_stack(self) -> list:
        return []

    def _root_object(self) -> _OHLCAbstractObject:
        return self

    def _evaluate(self, operation_list: list = None, key: str = ''):
        full_list = self[key]
        if full_list is None:
            raise ValueError("OHLCObject error: key not found: " + str(key))
        evaluated_result = OHLCObject.__evaluate_operation(raw_list=full_list,
                                                           operation_list=operation_list,
                                                           using_slice_int_hack=self.using_slice_int_hack)
        return evaluated_result

    @staticmethod
    def __evaluate_operation(raw_list: list, operation_list: list, using_slice_int_hack: bool = False):
        if operation_list is None:
            return raw_list
        if len(operation_list) == 0:
            return raw_list
        if using_slice_int_hack:
            if len(operation_list) == 2 and isinstance(operation_list[0], slice) and isinstance(operation_list[1], int):
                return OHLCObject.__evaluate_slice_int(raw_list, operation_list[0], operation_list[1])
        result = raw_list
        for operation in operation_list:
            if result is None:
                raise ValueError("OHLCObject error: None 无法被 evaluate")
            if isinstance(operation, slice):
                result = result[operation]
            if isinstance(operation, int):
                result = result[operation]
        return result

    @staticmethod
    def __make_index_valid(list_len: int, index: int, step: int) -> int:
        result_index = index
        if result_index < 0:
            result_index = list_len + result_index
        if step > 0:
            result_index = max(result_index, 0)
            result_index = min(result_index, list_len)
        elif step < 0:
            result_index = max(result_index, -1)
            result_index = min(result_index, list_len - 1)
        return result_index

    @staticmethod
    def __evaluate_slice_int(raw_list: list, operation_slice: slice, operation_int: int):
        # 非法输入防护
        if raw_list is None or len(raw_list) == 0:  # raw_list 为空，返回 None
            return None
        if operation_slice is None or operation_int is None:  # operation_slice 或 operation_int 为空，返回 None
            return None
        if operation_slice.step == 0:  # slice.step 为 0，返回 None
            return None
        # step start stop 的默认值
        step = operation_slice.step
        if step is None:
            step = 1
        # start stop 的范围限定
        start = operation_slice.start
        if start is None:
            start = 0 if step > 0 else len(raw_list)
        else:
            start = OHLCObject.__make_index_valid(len(raw_list), start, step)
        stop = operation_slice.stop
        if stop is None:
            stop = len(raw_list) if step > 0 else -1
        else:
            stop = OHLCObject.__make_index_valid(len(raw_list), stop, step)

        # 再来一波非法输入防护（解析 start stop 后的）
        if start > stop and step > 0:  # start > stop，正序，返回 None
            return None
        if start < stop and step < 0:  # start < stop，反序，返回 None
            return None

        # if step > 0:
        #     start = max(start, 0)
        #     stop = min(stop, len(raw_list))
        # elif step < 0:
        #     start = min(start, len(raw_list) - 1)
        #     stop = max(stop, -1)
        # 计算真正的 index，并从 raw list 中读取，返回
        if operation_int >= 0:
            real_index = start + step * operation_int
            return raw_list[real_index]
        elif operation_int < 0:
            range_count = abs(stop - start)  # slice 后，从start 到 stop 的数量
            sliced_count = (range_count + abs(step) - 1) // abs(step)  # slice 后，list 的数量
            sliced_index = sliced_count + operation_int  # 取的下标在 slice 后的 list 中的位置
            real_index = start + sliced_index * step
            return raw_list[real_index]
        return raw_list[operation_slice][operation_int]

    @staticmethod
    def raw_key_list():
        return ["timestamp",
                "open",
                "high",
                "low",
                "close",
                "vol",
                ]

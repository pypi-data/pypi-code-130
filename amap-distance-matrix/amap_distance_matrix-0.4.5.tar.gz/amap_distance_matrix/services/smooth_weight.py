from typing import List, Optional


class Item:
    def __init__(self, item: any, weight: int, current_weight: int, effective_weight: int):
        self.item: any = item
        self.weight: int = weight
        self.current_weight: int = current_weight
        self.effective_weight: int = effective_weight


class SmoothWeight:
    def __init__(self):
        self.items: List[Item] = []
        self.n = 0
        self.i_list = []
    
    def add(self, item: any, weight: int):
        self.i_list.append(item)
        self.items.append(Item(item, weight, 0, weight))
        self.n += 1
    
    def __contains__(self, item: any):
        return item in self.i_list
    
    def remove_all(self):
        self.items = []
        self.n = 0
    
    def reset(self):
        for i in self.items:
            i.effective_weight = i.weight
            i.current_weight = 0
    
    @property
    def next(self):
        item = self._next_weighted()
        if item:
            return item.item
        return None
    
    def _next_weighted(self) -> Optional[Item]:
        if self.n == 0:
            return None
        if self.n == 1:
            return self.items[0]
        return self._next_smooth_weighted()
    
    def reduce_weight(self, item: any):
        total = 0
        for i in self.items:
            total += i.effective_weight
        for i in self.items:
            if i.item == item:
                i.current_weight -= total
    
    def _next_smooth_weighted(self) -> Optional[Item]:
        total = 0
        best: Item = None
        for i in range(len(self.items)):
            item = self.items[i]
            if not item:
                continue
            item.current_weight += item.effective_weight
            total += item.effective_weight
            if item.effective_weight < item.weight:
                item.effective_weight += 1
            
            if best is None or item.current_weight > best.current_weight:
                best = item
        if best is None:
            return None
        
        best.current_weight -= total
        return best


__all__ = ["SmoothWeight"]

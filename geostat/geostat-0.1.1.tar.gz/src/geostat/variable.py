from typing import List
from dataclases import dataclass, replace

@dataclass
class PaperParameter:
    name: str
    lo: float
    hi: float

def realize_parameter(pps: List[PaperParameter]):
    if not pps:
        raise ValueError('Empty list of parameters')

    lo = np.maximum(pp.lo for pp in pps)
    hi = np.maximum(pp.hi for pp in pps)
    if lo >= hi:
        raise ValueError('Incompatible bounds ')


    def merge(self, other):
        if other is None:
            return self
        lo = np.maximum(self.lo, other.lo)
        hi = np.minimum(self.hi, other.hi)
        if lo >= hi:
            raise ValueError('')
        


            missing = list(filter(lambda s: isinstance(s, str), scale_tensor))
            if missing:
                raise ValueError("parameter(s) [%s] not found" % ', '.join(missing))
            x *= scale_tensor

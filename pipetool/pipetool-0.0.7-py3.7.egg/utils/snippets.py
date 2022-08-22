'''
Created on 2022年8月8日

@author: 86139
'''
import numpy as np
import random,os

def seed_everything(seed=None):
    max_seed_value = np.iinfo(np.uint32).max
    min_seed_value = np.iinfo(np.uint32).min

    if (seed is None) or not (min_seed_value <= seed <= max_seed_value):
        random.randint(np.iinfo(np.uint32).min, np.iinfo(np.uint32).max)
    print(f"Global seed set to {seed}")
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch 
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except:
        pass
    
    return seed

def seg_generator(iterables, seg_len, seg_backoff=0):
    '''
    滑窗实现
    '''
    if seg_len <= 0:
        yield iterables, 0
    else:
        #  # 确保iterables列表中每一项的条目数相同
        #  assert sum([len(x)
        #              for x in iterables]) == len(iterables[0]) * len(iterables)
        assert iterables[0] is not None
        s0 = 0
        while s0 < len(iterables[0]):
            s1 = s0 + seg_len
            segs = [x[s0:s1] if x else None for x in iterables]
            yield segs, s0
            s0 += seg_len - seg_backoff
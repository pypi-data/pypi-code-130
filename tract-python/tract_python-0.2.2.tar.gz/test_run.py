import tract_python
import numpy as np

tm = tract_python.TractModel.load_from_path("./test_simple_nnef")
results = tm.run(input_0=np.arange(6).reshape(1, 2, 3).astype(np.float32))
print(results)

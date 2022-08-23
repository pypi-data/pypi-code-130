import pyopencl as cl
import os
import numpy as np

def zero_default_opencl_context():
    os.environ["PYOPENCL_CTX"] = "0"

def run_kernel(name, shape, *, inputs = None, outputs_number = None, ctx=[], queue = [], prg = [], source_code = None, file_name = 'compute_shaders.cl', clear=False):
    """
    Runs OpenCL kernel
    :param name: str = name of kernel
    :param shape: Tuple[int, int] = shape of all inputs and outputs
    :param inputs: list = list of input frames
    :param outputs_number: int = number of elements in the output
    :param ctx: Cache - don't change
    :param queue: Cache - don't change
    :param prg: Cache - don't change
    :return: list = list of outputs (images)
    """
    if inputs is None or outputs_number is None:
        raise(Exception(f"inputs = \'{inputs}\' or outputs_number = \'{outputs_number}\' is None"))
    if len(ctx)==0 or clear:
        if len(ctx)>0:
            ctx.pop()
            queue.pop()
            prg.pop()
        ctx.append(cl.create_some_context())
        queue.append(cl.CommandQueue(ctx[0]))
        cl_code_source = ""
        if source_code is None:
            with open(file_name, 'r', encoding="utf8") as file:
                cl_code_source = file.read()
        else:
            cl_code_source = source_code
        prg.append(cl.Program(ctx[0], cl_code_source).build())
    if clear: return
    h = shape[0]
    w = shape[1]
    src_bufs = [cl.image_from_array(ctx[0], i, 4) for i in inputs]
    fmt = cl.ImageFormat(cl.channel_order.RGBA, cl.channel_type.UNSIGNED_INT8)
    dest_bufs = [cl.Image(ctx[0], cl.mem_flags.WRITE_ONLY, fmt, shape=(w, h)) for i in range(outputs_number)]
    # execute OpenCL function
    prg[0].__getattr__(name)(queue[0], (w, h), None, *src_bufs, *dest_bufs)
    # copy result back to host
    res=[]
    for i in range(outputs_number):
        dest = np.empty_like(inputs[0])
        cl.enqueue_copy(queue[0], dest, dest_bufs[i], origin=(0, 0), region=(w, h))
        res.append(dest)
    return res
"""
The entry for drawing quantum circuit diagram
"""
from .utils import _get_instructions
from .text import TextDrawing


def circuit_drawer(circuit, output, line_length):
    """Select the corresponding circuit drawer according to the output parameter"""
    if output == "text":
        return __text_circuit_drawer(circuit=circuit, line_length=line_length)


def __text_circuit_drawer(circuit, plot_barriers=True, vertical_compression="high", line_length=None):
    """Draw quantum circuit by ascii art"""
    # 1 获取量子比特位数、经典比特位数、DAG的节点
    qubits, cbits, nodes = _get_instructions(circuit)
    # 2 绘制量子电路
    text_drawing = TextDrawing(qubits=qubits, cbits=cbits, nodes=nodes, circuit=circuit)
    # 是否输出barriers，默认为True，即输出
    text_drawing.plot_barriers = plot_barriers
    # 画图时，线的最大长度
    text_drawing.line_length = line_length
    # text方式的垂直压缩方式，默认是：medium
    text_drawing.vertical_compression = vertical_compression

    # 3 返回绘制结果
    return text_drawing

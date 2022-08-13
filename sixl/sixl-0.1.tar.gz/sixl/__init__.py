import numpy as np, re, PIL.Image, IPython.core.getipython as IP, matplotlib.figure as mfig

__all__ = ["setup", "retina", "encode_img"]

def encode6(data):
    h, w = data.shape
    colors, counts = np.unique(data, return_counts=True)
    bg = colors[np.argmax(counts)]
    mult = np.array([[1],[2],[4],[8],[16],[32]][:h], dtype=np.uint8)
    out = [f"#{bg}!{w}{chr(mult.sum(dtype=np.uint8) + 63)}"]
    for color in colors:
        if color != bg:
            values = ((data == color) * mult).sum(axis=0, dtype=np.uint8)
            text = (values[:np.nonzero(values)[0][-1]+1] + 63).tobytes().decode("ASCII")
            rle = re.sub(r"(.)\1{3,}", lambda m: f"!{len(m[0])}{m[1]}", text)
            out.append(f"$#{color}{rle}")
    return out + ["-"]

def encode_palette(rgb): return [
        f"#{i};2;{r*100//255};{g*100//255};{b*100//255}" for i, (r,g,b) in enumerate(zip(rgb[::3], rgb[1::3], rgb[2::3]))
    ]

def encode_img(img):
    w, h = img.size
    img = img.convert("RGB").convert("P", palette=PIL.Image.ADAPTIVE, colors=256)
    out = [f'\033Pq"1;1;{w};{h}']
    out.extend(encode_palette(img.getpalette()))
    data = np.asarray(img)
    for y in range(0, h, 6): out.extend(encode6(data[y:y+6]))
    out.append("\033\\\n")
    return "\n".join(out)

def encode_fig(fig):
    c = fig.canvas
    return encode_img(PIL.Image.frombytes("RGB", c.get_width_height(), c.tostring_rgb())) if hasattr(c, "renderer") else ""

def setup():
    PIL.Image.Image._repr_pretty_ = lambda self, p, cyc: p.text(encode_img(self))
    IP.get_ipython().display_formatter.formatters["text/plain"].for_type(
        mfig.Figure,
        lambda fig, p, cyc: p.text(encode_fig(fig))
    )

def retina(scale=2):
    from matplotlib import pyplot as plt
    plt.rcParams["figure.dpi"] *= scale

setup()

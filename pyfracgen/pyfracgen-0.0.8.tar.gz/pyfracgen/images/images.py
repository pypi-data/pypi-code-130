import numpy as np
import matplotlib.colors as mcolors
import matplotlib.animation as animation
from matplotlib import pyplot as plt
from matplotlib import colors
from numpy.ma import masked_where


def stack_cmaps(cmap, n_stacks):
    
    colors = np.array(cmap(np.linspace(0, 1, 200))) 
    
    for n in range(n_stacks - 1):
        colors = np.vstack((colors, cmap(np.linspace(0, 1, 200))))

    mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)

    return mymap


def image(res, cmap=plt.cm.hot, ticks='off', gamma=0.3, vert_exag=0, ls=[315, 10]):

    arr = res.image_array
    width = res.width_inches
    height = res.height_inches
    dpi = res.dpi

    w, h = plt.figaspect(arr)
    fig, ax0 = plt.subplots(figsize=(w, h), dpi=dpi)
    fig.subplots_adjust(0, 0, 1, 1)
    plt.axis(ticks)

    norm = colors.PowerNorm(gamma)
    light = colors.LightSource(azdeg=ls[0], altdeg=ls[1])
    
    if vert_exag != 0.0:
        ls = light.shade(arr, cmap=cmap, norm=norm, vert_exag=vert_exag, blend_mode='hsv')
        ax0.imshow(ls, origin='lower')
    else: 
        ax0.imshow(arr, origin='lower', cmap=cmap, norm=norm)

    fs = plt.gcf()
    fs.set_size_inches(width, height)

    return fig, ax0


def nebula_image(res_blue, res_green, res_red, ticks='off', gamma=1.0):

    arr_blue = res_blue.image_array
    width = res_blue.width_inches
    height = res_blue.height_inches
    dpi = res_blue.dpi
    arr_green = res_green.image_array
    arr_red = res_red.image_array

    arr_blue /= np.amax(arr_blue)
    arr_green /= np.amax(arr_green)
    arr_red /= np.amax(arr_red)

    final = np.dstack((arr_red, arr_green, arr_blue))

    w, h = plt.figaspect(arr_blue)
    fig, ax0 = plt.subplots(figsize=(w, h), dpi=dpi)
    fig.subplots_adjust(0, 0, 1, 1)
    plt.axis(ticks)
    fs = plt.gcf()
    fs.set_size_inches(width, height)
    ax0.imshow(final**gamma, origin='lower')

    return fig, ax0


def markus_lyapunov_image(res, cmap_negative, cmap_positive, gammas=(1.0, 1.0), ticks='off',
                          denoise=True):

    arr = res.image_array
    width = res.width_inches
    height = res.height_inches
    dpi = res.dpi

    neg = masked_where(arr > 0.0, arr)
    pos = masked_where(arr < 0.0, arr)

    w, h = plt.figaspect(neg)
    fig, ax0 = plt.subplots(figsize=(width, height), dpi=dpi)
    ax0.imshow(neg, cmap=cmap_negative, origin='lower', norm=colors.PowerNorm(gammas[0]))
    ax0.imshow(pos, cmap=cmap_positive, origin='lower', norm=colors.PowerNorm(gammas[1]))

    fig.subplots_adjust(0, 0, 1, 1)
    plt.axis(ticks)
    fs = plt.gcf()
    fs.set_size_inches(width, height)

    return fig, ax0


def random_walk_image(res, cmap=plt.cm.hot, ticks='off', gamma=0.3, alpha_scale=1.0):

    arr = res.image_array
    width = res.width_inches
    height = res.height_inches
    dpi = res.dpi

    w, h = plt.figaspect(arr[:, :, 0])
    fig, ax0 = plt.subplots(figsize=(w, h), dpi=dpi)
    fig.subplots_adjust(0, 0, 1, 1)
    plt.axis(ticks)
    max_ind = float(arr.shape[-1] + 1)

    for i in range(arr.shape[-1]):
        
        im = arr[..., i]
        im = masked_where(im == 0, im)
        alpha = 1 - (i + 1)/max_ind
        alpha *= alpha_scale
        norm = colors.PowerNorm(gamma)
        ax0.imshow(im, origin='lower', alpha=alpha, cmap=cmap, norm=norm, interpolation=None)
        
    fs = plt.gcf()
    fs.set_size_inches(width, height)
        
    return fig, ax0


def save_animation(series, fps=15, bitrate=1800, cmap=plt.cm.hot, filename='ani', ticks='off',
                   gamma=0.3, vert_exag=0, ls=[315, 10]):

    width = series[0].width_inches
    height = series[0].height_inches
    dpi = series[0].dpi

    fig = plt.figure()
    fig.subplots_adjust(0, 0, 1, 1)
    fs = plt.gcf()
    fs.set_size_inches(width, height)
    plt.axis(ticks)

    writer = animation.PillowWriter(fps=fps, metadata=dict(artist='Me'), bitrate=bitrate)
    norm = colors.PowerNorm(gamma)
    light = colors.LightSource(azdeg=ls[0], altdeg=ls[1])

    ims = []
    for s in series:

        arr = s.image_array
        ls = light.shade(arr, cmap=cmap, norm=norm, vert_exag=vert_exag, blend_mode='hsv')
        im = plt.imshow(ls, origin='lower', norm=norm)
        ims.append([im])

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat_delay=1000)
    ani.save(f'{filename}.gif', dpi=dpi, writer=writer)

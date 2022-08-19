import numpy as np
import matplotlib.pyplot as plt
from skimage import draw, transform, measure
from vampire import extraction, model, plot


def check_argument_type(check_vars, check_vars_names, check_vars_type, check_vars_type_names):
    """
    Check type of input arguments.

    Parameters
    ----------
    check_vars : tuple
        Variables to be checked.
    check_vars_names : tuple
        Names of variables to be checked.
    check_vars_type : tuple
        Types of variables to be checked.
    check_vars_type_names : tuple
        Names of the types of variables to be checked.

    """
    for i in range(len(check_vars)):
        if not isinstance(check_vars[i], check_vars_type[i]):
            raise TypeError(f'Argument `{check_vars_names[i]}` needs to be type {check_vars_type_names[i]}.')
    return


def circle_img(xdim, ydim, radius, spacing=5):
    """
    Generate an image with circles of the same size.

    Parameters
    ----------
    xdim : int
        x (column) dimension of the image.
    ydim : int
        y (rows) dimension of the image.
    radius : int
        Radius of circles.
    spacing : int, optional
        Spacing between circles.

    Returns
    -------
    img : ndarray
        Image with circles of the same size.

    """
    # check argument type
    check_vars = (xdim, ydim, radius, spacing)
    check_vars_names = ('xdim', 'ydim', 'radius', 'spacing')
    check_vars_type = (int, int, int, int)
    check_vars_type_names = ('int', 'int', 'int', 'int')
    check_argument_type(check_vars, check_vars_names, check_vars_type, check_vars_type_names)

    # create empty image
    shape = (ydim, xdim)
    img = np.zeros(shape)
    # calculate parameters
    half_box = radius + spacing
    box = 2 * half_box
    center_x = np.arange(half_box, xdim - half_box, box)
    center_y = np.arange(half_box, ydim - half_box, box)

    # draw circles
    for i in range(len(center_y)):
        for j in range(len(center_x)):
            rr, cc = draw.disk((center_y[i], center_x[j]), radius, shape=shape)
            img[rr, cc] = 1

    return img


def ellipse_img(xdim, ydim, major_radius, minor_radius, spacing=5, rotation=0):
    """
    Generate an image with ellipses of the same size.

    Parameters
    ----------
    xdim : int
        x (column) dimension of the image.
    ydim : int
        y (rows) dimension of the image.
    major_radius : int
        Major axis length of ellipses.
    minor_radius : int
        Minor axis length of ellipses.
    spacing : int, optional
        Spacing between ellipses.
    rotation : float, optional
        Angle of rotation (in degrees) of ellipses.

    Returns
    -------
    img : ndarray
        Image with ellipses of the same size.

    """
    # check argument type
    check_vars = (xdim, ydim, major_radius, minor_radius, spacing)
    check_vars_names = ('xdim', 'ydim', 'major_radius', 'minor_radius', 'spacing')
    check_vars_type = (int, int, int, int, int)
    check_vars_type_names = ('int', 'int', 'int', 'int', 'int')
    check_argument_type(check_vars, check_vars_names, check_vars_type, check_vars_type_names)

    # create empty image
    shape = (ydim, xdim)
    img = np.zeros(shape)
    # calculate parameters
    half_box = major_radius + spacing
    box = 2 * half_box
    center_x = np.arange(half_box, xdim - half_box, box)
    center_y = np.arange(half_box, ydim - half_box, box)
    rotation = np.radians(rotation)

    # draw ellipses
    for i in range(len(center_y)):
        for j in range(len(center_x)):
            rr, cc = draw.ellipse(center_y[i], center_x[j], minor_radius, major_radius, rotation=rotation)
            img[rr, cc] = 1

    return img


def rectangle_img(xdim, ydim, major_dim, minor_dim, spacing=5, rotation=0):
    """
    Generate an image with rectangles of the same size.

    Parameters
    ----------
    xdim : int
        x (column) dimension of the image.
    ydim : int
        y (rows) dimension of the image.
    major_dim : int
        Major side length of rectangles.
    minor_dim : int
        Minor side length of rectangles.
    spacing : int, optional
        Spacing between rectangles.
    rotation : float, optional
        Angle of rotation (in degrees) of the image.

    Returns
    -------
    img : ndarray
        Image with rectangles of the same size.

    """
    # check argument type
    check_vars = (xdim, ydim, major_dim, minor_dim, spacing)
    check_vars_names = ('xdim', 'ydim', 'major_dim', 'minor_dim', 'spacing')
    check_vars_type = (int, int, int, int, int)
    check_vars_type_names = ('int', 'int', 'int', 'int', 'int')
    check_argument_type(check_vars, check_vars_names, check_vars_type, check_vars_type_names)

    # create empty image
    shape = (ydim, xdim)
    img = np.zeros(shape)
    # calculate parameters
    major_box = major_dim + 2*spacing
    minor_box = minor_dim + 2*spacing
    left_x = np.arange(major_box, xdim - major_box, major_box)
    top_y = np.arange(minor_box, ydim - minor_box, minor_box)

    # draw rectangles
    for i in range(len(top_y)):
        for j in range(len(left_x)):
            rr, cc = draw.rectangle((top_y[i], left_x[j]), extent=(minor_dim, major_dim))
            img[rr, cc] = 1

    # rotate image
    img = transform.rotate(img, rotation, resize=True)

    return img


def triangle_img(xdim, ydim, l1, l2, theta, spacing=5, rotation=0):
    """
    Generate an image with triangles of the same size
    defined by SAS with respect to origin.

    Parameters
    ----------
    xdim : int
        x (column) dimension of the image.
    ydim : int
        y (rows) dimension of the image.
    l1 : int
        Length of longer side making the angle.
    l2 : int
        Length of shorter side making the angle.
    theta : float
        Angle made by l1 and l2.
    spacing : int, optional
        Spacing between triangles.
    rotation : float, optional
        Angle of rotation (in degrees) of the image.

    Returns
    -------
    img : ndarray
        Image with triangles of the same size.

    """
    # check argument type
    check_vars = (xdim, ydim, l1, l2, spacing)
    check_vars_names = ('xdim', 'ydim', 'l1', 'l2', 'spacing')
    check_vars_type = (int, int, int, int, int)
    check_vars_type_names = ('int', 'int', 'int', 'int', 'int')
    check_argument_type(check_vars, check_vars_names, check_vars_type, check_vars_type_names)
    # require l1 to be longer side
    if l1 < l2:
        raise ValueError('`l1` is the longer side, `l2` is the shorter side.')
    # require angle be bounded by (0, 180)
    if 0 >= theta or theta >= 180:
        raise ValueError('`theta` has a range of (0, 180) in degrees.')

    def polar2cartesian(r, angle):
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        return x, y

    # create empty image
    shape = (ydim, xdim)
    img = np.zeros(shape)
    # calculate base triangle coordinates
    theta = np.radians(theta)
    x0 = 0  # origin
    y0 = 0  # origin
    x1 = l1  # horizontal
    y1 = 0  # horizontal
    x2, y2 = polar2cartesian(l2, theta)
    base_x = np.array([x0, x1, x2])
    base_y = np.array([y0, y1, y2])
    # calculate parameters
    half_major_box = l1 + spacing
    major_box = 2 * half_major_box
    minor_box = y2 + spacing
    shift_x = np.arange(half_major_box, xdim - half_major_box, major_box)
    shift_y = np.arange(minor_box, ydim - minor_box, minor_box)

    # draw triangles
    for i in range(len(shift_y)):
        for j in range(len(shift_x)):
            rr, cc = draw.polygon(base_y + shift_y[i], base_x + shift_x[j])
            img[rr, cc] = 1

    # rotate image
    img = transform.rotate(img, rotation, resize=True)

    return img


# img_set = []
# for radius in np.arange(20, 35, 5):
#     img = circle_img(500, 500, int(radius))
#     labeled_img = measure.label(img)
#     img_set.append(labeled_img)
# df = extraction.extract_properties_from_img_set(img_set)
# vampire_model = model.Vampire('circles', num_clusters=2, random_state=1)
# vampire_model.build(df)
# apply_properties_df = vampire_model.apply(df)
# plot.set_plot_style()
# plot.plot_representatives(vampire_model, apply_properties_df, alpha=0.5)
# plot.plot_distribution_contour_dendrogram(vampire_model,
#                                           apply_properties_df,
#                                           height_ratio=[4, 1, 1])
# plt.show()

# img_set = []
# for major in np.arange(10, 100, 5):
#     img = rectangle_img(500, 500, int(major), 5)
#     labeled_img = measure.label(img)
#     img_set.append(labeled_img)
# df = extraction.extract_properties_from_img_set(img_set)
# vampire_model = model.Vampire('rectangles', num_clusters=5, random_state=1)
# vampire_model.build(df)
# apply_properties_df = vampire_model.apply(df)
# plot.set_plot_style()
# plot.plot_representatives(vampire_model, apply_properties_df, alpha=0.5)
# plot.plot_distribution_contour_dendrogram(vampire_model,
#                                           apply_properties_df,
#                                           height_ratio=[4, 1, 1])
# plt.show()

# img_set = []
# for major in np.arange(10, 100, 5):
#     for angle in np.arange(0, 90, 30):
#         img = rectangle_img(500, 500, int(major), 5, rotation=angle)
#         labeled_img = measure.label(img)
#         img_set.append(labeled_img)
# df = extraction.extract_properties_from_img_set(img_set)
# vampire_model = model.Vampire('rectangles-rotated', num_clusters=5, random_state=1)
# vampire_model.build(df)
# apply_properties_df = vampire_model.apply(df)
# plot.set_plot_style()
# plot.plot_representatives(vampire_model, apply_properties_df, alpha=0.5)
# plot.plot_distribution_contour_dendrogram(vampire_model,
#                                           apply_properties_df,
#                                           height_ratio=[4, 1, 1])
# plt.show()


img_set = []
for l1 in np.arange(20, 100, 10):
    for angle in np.arange(10, 180, 30):
        img = triangle_img(500, 500, int(l1), 15, theta=angle)
        labeled_img = measure.label(img)
        img_set.append(labeled_img)
df = extraction.extract_properties_from_img_set(img_set)
vampire_model = model.Vampire('triangles', num_clusters=5, random_state=1)
vampire_model.build(df)
apply_properties_df = vampire_model.apply(df)
plot.set_plot_style()
plot.plot_representatives(vampire_model, apply_properties_df, alpha=0.5)
plot.plot_distribution_contour_dendrogram(vampire_model,
                                          apply_properties_df,
                                          height_ratio=[4, 1, 1])
plt.show()

# import matplotlib.pyplot as plt
# from vampire import processing
# plt.imshow(object_img)
# plt.plot(*contour, '.-')
# plt.plot(*processing.sample_contour(contour, 50), '.-')
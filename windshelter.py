import numpy as np
from numpy.lib.stride_tricks import as_strided
import rasterio
import os
from collections import deque


def sliding_window_view(arr, window_shape, steps):
    """
    Produce a view from a sliding, striding window over `arr`.
    The window is only placed in 'valid' positions - no overlapping
    over the boundary
    """

    in_shape = np.array(arr.shape[-len(steps):])  # [x, (...), z]
    window_shape = np.array(window_shape)  # [Wx, (...), Wz]
    steps = np.array(steps)  # [Sx, (...), Sz]
    nbytes = arr.strides[-1]  # size (bytes) of an element in `arr`

    # number of per-byte steps to take to fill window
    window_strides = tuple(np.cumprod(arr.shape[:0:-1])[::-1]) + (1,)
    # number of per-byte steps to take to place window
    step_strides = tuple(window_strides[-len(steps):] * steps)
    # number of bytes to step to populate sliding window view
    strides = tuple(int(i) * nbytes for i in step_strides + window_strides)

    outshape = tuple((in_shape - window_shape) // steps + 1)
    # outshape: ([X, (...), Z], ..., [Wx, (...), Wz])
    outshape = outshape + arr.shape[:-len(steps)] + tuple(window_shape)
    return as_strided(arr, shape=outshape, strides=strides, writeable=False)


def sector_mask(shape, centre, radius, angle_range):  # used in windshelter_prep
    """
    Return a boolean mask for a circular sector. The start/stop angles in
    `angle_range` should be given in clockwise order.
    """

    x, y = np.ogrid[:shape[0], :shape[1]]
    cx, cy = centre
    tmin, tmax = np.deg2rad(angle_range)

    # ensure stop angle > start angle
    if tmax < tmin:
        tmax += 2 * np.pi

    # convert cartesian --> polar coordinates
    r2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
    theta = np.arctan2(x - cx, y - cy) - tmin

    # wrap angles between 0 and 2*pi
    theta %= (2 * np.pi)

    # circular mask
    circmask = r2 <= radius * radius

    # angular mask
    anglemask = theta <= (tmax - tmin)

    a = circmask * anglemask

    return a


def windshelter_prep(radius, direction, tolerance, cellsize):
    x_size = y_size = 2 * radius + 1
    x_arr, y_arr = np.mgrid[0:x_size, 0:y_size]
    cell_center = (radius, radius)
    dist = (np.sqrt((x_arr - cell_center[0]) ** 2 + (y_arr - cell_center[1]) ** 2)) * cellsize
    # dist = np.round(dist, 5)

    mask = sector_mask(dist.shape, (radius, radius), radius, (direction, tolerance))

    return dist, mask


def windshelter(x, profile, prob, dist, mask, radius):  # applying the windshelter function
    data = x * mask
    data[data == profile['nodata']] = np.nan
    data[data == 0] = np.nan
    center = data[radius, radius]
    data[radius, radius] = np.nan
    data = np.arctan((data - center) / dist)
    data = np.nanquantile(data, prob)
    return data


def windshelter_window(array, profile, radius, prob, cell_size, wd='.'):
    dist, mask = windshelter_prep(radius, 180, 45, cell_size)
    window = sliding_window_view(array[-1], ((radius * 2) + 1, (radius * 2) + 1), (1, 1))

    nc = window.shape[0]
    nr = window.shape[1]
    ws = deque()

    for i in range(nc):
        for j in range(nr):
            data = window[i, j]
            data = windshelter(data, profile, prob, dist, mask, radius).tolist()
            ws.append(data)

    data = np.array(ws)
    data = data.reshape(nc, nr)
    data = np.pad(data, pad_width=radius, mode='constant', constant_values=0)
    data = data.reshape(1, data.shape[0], data.shape[1])

    profile.update({"dtype": "float64"})

    # Save raster to path using meta data from dem.tif (i.e. projection)
    with rasterio.open(os.path.join(wd, 'windshelter.tif'), "w", **profile) as dest:
        dest.write(data)

    print(os.path.join(wd, 'windshelter.tif'))


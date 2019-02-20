from astropy.io import fits
import numpy as np
import sys
import os

try:
    from PIL import Image
except ImportError:
    import Image


# Returns a byte-scaled image
def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    """
    Code source: https://github.com/scipy/scipy/blob/v0.19.1/scipy/misc/pilutil.py

    Byte scales an array (image).
    Byte scaling means converting the input image to uint8 dtype and scaling
    the range to ``(low, high)`` (default 0-255).
    The values smaller than `min` will be set to `min`, and same for `max`.
    If the input image already has dtype uint8, no scaling is done.

    Parameters
    ----------
    data : ndarray
        PIL image data array.
    cmin : scalar, optional
        Bias scaling of small values. Default is ``data.min()``.
    cmax : scalar, optional
        Bias scaling of large values. Default is ``data.max()``.
    high : scalar, optional
        Scale max value to `high`.  Default is 255.
    low : scalar, optional
        Scale min value to `low`.  Default is 0.
    Returns
    -------
    img_array : uint8 ndarray
        The byte-scaled array.
    Examples
    --------
    >>> from scipy.misc import bytescale
    >>> img = np.array([[ 91.06794177,   3.39058326,  84.4221549 ],
    ...                 [ 73.88003259,  80.91433048,   4.88878881],
    ...                 [ 51.53875334,  34.45808177,  27.5873488 ]])
    >>> bytescale(img)
    array([[255,   0, 236],
           [205, 225,   4],
           [140,  90,  70]], dtype=uint8)
    >>> bytescale(img, high=200, low=100)
    array([[200, 100, 192],
           [180, 188, 102],
           [155, 135, 128]], dtype=uint8)
    >>> bytescale(img, cmin=0, cmax=255)
    array([[91,  3, 84],
           [74, 81,  5],
           [52, 34, 28]], dtype=uint8)
    """
    if data.dtype == np.uint8:
        return data

    if high > 255:
        raise ValueError("`high` should be less than or equal to 255.")
    if low < 0:
        raise ValueError("`low` should be greater than or equal to 0.")
    if high < low:
        raise ValueError("`high` should be greater than or equal to `low`.")

    min_data = data.min()
    max_data = data.max()

    print(f"Initial brightness range: ({min_data},{max_data})")

    if cmin is None:
        cmin = min_data

    if cmax is None:
        cmax = max_data

    # The values smaller than `min` will be set to `min`, and same for `max`
    data[data < cmin] = cmin
    data[data > cmax] = cmax

    cscale = cmax - cmin
    if cscale < 0:
        raise ValueError("`cmax` should be larger than `cmin`.")
    elif cscale == 0:
        cscale = 1

    scale = float(high - low) / cscale
    bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype(np.uint8)


def array2image(data, smin, smax):
    """
    Converts an 2D array of image data to Image.

    The code is based on deprecated `toimage` function from 
    https://github.com/scipy/scipy/blob/v0.19.1/scipy/misc/pilutil.py

    Parameters
    ----------
    data : 2D list
        The image data from the FITS file.

    smin : int
    smax : int
        Specifies the range of the input pixel brightness values that will
        be linearly mapped to output range of (0,255):
            output = ((input - min) / (max - min)) * 255."

    Returns
    -------
    Image
        The Image object.

    """

    data = np.asarray(data)
    shape = list(data.shape)

    if len(shape) != 2:
        raise ValueError("ERROR: the image data needs to be in 2D.")

    shape = (shape[1], shape[0])  # columns show up first
    bytedata = bytescale(data, high=255, low=0, cmin=smin, cmax=smax)
    return Image.frombytes('L', shape, bytedata.tostring())


def fits2image(fits_path, output_path, smin=None, smax=None, rewrite=False, silent=True, extension=0, flipy=False):
    """
    Converts a FITS files to an image.

    Parameters
    ----------
    fits_path : str
        Path to existing input FITS file.

    output_path : str
        Path to the output image file that will be created. The image format is determined automatically from
    extension.

    smin : int
    smax : int
        Specifies the range of the input pixel brightness values that will
        be linearly mapped to output range of (0,255):
            output = ((input - min) / (max - min)) * 255."

        The values smaller than `min` will be set to `min`, and same for `max`.

    rewrite : bool
        If True the output file will be rewritten.

    silent : bool
        If True the utility does not print messages, except in case of errors.

    extension : int
        the FITS extension number that is used for image data (FITS files can contain multiple images, which are called 'extensions'). By default, the first extension is used (-extension=0). The extension numbers start from 0.

    flipy: bool
        Flip the image vertically.

    """

    if not os.path.exists(fits_path):
        print(f"ERROR: the input file does not exit: '{fits_path}'.")
        exit(2)

    if rewrite:
        if os.path.exists(output_path):
            os.remove(output_path)
    else:
        if os.path.exists(output_path):
            print(f"ERROR: the output file already exists: '{output_path}'. Use '-rewrite' option to allow rewriting the output file.")
            exit(3)

    # Create the output directory
    output_dir = os.path.dirname(output_path)

    if type(output_dir) == str and output_dir.strip() and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not silent:
        print("Exporting FITS file...")

    # Read the fits file data
    with fits.open(fits_path) as hdul:
        data = hdul[extension].data

        # Flip image vertically
        if flipy:
            data = np.flipud(data)

        # Save the data to image
        array2image(data=data, smin=smin, smax=smax).save(output_path)

        if not silent:
            print("Done")


def extract_argyments(x):
    key_value = x.lstrip('-').split('=')

    if len(key_value) == 1:
        return [key_value[0], True]

    return key_value


def int_option(options, name, default):
    """
    Returns an integer value of a command line option with `name` from `options` dictionary.

    Parameters
    ----------
    options : dict
        A dictionary containing command line options, where keys are the option names and values are the values.

    name : str
        The name of the command line option.

    default: int
        The default value of the command line option to use if it is missing in `options`.

    Returns
    -------
    int
        The value of the option.
    """

    if name in options:
        value = options[name]
        try:
            return int(value)
        except ValueError:
            print(f"ERROR: option '{name}' needs to be an integer number.")
            exit(1)
    else:
        return default


if __name__ == '__main__':
    arguments = sys.argv[1:]

    if len(arguments) < 2:
        print("ERROR: incorrect arguments.\n")
        print("Usage example:\n")
        print("$ ./fits2image input.fits output.png [-min=0] [-max=300] [-rewrite] [-silent] [-extension=0] [-flipy]\n")
        print("Options:")
        print("   -min, -max: specifies the range of the input pixel brightness values that will\n"
              "         be linearly mapped to output range of (0,255):\n"
              "             output = ((input - min) / (max - min)) * 255.\n\n"
              "   -rewrite: rewrites the output file.\n\n"
              "   -extension: the FITS extension number that is used for image data (FITS files can contain multiple images, which are called 'extensions'). By default, the first extension is used (-extension=0). The extension numbers start from 0.\n\n"
              "   -silent: do not show non-error output messages.\n\n"
              "   -flipy: flip the image vertically.\n\n")
        exit(4)

    fits_path = arguments[0]
    output_path = arguments[1]
    arguments = arguments[2:]

    options = {}

    if len(arguments) > 0:
        options = dict(map(extract_argyments, arguments))

    fits2image(fits_path=fits_path,
               output_path=output_path,
               rewrite=options.get('rewrite', False),
               silent=options.get('silent', False),
               smin=int_option(options=options, name='min', default=None),
               smax=int_option(options=options, name='max', default=None),
               extension=int_option(options=options, name='extension', default=0),
               flipy=options.get('flipy', False))

from astropy.io import fits
import numpy as np
import scipy.misc
import sys
import os


def fits2image(fits_path, output_path, smin=None, smax=None, rewrite=False, silent=True, extension=0):
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
        be linearly mapped to output range of (0,255) of the PNG pixels:
            output = ((input - min) / (max - min)) * 255."

    rewrite : bool
        If True the output file will be rewritten.

    silent : bool
        If True the utility does not print messages, except in case of errors.

    extension : int
        the FITS extension number that is used for image data (FITS files can contain multiple images, which are called 'extensions'). By default, the first extension is used (-extension=0). The extension numbers start from 0.

    """

    if not os.path.exists(fits_path):
        print(f"ERROR: the input file does not exit: '{fits_path}'.")
        exit(2)

    if rewrite:
        if os.path.exists(output_path):
            os.remove(output_path)
    else:
        if os.path.exists(output_path):
            print(f"ERROR: the output file already exists: '{output_path}'.")
            exit(3)

    # Create the output directory
    output_dir = os.path.dirname(output_path)

    if type(output_dir) == str and output_dir.strip() and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not silent:
        print("Exporting FITS file...")

    # Read the first fits file data
    with fits.open(fits_path) as hdul:
        data = hdul[extension].data
        data = np.flipud(data)
        scipy.misc.toimage(data, cmin=smin, cmax=smax).save(output_path)

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
        print("$ ./fits2png input.fits output.png [-min=0] [-max=300] [-rewrite] [-silent] [-extension=0]\n")
        print("Options:")
        print("   -min, -max: specifies the range of the input pixel brightness values that will\n"
              "         be linearly mapped to output range of (0,255) of the PNG pixels:\n"
              "             output = ((input - min) / (max - min)) * 255.\n\n"
              "   -rewrite: rewrites the output file.\n\n"
              "   -extension: the FITS extension number that is used for image data (FITS files can contain multiple images, which are called 'extensions'). By default, the first extension is used (-extension=0). The extension numbers start from 0.\n\n"
              "   -silent: do not show non-error output messages.")
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
               extension=int_option(options=options, name='extension', default=0))

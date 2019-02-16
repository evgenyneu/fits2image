# Export FITS to image file

This is a utility written in Python 3 that converts a FITS file into image format like png or jpeg.

## Installation

### Clone the repository

Run the following from the Terminal (requires [git to be installed](https://git-scm.com/downloads)):

```
git clone https://github.com/evgenyneu/fits2image.git
cd fits2image
```

### Install Python 3

Check if Python 3 is installed by running command

```
python3 --version
```

If Python 3 is installed, you will see its version number. If you see an error, then [install Python 3](https://www.python.org/downloads/).


### Install Python libraries

Run the following commands to install the libraries which are used by this utility:


```
pip3 install numpy
pip3 install scipy
pip3 install astropy
```

### Add executable to your PATH

Add the path to the `fits2image` directory to your `~/.bash_profile` (Mac) or `~/.bashrc` (Linux):

```
export PATH="/YOUR_PATH_HERE:${PATH}"
```

where YOUR_PATH_HERE is your full path to the `fits2image` directory. To quickly get this path, type `pwd` from the `fits2image` directory.

When this is done, restart your Terminal to take this new PATH into effect.



## Usage

Run the following command from the `fits2image` directory to export `input.fits` into `output.png`:


```
fits2image input.fits output.png
```


### Usage options

Run `./fits2png` without parameters to see the full list of options:

```
fits2image input.fits output.png [-min=0] [-max=300] [-rewrite] [-silent] [-extension=0]
```

* **-min, -max**: specifies the range of the input pixel brightness values that will be linearly mapped to output range of (0,255) of the PNG pixels: 

```
output = ((input - min) / (max - min)) * 255.
```

* **-rewrite**: rewrites the output file.

* **-extension**: the FITS extension number that is used for image data (FITS files can contain multiple images, which are called 'extensions'). By default, the first extension is used (-extension=0). The extension numbers start from 0.

* **-silent**: do not show non-error output messages.


## License

Dodo is released under the [MIT License](LICENSE).

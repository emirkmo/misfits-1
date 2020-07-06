# `misfits`

`misfits` is an interactive tool to measure spectral features in spectra of
transients and approximate errors if they're not available.

## Installation

### Setup virtual environment (optional, but recommended)
<pre><code>$ cd /directory/for/virtual/environments
$ python3 -m venv --copies misfits
$ source misfits/bin/activate</code></pre>

### Install `misfits`
<pre><code>$ cd /directory/of/misfits
$ pip install -r requirements.txt
$ python setup.py install</code></pre>

## Example

<pre><code>$ misfits lowpass rawsmooth velocity.gaussians montecarlo spectrum.fits -z 0.01</code></pre>

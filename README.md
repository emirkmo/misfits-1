# `misfits`

`misfits` is an interactive tool to measure spectral features in spectra of transients and approximate their errors.

## Installation

### Setup virtual environment (optional, but recommended)
<pre><code>$ cd /directory/for/virtual/environments
$ python3 -m venv --copies misfits
$ source misfits/bin/activate</code></pre>

### Installing `misfits`
<pre><code>$ cd /directory/of/misfits
$ pip install -r requirements.txt
$ python setup.py install</code></pre>

## Example

Estimate an error spectrum from a low-pass filtered spectrum and use it when fitting Gaussians to measure line velocities and their errors.
<pre><code>$ misfits lowpass rawsmooth velocity.gaussians montecarlo spectrum.fits</code></pre>

Run `$ misfits --help` for a list of methods and arguments.

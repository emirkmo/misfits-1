# create spectrum file with smoothed spectrum

input_file=spectrum.fits
smooth_method=lowpass

misfits $smooth_method - - - $1 --save - | \
    tail -n+2 | awk '{print $1" "$4}'

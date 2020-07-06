# create spectrum file with error spectrum in 3rd column

error_method=rawsmooth
smooth_method=lowpass # if necessary

misfits $smooth_method $error_method - - $1 --save - | \
    tail -n+2 | awk '{print $1" "$2" "$3}'

# batch process list of files

smooth_method=lowpass # if necessary
error_method=rawsmooth # if necessary
feature_method=velocity.gaussians # if necessary
uncertainty_method=montecarlo # if necessary

file=$(head -n1 $1)

echo "# $file"
misfits $smooth_method $error_method $feature_method $uncertainty_method \
    $file --save tmp

for file in $(tail -n+2 $1)
do

    echo "# $file"
    misfits $smooth_method $error_method $feature_method $uncertainty_method \
        $file --inherit tmp --headless --save tmp

done

rm tmp

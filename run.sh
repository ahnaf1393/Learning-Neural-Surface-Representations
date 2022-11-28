#! /bin/bash
source $HOME/anaconda3/etc/profile.d/conda.sh

echo 'Checking input type'
python check_input.py --loc $1 --number_frames 50

echo 'Running image segmentation'
cd './MiVOS-MiVOS-STCN'
python interactive_gui.py --images $1

echo 'Cleaning masks'
cd '..'
python clean_masks.py --loc $1

echo 'Running camera tracking'
IMAGEPATH="${1}/image"
MASKPATH="${1}/mask"
colmap automatic_reconstructor --workspace_path $1 --image_path $IMAGEPATH --mask_path $MASKPATH --data_type video --quality extreme --single_camera 1

echo 'Creating cameras file'
python create_npz.py --loc $1 --scale 4

echo 'Editing the conf file'
python edit_conf.py --loc $1

echo 'Loading environment: idr'
conda activate idr

echo 'Running IDR'
cd 'idr/code'
python training/exp_runner.py --train_cameras --conf ./confs/video_trained_cameras.conf --loc $1

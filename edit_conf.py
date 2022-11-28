from argparse import ArgumentParser
import glob
import cv2


parser = ArgumentParser()
parser.add_argument('--loc', help='Folder containing the input')
args = parser.parse_args()

height, width, _ = cv2.imread(glob.glob(args.loc +  '/image/*.png')[0]).shape


my_file = open("./idr/code/confs/video_trained_cameras.conf")
string_list = my_file.readlines()
my_file.close()


first_part = string_list[26][:15]
new_line = f'{first_part}{str(height)}, {str(width)}]\n'
print(new_line)
string_list[26] = new_line

my_file = open("./idr/code/confs/video_trained_cameras.conf", "w")
new_file_contents = "".join(string_list)

my_file.write(new_file_contents)
my_file.close()

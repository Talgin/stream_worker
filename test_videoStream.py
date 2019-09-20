import video_thread
import argparse


''' Reading arguments as input to model '''

parser = argparse.ArgumentParser(description='Video stream catching test')
parser.add_argument('--first-folder', default='/home/ti/Downloads/FindFace/FindFace/application/static/folders/first', help='')
parser.add_argument('--second-folder', default='/home/ti/Downloads/FindFace/FindFace/application/static/folders/second', help='')
parser.add_argument('--det-model', default='/home/ti/Downloads/MODELS/retinaface-R50/R50', help='path to load model.')
parser.add_argument('--source', default='rtsp://admin:Admin123!@10.150.30.202:554/live', help='path to load model.') 
parser.add_argument('--gpu', default=0, type=int, help='gpu id')
parser.add_argument('--scales', default='1080,1920', help='Frame dimensions')
parser.add_argument('--det-threshold', default=0.8, type=float, help='Detection threshold')
parser.add_argument('--rect', default=0, type=int, help='Whether draw rectangle or not')
parser.add_argument('--image-size', default=112, type=int, help='Dimensions of the detected face rectangle')
parser.add_argument('--txt', default=0, type=int, help='Whether put text with x, y coordinates of detected face or not')
parser.add_argument('--show-frame', default=1, type=int, help='Whether or not to show the frame: 1 -show, 0 - do not show')
parser.add_argument('--input-type', default=1, type=int, help='1 - use camera as input, 0 - use video file as input')
args = parser.parse_args()

''' End of reading args '''

# First folder where streamed frames were saved
first_folder = args.first_folder
# Second folder where the contents of the first folder were copied
second_folder = args.second_folder
# Detection model for face detection from stream
det_model = args.det_model
# Link to camera
source = args.source
# ID of the GPU to be used
gpuid = args.gpu
# Size of the camera image [1024, 1980]
splt = args.scales.split(',')  				
splt = int(splt[0]),int(splt[1])
scales = list(splt)
# Face detection threshold
det_threshold = args.det_threshold	
# 1 - draw rectangle, 0 - do not draw
rect = args.rect
# Size of the cropped image
img_size = args.image_size
# 1 - put text with coordinates of the face rectangle, 0 - do not put text
txt = args.txt
# 1 - show the frame with current detection, 0 - do not show the frames
show_frame = args.show_frame
# Choosing input type: 1 - camera, 0 - video
input_type = args.input_type


streams = video_thread.videoStream(first_folder, second_folder, det_model, source, gpuid, scales, det_threshold, rect, img_size, txt, show_frame, input_type)
# rtsp://admin:Admin1234!@10.150.30.203:554/live
# rtsp://admin:qwerty123456@10.150.30.207:554/Streaming/Channels/101
# fvs = WebcamVideoStream(src='rtsp://admin:Admin123!@10.150.30.202:554/live').start()	# back of the office

streams.begin()

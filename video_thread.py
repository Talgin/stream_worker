# This is faster version of video capture and face detection module that utilizes
# RetinaFace face detector
# You can change face detection model on the 24-th line changing the first parameter for detector
# Module uses Adrian Rosebrock's imutils library for faster video processing
import cv2
import sys
import numpy as np
import datetime
import os, time
import glob
from imutils.video import FileVideoStream
from imutils.video import FPS
from imutils.video import WebcamVideoStream
import imutils
from retinaface import RetinaFace
import skimage
import threading
from shutil import copyfile

class videoStream:
	def __init__(self, first_folder, second_folder, detection_model, source, gpu_id, scales, detection_threshold, rect, img_size, txt, show_frame, input_type):
		self.path_to_watch = first_folder		
		self.where_to_move = second_folder		
		self.detection_model = detection_model	# path to models folder, default: './MODELS/retinaface-R50/R50'
		self.source = source					# 'rtsp://admin:qwerty123456@10.150.30.207:554/Streaming/Channels/101'
		self.gpu_id = gpu_id
		self.scales = scales
		self.detection_threshold = detection_threshold
		self.rect = rect
		self.img_size = img_size
		self.txt = txt
		self.show_frame = show_frame
		self.input_type = input_type

	# Reading folder changes and performing face detection and cropping
	def readFolder(self):		
		before = dict([(f, None) for f in os.listdir(self.path_to_watch)])
		while 1:
		  time.sleep(1)
		  after = dict([(f, None) for f in os.listdir(self.path_to_watch)])
		  added = [f for f in after if not f in before]
		  if added > 0: 
		  	for f in added:
		  		copyfile(self.path_to_watch + '/' + f, self.where_to_move + '/' + f)

		  removed = [f for f in before if not f in after]
		  if added: print "Added: ", ", ".join(added)
		  if removed: print "Removed: ", ", ".join(removed)
		  before = after


	def begin(self):
		count = 1
		gpuid = self.gpu_id		# ID of the GPU to be used
		
		# Loading model for face detection
		detector = RetinaFace(self.detection_model, 0, gpuid, 'net3')
		fvs = None
		if self.input_type:
			# Reading input from camera
			try:
				fvs = WebcamVideoStream(src=self.source).start()	# inside the office		
				# time.sleep(0.5)
			except:
				print('bad link')
		else:
			fvs = FileVideoStream(self.source).start()
			# time.sleep(1)

		# Start fps counter
		fps = FPS().start()

		# Start folder reading and copying to second folder in thread
		thread = threading.Thread(target=self.readFolder, args=())
		thread.daemon = True
		thread.start() 

		cnt = 0
		# Main loop
		while True:
		  img = fvs.read()

		  scales = self.scales 
		    
		  # print(img.shape)
		  # print(scales[1])
		  im_shape = img.shape
		  target_size = scales[0]
		  max_size = scales[1]
		  im_size_min = np.min(im_shape[0:2])		  
		  im_size_max = np.max(im_shape[0:2])

		  im_scale = float(target_size) / float(im_size_min)
		  
		  if np.round(im_scale * im_size_max) > max_size:
		      im_scale = float(max_size) / float(im_size_max)

		  scales = [im_scale]
		  flip = False

		  for c in range(count):
		    faces, landmarks = detector.detect(img, self.detection_threshold, scales=scales, do_flip=flip)

		  if faces is not None:
		    print('Found ' + str(faces.shape[0]) + ' face(s)')
		    for i in range(faces.shape[0]):
		      box = faces[i].astype(np.int)		      
		      # Set filename 
		      filename = str(datetime.datetime.now()).replace(":", "_").replace(".", "_").replace("-", "_").replace(' ', '_') + '.jpg'
		      # Calculate cropping area
		      x = box[3] - box[1]
		      y = box[2] - box[0]
		      if x > 45 and y > 22:
		      	# print("x: " + str(x))
		      	# print("y: " + str(y))
		      	center_y = box[1] + ((box[3] - box[1])/2) 		# calculating center of the x side
		      	center_x = box[0] + ((box[2] - box[0])/2) 		# calculating center of the y side
		      	rect_y = center_y - self.img_size/2  			# calculating starting x of rectangle
		      	rect_x = center_x - self.img_size/2  			# calculating starting y of rectangle
		      	
		      	# If rect is True draw rectangle around face
		      	if self.rect:
		      	  # Rectangle around cropping area, we put more than img_size because sometimes borders of rectangle also get cropped
		      	  color = (0,255,0)
		      	  cv2.rectangle(img, (rect_x, rect_y), (rect_x + self.img_size + 3, rect_y + self.img_size + 3), color, 2)  	

		      	# If txt is True put text with coordinates of the face rectangle
		      	if self.txt:
		      	  font = cv2.FONT_HERSHEY_SIMPLEX
		      	  text = 'x: ' + str(box[0]) + ';  y: ' + str(box[1]) # + ' ' + str(box[2]) + ' ' + str(box[3])
		      	  cv2.putText(img,text,(50,50), font, 1, (0,255,255), 2, cv2.LINE_AA)
			      		      
		      	try:
		      	  cv2.imwrite(self.path_to_watch + '/' + filename, img)
		        except:
		      	  print('Folder not found!')

		      	# If show_frame True view frame on screen - this makes system a bit slower, because it consumes part of resources to show this frame
		      	if self.show_frame:
		      	  cv2.imshow('image', img)
		      
		  # Update fps counter
		  fps.update()

		  if cv2.waitKey(1) & 0xFF == ord('q'):
		    break
		  

		fps.stop()
		print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
		print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

		cv2.destroyAllWindows()
		fvs.stop()

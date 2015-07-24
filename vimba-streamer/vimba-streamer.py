from pymba import *
import numpy as np
import cv2
import time
import scipy
import scipy.misc
import numpy
import StringIO
import pymjpeg
import Image
import sys
import PIL
from PIL import Image

from server import MjpegServerBoss

#very crude example, assumes your camera is PixelMode = BAYERRG8

# start Vimba
with Vimba() as vimba:
    
        
    if "mono" in sys.argv:
        greyscale = True
    else:
        greyscale = False
    if "compressed" in sys.argv:
        rescaleImage = True
        IMAGE_WIDTH  = 512
        IMAGE_HEIGHT = 512
    else:
        rescaleImage = False
        IMAGE_WIDTH  = 1330
        IMAGE_HEIGHT = 1330

    print "Greyscale:", greyscale
    print "Rescale:  ", rescaleImage
    print "Width:    ", IMAGE_WIDTH
    print "Height:   ", IMAGE_HEIGHT

    # get system object
    system = vimba.getSystem()

    # Start MJPEG Server
    S = MjpegServerBoss()
    S.start_server()

    # list available cameras (after enabling discovery for GigE cameras)
    if system.GeVTLIsPresent:
        system.runFeatureCommand("GeVDiscoveryAllOnce")
        time.sleep(0.2)
    cameraIds = vimba.getCameraIds()
    selectedCameraID = cameraIds[0]
    for cameraId in cameraIds:
        print 'Camera ID: ', cameraId

    # get and open a camera
    try:
        camera0 = vimba.getCamera(selectedCameraID)
    except IndexError:
        print "No GigE Cameras Found. Check connections, IP, and Subnet then try again."
        sys.exit()
    
    camera0.openCamera()
    camera0.PixelFormat = "RGB8Packed"
    # list camera features
    #cameraFeatureNames = camera0.getFeatureNames()
    #for name in cameraFeatureNames:
    #    print 'Camera feature:', name

    # read info of a camera feature
    #featureInfo = camera0.getFeatureInfo('PixelFormat')
    #for field in featureInfo.getFieldNames():
    #    print field, '--', getattr(featureInfo, field)

    # get the value of a feature
    #print camera0.AcquisitionMode

    # set the value of a feature

    # create new frames for the camera
    frame0 = camera0.getFrame()    # creates a frame
    frame1 = camera0.getFrame()    # creates a second frame

    # announce frame
    frame0.announceFrame()

    # capture a camera image
    count = 0
    camera0.startCapture()
    print "Stream Started!"
    while 1:
        frame0.queueFrameCapture()
        camera0.runFeatureCommand('AcquisitionStart')
        camera0.runFeatureCommand('AcquisitionStop')
        frame0.waitFrameCapture()
        
        #a = frame0.getBufferByteData():
        # get image data...
        image_data = np.ndarray(buffer = frame0.getBufferByteData(),
                                       dtype = np.uint8,
                                       shape = (frame0.height,
                                                frame0.width, frame0.pixel_bytes))
        img = scipy.misc.toimage(image_data)
        img = img.rotate(90) 
        # Save bitmap image locally
        img.save("vimba-images/" + selectedCameraID + "_" + str(time.time()) + ".jpg", "JPEG")
        
        # Compress for UI
        if rescaleImage == True:
            img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), PIL.Image.ANTIALIAS)
        # Greyscale
        if greyscale == True:
            img = img.convert('L')
        output = StringIO.StringIO()
        img.save(output, "JPEG")

        contents=output.getvalue()
        output.close()
        # Send to server
        S.new_image_data(contents)
        count += 1

    camera0.endCapture()
    # clean up after capture
    camera0.revokeAllFrames()

    # close camera
    camera0.closeCamera()


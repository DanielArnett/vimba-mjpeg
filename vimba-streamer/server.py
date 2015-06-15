"""
INSTRUCTIONS FOR USE:
=====================

1) Towards the start of your code, import this module.

2) Towards the start of your code, start the server by running:

        S = MjpegServerBoss()
        S.start_server()

3) To update the image, run this line of code:

        S.new_image_data(img)

   ...where `img` is a **binary** string of the raw JPEG data you want to send
   to clients.
"""



import pymjpeg
from glob import glob
import sys

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import threading
import time



# Global constants.
LOOP_WAIT_TIME = 1.0



class MjpegRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global LOOP_WAIT_TIME

        self.send_response(200)
        # Response headers (multipart)
        for k, v in pymjpeg.request_headers().items():
            self.send_header(k, v) 
        # Multipart content
        while (True):
            self.end_headers()
            self.wfile.write(pymjpeg.boundary)
            self.end_headers()
            for k, v in pymjpeg.image_headers(content=self.server.image_data).items():
                self.send_header(k,v)
            self.end_headers()
            # Write the image data.
            print "Writing image data"
            self.wfile.write(self.server.image_data)
            # Wait...
            time.sleep(LOOP_WAIT_TIME)

    def log_message(self, format, *args):
        return



class MjpegServer(HTTPServer):
    def new_image_data (self, image_data):
        self.image_data = image_data



class MjpegServerBoss:
    def __init__ (self):
        self.httpd = None
        self.t1 = None
        self.image_data = ""

    def start_server (self):
        self.httpd = MjpegServer(('', 8001), MjpegRequestHandler)
        try:
            self.t1 = threading.Thread(target=self.httpd.serve_forever)
            self.t1.daemon = True
            self.t1.start()
        except:
            print "Unable to start new thread."

    def new_image_data (self, image_data):
        self.httpd.new_image_data(image_data)



def test_server ():
    S = MjpegServerBoss()
    S.start_server()
    for filename in glob('img/*'):
        f = open(filename, "rb")
        img = ""
        try:
            byte = f.read(1)
            while byte != "":
                img += byte
                byte = f.read(1)
        finally:
            f.close()
        S.new_image_data(img)
        time.sleep(2.5)
    print "Done!"

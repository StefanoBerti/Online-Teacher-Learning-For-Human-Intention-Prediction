import threading
from multiprocessing.connection import Client
import numpy as np
import pyrealsense2 as rs


class JustText(threading.Thread):
    def __init__(self, port):
        # Connect to master
        super().__init__()
        self.conn = None
        self.port = port

    def run(self):
        address = ('localhost', self.port)
        self.conn = Client(address, authkey=b'secret password')
        while True:
            msg = input("Enter command here: ")
            if msg == "close" or msg == "exit" or msg == "quit":
                break
            self.conn.send(msg)


class RealSense:
    def __init__(self, width=640, height=480):
        self.pipeline = rs.pipeline()
        configs = {'device': 'Intel RealSense D435i'}

        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.profile = self.pipeline.start(config)

        configs['depth'] = {'width': width, 'height': height, 'format': 'z16', 'fps': 30}
        configs['color'] = {'width': width, 'height': height, 'format': 'rgb8', 'fps': 30}

        HIGH_ACCURACY = 3
        HIGH_DENSITY = 4
        MEDIUM_DENSITY = 5
        self.profile.get_device().sensors[0].set_option(rs.option.visual_preset, HIGH_DENSITY)

        configs['options'] = {}
        for device in self.profile.get_device().sensors:
            configs['options'][device.name] = {}
            for option in device.get_supported_options():
                configs['options'][device.name][str(option)[7:]] = str(device.get_option(option))

        self.configs = configs
        self.align = rs.align(rs.stream.depth)

    def intrinsics(self):
        return self.profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()

    def read(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        # depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        # color_frame = aligned_frames.get_color_frame()
        depth_frame = frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = frames.get_color_frame()

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        return True, color_image
        # return color_image, depth_image

    def stop(self):
        self.pipeline.stop()

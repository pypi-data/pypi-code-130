import os
import cv2
import time
from threading import Thread


class Timer:
    def __init__(self, alpha=0.1):
        self.alpha = alpha
        self.time_previous = time.time()

        self.count = 0
        self.latency = 1e-9

    def __call__(self):
        self.count += 1
        time_now = time.time()
        self.time_delta = time_now - self.time_previous
        self.time_previous = time_now

        a = self.alpha
        self.latency = (1-a) * self.latency + a * self.time_delta

        return self.latency


class Video:
    def __init__(self, video_file):
        cap = cv2.VideoCapture(video_file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.cap = cap
        self.fps = fps
        self.size = (width, height)
        self.frame_count = frame_count

        self.timer = Timer()
        self.latency = self.timer.latency

    def __call__(self):
        success = True
        success, self.frame = self.cap.read()
        self.latency = self.timer()
        return success

    def __del__(self):
        self.cap.release()

    def get_pos(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES)

    def set_pos(self, pos):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, pos)


class Video2:
    def __init__(self, video_file, speed=1):
        cap = cv2.VideoCapture(video_file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.cap = cap
        self.fps = fps
        self.size = (width, height)
        self.frame_count = frame_count
        self.step = 1

        self.timer = Timer()
        self.latency = self.timer.latency

        self.success = True
        self.running = True

        self.time_sleep = 0.0
        self.speed = speed

        self.pos_reserved = -999999

        self.success, self.frame = self.cap.read()
        Thread(target=self.run, args=()).start()

        self.pos_prev = -1

    def __call__(self):
        while self.running and self.success:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                self.stop()
            elif key == 32:
                self.step ^= 1
            elif key == ord('q'):
                self.set_pos(self.get_pos() - 100)
            elif key == ord('w'):
                self.set_pos(self.get_pos() + 100)
            if self.pos_prev != self.get_pos():
                self.pos_prev = self.get_pos()
                break
        return self.running

    def run(self):
        while self.running and self.success:
            if self.step:
                self.success, self.frame = self.cap.read()
                self.latency = self.timer()

            time_run = self.timer.time_delta - self.time_sleep
            self.time_sleep = 1 / (self.fps * self.speed) - time_run
            if self.time_sleep < 1e-6:
                self.time_sleep = 1e-6
            time.sleep(self.time_sleep)

            if self.pos_reserved != -999999:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.pos_reserved)
                self.pos_reserved = -999999

    def stop(self):
        self.running = False

    def get_pos(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES)

    def set_pos(self, pos):
        self.pos_reserved = pos


class Writer:
    def __init__(self, video_file, fps, size):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(video_file, fourcc, fps, size)

    def __call__(self, image):
        self.writer.write(image)

    def __del__(self):
        self.writer.release()


class Viewer:
    def __init__(self, video_root):
        extensions = ['.mp4', '.webm', '.avi']
        self.video_root = video_root
        paths = []
        paths = []
        for (root, dirs, files) in os.walk(video_root):
            for f in files:
                if os.path.splitext(f)[1] in extensions:
                    path = os.path.join(root, f)
                    paths.append(path)
                    print(path)
        self.paths = paths
        self.idx = 0
        self.video = Video(self.paths[self.idx])
        self.step = 1

    def __call__(self):
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            return False
        elif key == 32:
            self.step ^= 1
        elif key == ord('q'):
            self.video.set_pos(self.video.get_pos() - 100)
        elif key == ord('w'):
            self.video.set_pos(self.video.get_pos() + 100)
        elif key == ord(']'):
            self.idx += 1
            if self.idx >= len(self.paths):
                self.idx = 0
            self.video = Video(self.paths[self.idx])
            self.video()
        elif key == ord('['):
            self.idx -= 1
            if self.idx < 0:
                self.idx = len(self.paths) - 1
            self.video = Video(self.paths[self.idx])
            self.video()

        success = True
        if self.step:
            success = self.video()
        if success == False:
            self.video = Video(self.paths[self.idx])
            success = self.video()
        return success

    def get_frame(self):
        return self.video.frame

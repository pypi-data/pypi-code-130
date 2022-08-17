import os
import cv2
import time
import numpy as np
from threading import Thread


class Timer:
    def __init__(self, alpha=0.1):
        self.alpha = alpha
        self.time_previous = time.time()

        self.count = 0
        self.latency = 1e-9
        self.time_delta = 0

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

        self.time_wait = 10
        self.checkpoints = [0, 0]

    def __call__(self):
        if self.process_keyinput():
            return False
        success = True
        if self.step:
            if self.step == 1:
                success = self.video()
            else:
                success = self.move(self.step)
        if self.checkpoints[0]:
            if self.video.get_pos() < self.checkpoints[0]:
                self.video.set_pos(self.checkpoints[0])
                success = self.video()
        if self.checkpoints[1]:
            if self.video.get_pos() > self.checkpoints[1]:
                self.video.set_pos(self.checkpoints[0])
                success = self.video()
        if success == False:
            self.video = Video(self.paths[self.idx])
            success = self.video()
        cv2.imshow('status', self.get_status_view())
        return success

    def process_keyinput(self):
        time_run = self.video.timer.time_delta * 1000 - self.time_wait
        time_wait = round(1000 / self.video.fps - time_run)
        if time_wait < 1:
            time_wait = 1
        self.time_wait = time_wait
        key = cv2.waitKey(time_wait) & 0xFF
        if key == 27:
            return True
        elif key == ord(' '):
            if self.step:
                self.step = 0
            else:
                self.step = 1
        elif key == 9:
            self.step = 1
        elif key == ord('q'):
            self.step -= 1
        elif key == ord('w'):
            self.step += 1
        elif key == ord('a'):
            self.move(-1)
        elif key == ord('s'):
            self.move(+1)
        elif key == ord('z'):
            self.move(-100)
        elif key == ord('x'):
            self.move(+100)
        elif key > 47 and key < 58:
            num = key - 48
            pos = num * self.video.frame_count // 10
            self.video.set_pos(pos)
            self.video()
        elif key == ord('-'):
            self.checkpoints[0] = int(self.video.get_pos())
        elif key == ord('='):
            self.checkpoints[1] = int(self.video.get_pos())
        elif key == 8:
            self.checkpoints = [0, 0]
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

    def move(self, diff):
        if diff != 1:
            self.video.set_pos(self.video.get_pos() + diff - 1)
        return self.video()

    def get_status_view(self):
        f, F = self.video.get_pos(), self.video.frame_count
        shape = (32, 480, 3)
        progress_bar = np.zeros(shape, dtype=np.uint8)
        if self.checkpoints[0]:
            x = int((self.checkpoints[0] - 1) / F * shape[1])
            cv2.line(progress_bar, (x, 0), (x, shape[0]), (0, 0, 255), 1)
        if self.checkpoints[1]:
            x = int((self.checkpoints[1] - 1) / F * shape[1])
            cv2.line(progress_bar, (x, 0), (x, shape[0]), (255, 0, 0), 1)
        x = int(f / F * shape[1])
        cv2.line(progress_bar, (x, 0), (x, shape[0]), (0, 255, 0), 1)

        shape = (160, 480, 3)
        view = np.zeros(shape, dtype=np.uint8)
        logs = [
            self.paths[self.idx],
            'File index = %d / %d' % (self.idx, len(self.paths)),
            '(W, H) = (%d, %d)' % (self.video.size[0], self.video.size[1]),
            'Frame = %d / %d (%+d)' % (f, F, self.step),
            'Video FPS: %f' % self.video.fps,
            'Play FPS: %f' % (1 / self.video.latency),
        ]
        p = [5, 20]
        for log in logs:
            cv2.putText(view, log, p, 0, 0.5, (0, 255, 255), 1)
            p[1] += 20

        return np.concatenate([progress_bar, view], axis=0)

    def get_frame(self):
        return self.video.frame

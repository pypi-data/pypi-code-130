import threading

class temp_worker(threading.Thread):
    def __init__(self, map_result_L1, thread_id, map_fxn, args):
        threading.Thread.__init__(self)
        self.map_result_L1 = map_result_L1
        self.thread_id = thread_id
        self.map_fxn = map_fxn
        self.args = args
    def run(self):
        self.map_result_L1[self.thread_id] = self.map_fxn(*self.args)


def map_reduce( reduce_fxn, map_fxn_L1, map_args_L1 ):
    map_result_L1 = {}
    workers = [
            temp_worker( map_result_L1, i, map_fxn_L1[i], map_args_L1[i] )
            for i in range(0, len(map_fxn_L1))
        ]
    for i in range(0, len(map_fxn_L1)):
        workers[i].start()
    for i in range(0, len(map_fxn_L1)):
        workers[i].join()
    reduce_fxn(map_result_L1)

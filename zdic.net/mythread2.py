import time
import threading

class MyThread(threading.Thread):
    def __init__(self, threadID, name, args, func=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.args = args
        self.func = func
        self.results = []

    def run(self):
        print("Starting " + self.name)
        time_start = time.time()
        args = self.args
        args['name'] = self.name
        res = self.func(args)
        if not res:
            print(url, 'failed')
        else:
            if type(res) is dict: # 返回结果是dict
                self.results.append(res)
            elif type(res) is list: # 返回结果是list
                self.results.extend(res)
            else:
                print('invalid type return')

        print("{}: {} words finished cost {} seconds".format(self.name, len(self.results), round(time.time()-time_start)))
        print("Exiting " + self.name)

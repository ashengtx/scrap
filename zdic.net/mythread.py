import time
import threading

class MyThread(threading.Thread):
    def __init__(self, threadID, name, urls, func=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.urls = urls
        self.func = func
        self.results = []

    def run(self):
        print("Starting " + self.name)
        time_start = time.time()
        n = 0
        total_num = len(self.urls)
        for url in self.urls:
            res = self.func(url)
            if not res:
                print(url, 'failed')
            else:
                if type(res) is dict: # 返回结果是dict
                    self.results.append(res)
                elif type(res) is list: # 返回结果是list
                    self.results.extend(res)
                else:
                    print('invalid type return')
            n += 1
            if n % 100 == 0:
                print("{} scrap {}/{} urls cost {} seconds.".format(self.name, n, total_num, round(time.time()-time_start)))
        print("{}: {} words finished cost {} seconds".format(self.name, len(self.results), round(time.time()-time_start)))
        print("Exiting " + self.name)

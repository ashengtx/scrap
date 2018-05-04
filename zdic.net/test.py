import time, threading

# 新线程执行的代码:
def loop():
    print('thread %s is running...' % threading.current_thread().name)
    n = 0
    while n < 150:
        n = n + 1
        print('thread %s >>> %s' % (threading.current_thread().name, n))
        time.sleep(1)
    print('thread %s ended.' % threading.current_thread().name)

print('thread %s is running...' % threading.current_thread().name)
for m in range(8):
    t = threading.Thread(target=loop, name='LoopThread_'+str(m))
    t.start()
#t.join()
print('thread %s ended.' % threading.current_thread().name)

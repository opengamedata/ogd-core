from multiprocessing import Process, Value, Array, Queue

class ProcClass(Process):
    def __init__(self):
        self._x = 0

    def run(self, n, a):#, q:Queue):
        n.value = 3.1415927
        for i in range(len(a)):
            a[i] = -a[i]
            self._x += a[i]
            print(f"self._x now ={self._x} after adding {a[i]}")
        # q.put(self)

if __name__ == '__main__':
    num = Value('d', 0.0)
    arr = Array('i', range(10))

    proc = ProcClass()
    q = Queue()
    p = Process(target=proc.f, args=(num, arr, q))
    p.start()
    p.join()
    proc = q.get()

    print(f"num.val = {num.value}")
    print(f"arr = {arr[:]}")
    print(f"proc._x = {proc._x}")

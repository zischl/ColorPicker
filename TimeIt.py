import time

def TimeIT(func):
        def inner(*args, **kwargs): 
            time1= time.perf_counter()
            bleh = func(*args, **kwargs)
            time2= time.perf_counter()
            print("Time Taken : ",time2-time1)
            return bleh
        return inner

def TimeITAvg(id):
    if id not in Chronos.chronodict: Chronos.chronodict[id] = [] 
    def Outer(func):
        def inner(*args, **kwargs): 
            time1= time.perf_counter()
            bleh = func(*args, **kwargs)
            time2= time.perf_counter()
            Chronos.chronodict[id].append(time2-time1)
            return bleh
        return inner
    return Outer
    
class Chronos():
    chronodict = {}
    def __init__(self):
        pass
    
    @classmethod
    def PerfIT(self):
        self.avgTime(*Chronos.chronodict.values())

    def avgTime(*args):
        
        limit = min(len(chronolist) for chronolist in Chronos.chronodict.values())
        
        for chronofunc, chronolist in Chronos.chronodict.items():
            print(f"Average Time Taken for function {chronofunc} :",sum(chronolist[:limit])/len(chronolist[:limit]))
            print(f"Min Time Taken for function {chronofunc} :",min(chronolist[:limit]))
            print(f"Max Time Taken for function {chronofunc} :",max(chronolist[:limit]))
import time
def TimeIT(func):
        def inner(*args, **kwargs): 
            time1= time.perf_counter()
            bleh = func(*args, **kwargs)
            time2= time.perf_counter()
            print("Time Taken : ",time2-time1)
            return bleh
        return inner
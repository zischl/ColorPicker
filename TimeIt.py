import time
def TimeIT(func):
        def inner(*args): 
            time1= time.perf_counter()
            bleh = func(*args)
            time2= time.perf_counter()
            print("Time Taken : ",time2-time1)
            return bleh
        return inner
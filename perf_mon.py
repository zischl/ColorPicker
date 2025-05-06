
def perf_mon():
    import threading
    def monitor_usage():
        import psutil
        import os
        import time
        """Continuously monitor and print CPU and memory usage."""
        process = psutil.Process(os.getpid())  # Get current process
        while True:
            cpu_usage = process.cpu_percent(interval=1)  # CPU usage (1 sec interval)
            memory_info = process.memory_info().rss / (1024 * 1024)  # Memory usage in MB
            print(f"CPU Usage: {cpu_usage}% | Memory Usage: {memory_info:.2f} MB")
            time.sleep(1)  # Delay to prevent spamming
            
    
    monitor_thread = threading.Thread(target=monitor_usage, daemon=True)
    monitor_thread.start()

     

            

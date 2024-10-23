# Peterson's Algorithm Implementation in Python
import threading
import time

class PetersonLock:
    def __init__(self):
        # Shared variables
        self.flag = [False, False]  # Array to track process intentions
        self.turn = 0               # Variable to indicate whose turn it is
        
    def lock(self, process_id):
        other = 1 - process_id      # Calculate other process ID
        
        # Entry Protocol
        self.flag[process_id] = True        # Signal intention to enter
        self.turn = other                   # Give away the turn
        
        # Wait while other process is in critical section and it's not our turn
        while self.flag[other] and self.turn == other:
            pass    # Busy wait
            
    def unlock(self, process_id):
        # Exit Protocol
        self.flag[process_id] = False       # Signal completion

# Example Implementation
class SharedResource:
    def __init__(self):
        self.value = 0
        self.lock = PetersonLock()

    def increment(self, process_id):
        self.lock.lock(process_id)          # Enter critical section
        
        # Critical Section
        current = self.value
        time.sleep(0.1)                     # Simulate some work
        self.value = current + 1
        print(f"Process {process_id}: Incremented value to {self.value}")
        
        self.lock.unlock(process_id)        # Exit critical section

# Test the implementation
def process_function(shared_resource, process_id, iterations):
    for _ in range(iterations):
        shared_resource.increment(process_id)
        time.sleep(0.2)  # Some non-critical section work

def main():
    # Create shared resource
    shared_resource = SharedResource()
    
    # Create two threads
    t1 = threading.Thread(target=process_function, 
                         args=(shared_resource, 0, 3))
    t2 = threading.Thread(target=process_function, 
                         args=(shared_resource, 1, 3))
    
    # Start threads
    print("Starting threads...")
    t1.start()
    t2.start()
    
    # Wait for threads to complete
    t1.join()
    t2.join()
    print(f"Final value: {shared_resource.value}")

if __name__ == "__main__":
    main()

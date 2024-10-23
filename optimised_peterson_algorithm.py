# Enhanced Peterson's Algorithm Implementation in Python
import threading
import time
from typing import Optional
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PetersonError(Exception):
    """Custom exception for Peterson's Algorithm errors"""
    pass

@dataclass
class ProcessStats:
    """Track statistics for each process"""
    entries: int = 0
    wait_time: float = 0.0
    fails: int = 0

class PetersonLock:
    def __init__(self):
        self.flag = [False, False]
        self.turn = 0
        self.stats = {0: ProcessStats(), 1: ProcessStats()}
        self._lock_timeout = 5.0  # Timeout in seconds
        
    def lock(self, process_id: int) -> bool:
        if process_id not in [0, 1]:
            raise PetersonError(f"Invalid process ID: {process_id}. Must be 0 or 1.")
            
        other = 1 - process_id
        start_time = time.time()
        
        try:
            self.flag[process_id] = True
            self.turn = other
            
            # Wait with timeout
            while self.flag[other] and self.turn == other:
                if time.time() - start_time > self._lock_timeout:
                    self.flag[process_id] = False
                    self.stats[process_id].fails += 1
                    raise PetersonError(f"Process {process_id} timed out waiting for lock")
                time.sleep(0.01)  # Small sleep to prevent CPU burning
                
            self.stats[process_id].entries += 1
            self.stats[process_id].wait_time += time.time() - start_time
            return True
            
        except Exception as e:
            self.flag[process_id] = False
            logging.error(f"Error in lock acquisition: {str(e)}")
            raise PetersonError(f"Lock acquisition failed: {str(e)}")
            
    def unlock(self, process_id: int) -> None:
        if process_id not in [0, 1]:
            raise PetersonError(f"Invalid process ID: {process_id}. Must be 0 or 1.")
            
        try:
            self.flag[process_id] = False
        except Exception as e:
            logging.error(f"Error in lock release: {str(e)}")
            raise PetersonError(f"Lock release failed: {str(e)}")
            
    def get_stats(self) -> dict:
        """Return statistics about lock usage"""
        return {
            f"Process_{pid}": {
                "entries": stats.entries,
                "avg_wait_time": stats.wait_time / stats.entries if stats.entries > 0 else 0,
                "fails": stats.fails
            }
            for pid, stats in self.stats.items()
        }

class SharedResource:
    def __init__(self):
        self.value = 0
        self.lock = PetersonLock()
        self.access_log = []
        
    def increment(self, process_id: int, amount: int = 1) -> None:
        try:
            start_time = time.time()
            self.lock.lock(process_id)
            
            # Critical Section
            current = self.value
            time.sleep(0.1)  # Simulate work
            self.value = current + amount
            
            # Log access
            self.access_log.append({
                'process_id': process_id,
                'operation': 'increment',
                'amount': amount,
                'timestamp': time.time(),
                'duration': time.time() - start_time
            })
            
            logging.info(f"Process {process_id}: Incremented value by {amount} to {self.value}")
            
        except PetersonError as e:
            logging.error(f"Process {process_id} failed: {str(e)}")
            raise
        finally:
            self.lock.unlock(process_id)

def run_test_case(shared_resource: SharedResource, process_id: int, 
                  operations: list, delay: float = 0.2) -> None:
    """Run a series of operations on the shared resource"""
    for op in operations:
        try:
            shared_resource.increment(process_id, op)
            time.sleep(delay)
        except PetersonError as e:
            logging.error(f"Operation failed: {str(e)}")

def test_basic_functionality():
    """Test basic incrementing with two processes"""
    shared_resource = SharedResource()
    
    t1 = threading.Thread(target=run_test_case, 
                         args=(shared_resource, 0, [1, 1, 1]))
    t2 = threading.Thread(target=run_test_case, 
                         args=(shared_resource, 1, [1, 1, 1]))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    logging.info(f"Basic test final value: {shared_resource.value}")
    return shared_resource.value == 6

def test_different_increments():
    """Test different increment values"""
    shared_resource = SharedResource()
    
    t1 = threading.Thread(target=run_test_case, 
                         args=(shared_resource, 0, [2, 3, 4]))
    t2 = threading.Thread(target=run_test_case, 
                         args=(shared_resource, 1, [1, 2, 3]))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    logging.info(f"Different increments test final value: {shared_resource.value}")
    return shared_resource.value == 15

def test_error_handling():
    """Test error handling with invalid process ID"""
    shared_resource = SharedResource()
    try:
        shared_resource.increment(2)  # Invalid process ID
        return False
    except PetersonError:
        return True

def main():
    logging.info("Starting Peterson's Algorithm tests...")
    
    # Run all test cases
    test_results = {
        "Basic Functionality": test_basic_functionality(),
        "Different Increments": test_different_increments(),
        "Error Handling": test_error_handling()
    }
    
    # Print test results
    logging.info("\nTest Results:")
    for test_name, result in test_results.items():
        logging.info(f"{test_name}: {'PASS' if result else 'FAIL'}")
    
    # Create a shared resource for demonstration
    shared_resource = SharedResource()
    
    # Run complex test case with multiple threads
    operations1 = [1, 2, 3, 4, 5]
    operations2 = [2, 4, 6, 8, 10]
    
    t1 = threading.Thread(target=run_test_case, 
                         args=(shared_resource, 0, operations1))
    t2 = threading.Thread(target=run_test_case, 
                         args=(shared_resource, 1, operations2))
    
    logging.info("\nStarting complex test case...")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    # Print final results and statistics
    logging.info(f"\nFinal value: {shared_resource.value}")
    logging.info("\nLock Statistics:")
    for pid, stats in shared_resource.lock.get_stats().items():
        logging.info(f"{pid}:")
        for stat_name, stat_value in stats.items():
            logging.info(f"  {stat_name}: {stat_value}")
            
    logging.info("\nAccess Log:")
    for entry in shared_resource.access_log:
        logging.info(f"Process {entry['process_id']}: {entry['operation']} "
                    f"by {entry['amount']} (took {entry['duration']:.3f}s)")

if __name__ == "__main__":
    main()

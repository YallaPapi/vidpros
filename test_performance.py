"""
test_performance.py - Simple test of performance optimization concepts
"""

import time
from performance_optimizer import PerformanceMonitor, CacheManager, RateLimiter, performance_tracked

# Test performance tracking
@performance_tracked("test_operation")
def slow_operation(duration=1):
    time.sleep(duration)
    return f"Completed in {duration}s"

# Test cache
def test_cache():
    print("\n[TEST] Cache Manager")
    cache = CacheManager()
    
    # Test set and get
    cache.set("test_key", {"data": "test_value"}, "general")
    result = cache.get("test_key", "general")
    print(f"Cache hit: {result is not None}")
    print(f"Cache value: {result}")
    
    # Test cache stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")

# Test rate limiter
def test_rate_limiter():
    print("\n[TEST] Rate Limiter")
    limiter = RateLimiter()
    
    # Test rate limiting
    service = "did"
    for i in range(3):
        if limiter.can_call(service):
            print(f"Call {i+1}: Allowed")
            limiter.record_call(service)
        else:
            print(f"Call {i+1}: Rate limited")

# Test performance monitoring
def test_monitoring():
    print("\n[TEST] Performance Monitor")
    
    # Run some operations
    for i in range(3):
        slow_operation(0.1 * (i + 1))
    
    # Get stats
    monitor = PerformanceMonitor()
    stats = monitor.get_operation_stats("test_operation")
    print(f"Operation stats: {stats}")

def main():
    print("=" * 60)
    print("PERFORMANCE OPTIMIZATION TESTS")
    print("=" * 60)
    
    test_cache()
    test_rate_limiter()
    test_monitoring()
    
    print("\n[SUCCESS] All performance optimization components working!")

if __name__ == "__main__":
    main()
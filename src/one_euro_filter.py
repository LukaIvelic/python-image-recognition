"""
One Euro Filter implementation.
Adaptive smoothing for noisy signals with low latency.
Based on the paper by Casiez et al. (2012).
"""

import math
import time

class LowPassFilter:
    def __init__(self, alpha, init_val=0):
        self.y = init_val
        self.s = init_val
        self.alpha = alpha
        self.initialized = False

    def filter(self, value):
        if self.initialized:
            result = self.alpha * value + (1.0 - self.alpha) * self.s
        else:
            result = value
            self.initialized = True
        self.y = value
        self.s = result
        return result

    def filter_with_alpha(self, value, alpha):
        self.alpha = alpha
        return self.filter(value)
    
    def has_last_raw_value(self):
        return self.initialized
    
    def last_raw_value(self):
        return self.y

class OneEuroFilter:
    def __init__(self, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        """
        Initialize the One Euro Filter.
        
        Args:
            min_cutoff: Minimum cutoff frequency (Hz). Lower = more smoothing at low speeds.
            beta: Speed coefficient. Higher = less lag at high speeds.
            d_cutoff: Cutoff frequency for the derivative (Hz).
        """
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        
        self.x_filter = LowPassFilter(alpha=1.0)
        self.dx_filter = LowPassFilter(alpha=1.0)
        self.last_time = None
        
    def _alpha(self, rate, cutoff):
        tau = 1.0 / (2 * math.pi * cutoff)
        te = 1.0 / rate
        return 1.0 / (1.0 + tau / te)

    def filter(self, x, timestamp=None):
        """
        Filter the signal x.
        
        Args:
            x: Current signal value
            timestamp: Current timestamp (seconds). If None, uses time.time()
        
        Returns:
            Filtered value
        """
        if timestamp is None:
            timestamp = time.time()
            
        # First sample
        if self.last_time is None:
            self.last_time = timestamp
            return self.x_filter.filter(x)
            
        # Time difference
        dt = timestamp - self.last_time
        
        # Avoid division by zero could happen if called too fast?
        # If dt is too small, assume a default rate or skip?
        if dt <= 0.0:
            return self.x_filter.s # Return last filtered value
            
        rate = 1.0 / dt
        
        # Estimate derivative (speed)
        dx = (x - self.x_filter.last_raw_value()) * rate
        dx_hat = self.dx_filter.filter_with_alpha(dx, self._alpha(rate, self.d_cutoff))
        
        # Calculate adaptive cutoff
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        
        # Filter signal
        x_hat = self.x_filter.filter_with_alpha(x, self._alpha(rate, cutoff))
        
        self.last_time = timestamp
        return x_hat

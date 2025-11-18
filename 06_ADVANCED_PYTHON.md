# Module 6: Advanced Python Features

## 🎯 Goals
- Master async/await programming
- Understand decorators and their applications
- Learn generators and iterators
- Use type hints effectively
- Apply functional programming concepts
- Understand advanced patterns in the main codebase

## 📋 Prerequisites
Completed Modules 1-5: All previous Python concepts

## 1. Asynchronous Programming

### Understanding Async/Await
```python
import asyncio
import aiohttp
import time
from datetime import datetime

# Basic async function
async def simple_async_function():
    """Basic async function demonstration"""
    print("Starting async function...")
    await asyncio.sleep(1)  # Simulates async I/O operation
    print("Async function completed!")
    return "Result"

# Running async functions
async def main():
    result = await simple_async_function()
    print(f"Got result: {result}")

# Run the async function
# asyncio.run(main())

# Concurrent execution
async def fetch_data(url, session):
    """Simulate fetching data from URL"""
    print(f"Fetching {url}...")
    await asyncio.sleep(1)  # Simulate network delay
    return f"Data from {url}"

async def fetch_multiple_urls():
    """Fetch multiple URLs concurrently"""
    urls = ["http://api1.com", "http://api2.com", "http://api3.com"]
    
    # Sequential (slow)
    start_time = time.time()
    results_sequential = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            result = await fetch_data(url, session)
            results_sequential.append(result)
    sequential_time = time.time() - start_time
    
    # Concurrent (fast)
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(url, session) for url in urls]
        results_concurrent = await asyncio.gather(*tasks)
    concurrent_time = time.time() - start_time
    
    print(f"Sequential time: {sequential_time:.2f}s")
    print(f"Concurrent time: {concurrent_time:.2f}s")
    
    return results_concurrent

# Real-world async patterns
class AsyncDataProcessor:
    """Async data processor with rate limiting and error handling"""
    
    def __init__(self, max_concurrent=10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def process_item(self, item):
        """Process a single item with rate limiting"""
        async with self.semaphore:  # Limit concurrent operations
            try:
                # Simulate processing
                await asyncio.sleep(0.5)
                return f"Processed: {item}"
            except Exception as e:
                return f"Error processing {item}: {e}"
    
    async def process_batch(self, items):
        """Process multiple items concurrently"""
        tasks = [self.process_item(item) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Usage
async def demo_async_processing():
    items = [f"item_{i}" for i in range(20)]
    
    async with AsyncDataProcessor(max_concurrent=5) as processor:
        results = await processor.process_batch(items)
        
    for result in results:
        print(result)

# asyncio.run(demo_async_processing())
```

### Async Context Managers and Iterators
```python
import asyncio
import aiofiles
from pathlib import Path

# Async context manager
class AsyncDatabaseConnection:
    """Async database connection context manager"""
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
    
    async def __aenter__(self):
        print(f"Connecting to {self.connection_string}...")
        await asyncio.sleep(0.1)  # Simulate connection time
        self.connection = f"Connected to {self.connection_string}"
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Closing database connection...")
        await asyncio.sleep(0.1)  # Simulate cleanup
        self.connection = None

# Async iterator
class AsyncFileReader:
    """Async file reader that yields lines"""
    
    def __init__(self, file_path):
        self.file_path = file_path
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        # This is simplified - real implementation would use aiofiles
        if not hasattr(self, '_lines'):
            # Simulate reading file asynchronously
            await asyncio.sleep(0.1)
            self._lines = [f"Line {i}" for i in range(5)]
            self._index = 0
        
        if self._index >= len(self._lines):
            raise StopAsyncIteration
        
        line = self._lines[self._index]
        self._index += 1
        return line

# Using async context managers and iterators
async def demo_async_patterns():
    # Async context manager
    async with AsyncDatabaseConnection("postgresql://localhost") as db:
        print(f"Using connection: {db}")
    
    # Async iterator
    async for line in AsyncFileReader("example.txt"):
        print(f"Read: {line}")

# asyncio.run(demo_async_patterns())
```

## 2. Decorators

### Function Decorators
```python
import time
import functools
from datetime import datetime
import logging

# Basic decorator
def timer_decorator(func):
    """Decorator to measure execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

# Decorator with parameters
def retry_decorator(max_attempts=3, delay=1):
    """Decorator to retry function execution on failure"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
        return wrapper
    return decorator

# Async decorator
def async_timer_decorator(func):
    """Async version of timer decorator"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

# Logging decorator
def log_calls(logger=None):
    """Decorator to log function calls"""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_str = ", ".join([repr(arg) for arg in args])
            kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in kwargs.items()])
            all_args = ", ".join(filter(None, [args_str, kwargs_str]))
            
            logger.info(f"Calling {func.__name__}({all_args})")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func.__name__} returned {repr(result)}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
                raise
        return wrapper
    return decorator

# Using decorators
@timer_decorator
@retry_decorator(max_attempts=3, delay=0.5)
def unreliable_function(success_rate=0.3):
    """Function that randomly fails"""
    import random
    if random.random() < success_rate:
        return "Success!"
    else:
        raise Exception("Random failure")

@log_calls()
def calculate_factorial(n):
    """Calculate factorial with logging"""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

# Class decorators
def singleton(cls):
    """Decorator to make a class a singleton"""
    instances = {}
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class DatabaseManager:
    """Singleton database manager"""
    def __init__(self):
        print("Creating DatabaseManager instance")
        self.connections = {}

# Property decorators
class Temperature:
    """Class demonstrating property decorators"""
    
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Get temperature in Celsius"""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Set temperature in Celsius"""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero is not possible")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """Get temperature in Fahrenheit"""
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """Set temperature via Fahrenheit"""
        self.celsius = (value - 32) * 5/9

# Usage examples
# result = unreliable_function(0.7)
# factorial_5 = calculate_factorial(5)

db1 = DatabaseManager()
db2 = DatabaseManager()
# print(db1 is db2)  # True - same instance

temp = Temperature(25)
# print(f"{temp.celsius}°C = {temp.fahrenheit}°F")
```

### Class and Method Decorators
```python
# Method decorators
class APIClient:
    """API client with various method decorators"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self._cache = {}
    
    def cache_result(self, timeout=300):
        """Decorator to cache method results"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = f"{func.__name__}:{hash((args, frozenset(kwargs.items())))}"
                
                if cache_key in self._cache:
                    cached_result, timestamp = self._cache[cache_key]
                    if time.time() - timestamp < timeout:
                        print(f"Cache hit for {func.__name__}")
                        return cached_result
                
                print(f"Cache miss for {func.__name__}")
                result = func(self, *args, **kwargs)
                self._cache[cache_key] = (result, time.time())
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def rate_limit(calls_per_second=1):
        """Decorator to rate limit method calls"""
        min_interval = 1.0 / calls_per_second
        last_called = {}
        
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                now = time.time()
                if func.__name__ in last_called:
                    elapsed = now - last_called[func.__name__]
                    if elapsed < min_interval:
                        sleep_time = min_interval - elapsed
                        time.sleep(sleep_time)
                
                last_called[func.__name__] = time.time()
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @cache_result(timeout=60)
    @rate_limit(calls_per_second=2)
    def get_user_data(self, user_id):
        """Get user data with caching and rate limiting"""
        # Simulate API call
        time.sleep(0.5)
        return {"user_id": user_id, "name": f"User {user_id}", "timestamp": time.time()}

# Dataclass decorator (Python 3.7+)
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class User:
    """User class using dataclass decorator"""
    id: int
    name: str
    email: str
    age: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Called after initialization"""
        if self.email and '@' not in self.email:
            raise ValueError("Invalid email format")

# Usage
client = APIClient("https://api.example.com")
# user_data = client.get_user_data(123)  # API call + cache
# user_data2 = client.get_user_data(123)  # Cache hit

user = User(1, "Alice", "alice@example.com", 30, ["admin", "user"])
```

## 3. Generators and Iterators

### Generator Functions
```python
def fibonacci_generator(max_count):
    """Generate Fibonacci numbers"""
    a, b = 0, 1
    count = 0
    while count < max_count:
        yield a
        a, b = b, a + b
        count += 1

def file_line_generator(file_path):
    """Generator to read file line by line (memory efficient)"""
    try:
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, 1):
                yield line_number, line.strip()
    except FileNotFoundError:
        print(f"File {file_path} not found")

def batch_generator(iterable, batch_size):
    """Generate batches from an iterable"""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:  # Yield remaining items
        yield batch

# Advanced generator patterns
def data_processing_pipeline(data_source):
    """Data processing pipeline using generators"""
    
    def extract_data():
        """Extract data from source"""
        for item in data_source:
            yield item
    
    def transform_data(data_stream):
        """Transform data"""
        for item in data_stream:
            if item.strip():  # Skip empty lines
                yield item.upper()
    
    def filter_data(data_stream, pattern):
        """Filter data"""
        for item in data_stream:
            if pattern in item:
                yield item
    
    def load_data(data_stream):
        """Load/consume data"""
        results = []
        for item in data_stream:
            results.append(f"Processed: {item}")
        return results
    
    # Pipeline execution
    extracted = extract_data()
    transformed = transform_data(extracted)
    filtered = filter_data(transformed, "IMPORTANT")
    return load_data(filtered)

# Async generators
async def async_data_generator(urls):
    """Async generator for fetching data from URLs"""
    for url in urls:
        # Simulate async API call
        await asyncio.sleep(0.1)
        yield f"Data from {url}"

async def consume_async_generator():
    """Consume async generator"""
    urls = ["http://api1.com", "http://api2.com", "http://api3.com"]
    
    async for data in async_data_generator(urls):
        print(f"Received: {data}")

# Usage examples
# Fibonacci
fib_gen = fibonacci_generator(10)
# for num in fib_gen:
#     print(num)

# Batching
large_list = list(range(100))
for batch in batch_generator(large_list, 10):
    print(f"Batch of {len(batch)}: {batch[:3]}...")  # Show first 3 items
```

### Custom Iterators
```python
class NumberRange:
    """Custom iterator for number ranges"""
    
    def __init__(self, start, end, step=1):
        self.start = start
        self.end = end
        self.step = step
        self.current = start
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if (self.step > 0 and self.current >= self.end) or \
           (self.step < 0 and self.current <= self.end):
            raise StopIteration
        
        value = self.current
        self.current += self.step
        return value

class CircularIterator:
    """Iterator that cycles through items infinitely"""
    
    def __init__(self, items):
        self.items = items
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.items:
            raise StopIteration
        
        value = self.items[self.index]
        self.index = (self.index + 1) % len(self.items)
        return value

# Usage
range_iter = NumberRange(0, 10, 2)
# for num in range_iter:
#     print(num)  # 0, 2, 4, 6, 8

circular = CircularIterator(['A', 'B', 'C'])
# for i, item in enumerate(circular):
#     if i >= 10:
#         break
#     print(item)  # A, B, C, A, B, C, ...
```

## 4. Type Hints and Static Analysis

```python
from typing import List, Dict, Optional, Union, Callable, TypeVar, Generic
from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Basic type hints
def greet_user(name: str, age: int) -> str:
    """Function with basic type hints"""
    return f"Hello {name}, you are {age} years old"

def process_data(
    data: List[Dict[str, Union[str, int]]],
    processor: Callable[[Dict[str, Union[str, int]]], str]
) -> List[str]:
    """Function with complex type hints"""
    return [processor(item) for item in data]

# Generic types
T = TypeVar('T')

class Stack(Generic[T]):
    """Generic stack implementation"""
    
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        """Push item onto stack"""
        self._items.append(item)
    
    def pop(self) -> T:
        """Pop item from stack"""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()
    
    def peek(self) -> Optional[T]:
        """Peek at top item"""
        return self._items[-1] if self._items else None
    
    def is_empty(self) -> bool:
        """Check if stack is empty"""
        return len(self._items) == 0

# Protocol (structural subtyping)
@runtime_checkable
class Drawable(Protocol):
    """Protocol for drawable objects"""
    def draw(self) -> str: ...
    def get_area(self) -> float: ...

@dataclass
class Circle:
    radius: float
    
    def draw(self) -> str:
        return f"Drawing circle with radius {self.radius}"
    
    def get_area(self) -> float:
        return 3.14159 * self.radius ** 2

@dataclass
class Rectangle:
    width: float
    height: float
    
    def draw(self) -> str:
        return f"Drawing rectangle {self.width}x{self.height}"
    
    def get_area(self) -> float:
        return self.width * self.height

def draw_shape(shape: Drawable) -> str:
    """Function that works with any drawable object"""
    return shape.draw()

# Type aliases
UserId = int
UserData = Dict[str, Union[str, int, List[str]]]
DatabaseConnection = object  # Placeholder for actual type

class UserManager:
    """User manager with comprehensive type hints"""
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        self.db = db_connection
        self._cache: Dict[UserId, UserData] = {}
    
    def get_user(self, user_id: UserId) -> Optional[UserData]:
        """Get user by ID"""
        if user_id in self._cache:
            return self._cache[user_id]
        
        # Simulate database lookup
        user_data: UserData = {
            "id": user_id,
            "name": f"User {user_id}",
            "tags": ["user"]
        }
        
        self._cache[user_id] = user_data
        return user_data
    
    def batch_get_users(self, user_ids: List[UserId]) -> Dict[UserId, UserData]:
        """Get multiple users"""
        result: Dict[UserId, UserData] = {}
        
        for user_id in user_ids:
            user_data = self.get_user(user_id)
            if user_data:
                result[user_id] = user_data
        
        return result

# Usage with type checking
string_stack: Stack[str] = Stack()
string_stack.push("hello")
string_stack.push("world")

int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)

# Shapes
circle = Circle(5.0)
rectangle = Rectangle(4.0, 6.0)

shapes: List[Drawable] = [circle, rectangle]
for shape in shapes:
    print(draw_shape(shape))
```

## 5. Functional Programming Concepts

```python
from functools import reduce, partial, wraps
from itertools import islice, groupby, chain
from operator import itemgetter, attrgetter

# Higher-order functions
def apply_to_list(func: Callable, items: List) -> List:
    """Apply function to each item in list"""
    return [func(item) for item in items]

def compose(*functions):
    """Function composition"""
    def composed(x):
        for func in reversed(functions):
            x = func(x)
        return x
    return composed

# Partial application
def multiply(x: int, y: int) -> int:
    return x * y

multiply_by_2 = partial(multiply, 2)
multiply_by_10 = partial(multiply, 10)

# Currying
def curry_add(x):
    """Curried addition function"""
    def add_x(y):
        return x + y
    return add_x

add_5 = curry_add(5)
add_10 = curry_add(10)

# Functional data processing
class FunctionalProcessor:
    """Functional programming utilities for data processing"""
    
    @staticmethod
    def pipeline(*functions):
        """Create a processing pipeline"""
        def process(data):
            result = data
            for func in functions:
                result = func(result)
            return result
        return process
    
    @staticmethod
    def filter_map_reduce(data, filter_func, map_func, reduce_func, initial=None):
        """Functional filter-map-reduce pattern"""
        filtered = filter(filter_func, data)
        mapped = map(map_func, filtered)
        if initial is not None:
            return reduce(reduce_func, mapped, initial)
        return reduce(reduce_func, mapped)
    
    @staticmethod
    def group_and_process(data, key_func, process_func):
        """Group data by key and process each group"""
        sorted_data = sorted(data, key=key_func)
        grouped = groupby(sorted_data, key=key_func)
        return {key: process_func(list(group)) for key, group in grouped}

# Functional data analysis example
def analyze_sales_functional(sales_data):
    """Functional approach to sales data analysis"""
    
    # Define small, pure functions
    def is_high_value(sale):
        return sale['amount'] > 1000
    
    def extract_amount(sale):
        return sale['amount']
    
    def sum_amounts(acc, amount):
        return acc + amount
    
    def average_group(sales_list):
        if not sales_list:
            return 0
        return sum(sale['amount'] for sale in sales_list) / len(sales_list)
    
    # Create processing pipeline
    processor = FunctionalProcessor()
    
    # High-value sales total
    high_value_total = processor.filter_map_reduce(
        sales_data,
        is_high_value,
        extract_amount,
        sum_amounts,
        0
    )
    
    # Average by category
    category_averages = processor.group_and_process(
        sales_data,
        itemgetter('category'),
        average_group
    )
    
    return {
        'high_value_total': high_value_total,
        'category_averages': category_averages
    }

# Memoization decorator
def memoize(func):
    """Decorator to cache function results"""
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create hashable key
        key = (args, frozenset(kwargs.items()))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    return wrapper

@memoize
def expensive_fibonacci(n):
    """Fibonacci with memoization"""
    if n <= 1:
        return n
    return expensive_fibonacci(n-1) + expensive_fibonacci(n-2)

# Usage examples
numbers = [1, 2, 3, 4, 5]
doubled = apply_to_list(lambda x: x * 2, numbers)

# Function composition
square = lambda x: x ** 2
add_one = lambda x: x + 1
square_then_add = compose(add_one, square)

# result = square_then_add(5)  # (5^2) + 1 = 26

# Sales data analysis
sales_data = [
    {'amount': 500, 'category': 'A'},
    {'amount': 1500, 'category': 'B'},
    {'amount': 800, 'category': 'A'},
    {'amount': 2000, 'category': 'C'}
]

# analysis = analyze_sales_functional(sales_data)
```

## 🏃‍♂️ Real-World Application Exercise

### Building an Async Web Scraper with Advanced Features
```python
import asyncio
import aiohttp
import aiofiles
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    url: str
    status_code: int
    content: Optional[str] = None
    error: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'url': self.url,
            'status_code': self.status_code,
            'content_length': len(self.content) if self.content else 0,
            'error': self.error,
            'scraped_at': self.scraped_at.isoformat()
        }

class AsyncWebScraper:
    """Advanced async web scraper with rate limiting and caching"""
    
    def __init__(self, max_concurrent: int = 10, rate_limit: float = 1.0):
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.last_request_time = 0.0
        self.results: List[ScrapingResult] = []
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'AsyncWebScraper/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @retry_decorator(max_attempts=3, delay=1)
    async def fetch_url(self, url: str) -> ScrapingResult:
        """Fetch a single URL with rate limiting and error handling"""
        async with self.semaphore:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.rate_limit:
                await asyncio.sleep(self.rate_limit - time_since_last)
            self.last_request_time = time.time()
            
            try:
                self.logger.info(f"Fetching: {url}")
                async with self.session.get(url) as response:
                    content = await response.text()
                    return ScrapingResult(
                        url=url,
                        status_code=response.status,
                        content=content
                    )
            except Exception as e:
                self.logger.error(f"Error fetching {url}: {e}")
                return ScrapingResult(
                    url=url,
                    status_code=0,
                    error=str(e)
                )
    
    async def scrape_urls(self, urls: List[str]) -> AsyncGenerator[ScrapingResult, None]:
        """Scrape multiple URLs and yield results as they complete"""
        tasks = [self.fetch_url(url) for url in urls]
        
        for coro in asyncio.as_completed(tasks):
            result = await coro
            self.results.append(result)
            yield result
    
    async def save_results(self, filename: str) -> None:
        """Save results to JSON file"""
        data = [result.to_dict() for result in self.results]
        
        async with aiofiles.open(filename, 'w') as f:
            await f.write(json.dumps(data, indent=2))
        
        self.logger.info(f"Saved {len(data)} results to {filename}")
    
    def get_statistics(self) -> Dict:
        """Get scraping statistics"""
        if not self.results:
            return {"message": "No results yet"}
        
        successful = [r for r in self.results if r.error is None]
        failed = [r for r in self.results if r.error is not None]
        
        return {
            "total_urls": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(self.results) * 100,
            "average_content_length": sum(
                len(r.content) for r in successful if r.content
            ) / len(successful) if successful else 0
        }

# Usage example
async def main_scraping_demo():
    """Demonstrate the async web scraper"""
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/status/404",
        "https://httpbin.org/json",
        "https://httpbin.org/html"
    ]
    
    async with AsyncWebScraper(max_concurrent=3, rate_limit=0.5) as scraper:
        print("Starting web scraping...")
        
        async for result in scraper.scrape_urls(urls):
            if result.error:
                print(f"❌ {result.url}: {result.error}")
            else:
                print(f"✅ {result.url}: {result.status_code} ({len(result.content)} chars)")
        
        # Save results and show statistics
        await scraper.save_results("scraping_results.json")
        stats = scraper.get_statistics()
        
        print(f"\nScraping completed!")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Average content length: {stats['average_content_length']:.0f} characters")

# Run the demo
# asyncio.run(main_scraping_demo())
```

## 🔍 Understanding the Main Codebase

Now you can understand advanced patterns in `main.py`:

```python
# Async startup event
@app.on_event("startup")
async def startup_event():
    """Initialize components asynchronously"""
    # This runs once when the app starts
    
# Type hints throughout
search_engine: SemanticSearchEngine = None
rag_engine: RAGEngine = None

# Async route handlers
@app.post("/search", response_model=List[SearchResult])
async def semantic_search(query: SearchQuery):
    """Async route with type hints"""
    
# Error handling with custom exceptions
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom error handler"""
```

## ⚡ Best Practices Summary

1. **Use async/await** for I/O-bound operations
2. **Apply decorators** for cross-cutting concerns (logging, caching, retry)
3. **Use type hints** for better code documentation and IDE support
4. **Leverage generators** for memory-efficient data processing
5. **Apply functional programming** for data transformations
6. **Use context managers** for resource management
7. **Handle errors gracefully** with proper exception handling

## 🎯 Final Assessment

After completing all modules, you should be able to:

✅ Read and understand the entire main codebase  
✅ Write FastAPI applications with async support  
✅ Use advanced Python features effectively  
✅ Handle data processing with pandas/numpy  
✅ Apply proper error handling and logging  
✅ Use type hints and modern Python patterns  

## 🚀 Next Steps

1. **Explore the main codebase** - You now have all the knowledge needed!
2. **Build your own projects** using these patterns
3. **Contribute to open source** Python projects
4. **Learn domain-specific libraries** (LangChain, ML libraries, etc.)

**Time to spend:** 4-5 hours

**Total Learning Time:** 18-27 hours

Congratulations! You're now ready to dive deep into Python development and understand complex codebases like the LangChain semantic search engine! 🎉
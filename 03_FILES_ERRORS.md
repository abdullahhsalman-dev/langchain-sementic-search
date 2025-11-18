# Module 3: File I/O & Error Handling

## 🎯 Goals
- Master file operations and path manipulation
- Handle exceptions gracefully
- Use context managers effectively
- Work with different file formats (JSON, CSV, text)
- Understand Python's approach to resource management

## 📋 Prerequisites
Completed Modules 1-2: Python Basics & OOP

## 1. File Operations

### Basic File I/O
```python
# Writing to a file (old way - not recommended)
file = open("example.txt", "w")
file.write("Hello, World!")
file.close()  # Must remember to close!

# Reading from a file (old way)
file = open("example.txt", "r")
content = file.read()
file.close()
print(content)

# The Python way - using context managers
with open("example.txt", "w") as file:
    file.write("Hello, Python!")
# File is automatically closed when exiting the 'with' block

with open("example.txt", "r") as file:
    content = file.read()
    print(content)
```

### File Modes and Methods
```python
# Different file modes
modes = {
    'r': 'Read (default)',
    'w': 'Write (overwrites existing)',
    'a': 'Append',
    'x': 'Create (fails if exists)',
    'b': 'Binary mode (add to others)',
    't': 'Text mode (default)',
    '+': 'Read and write'
}

# Reading methods
with open("large_file.txt", "r") as file:
    # Read entire file
    content = file.read()
    
    # Read line by line (memory efficient)
    file.seek(0)  # Reset to beginning
    for line in file:
        print(line.strip())
    
    # Read all lines into list
    file.seek(0)
    lines = file.readlines()
    
    # Read one line at a time
    file.seek(0)
    first_line = file.readline()

# Writing methods
data_to_write = ["Line 1\n", "Line 2\n", "Line 3\n"]
with open("output.txt", "w") as file:
    # Write string
    file.write("Header\n")
    
    # Write multiple lines
    file.writelines(data_to_write)
```

### Working with Paths
```python
import os
from pathlib import Path

# Old way (os.path)
current_dir = os.getcwd()
file_path = os.path.join(current_dir, "data", "file.txt")
directory = os.path.dirname(file_path)
filename = os.path.basename(file_path)

# Modern way (pathlib) - recommended
current_path = Path.cwd()
file_path = current_path / "data" / "file.txt"
directory = file_path.parent
filename = file_path.name
extension = file_path.suffix

# Path operations
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist

# Check if path exists
if file_path.exists():
    print(f"File size: {file_path.stat().st_size} bytes")
    print(f"Is file: {file_path.is_file()}")
    print(f"Is directory: {file_path.is_dir()}")

# Iterate over directory contents
for item in data_dir.iterdir():
    if item.is_file():
        print(f"File: {item.name}")
    elif item.is_dir():
        print(f"Directory: {item.name}")

# Find files by pattern
txt_files = list(data_dir.glob("*.txt"))
all_python_files = list(Path(".").rglob("*.py"))  # Recursive search
```

### Working with JSON
```python
import json

# Writing JSON
data = {
    "name": "Alice",
    "age": 30,
    "skills": ["Python", "JavaScript", "SQL"],
    "is_employed": True,
    "address": {
        "street": "123 Main St",
        "city": "New York"
    }
}

# Write to JSON file
with open("person.json", "w") as file:
    json.dump(data, file, indent=2)  # Pretty formatted

# Read from JSON file
with open("person.json", "r") as file:
    loaded_data = json.load(file)
    print(loaded_data["name"])

# JSON string operations
json_string = json.dumps(data, indent=2)
parsed_data = json.loads(json_string)

# Handling custom objects
from datetime import datetime

class Person:
    def __init__(self, name, birth_date):
        self.name = name
        self.birth_date = birth_date

def person_serializer(obj):
    """Custom JSON serializer"""
    if isinstance(obj, Person):
        return {
            'name': obj.name,
            'birth_date': obj.birth_date.isoformat()
        }
    elif isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

person = Person("Bob", datetime.now())
json_data = json.dumps(person, default=person_serializer, indent=2)
```

### Working with CSV
```python
import csv

# Writing CSV
data = [
    ["Name", "Age", "City"],
    ["Alice", 30, "New York"],
    ["Bob", 25, "Los Angeles"],
    ["Carol", 35, "Chicago"]
]

with open("people.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(data)

# Reading CSV
with open("people.csv", "r") as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip header
    for row in reader:
        name, age, city = row
        print(f"{name} is {age} years old and lives in {city}")

# Using DictReader/DictWriter (more convenient)
with open("people.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(f"{row['Name']} lives in {row['City']}")

# Writing with DictWriter
people = [
    {"name": "David", "age": 28, "city": "Boston"},
    {"name": "Eve", "age": 32, "city": "Seattle"}
]

with open("people_dict.csv", "w", newline="") as file:
    fieldnames = ["name", "age", "city"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(people)
```

## 2. Exception Handling

### Basic Exception Handling
```python
# Basic try-except
try:
    number = int(input("Enter a number: "))
    result = 10 / number
    print(f"Result: {result}")
except ValueError:
    print("Please enter a valid number")
except ZeroDivisionError:
    print("Cannot divide by zero")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
else:
    print("Operation completed successfully")
finally:
    print("This always runs")
```

### Specific Exception Handling
```python
def safe_file_read(filename):
    """Safely read a file with comprehensive error handling"""
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return None
    except PermissionError:
        print(f"Error: Permission denied to read '{filename}'")
        return None
    except UnicodeDecodeError:
        print(f"Error: Cannot decode '{filename}' - invalid characters")
        return None
    except Exception as e:
        print(f"Unexpected error reading '{filename}': {e}")
        return None

def safe_json_parse(json_string):
    """Safely parse JSON with error handling"""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")
        return None
    except TypeError as e:
        print(f"Invalid input type: {e}")
        return None

# Usage
content = safe_file_read("data.txt")
if content:
    data = safe_json_parse(content)
    if data:
        print("Successfully processed data")
```

### Custom Exceptions
```python
class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass

def validate_email(email):
    """Validate email format"""
    if not email:
        raise ValidationError("Email cannot be empty", field="email")
    if "@" not in email:
        raise ValidationError("Invalid email format", field="email")
    return True

def load_config(config_path):
    """Load configuration with custom error handling"""
    if not Path(config_path).exists():
        raise ConfigurationError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            
        # Validate required fields
        required_fields = ["database_url", "api_key"]
        for field in required_fields:
            if field not in config:
                raise ConfigurationError(f"Missing required field: {field}")
                
        return config
    except json.JSONDecodeError:
        raise ConfigurationError(f"Invalid JSON in config file: {config_path}")

# Usage with custom exceptions
try:
    validate_email("user@example.com")
    config = load_config("config.json")
except ValidationError as e:
    print(f"Validation error in field '{e.field}': {e.message}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Exception Best Practices
```python
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_data_processor(file_path):
    """Example of robust error handling with logging"""
    try:
        # Validate input
        if not isinstance(file_path, (str, Path)):
            raise TypeError("file_path must be a string or Path object")
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.suffix == '.json':
            raise ValueError("Only JSON files are supported")
        
        # Process file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Validate data structure
        if not isinstance(data, list):
            raise ValueError("JSON must contain a list of items")
        
        # Process data
        processed_items = []
        for i, item in enumerate(data):
            try:
                # Validate each item
                if not isinstance(item, dict):
                    logger.warning(f"Skipping invalid item at index {i}: not a dictionary")
                    continue
                
                if 'name' not in item:
                    logger.warning(f"Skipping item at index {i}: missing 'name' field")
                    continue
                
                processed_items.append(item)
                
            except Exception as e:
                logger.error(f"Error processing item at index {i}: {e}")
                continue  # Skip problematic item but continue processing
        
        logger.info(f"Successfully processed {len(processed_items)} items")
        return processed_items
        
    except (FileNotFoundError, TypeError, ValueError) as e:
        logger.error(f"Input validation error: {e}")
        raise  # Re-raise for caller to handle
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise RuntimeError(f"Data processing failed: {e}")
```

## 3. Context Managers

### Understanding Context Managers
```python
# The file context manager automatically handles cleanup
with open("example.txt", "w") as file:
    file.write("Hello")
# File is automatically closed here, even if an exception occurs

# Creating custom context managers
class DatabaseConnection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
    
    def __enter__(self):
        """Called when entering the 'with' block"""
        print("Connecting to database...")
        # Simulate database connection
        self.connection = f"Connected to {self.connection_string}"
        return self.connection
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Called when exiting the 'with' block"""
        print("Closing database connection...")
        self.connection = None
        # Return False to propagate any exceptions
        return False

# Usage
with DatabaseConnection("postgresql://localhost:5432/mydb") as db:
    print(f"Using connection: {db}")
    # Simulate some database operations
    print("Performing database operations...")
# Connection is automatically closed here

# Using contextlib for simpler context managers
from contextlib import contextmanager

@contextmanager
def temporary_file(filename):
    """Context manager for temporary files"""
    print(f"Creating temporary file: {filename}")
    try:
        # Setup
        with open(filename, 'w') as f:
            yield f  # This is what gets returned to 'as' variable
    finally:
        # Cleanup
        print(f"Cleaning up temporary file: {filename}")
        Path(filename).unlink(missing_ok=True)

# Usage
with temporary_file("temp_data.txt") as temp_file:
    temp_file.write("Temporary data")
    temp_file.write("More data")
# File is automatically deleted here
```

## 🏃‍♂️ Practical Exercises

### Exercise 1: Configuration Manager
```python
class ConfigManager:
    """A robust configuration manager with validation and defaults"""
    
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = {}
        self.defaults = {
            "debug": False,
            "port": 8000,
            "host": "localhost",
            "max_connections": 100
        }
    
    def load(self):
        """Load configuration with error handling and defaults"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as file:
                    loaded_config = json.load(file)
                    
                # Merge with defaults
                self.config = {**self.defaults, **loaded_config}
            else:
                print(f"Config file not found, using defaults: {self.config_path}")
                self.config = self.defaults.copy()
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load config: {e}")
    
    def save(self):
        """Save current configuration"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as file:
                json.dump(self.config, file, indent=2)
                
        except Exception as e:
            raise RuntimeError(f"Failed to save config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value with optional default"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value

# Test the configuration manager
config = ConfigManager("app_config.json")
config.load()
print(f"Port: {config.get('port')}")
config.set('debug', True)
config.save()
```

### Exercise 2: Log File Analyzer
```python
import re
from collections import Counter
from datetime import datetime

class LogAnalyzer:
    """Analyze log files for patterns and errors"""
    
    def __init__(self, log_file_path):
        self.log_file_path = Path(log_file_path)
        self.entries = []
    
    def parse_log_entry(self, line):
        """Parse a single log entry"""
        # Example log format: "2023-01-01 12:00:00 [ERROR] Database connection failed"
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.*)'
        match = re.match(pattern, line.strip())
        
        if match:
            timestamp_str, level, message = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return {
                'timestamp': timestamp,
                'level': level,
                'message': message,
                'raw_line': line.strip()
            }
        return None
    
    def load_and_parse(self):
        """Load and parse the log file"""
        try:
            with open(self.log_file_path, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        entry = self.parse_log_entry(line)
                        if entry:
                            entry['line_number'] = line_num
                            self.entries.append(entry)
                    except Exception as e:
                        print(f"Error parsing line {line_num}: {e}")
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading log file: {e}")
    
    def analyze(self):
        """Analyze the log entries"""
        if not self.entries:
            return {"error": "No valid log entries found"}
        
        # Count by log level
        level_counts = Counter(entry['level'] for entry in self.entries)
        
        # Find error messages
        errors = [entry for entry in self.entries if entry['level'] == 'ERROR']
        
        # Time range
        timestamps = [entry['timestamp'] for entry in self.entries]
        time_range = {
            'start': min(timestamps),
            'end': max(timestamps),
            'duration': max(timestamps) - min(timestamps)
        }
        
        return {
            'total_entries': len(self.entries),
            'level_counts': dict(level_counts),
            'error_count': len(errors),
            'time_range': time_range,
            'errors': errors[:10]  # First 10 errors
        }
    
    def generate_report(self, output_file=None):
        """Generate analysis report"""
        analysis = self.analyze()
        
        report = f"""
Log Analysis Report
==================
File: {self.log_file_path}
Analysis Time: {datetime.now()}

Summary:
- Total Entries: {analysis['total_entries']}
- Time Range: {analysis['time_range']['start']} to {analysis['time_range']['end']}
- Duration: {analysis['time_range']['duration']}

Log Levels:
"""
        for level, count in analysis['level_counts'].items():
            report += f"- {level}: {count}\n"
        
        if analysis['error_count'] > 0:
            report += f"\nRecent Errors ({len(analysis['errors'])}):\n"
            for error in analysis['errors']:
                report += f"- [{error['timestamp']}] {error['message']}\n"
        
        if output_file:
            with open(output_file, 'w') as file:
                file.write(report)
        
        return report

# Test the log analyzer
# analyzer = LogAnalyzer("app.log")
# analyzer.load_and_parse()
# print(analyzer.generate_report("log_analysis.txt"))
```

## 🔍 Key Concepts Summary

| Concept | Description | Use Case |
|---------|-------------|----------|
| **Context Managers** | `with` statement for resource management | Files, database connections, locks |
| **Exception Handling** | Try/except for error management | Robust applications |
| **Path Operations** | `pathlib` for file system operations | Cross-platform file handling |
| **File Formats** | JSON, CSV, text handling | Data processing |
| **Logging** | Structured error and info logging | Debugging and monitoring |

## ⚡ Best Practices

1. **Always use context managers** for file operations
2. **Handle specific exceptions** before general ones
3. **Use `pathlib`** instead of `os.path`
4. **Log errors** instead of just printing them
5. **Validate inputs** early and often
6. **Use custom exceptions** for domain-specific errors
7. **Clean up resources** in finally blocks or context managers

## 🚀 Real-World Application
In the main codebase, notice:
- `data_loader.py` uses robust file handling
- Proper exception handling throughout
- JSON processing for configuration
- Path operations for file management

## 🎯 Next Steps
- Practice exception handling patterns
- Build robust file processing utilities
- Understand resource management patterns
- Move to Module 4: Web Development

**Time to spend:** 2-3 hours

Ready to build web applications? → `04_WEB_DEVELOPMENT.md`
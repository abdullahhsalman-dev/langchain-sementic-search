# Module 1: Python Basics & Syntax

## 🎯 Goals
- Master Python's unique syntax patterns
- Understand data types and structures
- Learn Pythonic ways of writing code
- Get comfortable with Python's philosophy

## 📋 Prerequisites
You know programming fundamentals from other languages.

## 🐍 Python Philosophy
Python values **readability** and **simplicity**. The Zen of Python:
```python
import this  # Run this in Python interpreter
```

## 1. Variables & Data Types

### Dynamic Typing
```python
# No need to declare types
name = "Alice"          # str
age = 30               # int
height = 5.6           # float
is_student = True      # bool
data = None           # NoneType

# Variables can change type
x = 42
x = "Hello"  # This is fine!
```

### String Operations (Python's strength)
```python
# String formatting (modern way)
name = "Bob"
age = 25
message = f"Hello {name}, you are {age} years old"

# Multi-line strings
text = """
This is a
multi-line string
"""

# String methods
text = "  Python Programming  "
print(text.strip().lower().replace("python", "awesome"))
```

## 2. Data Structures

### Lists (Dynamic Arrays)
```python
# Creating lists
fruits = ["apple", "banana", "orange"]
mixed = [1, "hello", True, 3.14]

# List comprehensions (very Pythonic!)
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]

# Useful methods
fruits.append("grape")
fruits.extend(["kiwi", "mango"])
first_fruit = fruits.pop(0)
```

### Dictionaries (Hash Maps)
```python
# Creating dictionaries
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}

# Dictionary comprehensions
squares_dict = {x: x**2 for x in range(5)}

# Safe access
age = person.get("age", 0)  # Returns 0 if key doesn't exist
```

### Tuples (Immutable Sequences)
```python
# Creating tuples
coordinates = (10, 20)
person_info = ("Alice", 30, "Engineer")

# Tuple unpacking (very useful!)
x, y = coordinates
name, age, job = person_info
```

### Sets (Unique Elements)
```python
# Creating sets
unique_numbers = {1, 2, 3, 4, 5}
colors = set(["red", "blue", "red", "green"])  # Duplicates removed

# Set operations
set1 = {1, 2, 3}
set2 = {3, 4, 5}
intersection = set1 & set2
union = set1 | set2
```

## 3. Control Flow

### If Statements
```python
# Python uses indentation for blocks!
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"

# Ternary operator
status = "pass" if score >= 60 else "fail"
```

### Loops
```python
# For loops (very different from other languages)
fruits = ["apple", "banana", "orange"]

# Iterate over items directly
for fruit in fruits:
    print(fruit)

# With index if needed
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Range for numbers
for i in range(5):        # 0 to 4
    print(i)

# While loops
count = 0
while count < 5:
    print(count)
    count += 1
```

## 4. Functions

### Basic Functions
```python
def greet(name, greeting="Hello"):
    """Function with default parameter and docstring"""
    return f"{greeting}, {name}!"

# Keyword arguments
message = greet(name="Alice", greeting="Hi")
```

### Advanced Function Features
```python
# Variable arguments
def sum_all(*args):
    return sum(args)

result = sum_all(1, 2, 3, 4, 5)

# Keyword arguments
def create_person(**kwargs):
    return kwargs

person = create_person(name="Bob", age=30, city="LA")

# Lambda functions (for simple operations)
square = lambda x: x**2
numbers = [1, 2, 3, 4, 5]
squared = list(map(square, numbers))
```

## 5. List Comprehensions & Generator Expressions

### List Comprehensions
```python
# Instead of:
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x**2)

# Write this:
squares = [x**2 for x in range(10) if x % 2 == 0]

# Nested comprehensions
matrix = [[i*j for j in range(3)] for i in range(3)]
```

### Generator Expressions (Memory Efficient)
```python
# For large datasets, use generators
squares_gen = (x**2 for x in range(1000000))  # Doesn't create list immediately

# Convert to list when needed
first_10_squares = list(squares_gen)[:10]
```

## 🏃‍♂️ Quick Exercises

### Exercise 1: Data Processing
```python
# Given a list of temperatures in Celsius, convert to Fahrenheit
celsius_temps = [0, 20, 30, 40, 100]

# Your solution here (use list comprehension)
fahrenheit_temps = [c * 9/5 + 32 for c in celsius_temps]
print(fahrenheit_temps)
```

### Exercise 2: String Processing
```python
# Clean and process a list of email addresses
emails = ["  ALICE@GMAIL.COM  ", "bob@yahoo.com", "  CHARLIE@HOTMAIL.COM"]

# Your solution: clean whitespace, lowercase, extract domain
clean_emails = [email.strip().lower() for email in emails]
domains = [email.split('@')[1] for email in clean_emails]
print(clean_emails)
print(domains)
```

### Exercise 3: Dictionary Operations
```python
# Count word frequency in a text
text = "python is great python is powerful python is fun"
words = text.split()

# Your solution here
word_count = {}
for word in words:
    word_count[word] = word_count.get(word, 0) + 1

# Or using dict comprehension
from collections import Counter
word_count = Counter(words)
print(word_count)
```

## 🔍 Key Python Concepts vs Other Languages

| Concept | Python | Other Languages |
|---------|--------|-----------------|
| **Indentation** | Defines code blocks | Uses {}, begin/end |
| **Variables** | Dynamic typing | Often static typing |
| **Strings** | Immutable, rich methods | Varies |
| **Lists** | Dynamic, heterogeneous | Often typed arrays |
| **Iteration** | `for item in collection` | `for(i=0; i<len; i++)` |
| **Boolean** | `True/False` | `true/false` |

## ⚡ Python Best Practices

1. **Use descriptive variable names**: `user_age` not `ua`
2. **Follow PEP 8**: Python's style guide
3. **Use list comprehensions** for simple transformations
4. **Prefer `is` for None checks**: `if x is None:`
5. **Use f-strings** for string formatting
6. **Write docstrings** for functions and classes

## 🎯 Next Steps
- Practice with the exercises above
- Get comfortable with Python's indentation
- Try solving simple problems with list comprehensions
- Move to Module 2: OOP & Modules

**Time to spend:** 2-4 hours of focused practice

Ready for object-oriented Python? → `02_OOP_MODULES.md`
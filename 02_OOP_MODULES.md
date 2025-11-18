# Module 2: Object-Oriented Python & Modules

## 🎯 Goals
- Master Python's class system and OOP patterns
- Understand modules, packages, and project structure
- Learn Python's approach to encapsulation and inheritance
- Build reusable, modular code

## 📋 Prerequisites
Completed Module 1: Python Basics

## 1. Classes and Objects

### Basic Class Structure
```python
class Person:
    """A simple Person class"""
    
    # Class variable (shared by all instances)
    species = "Homo sapiens"
    
    def __init__(self, name, age):
        """Constructor method"""
        self.name = name        # Instance variable
        self.age = age          # Instance variable
        self._id = None         # Protected (convention)
        self.__secret = "hidden"  # Private (name mangling)
    
    def greet(self):
        """Instance method"""
        return f"Hello, I'm {self.name}"
    
    def celebrate_birthday(self):
        """Modify instance state"""
        self.age += 1
        return f"{self.name} is now {self.age} years old!"
    
    @classmethod
    def from_birth_year(cls, name, birth_year):
        """Alternative constructor"""
        from datetime import datetime
        age = datetime.now().year - birth_year
        return cls(name, age)
    
    @staticmethod
    def is_adult(age):
        """Utility method (doesn't need instance or class)"""
        return age >= 18
    
    def __str__(self):
        """String representation for users"""
        return f"Person(name={self.name}, age={self.age})"
    
    def __repr__(self):
        """String representation for developers"""
        return f"Person('{self.name}', {self.age})"

# Using the class
person1 = Person("Alice", 30)
person2 = Person.from_birth_year("Bob", 1990)

print(person1.greet())
print(Person.is_adult(person1.age))
print(person1)  # Uses __str__
```

### Inheritance and Polymorphism
```python
class Employee(Person):
    """Employee inherits from Person"""
    
    def __init__(self, name, age, employee_id, salary):
        super().__init__(name, age)  # Call parent constructor
        self.employee_id = employee_id
        self.salary = salary
        self.is_employed = True
    
    def greet(self):
        """Override parent method"""
        return f"Hello, I'm {self.name}, Employee #{self.employee_id}"
    
    def get_annual_salary(self):
        """New method specific to Employee"""
        return self.salary * 12
    
    def quit_job(self):
        """Change employment status"""
        self.is_employed = False
        return f"{self.name} has quit their job"

class Manager(Employee):
    """Manager inherits from Employee"""
    
    def __init__(self, name, age, employee_id, salary, team_size):
        super().__init__(name, age, employee_id, salary)
        self.team_size = team_size
    
    def greet(self):
        """Override again"""
        return f"Hello, I'm {self.name}, Manager of {self.team_size} people"
    
    def hire_employee(self):
        """Manager-specific method"""
        self.team_size += 1
        return f"Team size is now {self.team_size}"

# Polymorphism in action
people = [
    Person("Alice", 30),
    Employee("Bob", 25, "E001", 50000),
    Manager("Carol", 35, "M001", 80000, 5)
]

for person in people:
    print(person.greet())  # Each class's greet() method is called
```

### Properties and Descriptors
```python
class BankAccount:
    """Demonstrates properties and validation"""
    
    def __init__(self, owner, initial_balance=0):
        self.owner = owner
        self._balance = initial_balance  # Protected attribute
        self._transaction_history = []
    
    @property
    def balance(self):
        """Getter for balance"""
        return self._balance
    
    @balance.setter
    def balance(self, amount):
        """Setter with validation"""
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = amount
    
    @property
    def transaction_history(self):
        """Read-only property"""
        return self._transaction_history.copy()
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
        self._transaction_history.append(f"Deposited ${amount}")
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        self._transaction_history.append(f"Withdrew ${amount}")

# Usage
account = BankAccount("Alice", 1000)
account.deposit(500)
print(account.balance)  # Uses property getter
# account.balance = -100  # Would raise ValueError
```

## 2. Modules and Packages

### Creating Modules
**File: `math_utils.py`**
```python
"""
Mathematical utilities module
Demonstrates module creation and documentation
"""

PI = 3.14159

def calculate_circle_area(radius):
    """Calculate the area of a circle"""
    return PI * radius ** 2

def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)

class Calculator:
    """A simple calculator class"""
    
    @staticmethod
    def add(a, b):
        return a + b
    
    @staticmethod
    def multiply(a, b):
        return a * b

# Module-level execution
if __name__ == "__main__":
    # This runs only when module is executed directly
    print("Testing math_utils module")
    print(f"Circle area (radius=5): {calculate_circle_area(5)}")
    print(f"Factorial of 5: {factorial(5)}")
```

### Importing Modules
```python
# Different ways to import
import math_utils
from math_utils import calculate_circle_area, PI
from math_utils import Calculator as Calc
import math_utils as math

# Using imports
area = calculate_circle_area(10)
result = Calc.add(5, 3)
area2 = math.calculate_circle_area(5)
```

### Package Structure
```
my_project/
├── __init__.py          # Makes it a package
├── main.py
├── utils/
│   ├── __init__.py
│   ├── string_utils.py
│   └── file_utils.py
└── models/
    ├── __init__.py
    ├── user.py
    └── product.py
```

**File: `utils/__init__.py`**
```python
"""
Utils package initialization
Controls what gets imported with 'from utils import *'
"""

from .string_utils import clean_string, validate_email
from .file_utils import read_config, write_log

# Package version
__version__ = "1.0.0"

# Control * imports
__all__ = ["clean_string", "validate_email", "read_config", "write_log"]
```

**File: `utils/string_utils.py`**
```python
"""String manipulation utilities"""

import re

def clean_string(text):
    """Remove extra whitespace and normalize"""
    return " ".join(text.split())

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def slug_from_title(title):
    """Create URL-friendly slug from title"""
    # Remove special characters, lowercase, replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    return re.sub(r'\s+', '-', slug)
```

### Import Patterns and Best Practices
```python
# Standard library imports first
import os
import sys
from datetime import datetime

# Third-party imports second
import requests
import pandas as pd

# Local application imports last
from .models.user import User
from .utils.string_utils import clean_string

# Avoid wildcard imports in production code
# from module import *  # Don't do this

# Relative imports in packages
from ..models import User        # Go up one level
from .string_utils import clean_string  # Same level
```

## 3. Special Methods (Magic Methods)

```python
class Vector:
    """Demonstrates magic methods for operator overloading"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        """String representation for end users"""
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self):
        """Unambiguous string representation"""
        return f"Vector({self.x}, {self.y})"
    
    def __add__(self, other):
        """Addition operator +"""
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        return NotImplemented
    
    def __mul__(self, scalar):
        """Multiplication operator *"""
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented
    
    def __eq__(self, other):
        """Equality operator =="""
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False
    
    def __len__(self):
        """Length/magnitude of vector"""
        return int((self.x**2 + self.y**2)**0.5)
    
    def __getitem__(self, key):
        """Make object subscriptable"""
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("Vector index out of range")

# Usage
v1 = Vector(3, 4)
v2 = Vector(1, 2)
v3 = v1 + v2      # Uses __add__
v4 = v1 * 2       # Uses __mul__
print(len(v1))    # Uses __len__
print(v1[0])      # Uses __getitem__
print(v1 == v2)   # Uses __eq__
```

## 🏃‍♂️ Practical Exercises

### Exercise 1: Build a Library System
```python
class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_checked_out = False
    
    def __str__(self):
        status = "Checked out" if self.is_checked_out else "Available"
        return f"{self.title} by {self.author} - {status}"

class Library:
    def __init__(self, name):
        self.name = name
        self.books = {}  # ISBN -> Book
        self.members = set()
    
    def add_book(self, book):
        self.books[book.isbn] = book
    
    def register_member(self, member_name):
        self.members.add(member_name)
    
    def check_out_book(self, isbn, member):
        if member not in self.members:
            return "Member not registered"
        if isbn not in self.books:
            return "Book not found"
        if self.books[isbn].is_checked_out:
            return "Book already checked out"
        
        self.books[isbn].is_checked_out = True
        return f"Book checked out to {member}"
    
    def return_book(self, isbn):
        if isbn in self.books and self.books[isbn].is_checked_out:
            self.books[isbn].is_checked_out = False
            return "Book returned successfully"
        return "Book not found or not checked out"

# Test the system
library = Library("City Library")
book1 = Book("Python Programming", "John Doe", "123456")
library.add_book(book1)
library.register_member("Alice")
print(library.check_out_book("123456", "Alice"))
```

### Exercise 2: Create a Simple Package
Create this structure:
```
calculator_package/
├── __init__.py
├── basic_ops.py
└── scientific.py
```

**`basic_ops.py`:**
```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

**`scientific.py`:**
```python
import math

def power(base, exponent):
    return base ** exponent

def square_root(x):
    if x < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(x)

def factorial(n):
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    return math.factorial(n)
```

**`__init__.py`:**
```python
from .basic_ops import add, subtract, multiply, divide
from .scientific import power, square_root, factorial

__version__ = "1.0.0"
__all__ = ["add", "subtract", "multiply", "divide", "power", "square_root", "factorial"]
```

## 🔍 Key OOP Concepts in Python

| Concept | Python Way | Notes |
|---------|------------|-------|
| **Encapsulation** | `_protected`, `__private` | Convention-based |
| **Inheritance** | `class Child(Parent):` | Multiple inheritance supported |
| **Polymorphism** | Duck typing | "If it walks like a duck..." |
| **Abstraction** | Abstract base classes | `from abc import ABC, abstractmethod` |

## ⚡ Best Practices

1. **Use meaningful class names**: `UserAccount` not `UA`
2. **Follow the Single Responsibility Principle**
3. **Prefer composition over inheritance** when possible
4. **Use properties for computed attributes**
5. **Document your classes and methods**
6. **Keep modules focused and cohesive**
7. **Use `__init__.py` to control package imports**

## 🚀 Real-World Application
Look at the main codebase's structure:
- `src/` package with `__init__.py`
- Modular classes: `DocumentProcessor`, `SemanticSearchEngine`
- Clear separation of concerns
- Properties and methods that encapsulate functionality

## 🎯 Next Steps
- Practice building classes with inheritance
- Create your own package structure
- Understand how the main codebase uses OOP patterns
- Move to Module 3: File I/O & Error Handling

**Time to spend:** 3-5 hours

Ready to handle files and errors? → `03_FILES_ERRORS.md`
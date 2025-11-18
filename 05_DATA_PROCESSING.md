# Module 5: Data Processing with pandas & numpy

## 🎯 Goals
- Master pandas for data manipulation and analysis
- Understand numpy for numerical computing
- Work with JSON, CSV, and structured data
- Learn data cleaning and transformation techniques
- Understand patterns used in data-heavy applications

## 📋 Prerequisites
Completed Modules 1-4: Python Basics, OOP, File I/O, Web Development

## 1. NumPy Fundamentals

### Arrays and Basic Operations
```python
import numpy as np

# Creating arrays
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.array([[1, 2, 3], [4, 5, 6]])
zeros = np.zeros((3, 4))
ones = np.ones((2, 3))
identity = np.eye(3)
random_arr = np.random.random((2, 3))

# Array properties
print(f"Shape: {arr2.shape}")        # (2, 3)
print(f"Size: {arr2.size}")          # 6
print(f"Dtype: {arr2.dtype}")        # int64
print(f"Dimensions: {arr2.ndim}")    # 2

# Mathematical operations (vectorized)
arr = np.array([1, 2, 3, 4, 5])
result = arr * 2              # [2, 4, 6, 8, 10]
squared = arr ** 2            # [1, 4, 9, 16, 25]
sqrt_arr = np.sqrt(arr)       # [1.0, 1.414, 1.732, 2.0, 2.236]

# Array operations
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])
addition = arr1 + arr2        # [5, 7, 9]
dot_product = np.dot(arr1, arr2)  # 32

# Statistical operations
data = np.random.normal(100, 15, 1000)  # Normal distribution
print(f"Mean: {np.mean(data):.2f}")
print(f"Std: {np.std(data):.2f}")
print(f"Min: {np.min(data):.2f}")
print(f"Max: {np.max(data):.2f}")
```

### Array Indexing and Slicing
```python
# 1D array indexing
arr = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
print(arr[0])         # 0
print(arr[-1])        # 9
print(arr[2:7])       # [2, 3, 4, 5, 6]
print(arr[::2])       # [0, 2, 4, 6, 8]

# 2D array indexing
matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(matrix[0, 1])   # 2 (row 0, column 1)
print(matrix[1, :])   # [4, 5, 6] (entire row 1)
print(matrix[:, 2])   # [3, 6, 9] (entire column 2)

# Boolean indexing
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
mask = data > 5
filtered = data[mask]  # [6, 7, 8, 9, 10]

# Fancy indexing
indices = np.array([1, 3, 5])
selected = data[indices]  # [2, 4, 6]
```

## 2. Pandas Fundamentals

### Series and DataFrames
```python
import pandas as pd

# Creating Series
s = pd.Series([1, 2, 3, 4, 5], index=['a', 'b', 'c', 'd', 'e'])
print(s['a'])  # 1

# Creating DataFrames
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [25, 30, 35, 28],
    'city': ['New York', 'London', 'Tokyo', 'Paris'],
    'salary': [70000, 80000, 90000, 75000]
}

df = pd.DataFrame(data)
print(df.head())
print(df.info())
print(df.describe())

# From CSV
# df = pd.read_csv('data.csv')

# From JSON
# df = pd.read_json('data.json')

# Basic operations
print(df.shape)           # (4, 4)
print(df.columns.tolist()) # ['name', 'age', 'city', 'salary']
print(df.index.tolist())   # [0, 1, 2, 3]
```

### Data Selection and Indexing
```python
# Column selection
names = df['name']              # Series
name_age = df[['name', 'age']]  # DataFrame

# Row selection
first_row = df.iloc[0]          # By position
alice = df.loc[0]               # By index label

# Boolean indexing
high_earners = df[df['salary'] > 75000]
young_high_earners = df[(df['age'] < 30) & (df['salary'] > 70000)]

# Query method (more readable)
result = df.query('age > 25 and salary > 70000')

# Setting and getting values
df.loc[0, 'age'] = 26          # Set single value
df.loc[df['name'] == 'Alice', 'salary'] = 72000  # Conditional update

# Adding new columns
df['bonus'] = df['salary'] * 0.1
df['full_info'] = df['name'] + ' (' + df['age'].astype(str) + ')'

# Dropping columns and rows
df_clean = df.drop(['bonus'], axis=1)  # Drop column
df_clean = df.drop([0], axis=0)        # Drop row
```

### Data Cleaning and Transformation
```python
# Sample messy data
messy_data = {
    'name': ['Alice', 'Bob', None, 'Diana', ''],
    'age': [25, 'thirty', 35, 28, None],
    'email': ['alice@email.com', 'BOB@EMAIL.COM', 'charlie@email', 'diana@email.com', None],
    'salary': ['70,000', '80000', '90,000', '75000', 'not_specified']
}

df_messy = pd.DataFrame(messy_data)

# Handle missing values
print(df_messy.isnull().sum())         # Count nulls per column
df_clean = df_messy.dropna()           # Drop rows with any null
df_filled = df_messy.fillna({'age': 0, 'email': 'no_email@example.com'})

# Clean string data
df_messy['name'] = df_messy['name'].str.strip()  # Remove whitespace
df_messy['email'] = df_messy['email'].str.lower()  # Lowercase

# Data type conversion
def clean_salary(salary_str):
    """Clean salary column"""
    if pd.isna(salary_str) or salary_str == 'not_specified':
        return None
    return int(str(salary_str).replace(',', ''))

df_messy['salary_clean'] = df_messy['salary'].apply(clean_salary)

# Handle text data
def parse_age(age_val):
    """Parse age from various formats"""
    if pd.isna(age_val):
        return None
    if isinstance(age_val, str):
        age_mapping = {'thirty': 30, 'twenty': 20}
        return age_mapping.get(age_val.lower(), None)
    return int(age_val)

df_messy['age_clean'] = df_messy['age'].apply(parse_age)

# Regular expressions for validation
import re

def validate_email(email):
    """Validate email format"""
    if pd.isna(email):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

df_messy['email_valid'] = df_messy['email'].apply(validate_email)

print(df_messy)
```

### Grouping and Aggregation
```python
# Sample sales data
sales_data = {
    'date': pd.date_range('2023-01-01', periods=100, freq='D'),
    'product': np.random.choice(['A', 'B', 'C'], 100),
    'category': np.random.choice(['Electronics', 'Clothing', 'Books'], 100),
    'sales': np.random.randint(100, 1000, 100),
    'quantity': np.random.randint(1, 10, 100)
}

sales_df = pd.DataFrame(sales_data)
sales_df['revenue'] = sales_df['sales'] * sales_df['quantity']

# Basic grouping
product_summary = sales_df.groupby('product').agg({
    'revenue': ['sum', 'mean', 'count'],
    'quantity': 'sum'
})

# Multiple grouping
category_product = sales_df.groupby(['category', 'product']).agg({
    'revenue': 'sum',
    'quantity': 'sum'
}).round(2)

# Custom aggregation functions
def revenue_stats(series):
    return {
        'total': series.sum(),
        'avg': series.mean(),
        'max_sale': series.max()
    }

custom_agg = sales_df.groupby('product')['revenue'].apply(revenue_stats)

# Time-based grouping
sales_df['month'] = sales_df['date'].dt.month
monthly_sales = sales_df.groupby('month')['revenue'].sum()

print("Product Summary:")
print(product_summary)
print("\nMonthly Sales:")
print(monthly_sales)
```

### Data Merging and Joining
```python
# Sample datasets
customers = pd.DataFrame({
    'customer_id': [1, 2, 3, 4],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'city': ['New York', 'London', 'Tokyo', 'Paris']
})

orders = pd.DataFrame({
    'order_id': [101, 102, 103, 104, 105],
    'customer_id': [1, 2, 1, 3, 2],
    'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Tablet'],
    'amount': [1000, 25, 75, 300, 500]
})

# Inner join (default)
merged = pd.merge(customers, orders, on='customer_id')

# Left join (keep all customers)
left_merged = pd.merge(customers, orders, on='customer_id', how='left')

# Right join (keep all orders)
right_merged = pd.merge(customers, orders, on='customer_id', how='right')

# Outer join (keep all records)
outer_merged = pd.merge(customers, orders, on='customer_id', how='outer')

# Concatenating DataFrames
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})

# Vertical concatenation
vertical = pd.concat([df1, df2], ignore_index=True)

# Horizontal concatenation
horizontal = pd.concat([df1, df2], axis=1)

print("Merged Data:")
print(merged)
```

## 3. Working with Real-World Data

### JSON Data Processing
```python
import json
import pandas as pd

# Sample API-like JSON data
api_data = {
    "users": [
        {
            "id": 1,
            "name": "Alice",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "coordinates": {"lat": 40.7128, "lng": -74.0060}
            },
            "orders": [
                {"product": "Laptop", "price": 1000, "date": "2023-01-15"},
                {"product": "Mouse", "price": 25, "date": "2023-02-01"}
            ]
        },
        {
            "id": 2,
            "name": "Bob",
            "address": {
                "street": "456 Oak Ave",
                "city": "London",
                "coordinates": {"lat": 51.5074, "lng": -0.1278}
            },
            "orders": [
                {"product": "Keyboard", "price": 75, "date": "2023-01-20"}
            ]
        }
    ]
}

def flatten_user_data(api_data):
    """Flatten nested JSON structure into a DataFrame"""
    flattened_users = []
    
    for user in api_data['users']:
        base_user = {
            'user_id': user['id'],
            'name': user['name'],
            'street': user['address']['street'],
            'city': user['address']['city'],
            'latitude': user['address']['coordinates']['lat'],
            'longitude': user['address']['coordinates']['lng']
        }
        
        # Flatten orders
        for order in user['orders']:
            user_order = base_user.copy()
            user_order.update({
                'product': order['product'],
                'price': order['price'],
                'order_date': pd.to_datetime(order['date'])
            })
            flattened_users.append(user_order)
    
    return pd.DataFrame(flattened_users)

users_df = flatten_user_data(api_data)
print(users_df)

# Aggregating the flattened data
user_summary = users_df.groupby(['user_id', 'name', 'city']).agg({
    'price': ['sum', 'mean', 'count'],
    'order_date': ['min', 'max']
}).round(2)

print("\nUser Summary:")
print(user_summary)
```

### CSV Data Processing Pipeline
```python
def process_sales_data(file_path):
    """Complete data processing pipeline for sales data"""
    
    try:
        # Load data
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} records")
        
        # Data quality assessment
        print("\nData Quality Report:")
        print(f"Missing values per column:")
        print(df.isnull().sum())
        print(f"\nData types:")
        print(df.dtypes)
        
        # Data cleaning
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df['customer_name'].fillna('Unknown Customer', inplace=True)
        df['sales_amount'].fillna(0, inplace=True)
        
        # Data type conversions
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['sales_amount'] = pd.to_numeric(df['sales_amount'], errors='coerce')
        
        # Feature engineering
        df['year'] = df['order_date'].dt.year
        df['month'] = df['order_date'].dt.month
        df['quarter'] = df['order_date'].dt.quarter
        df['day_of_week'] = df['order_date'].dt.day_name()
        
        # Business logic
        def categorize_sale_amount(amount):
            if amount > 1000:
                return 'High'
            elif amount > 500:
                return 'Medium'
            else:
                return 'Low'
        
        df['sale_category'] = df['sales_amount'].apply(categorize_sale_amount)
        
        # Analysis
        analysis_results = {
            'total_sales': df['sales_amount'].sum(),
            'average_sale': df['sales_amount'].mean(),
            'total_orders': len(df),
            'unique_customers': df['customer_name'].nunique(),
            'date_range': {
                'start': df['order_date'].min(),
                'end': df['order_date'].max()
            },
            'top_customers': df.groupby('customer_name')['sales_amount'].sum().sort_values(ascending=False).head(),
            'monthly_trends': df.groupby('month')['sales_amount'].sum(),
            'category_breakdown': df['sale_category'].value_counts()
        }
        
        return df, analysis_results
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return None, None

# Example usage (commented out as we don't have the file)
# df, results = process_sales_data('sales_data.csv')
# if df is not None:
#     print("\nProcessing complete!")
#     print(f"Total sales: ${results['total_sales']:,.2f}")
```

## 4. Time Series and Date Handling

```python
# Creating date ranges
dates = pd.date_range('2023-01-01', periods=365, freq='D')
business_days = pd.bdate_range('2023-01-01', periods=250)

# Sample time series data
ts_data = pd.DataFrame({
    'date': dates,
    'value': np.random.randn(365).cumsum() + 100,
    'category': np.random.choice(['A', 'B', 'C'], 365)
})

ts_data.set_index('date', inplace=True)

# Time-based operations
monthly_avg = ts_data['value'].resample('M').mean()
quarterly_sum = ts_data['value'].resample('Q').sum()

# Rolling operations
ts_data['rolling_mean_7'] = ts_data['value'].rolling(window=7).mean()
ts_data['rolling_std_30'] = ts_data['value'].rolling(window=30).std()

# Date filtering
q1_data = ts_data['2023-01-01':'2023-03-31']
recent_data = ts_data.last('30D')

print("Monthly averages:")
print(monthly_avg.head())
```

## 🏃‍♂️ Practical Exercises

### Exercise 1: Customer Analytics Dashboard
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CustomerAnalytics:
    """Customer analytics engine for e-commerce data"""
    
    def __init__(self):
        self.customers = None
        self.orders = None
        self.products = None
        self.merged_data = None
    
    def load_sample_data(self):
        """Generate sample e-commerce data"""
        np.random.seed(42)
        
        # Customers data
        self.customers = pd.DataFrame({
            'customer_id': range(1, 1001),
            'name': [f'Customer_{i}' for i in range(1, 1001)],
            'email': [f'customer{i}@email.com' for i in range(1, 1001)],
            'registration_date': pd.date_range('2022-01-01', periods=1000, freq='D'),
            'city': np.random.choice(['New York', 'London', 'Tokyo', 'Paris', 'Berlin'], 1000),
            'age': np.random.randint(18, 70, 1000)
        })
        
        # Products data
        products = ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Mouse', 'Keyboard', 'Monitor']
        categories = ['Electronics', 'Electronics', 'Electronics', 'Audio', 'Accessories', 'Accessories', 'Electronics']
        prices = [1000, 800, 500, 200, 25, 75, 300]
        
        self.products = pd.DataFrame({
            'product_name': products,
            'category': categories,
            'price': prices
        })
        
        # Orders data (more orders than customers - repeat customers)
        self.orders = pd.DataFrame({
            'order_id': range(1, 5001),
            'customer_id': np.random.randint(1, 1001, 5000),
            'product_name': np.random.choice(products, 5000),
            'quantity': np.random.randint(1, 5, 5000),
            'order_date': pd.date_range('2023-01-01', periods=5000, freq='H'),
            'discount': np.random.choice([0, 0.1, 0.2], 5000, p=[0.7, 0.2, 0.1])
        })
    
    def prepare_data(self):
        """Merge and prepare data for analysis"""
        # Merge orders with products to get prices
        orders_with_products = pd.merge(self.orders, self.products, on='product_name')
        
        # Merge with customers
        self.merged_data = pd.merge(orders_with_products, self.customers, on='customer_id')
        
        # Calculate revenue
        self.merged_data['unit_price'] = self.merged_data['price'] * (1 - self.merged_data['discount'])
        self.merged_data['total_revenue'] = self.merged_data['unit_price'] * self.merged_data['quantity']
        
        # Add time-based features
        self.merged_data['order_month'] = self.merged_data['order_date'].dt.month
        self.merged_data['order_quarter'] = self.merged_data['order_date'].dt.quarter
        self.merged_data['order_day_name'] = self.merged_data['order_date'].dt.day_name()
    
    def customer_lifetime_value(self):
        """Calculate customer lifetime value metrics"""
        clv_metrics = self.merged_data.groupby('customer_id').agg({
            'total_revenue': ['sum', 'mean', 'count'],
            'order_date': ['min', 'max'],
            'quantity': 'sum'
        }).round(2)
        
        # Flatten column names
        clv_metrics.columns = ['total_spent', 'avg_order_value', 'order_count', 'first_order', 'last_order', 'total_items']
        
        # Calculate days as customer
        clv_metrics['days_as_customer'] = (clv_metrics['last_order'] - clv_metrics['first_order']).dt.days + 1
        clv_metrics['avg_days_between_orders'] = clv_metrics['days_as_customer'] / clv_metrics['order_count']
        
        return clv_metrics.sort_values('total_spent', ascending=False)
    
    def product_performance(self):
        """Analyze product performance"""
        performance = self.merged_data.groupby(['product_name', 'category']).agg({
            'total_revenue': 'sum',
            'quantity': 'sum',
            'order_id': 'count',
            'discount': 'mean'
        }).round(2)
        
        performance.columns = ['revenue', 'units_sold', 'order_count', 'avg_discount']
        performance['avg_revenue_per_order'] = (performance['revenue'] / performance['order_count']).round(2)
        
        return performance.sort_values('revenue', ascending=False)
    
    def monthly_trends(self):
        """Analyze monthly sales trends"""
        monthly = self.merged_data.groupby('order_month').agg({
            'total_revenue': 'sum',
            'order_id': 'count',
            'customer_id': 'nunique'
        }).round(2)
        
        monthly.columns = ['revenue', 'orders', 'unique_customers']
        monthly['avg_order_value'] = (monthly['revenue'] / monthly['orders']).round(2)
        
        return monthly
    
    def generate_report(self):
        """Generate comprehensive analytics report"""
        if self.merged_data is None:
            self.prepare_data()
        
        # Calculate key metrics
        total_revenue = self.merged_data['total_revenue'].sum()
        total_orders = self.merged_data['order_id'].nunique()
        unique_customers = self.merged_data['customer_id'].nunique()
        avg_order_value = self.merged_data.groupby('order_id')['total_revenue'].sum().mean()
        
        # Get top performers
        top_customers = self.customer_lifetime_value().head(5)
        top_products = self.product_performance().head(5)
        monthly_trends = self.monthly_trends()
        
        report = f"""
CUSTOMER ANALYTICS REPORT
=========================

SUMMARY METRICS:
- Total Revenue: ${total_revenue:,.2f}
- Total Orders: {total_orders:,}
- Unique Customers: {unique_customers:,}
- Average Order Value: ${avg_order_value:.2f}

TOP 5 CUSTOMERS BY SPENDING:
{top_customers[['total_spent', 'order_count', 'avg_order_value']]}

TOP 5 PRODUCTS BY REVENUE:
{top_products[['revenue', 'units_sold', 'avg_revenue_per_order']]}

MONTHLY TRENDS:
{monthly_trends}
        """
        
        return report

# Usage example
analytics = CustomerAnalytics()
analytics.load_sample_data()
analytics.prepare_data()
report = analytics.generate_report()
print(report)
```

## 🔍 Key Data Processing Concepts

| Library | Purpose | Common Use Cases |
|---------|---------|------------------|
| **NumPy** | Numerical computing | Mathematical operations, arrays |
| **Pandas** | Data manipulation | CSV/JSON processing, analysis |
| **JSON** | Data interchange | API responses, configuration |
| **Datetime** | Time handling | Time series, date calculations |

## ⚡ Best Practices

1. **Use vectorized operations** instead of loops when possible
2. **Handle missing data explicitly** - don't ignore it
3. **Validate data types** after loading from external sources
4. **Use meaningful variable names** for DataFrames and columns
5. **Document data transformations** for reproducibility
6. **Profile performance** for large datasets
7. **Save intermediate results** for long processing pipelines

## 🚀 Real-World Application
In the main codebase, you'll see data processing patterns like:
- JSON handling for configuration and API responses
- Text processing for document chunks
- Vector operations for embeddings
- Metadata management for document tracking

## 🎯 Next Steps
- Practice with real datasets from your domain
- Learn about data visualization (matplotlib, seaborn)
- Understand the data flow in the main codebase
- Move to Module 6: Advanced Python Features

**Time to spend:** 3-4 hours

Ready for advanced Python features? → `06_ADVANCED_PYTHON.md`
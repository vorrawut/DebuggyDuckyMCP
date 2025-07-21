"""
Test code example with intentional issues for intelligent agent analysis.
This file demonstrates various code patterns and issues that the agent can detect.
"""


class UserManager:
    """A class to manage users - but with some issues."""
    
    def __init__(self):
        self.users = []
        self.db = None
    
    def add_user(self, data):
        # Issue: No input validation
        # Issue: Bare except clause
        # Issue: eval() usage (security risk)
        try:
            processed_data = eval(data)  # Security vulnerability!
            self.users.append(processed_data)
            return True
        except:  # Too broad exception handling
            return False
    
    def get_user(self, idx):
        # Issue: No bounds checking
        return self.users[idx]
    
    def process_users(self):
        # Issue: Nested loops (performance)
        results = []
        for user in self.users:
            for field in user:
                for value in field:  # Triple nested loop!
                    results.append(value.upper())
        return results
    
    def save_to_file(self, filename):
        # Issue: No error handling for file operations
        with open(filename, 'w') as f:
            f.write(str(self.users))


def helper_func(x):
    """Helper function with unclear purpose."""
    # Issue: Single letter variable
    # Issue: No type hints
    # Issue: Unclear naming
    if x > 10:
        return x * 2
    else:
        return x / 2


class DataProcessor:
    """Class with better practices for comparison."""
    
    def __init__(self, data_source: str):
        """Initialize with proper type hints and validation."""
        if not data_source:
            raise ValueError("Data source cannot be empty")
        self.data_source = data_source
        self.processed_data = []
    
    def process_data(self, input_data: list) -> list:
        """Process data with proper error handling and documentation.
        
        Args:
            input_data: List of data items to process
            
        Returns:
            List of processed data items
            
        Raises:
            ValueError: If input_data is not a list
        """
        if not isinstance(input_data, list):
            raise ValueError("Input data must be a list")
        
        try:
            result = []
            for item in input_data:
                if self._is_valid_item(item):
                    result.append(self._transform_item(item))
            return result
        except Exception as e:
            logger.error(f"Failed to process data: {e}")
            raise
    
    def _is_valid_item(self, item) -> bool:
        """Check if an item is valid for processing."""
        return item is not None and hasattr(item, '__len__')
    
    def _transform_item(self, item):
        """Transform a single data item."""
        return str(item).strip().lower() 
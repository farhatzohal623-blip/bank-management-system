"""
Complete Bank System using OOP Concepts
=====================================

This project demonstrates all major OOP concepts:
- Classes & Objects
- Methods & Constructors  
- Inheritance & Encapsulation
- Magic Methods
- Polymorphism & Abstraction
- Composition vs Inheritance
- Design Patterns: Singleton, Factory
- Data persistence with pandas CSV
"""

# Import pandas library for CSV data operations
import pandas as pd
# Import uuid library for generating unique identifiers
import uuid
# Import ABC and abstractmethod for creating abstract base classes
from abc import ABC, abstractmethod
# Import datetime for handling timestamps
from datetime import datetime
# Import typing utilities for type hints
from typing import List, Dict, Optional


class Account(ABC):
    """Abstract base class for all account types - demonstrates Abstraction"""
    
    def __init__(self, account_number: str, customer_id: str, initial_balance: float = 0.0):
        # Store account number as protected attribute (encapsulation)
        self._account_number = account_number  # Encapsulation: protected attribute
        # Store customer ID as private attribute (strong encapsulation)
        self.__customer_id = customer_id      # Encapsulation: private attribute
        # Store account balance as protected attribute
        self._balance = initial_balance
        # Record when account was created
        self._created_at = datetime.now()
        # Initialize empty list to track all transactions
        self._transaction_history = []
    
    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        """Abstract method - must be implemented by subclasses"""
        pass  # No implementation - subclasses must provide their own
    
    @abstractmethod
    def get_account_type(self) -> str:
        """Abstract method - must be implemented by subclasses"""
        pass  # No implementation - subclasses must provide their own
    
    def deposit(self, amount: float) -> bool:
        """Common deposit method for all account types"""
        # Validate that deposit amount is positive
        if amount <= 0:
            return False  # Invalid deposit amount
        
        # Add amount to account balance
        self._balance += amount
        # Record the deposit transaction
        self._add_transaction("DEPOSIT", amount)
        return True  # Deposit successful
    
    def get_balance(self) -> float:
        """Getter method - encapsulation"""
        return self._balance  # Return current balance
    
    def get_account_number(self) -> str:
        """Getter method - encapsulation"""
        return self._account_number  # Return account number
    
    def get_customer_id(self) -> str:
        """Getter method - encapsulation"""
        return self.__customer_id  # Return customer ID
    
    def _add_transaction(self, transaction_type: str, amount: float):
        """Protected method for internal use"""
        # Create transaction record dictionary
        transaction = {
            'type': transaction_type,           # Type of transaction (DEPOSIT, WITHDRAW, etc.)
            'amount': amount,                   # Transaction amount
            'balance_after': self._balance,     # Balance after transaction
            'timestamp': datetime.now().isoformat()  # When transaction occurred
        }
        # Add transaction to history list
        self._transaction_history.append(transaction)
    
    def get_transaction_history(self) -> List[Dict]:
        """Getter method for transaction history"""
        return self._transaction_history.copy()  # Return copy to protect original
    
    # Magic Methods
    def __str__(self) -> str:
        """String representation of account"""
        return f"{self.get_account_type()} Account #{self._account_number} - Balance: ${self._balance:.2f}"
    
    def __repr__(self) -> str:
        """Official string representation"""
        return f"{self.__class__.__name__}(account_number='{self._account_number}', balance={self._balance})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison based on account number"""
        # Check if other object is also an Account
        if isinstance(other, Account):
            return self._account_number == other._account_number
        return False  # Not equal if not an Account object
    
    def __lt__(self, other) -> bool:
        """Less than comparison based on balance"""
        # Check if other object is also an Account
        if isinstance(other, Account):
            return self._balance < other._balance
        return False  # Cannot compare if not an Account object


class SavingsAccount(Account):
    """Savings Account with interest rate - demonstrates Inheritance"""
    
    INTEREST_RATE = 0.02  # Class attribute for interest rate (2%)
    
    def __init__(self, account_number: str, customer_id: str, initial_balance: float = 0.0):
        # Call parent class constructor
        super().__init__(account_number, customer_id, initial_balance)
        # Set monthly withdrawal limit for savings accounts
        self._withdrawal_limit = 6  # Monthly withdrawal limit
    
    def withdraw(self, amount: float) -> bool:
        """Polymorphic method with savings account specific logic"""
        # Validate withdrawal amount
        if amount <= 0 or amount > self._balance:
            return False  # Invalid withdrawal amount
        
        # Check withdrawal limit for savings account
        monthly_withdrawals = self._count_monthly_withdrawals()
        if monthly_withdrawals >= self._withdrawal_limit:
            print(f"Withdrawal limit of {self._withdrawal_limit} per month reached")
            return False  # Limit exceeded
        
        # Process withdrawal
        self._balance -= amount
        self._add_transaction("WITHDRAW", amount)
        return True  # Withdrawal successful
    
    def apply_interest(self) -> float:
        """Apply monthly interest - savings account specific feature"""
        # Calculate interest amount
        interest = self._balance * self.INTEREST_RATE
        # Add interest to balance
        self._balance += interest
        # Record interest transaction
        self._add_transaction("INTEREST", interest)
        return interest  # Return interest amount earned
    
    def get_account_type(self) -> str:
        """Polymorphic method"""
        return "Savings"  # Return account type string
    
    def _count_monthly_withdrawals(self) -> int:
        """Count withdrawals in current month"""
        # Get current month and year
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Initialize counter
        count = 0
        # Loop through all transactions
        for transaction in self._transaction_history:
            # Check if transaction is a withdrawal
            if transaction['type'] == 'WITHDRAW':
                # Parse transaction timestamp
                trans_date = datetime.fromisoformat(transaction['timestamp'])
                # Check if withdrawal occurred in current month and year
                if trans_date.month == current_month and trans_date.year == current_year:
                    count += 1  # Increment counter
        return count  # Return monthly withdrawal count


class CheckingAccount(Account):
    """Checking Account with overdraft protection - demonstrates Inheritance"""
    
    OVERDRAFT_LIMIT = 500.0  # Class attribute for overdraft limit
    TRANSACTION_FEE = 1.0     # Class attribute for transaction fee
    
    def __init__(self, account_number: str, customer_id: str, initial_balance: float = 0.0):
        # Call parent class constructor
        super().__init__(account_number, customer_id, initial_balance)
        # Initialize overdraft protection flag
        self._has_overdraft_protection = True
    
    def withdraw(self, amount: float) -> bool:
        """Polymorphic method with checking account specific logic"""
        # Validate withdrawal amount
        if amount <= 0:
            return False  # Invalid withdrawal amount
        
        # Calculate total withdrawal including transaction fee
        total_withdrawal = amount + self.TRANSACTION_FEE
        
        # Check overdraft protection
        if self._has_overdraft_protection:
            # Allow overdraft up to limit
            if self._balance - total_withdrawal < -self.OVERDRAFT_LIMIT:
                return False  # Overdraft limit exceeded
        else:
            # No overdraft protection - must have sufficient funds
            if total_withdrawal > self._balance:
                return False  # Insufficient funds
        
        # Process withdrawal
        self._balance -= total_withdrawal
        # Record withdrawal transaction
        self._add_transaction("WITHDRAW", amount)
        # Record fee transaction
        self._add_transaction("FEE", self.TRANSACTION_FEE)
        return True  # Withdrawal successful
    
    def get_account_type(self) -> str:
        """Polymorphic method"""
        return "Checking"  # Return account type string
    
    def toggle_overdraft_protection(self):
        """Toggle overdraft protection"""
        # Flip the boolean value
        self._has_overdraft_protection = not self._has_overdraft_protection


class Customer:
    """Customer class - demonstrates Composition relationship with Bank"""
    
    def __init__(self, customer_id: str, name: str, email: str, phone: str):
        # Store customer ID as protected attribute
        self._customer_id = customer_id
        # Store customer name as protected attribute
        self._name = name
        # Store customer email as protected attribute
        self._email = email
        # Store customer phone as protected attribute
        self._phone = phone
        # Initialize list to hold customer's accounts (Composition)
        self._accounts = []  # Composition: Customer has Accounts
        # Record when customer was created
        self._created_at = datetime.now()
    
    def add_account(self, account: Account):
        """Add account to customer - demonstrates Composition"""
        # Verify account belongs to this customer
        if account.get_customer_id() == self._customer_id:
            # Add account to customer's account list
            self._accounts.append(account)
            return True  # Account added successfully
        return False  # Account belongs to different customer
    
    def remove_account(self, account_number: str) -> bool:
        """Remove account from customer"""
        # Loop through accounts with index
        for i, account in enumerate(self._accounts):
            # Check if account number matches
            if account.get_account_number() == account_number:
                # Remove account from list
                del self._accounts[i]
                return True  # Account removed successfully
        return False  # Account not found
    
    def get_accounts(self) -> List[Account]:
        """Get all customer accounts"""
        return self._accounts.copy()  # Return copy to protect original
    
    def get_total_balance(self) -> float:
        """Calculate total balance across all accounts"""
        # Sum balances of all accounts using generator expression
        return sum(account.get_balance() for account in self._accounts)
    
    # Getters with encapsulation
    def get_customer_id(self) -> str:
        return self._customer_id  # Return customer ID
    
    def get_name(self) -> str:
        return self._name  # Return customer name
    
    def get_email(self) -> str:
        return self._email  # Return customer email
    
    def get_phone(self) -> str:
        return self._phone  # Return customer phone
    
    # Magic Methods
    def __str__(self) -> str:
        """String representation of customer"""
        return f"Customer: {self._name} (ID: {self._customer_id}) - Accounts: {len(self._accounts)}"
    
    def __repr__(self) -> str:
        """Official string representation"""
        return f"Customer(id='{self._customer_id}', name='{self._name}')"


class Bank:
    """Bank class with Singleton pattern and Factory methods"""
    
    _instance = None  # Class variable to hold singleton instance
    
    def __new__(cls):
        """Singleton pattern implementation"""
        # Check if instance already exists
        if cls._instance is None:
            # Create new instance if it doesn't exist
            cls._instance = super().__new__(cls)
            # Mark as not initialized
            cls._instance._initialized = False
        # Return existing instance
        return cls._instance
    
    def __init__(self):
        """Initialize bank only once"""
        # Check if already initialized
        if self._initialized:
            return  # Skip initialization if already done
        
        # Set bank name
        self._name = "Central Bank"
        # Initialize dictionary to hold customers (Composition)
        self._customers = {}  # Composition: Bank has Customers
        # Initialize dictionary to hold accounts (Composition)
        self._accounts = {}   # Composition: Bank has Accounts
        # Set data file name  for CSV operations
        self._data_file = "bank_data.csv"
        # Mark as initialized
        self._initialized = True
    
    # Factory Methods
    @classmethod
    def create_savings_account(cls, customer_id: str, initial_balance: float = 0.0) -> SavingsAccount:
        """Factory method for creating savings accounts"""
        # Generate unique account number (first 8 characters of UUID)
        account_number = str(uuid.uuid4())[:8]
        # Create and return new savings account
        return SavingsAccount(account_number, customer_id, initial_balance)
    
    @classmethod
    def create_checking_account(cls, customer_id: str, initial_balance: float = 0.0) -> CheckingAccount:
        """Factory method for creating checking accounts"""
        # Generate unique account number (first 8 characters of UUID)
        account_number = str(uuid.uuid4())[:8]
        # Create and return new checking account
        return CheckingAccount(account_number, customer_id, initial_balance)
    
    def add_customer(self, name: str, email: str, phone: str) -> Customer:
        """Add new customer to bank"""
        # Generate unique customer ID (first 8 characters of UUID)
        customer_id = str(uuid.uuid4())[:8]
        # Create new customer object
        customer = Customer(customer_id, name, email, phone)
        # Add customer to bank's customer dictionary
        self._customers[customer_id] = customer
        return customer  # Return created customer
    
    def add_account(self, account: Account, customer_id: str) -> bool:
        """Add account to bank and customer"""
        # Check if customer exists
        if customer_id in self._customers:
            # Get customer object
            customer = self._customers[customer_id]
            # Add account to customer
            if customer.add_account(account):
                # Add account to bank's account dictionary
                self._accounts[account.get_account_number()] = account
                return True  # Account added successfully
        return False  # Customer not found or account not added
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        return self._customers.get(customer_id)  # Return customer or None
    
    def get_account(self, account_number: str) -> Optional[Account]:
        """Get account by number"""
        return self._accounts.get(account_number)  # Return account or None
    
    def get_all_customers(self) -> List[Customer]:
        """Get all customers"""
        return list(self._customers.values())  # Return list of all customers
    
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        return list(self._accounts.values())  # Return list of all accounts
    
    def get_total_deposits(self) -> float:
        """Get total deposits across all accounts"""
        # Sum balances of all accounts using generator expression
        return sum(account.get_balance() for account in self._accounts.values())
    
    # Data persistence methods
    def save_to_csv(self) -> bool:
        """Save bank data to CSV using pandas"""
        try:
            # Initialize lists to hold data
            customers_data = []
            accounts_data = []
            transactions_data = []
            
            # Export customers
            for customer in self.get_all_customers():
                # Create customer data dictionary
                customers_data.append({
                    'customer_id': customer.get_customer_id(),
                    'name': customer.get_name(),
                    'email': customer.get_email(),
                    'phone': customer.get_phone(),
                    'created_at': customer._created_at.isoformat()
                })
            
            # Export accounts
            for account in self.get_all_accounts():
                # Create account data dictionary
                accounts_data.append({
                    'account_number': account.get_account_number(),
                    'customer_id': account.get_customer_id(),
                    'account_type': account.get_account_type(),
                    'balance': account.get_balance(),
                    'created_at': account._created_at.isoformat()
                })
                
                # Export transactions for each account
                for transaction in account.get_transaction_history():
                    # Create transaction data dictionary
                    transactions_data.append({
                        'account_number': account.get_account_number(),
                        'transaction_type': transaction['type'],
                        'amount': transaction['amount'],
                        'balance_after': transaction['balance_after'],
                        'timestamp': transaction['timestamp']
                    })
            
            # Save data to CSV files using pandas
            pd.DataFrame(customers_data).to_csv('customers.csv', index=False)
            pd.DataFrame(accounts_data).to_csv('accounts.csv', index=False)
            pd.DataFrame(transactions_data).to_csv('transactions.csv', index=False)
            
            # Print success message
            print("Bank data saved successfully to CSV files")
            return True  # Save successful
            
        except Exception as e:
            # Handle any errors during save
            print(f"Error saving data: {e}")
            return False  # Save failed
    
    def load_from_csv(self) -> bool:
        """Load bank data from CSV using pandas"""
        try:
            # Load customers from CSV
            customers_df = pd.read_csv('customers.csv')
            # Iterate through customer rows
            for _, row in customers_df.iterrows():
                # Create customer object from CSV data
                customer = Customer(
                    row['customer_id'],
                    row['name'],
                    row['email'],
                    row['phone']
                )
                # Add customer to bank
                self._customers[row['customer_id']] = customer
            
            # Load accounts from CSV
            accounts_df = pd.read_csv('accounts.csv')
            # Iterate through account rows
            for _, row in accounts_df.iterrows():
                # Create appropriate account type based on account_type column
                if row['account_type'] == 'Savings':
                    account = SavingsAccount(
                        row['account_number'],
                        row['customer_id'],
                        row['balance']
                    )
                else:  # Checking account
                    account = CheckingAccount(
                        row['account_number'],
                        row['customer_id'],
                        row['balance']
                    )
                
                # Add account to bank
                self._accounts[row['account_number']] = account
                
                # Add account to corresponding customer
                customer = self._customers.get(row['customer_id'])
                if customer:
                    customer.add_account(account)
            
            # Load transactions (simplified - would need more complex logic for full restoration)
            transactions_df = pd.read_csv('transactions.csv')
            # Print number of loaded transactions
            print(f"Loaded {len(transactions_df)} transactions")
            
            # Print success message
            print("Bank data loaded successfully from CSV files")
            return True  # Load successful
            
        except FileNotFoundError:
            # Handle case where no data files exist
            print("No existing data files found - starting with empty bank")
            return True  # Not an error, just no existing data
        except Exception as e:
            # Handle any other errors during load
            print(f"Error loading data: {e}")
            return False  # Load failed
    
    # Magic Methods
    def __str__(self) -> str:
        """String representation of bank"""
        return f"{self._name} - Customers: {len(self._customers)}, Accounts: {len(self._accounts)}, Total Deposits: ${self.get_total_deposits():.2f}"
    
    def __len__(self) -> int:
        """Return number of customers"""
        return len(self._customers)  # Return customer count


# Demo function to showcase all OOP concepts
def demo_bank_system():
    """Demonstrate all OOP concepts and bank functionality"""
    # Print demo header
    print("=" * 60)
    print("BANK SYSTEM DEMO - SHOWCASING OOP CONCEPTS")
    print("=" * 60)
    
    # Singleton pattern - same instance returned
    bank1 = Bank()  # Create first bank instance
    bank2 = Bank()  # Create second bank instance (should be same as first)
    print(f"Singleton Pattern: bank1 is bank2 = {bank1 is bank2}")
    
    # Load existing data or start fresh
    bank1.load_from_csv()
    
    # Create customers
    print("\n1. Creating Customers (Objects & Classes)")
    customer1 = bank1.add_customer("John Doe", "john@email.com", "555-0101")
    customer2 = bank1.add_customer("Jane Smith", "jane@email.com", "555-0102")
    
    # Display created customers
    print(f"Created: {customer1}")
    print(f"Created: {customer2}")
    
    # Factory pattern - create different account types
    print("\n2. Factory Pattern - Creating Accounts")
    # Use factory methods to create accounts
    savings1 = Bank.create_savings_account(customer1.get_customer_id(), 1000.0)
    checking1 = Bank.create_checking_account(customer1.get_customer_id(), 500.0)
    savings2 = Bank.create_savings_account(customer2.get_customer_id(), 2000.0)
    
    # Add accounts to bank (Composition)
    bank1.add_account(savings1, customer1.get_customer_id())
    bank1.add_account(checking1, customer1.get_customer_id())
    bank1.add_account(savings2, customer2.get_customer_id())
    
    # Display created accounts
    print(f"Created: {savings1}")
    print(f"Created: {checking1}")
    print(f"Created: {savings2}")
    
    # Polymorphism - different withdraw behavior
    print("\n3. Polymorphism - Different Account Behaviors")
    print(f"Savings balance before: ${savings1.get_balance()}")
    savings1.withdraw(100)  # Withdraw from savings account
    print(f"Savings balance after withdraw: ${savings1.get_balance()}")
    
    print(f"Checking balance before: ${checking1.get_balance()}")
    checking1.withdraw(100)  # Withdraw from checking account (with fee)
    print(f"Checking balance after withdraw (with fee): ${checking1.get_balance()}")
    
    # Magic methods demonstration
    print("\n4. Magic Methods")
    accounts = bank1.get_all_accounts()
    print(f"Accounts: {accounts}")  # Uses __repr__
    print(f"Sorted accounts by balance: {sorted(accounts)}")  # Uses __lt__
    print(f"Account comparison: {savings1 == savings2}")  # Uses __eq__
    print(f"Bank length (customers): {len(bank1)}")  # Uses __len__
    
    # Encapsulation - accessing private/protected members
    print("\n5. Encapsulation")
    print(f"Public getter - Balance: ${savings1.get_balance()}")
    print(f"Direct access to protected: {savings1._balance}")
    # print(savings1.__customer_id)  # This would cause AttributeError
    
    # Inheritance and specific methods
    print("\n6. Inheritance - Savings Account Features")
    interest_earned = savings1.apply_interest()  # Savings account specific method
    print(f"Interest applied: ${interest_earned:.2f}")
    print(f"New balance: ${savings1.get_balance()}")
    
    # Transaction history
    print("\n7. Transaction History")
    for transaction in savings1.get_transaction_history():
        print(f"  {transaction['type']}: ${transaction['amount']:.2f}")
    
    # Customer summary
    print("\n8. Composition - Customer Summary")
    print(f"{customer1}")  # Uses __str__
    print(f"Total balance across all accounts: ${customer1.get_total_balance():.2f}")
    
    # Bank summary
    print(f"\n9. Bank Summary")
    print(bank1)  # Uses __str__
    
    # Save data to CSV
    print("\n10. Data Persistence with Pandas")
    bank1.save_to_csv()  # Save all data to CSV files
    
    # Print demo completion message
    print("\n" + "=" * 60)
    print("DEMO COMPLETE - ALL OOP CONCEPTS DEMONSTRATED")
    print("=" * 60)


# Main execution block
if __name__ == "__main__":
    # Run demo when script is executed directly
    demo_bank_system()

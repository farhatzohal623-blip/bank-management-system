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

import pandas as pd
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional


class Account(ABC):
    """Abstract base class for all account types - demonstrates Abstraction"""
    
    def __init__(self, account_number: str, customer_id: str, initial_balance: float = 0.0):
        self._account_number = account_number  # Encapsulation: protected attribute
        self.__customer_id = customer_id      # Encapsulation: private attribute
        self._balance = initial_balance
        self._created_at = datetime.now()
        self._transaction_history = []
    
    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        """Abstract method - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_account_type(self) -> str:
        """Abstract method - must be implemented by subclasses"""
        pass
    
    def deposit(self, amount: float) -> bool:
        """Common deposit method for all account types"""
        if amount <= 0:
            return False
        
        self._balance += amount
        self._add_transaction("DEPOSIT", amount)
        return True
    
    def get_balance(self) -> float:
        """Getter method - encapsulation"""
        return self._balance
    
    def get_account_number(self) -> str:
        """Getter method - encapsulation"""
        return self._account_number
    
    def get_customer_id(self) -> str:
        """Getter method - encapsulation"""
        return self.__customer_id
    
    def _add_transaction(self, transaction_type: str, amount: float):
        """Protected method for internal use"""
        transaction = {
            'type': transaction_type,
            'amount': amount,
            'balance_after': self._balance,
            'timestamp': datetime.now().isoformat()
        }
        self._transaction_history.append(transaction)
    
    def get_transaction_history(self) -> List[Dict]:
        """Getter method for transaction history"""
        return self._transaction_history.copy()
    
    # Magic Methods
    def __str__(self) -> str:
        """String representation of account"""
        return f"{self.get_account_type()} Account #{self._account_number} - Balance: ${self._balance:.2f}"
    
    def __repr__(self) -> str:
        """Official string representation"""
        return f"{self.__class__.__name__}(account_number='{self._account_number}', balance={self._balance})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison based on account number"""
        if isinstance(other, Account):
            return self._account_number == other._account_number
        return False
    
    def __lt__(self, other) -> bool:
        """Less than comparison based on balance"""
        if isinstance(other, Account):
            return self._balance < other._balance
        return False


class SavingsAccount(Account):
    """Savings Account with interest rate - demonstrates Inheritance"""
    
    INTEREST_RATE = 0.02  # Class attribute
    
    def __init__(self, account_number: str, customer_id: str, initial_balance: float = 0.0):
        super().__init__(account_number, customer_id, initial_balance)
        self._withdrawal_limit = 6  # Monthly withdrawal limit
    
    def withdraw(self, amount: float) -> bool:
        """Polymorphic method with savings account specific logic"""
        if amount <= 0 or amount > self._balance:
            return False
        
        # Check withdrawal limit
        monthly_withdrawals = self._count_monthly_withdrawals()
        if monthly_withdrawals >= self._withdrawal_limit:
            print(f"Withdrawal limit of {self._withdrawal_limit} per month reached")
            return False
        
        self._balance -= amount
        self._add_transaction("WITHDRAW", amount)
        return True
    
    def apply_interest(self) -> float:
        """Apply monthly interest - savings account specific feature"""
        interest = self._balance * self.INTEREST_RATE
        self._balance += interest
        self._add_transaction("INTEREST", interest)
        return interest
    
    def get_account_type(self) -> str:
        """Polymorphic method"""
        return "Savings"
    
    def _count_monthly_withdrawals(self) -> int:
        """Count withdrawals in current month"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        count = 0
        for transaction in self._transaction_history:
            if transaction['type'] == 'WITHDRAW':
                trans_date = datetime.fromisoformat(transaction['timestamp'])
                if trans_date.month == current_month and trans_date.year == current_year:
                    count += 1
        return count


class CheckingAccount(Account):
    """Checking Account with overdraft protection - demonstrates Inheritance"""
    
    OVERDRAFT_LIMIT = 500.0  # Class attribute
    TRANSACTION_FEE = 1.0     # Class attribute
    
    def __init__(self, account_number: str, customer_id: str, initial_balance: float = 0.0):
        super().__init__(account_number, customer_id, initial_balance)
        self._has_overdraft_protection = True
    
    def withdraw(self, amount: float) -> bool:
        """Polymorphic method with checking account specific logic"""
        if amount <= 0:
            return False
        
        total_withdrawal = amount + self.TRANSACTION_FEE
        
        if self._has_overdraft_protection:
            # Allow overdraft up to limit
            if self._balance - total_withdrawal < -self.OVERDRAFT_LIMIT:
                return False
        else:
            # No overdraft protection
            if total_withdrawal > self._balance:
                return False
        
        self._balance -= total_withdrawal
        self._add_transaction("WITHDRAW", amount)
        self._add_transaction("FEE", self.TRANSACTION_FEE)
        return True
    
    def get_account_type(self) -> str:
        """Polymorphic method"""
        return "Checking"
    
    def toggle_overdraft_protection(self):
        """Toggle overdraft protection"""
        self._has_overdraft_protection = not self._has_overdraft_protection


class Customer:
    """Customer class - demonstrates Composition relationship with Bank"""
    
    def __init__(self, customer_id: str, name: str, email: str, phone: str):
        self._customer_id = customer_id
        self._name = name
        self._email = email
        self._phone = phone
        self._accounts = []  # Composition: Customer has Accounts
        self._created_at = datetime.now()
    
    def add_account(self, account: Account):
        """Add account to customer - demonstrates Composition"""
        if account.get_customer_id() == self._customer_id:
            self._accounts.append(account)
            return True
        return False
    
    def remove_account(self, account_number: str) -> bool:
        """Remove account from customer"""
        for i, account in enumerate(self._accounts):
            if account.get_account_number() == account_number:
                del self._accounts[i]
                return True
        return False
    
    def get_accounts(self) -> List[Account]:
        """Get all customer accounts"""
        return self._accounts.copy()
    
    def get_total_balance(self) -> float:
        """Calculate total balance across all accounts"""
        return sum(account.get_balance() for account in self._accounts)
    
    # Getters with encapsulation
    def get_customer_id(self) -> str:
        return self._customer_id
    
    def get_name(self) -> str:
        return self._name
    
    def get_email(self) -> str:
        return self._email
    
    def get_phone(self) -> str:
        return self._phone
    
    # Magic Methods
    def __str__(self) -> str:
        return f"Customer: {self._name} (ID: {self._customer_id}) - Accounts: {len(self._accounts)}"
    
    def __repr__(self) -> str:
        return f"Customer(id='{self._customer_id}', name='{self._name}')"


class Bank:
    """Bank class with Singleton pattern and Factory methods"""
    
    _instance = None  # Singleton instance
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize bank only once"""
        if self._initialized:
            return
        
        self._name = "Central Bank"
        self._customers = {}  # Composition: Bank has Customers
        self._accounts = {}   # Composition: Bank has Accounts
        self._data_file = "bank_data.csv"
        self._initialized = True
    
    # Factory Methods
    @classmethod
    def create_savings_account(cls, customer_id: str, initial_balance: float = 0.0) -> SavingsAccount:
        """Factory method for creating savings accounts"""
        account_number = str(uuid.uuid4())[:8]
        return SavingsAccount(account_number, customer_id, initial_balance)
    
    @classmethod
    def create_checking_account(cls, customer_id: str, initial_balance: float = 0.0) -> CheckingAccount:
        """Factory method for creating checking accounts"""
        account_number = str(uuid.uuid4())[:8]
        return CheckingAccount(account_number, customer_id, initial_balance)
    
    def add_customer(self, name: str, email: str, phone: str) -> Customer:
        """Add new customer to bank"""
        customer_id = str(uuid.uuid4())[:8]
        customer = Customer(customer_id, name, email, phone)
        self._customers[customer_id] = customer
        return customer
    
    def add_account(self, account: Account, customer_id: str) -> bool:
        """Add account to bank and customer"""
        if customer_id in self._customers:
            customer = self._customers[customer_id]
            if customer.add_account(account):
                self._accounts[account.get_account_number()] = account
                return True
        return False
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        return self._customers.get(customer_id)
    
    def get_account(self, account_number: str) -> Optional[Account]:
        """Get account by number"""
        return self._accounts.get(account_number)
    
    def get_all_customers(self) -> List[Customer]:
        """Get all customers"""
        return list(self._customers.values())
    
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        return list(self._accounts.values())
    
    def get_total_deposits(self) -> float:
        """Get total deposits across all accounts"""
        return sum(account.get_balance() for account in self._accounts.values())
    
    # Data persistence methods
    def save_to_csv(self) -> bool:
        """Save bank data to CSV using pandas"""
        try:
            customers_data = []
            accounts_data = []
            transactions_data = []
            
            # Export customers
            for customer in self.get_all_customers():
                customers_data.append({
                    'customer_id': customer.get_customer_id(),
                    'name': customer.get_name(),
                    'email': customer.get_email(),
                    'phone': customer.get_phone(),
                    'created_at': customer._created_at.isoformat()
                })
            
            # Export accounts
            for account in self.get_all_accounts():
                accounts_data.append({
                    'account_number': account.get_account_number(),
                    'customer_id': account.get_customer_id(),
                    'account_type': account.get_account_type(),
                    'balance': account.get_balance(),
                    'created_at': account._created_at.isoformat()
                })
                
                # Export transactions
                for transaction in account.get_transaction_history():
                    transactions_data.append({
                        'account_number': account.get_account_number(),
                        'transaction_type': transaction['type'],
                        'amount': transaction['amount'],
                        'balance_after': transaction['balance_after'],
                        'timestamp': transaction['timestamp']
                    })
            
            # Save to CSV files
            pd.DataFrame(customers_data).to_csv('customers.csv', index=False)
            pd.DataFrame(accounts_data).to_csv('accounts.csv', index=False)
            pd.DataFrame(transactions_data).to_csv('transactions.csv', index=False)
            
            print("Bank data saved successfully to CSV files")
            return True
            
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_from_csv(self) -> bool:
        """Load bank data from CSV using pandas"""
        try:
            # Load customers
            customers_df = pd.read_csv('customers.csv')
            for _, row in customers_df.iterrows():
                customer = Customer(
                    row['customer_id'],
                    row['name'],
                    row['email'],
                    row['phone']
                )
                self._customers[row['customer_id']] = customer
            
            # Load accounts
            accounts_df = pd.read_csv('accounts.csv')
            for _, row in accounts_df.iterrows():
                if row['account_type'] == 'Savings':
                    account = SavingsAccount(
                        row['account_number'],
                        row['customer_id'],
                        row['balance']
                    )
                else:  # Checking
                    account = CheckingAccount(
                        row['account_number'],
                        row['customer_id'],
                        row['balance']
                    )
                
                self._accounts[row['account_number']] = account
                
                # Add account to customer
                customer = self._customers.get(row['customer_id'])
                if customer:
                    customer.add_account(account)
            
            # Load transactions (simplified - would need more complex logic for full restoration)
            transactions_df = pd.read_csv('transactions.csv')
            print(f"Loaded {len(transactions_df)} transactions")
            
            print("Bank data loaded successfully from CSV files")
            return True
            
        except FileNotFoundError:
            print("No existing data files found - starting with empty bank")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    # Magic Methods
    def __str__(self) -> str:
        return f"{self._name} - Customers: {len(self._customers)}, Accounts: {len(self._accounts)}, Total Deposits: ${self.get_total_deposits():.2f}"
    
    def __len__(self) -> int:
        """Return number of customers"""
        return len(self._customers)


# Demo function to showcase all OOP concepts
def demo_bank_system():
    """Demonstrate all OOP concepts and bank functionality"""
    print("=" * 60)
    print("BANK SYSTEM DEMO - SHOWCASING OOP CONCEPTS")
    print("=" * 60)
    
    # Singleton pattern - same instance returned
    bank1 = Bank()
    bank2 = Bank()
    print(f"Singleton Pattern: bank1 is bank2 = {bank1 is bank2}")
    
    # Load existing data or start fresh
    bank1.load_from_csv()
    
    # Create customers
    print("\n1. Creating Customers (Objects & Classes)")
    customer1 = bank1.add_customer("John Doe", "john@email.com", "555-0101")
    customer2 = bank1.add_customer("Jane Smith", "jane@email.com", "555-0102")
    
    print(f"Created: {customer1}")
    print(f"Created: {customer2}")
    
    # Factory pattern - create different account types
    print("\n2. Factory Pattern - Creating Accounts")
    savings1 = Bank.create_savings_account(customer1.get_customer_id(), 1000.0)
    checking1 = Bank.create_checking_account(customer1.get_customer_id(), 500.0)
    savings2 = Bank.create_savings_account(customer2.get_customer_id(), 2000.0)
    
    # Add accounts to bank (Composition)
    bank1.add_account(savings1, customer1.get_customer_id())
    bank1.add_account(checking1, customer1.get_customer_id())
    bank1.add_account(savings2, customer2.get_customer_id())
    
    print(f"Created: {savings1}")
    print(f"Created: {checking1}")
    print(f"Created: {savings2}")
    
    # Polymorphism - different withdraw behavior
    print("\n3. Polymorphism - Different Account Behaviors")
    print(f"Savings balance before: ${savings1.get_balance()}")
    savings1.withdraw(100)
    print(f"Savings balance after withdraw: ${savings1.get_balance()}")
    
    print(f"Checking balance before: ${checking1.get_balance()}")
    checking1.withdraw(100)
    print(f"Checking balance after withdraw (with fee): ${checking1.get_balance()}")
    
    # Magic methods demonstration
    print("\n4. Magic Methods")
    accounts = bank1.get_all_accounts()
    print(f"Accounts: {accounts}")
    print(f"Sorted accounts by balance: {sorted(accounts)}")
    print(f"Account comparison: {savings1 == savings2}")
    print(f"Bank length (customers): {len(bank1)}")
    
    # Encapsulation - accessing private/protected members
    print("\n5. Encapsulation")
    print(f"Public getter - Balance: ${savings1.get_balance()}")
    print(f"Direct access to protected: {savings1._balance}")
    # print(savings1.__customer_id)  # This would cause AttributeError
    
    # Inheritance and specific methods
    print("\n6. Inheritance - Savings Account Features")
    interest_earned = savings1.apply_interest()
    print(f"Interest applied: ${interest_earned:.2f}")
    print(f"New balance: ${savings1.get_balance()}")
    
    # Transaction history
    print("\n7. Transaction History")
    for transaction in savings1.get_transaction_history():
        print(f"  {transaction['type']}: ${transaction['amount']:.2f}")
    
    # Customer summary
    print("\n8. Composition - Customer Summary")
    print(f"{customer1}")
    print(f"Total balance across all accounts: ${customer1.get_total_balance():.2f}")
    
    # Bank summary
    print(f"\n9. Bank Summary")
    print(bank1)
    
    # Save data to CSV
    print("\n10. Data Persistence with Pandas")
    bank1.save_to_csv()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE - ALL OOP CONCEPTS DEMONSTRATED")
    print("=" * 60)


if __name__ == "__main__":
    demo_bank_system()

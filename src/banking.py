import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class InsufficientFundsError(Exception):
    """Raised when an account has insufficient funds for a withdrawal."""

    def __init__(self, message: str, amount: float) -> None:
        self.amount = amount
        super().__init__(message)


class BankAccount:
    # Represents a bank account and its banking operations.

    # Creates a new bank account with account details and starting balance.
    def __init__(
        self,
        account_number: str,
        currency: str = "USD",
        _account_type: str = "checking",
        initial_balance: float = 0.0,
    ) -> None:

        self.account_number = account_number
        self.currency = currency
        self._account_type = _account_type
        self.balance = initial_balance

    # Returns the account number.
    @property
    def account_number(self) -> str:
        return self._account_number

    # Updates the account number.
    @account_number.setter
    def account_number(self, value: str) -> None:
        self._account_number = value

    # Returns the account currency.
    @property
    def currency(self) -> str:
        return self._currency

    # Updates the account currency.
    @currency.setter
    def currency(self, value: str) -> None:
        self._currency = value

    # Returns the account type.
    @property
    def account_type(self) -> str:
        return self._account_type

    # Returns the current account balance.
    @property
    def balance(self) -> float:
        return self.__balance

    # Validates and updates the account balance.
    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            logging.error("Balance cannot be negative: %.2f", value)
            raise ValueError("Balance cannot be negative.")

        self.__balance = value

    # Adds money to the account balance.
    def deposit(self, amount: float) -> None:
        if amount < 0:
            logging.error("Deposit amount cannot be negative: %.2f", amount)
            raise ValueError("Deposit amount cannot be negative.")

        self.__balance += amount
        logging.info(
            "Deposit completed. Updated balance: %.2f",
            self.__balance,
        )

    # Removes money from the account balance if sufficient funds exist.
    def withdraw(self, amount: float) -> None:
        if amount < 0:
            logging.error("Withdrawal amount cannot be negative: %.2f", amount)
            raise ValueError("Withdrawal amount cannot be negative.")

        minimum_balance = 100.0 if self._account_type == "savings" else 0.0

        if self.__balance - amount < minimum_balance:
            message = (
                f"Insufficient funds. The {self._account_type} account "
                f"must retain a minimum balance of {minimum_balance:.2f} "
                f"{self.currency}."
            )
            logging.error("%s Attempted withdrawal: %.2f", message, amount)
            raise InsufficientFundsError(message, amount)

        self.__balance -= amount
        logging.info(
            "Withdrawal completed. Updated balance: %.2f",
            self.__balance,
        )

    # Converts and prints the account balance in a target currency.
    def convert_currency(
        self,
        target_currency: str,
        exchange_rate: float,
    ) -> None:
        if exchange_rate <= 0:
            logging.error(
                "Exchange rate must be greater than zero: %.2f",
                exchange_rate,
            )
            raise ValueError("Exchange rate must be greater than zero.")

        converted_balance = self.__balance * exchange_rate

        print(f"Converted balance: {converted_balance:.2f} {target_currency}")

    # Creates a savings account with a minimum initial balance of 100.
    @classmethod
    def create_savings(
        cls,
        account_number: str,
        currency: str = "USD",
        initial_balance: float = 100.0,
    ) -> BankAccount:
        if initial_balance < 100:
            logging.error(
                "Savings account initial balance cannot be below 100: %.2f",
                initial_balance,
            )
            raise ValueError("Savings account initial balance cannot be below 100.")

        return cls(
            account_number=account_number,
            currency=currency,
            _account_type="savings",
            initial_balance=initial_balance,
        )

    # Returns True only if the account number contains exactly 10 digits.
    @staticmethod
    def is_valid_account_number(account_number: str) -> bool:
        return len(account_number) == 10 and account_number.isdigit()


# Represents a customer who owns one or more bank accounts.
class Customer:
    # Tracks the total number of customers created.
    user_count = 0

    # Creates a customer and validates they are at least 18 years old.
    def __init__(
        self,
        name: str,
        birth_date: str,
    ) -> None:

        birth = datetime.strptime(
            birth_date,
            "%Y-%m-%d",
        )

        today = datetime.today()

        age = (
            today.year
            - birth.year
            - ((today.month, today.day) < (birth.month, birth.day))
        )

        if age < 18:
            logging.error("Customer must be at least 18 years old.")
            raise ValueError("Customer must be at least 18 years old.")

        self.name = name
        self.birth_date = birth_date

        Customer.user_count += 1

        self._user_id = Customer.user_count

        self.__accounts = []

    # Returns the customer's unique user ID.
    @property
    def user_id(self) -> int:
        return self._user_id

    # Returns the customer's bank accounts.
    @property
    def accounts(self) -> list[BankAccount]:
        return self.__accounts

    # Adds a valid bank account to the customer's account collection.
    def add_account(
        self,
        account: BankAccount,
    ) -> None:
        if BankAccount.is_valid_account_number(account.account_number):
            self.__accounts.append(account)
            logging.info(
                "Account %s added successfully.",
                account.account_number,
            )
        else:
            logging.error(
                "Invalid account number: %s",
                account.account_number,
            )

    # Calculates and returns the total balance across all accounts.
    def get_total_balance(self) -> float:
        total_balance = 0.0

        for account in self.__accounts:
            total_balance += account.balance

        return total_balance

    # Transfers funds between two customer accounts.
    def transfer(
        self,
        source_account: BankAccount,
        target_account: BankAccount,
        amount: float,
    ) -> None:
        try:
            source_account.withdraw(amount)
            target_account.deposit(amount)

            logging.info(
                "Transfer of %.2f completed.",
                amount,
            )

        except (ValueError, InsufficientFundsError) as error:
            logging.error(
                "Transfer failed: %s",
                error,
            )


# Stores all customers created during program execution.
customers: list[Customer] = []


# Finds and returns a customer using their user ID.
def find_customer(user_id: int) -> Customer | None:
    for customer in customers:
        if customer.user_id == user_id:
            return customer

    return None


# Finds an account belonging to a customer using its account number.
def find_account(
    customer: Customer,
    account_number: str,
) -> BankAccount | None:
    for account in customer.accounts:
        if account.account_number == account_number:
            return account

    return None


# Displays the banking menu and processes user selections.
def menu() -> None:
    while True:
        print("\nSecure Banking System")
        print("1. Add Customer")
        print("2. Add Bank Account")
        print("3. Deposit")
        print("4. Withdraw")
        print("5. Transfer")
        print("6. Convert Currency")
        print("7. View Total Balance")
        print("8. Exit")

        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                add_customer_menu()

            elif choice == "2":
                add_account_menu()

            elif choice == "3":
                deposit_menu()

            elif choice == "4":
                withdraw_menu()

            elif choice == "5":
                transfer_menu()

            elif choice == "6":
                convert_currency_menu()

            elif choice == "7":
                total_balance_menu()

            elif choice == "8":
                print("Exiting the banking system.")
                break

            else:
                print("Invalid option. Select a number from 1 through 8.")

        except ValueError as error:
            logging.error("Invalid value: %s", error)
            print(f"Error: {error}")

        except InsufficientFundsError as error:
            logging.error(
                "Insufficient funds: %s. Attempted amount: %.2f",
                error,
                error.amount,
            )
            print(f"Error: {error}")


# Collects input and adds a new customer.
def add_customer_menu() -> None:
    name = input("Customer name: ").strip()
    birth_date = input("Birth date (YYYY-MM-DD): ").strip()

    customer = Customer(
        name=name,
        birth_date=birth_date,
    )

    customers.append(customer)

    print(f"Customer added successfully. User ID: {customer.user_id}")


# Collects input and adds a bank account to a customer.
def add_account_menu() -> None:
    user_id = int(input("Customer user ID: "))
    customer = find_customer(user_id)

    if customer is None:
        logging.error("Customer ID %s was not found.", user_id)
        print("Customer not found.")
        return

    account_number = input("Account number: ").strip()

    if not BankAccount.is_valid_account_number(account_number):
        logging.error(
            "Invalid account number: %s",
            account_number,
        )
        print("The account number must contain exactly 10 digits.")
        return

    currency = input("Currency code, or press Enter for USD: ").strip().upper()

    if not currency:
        currency = "USD"

    account_type = input("Account type (checking/savings): ").strip().lower()

    initial_balance = float(input("Initial balance: "))

    if account_type == "savings":
        account = BankAccount.create_savings(
            account_number=account_number,
            currency=currency,
            initial_balance=initial_balance,
        )

    elif account_type == "checking":
        account = BankAccount(
            account_number=account_number,
            currency=currency,
            _account_type="checking",
            initial_balance=initial_balance,
        )

    else:
        raise ValueError("Account type must be checking or savings.")

    customer.add_account(account)
    print("Bank account added successfully.")


# Collects input and deposits money into an account.
def deposit_menu() -> None:
    customer, account = select_customer_account()

    if customer is None or account is None:
        return

    amount = float(input("Deposit amount: "))
    account.deposit(amount)

    print(f"Deposit completed. Balance: {account.balance:.2f}")


# Collects input and withdraws money from an account.
def withdraw_menu() -> None:
    customer, account = select_customer_account()

    if customer is None or account is None:
        return

    amount = float(input("Withdrawal amount: "))
    account.withdraw(amount)

    print(f"Withdrawal completed. Balance: {account.balance:.2f}")


# Collects input and transfers funds between two customer accounts.
def transfer_menu() -> None:
    user_id = int(input("Customer user ID: "))
    customer = find_customer(user_id)

    if customer is None:
        logging.error("Customer ID %s was not found.", user_id)
        print("Customer not found.")
        return

    source_number = input("Source account number: ").strip()
    target_number = input("Target account number: ").strip()

    source_account = find_account(customer, source_number)
    target_account = find_account(customer, target_number)

    if source_account is None:
        logging.error(
            "Source account %s was not found.",
            source_number,
        )
        print("Source account not found.")
        return

    if target_account is None:
        logging.error(
            "Target account %s was not found.",
            target_number,
        )
        print("Target account not found.")
        return

    if source_account is target_account:
        logging.error("Source and target accounts cannot be the same.")
        print("Source and target accounts must be different.")
        return

    amount = float(input("Transfer amount: "))

    customer.transfer(
        source_account=source_account,
        target_account=target_account,
        amount=amount,
    )

    print("Transfer request processed.")


# Collects input and displays the balance in another currency.
def convert_currency_menu() -> None:
    customer, account = select_customer_account()

    if customer is None or account is None:
        return

    target_currency = input("Target currency code: ").strip().upper()

    exchange_rate = float(input("Exchange rate: "))

    account.convert_currency(
        target_currency=target_currency,
        exchange_rate=exchange_rate,
    )


# Displays the combined balance of all customer accounts.
def total_balance_menu() -> None:
    user_id = int(input("Customer user ID: "))
    customer = find_customer(user_id)

    if customer is None:
        logging.error("Customer ID %s was not found.", user_id)
        print("Customer not found.")
        return

    total_balance = customer.get_total_balance()

    print(f"Total account balance: {total_balance:.2f}")


# Finds a customer and one of their accounts from user input.
def select_customer_account() -> tuple[Customer | None, BankAccount | None]:
    user_id = int(input("Customer user ID: "))
    customer = find_customer(user_id)

    if customer is None:
        logging.error("Customer ID %s was not found.", user_id)
        print("Customer not found.")
        return None, None

    account_number = input("Account number: ").strip()
    account = find_account(customer, account_number)

    if account is None:
        logging.error(
            "Account %s was not found.",
            account_number,
        )
        print("Account not found.")
        return customer, None

    return customer, account


# Starts the banking application when this file is run directly.
if __name__ == "__main__":
    menu()

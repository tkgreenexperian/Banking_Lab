from datetime import datetime, timedelta

import pytest

from src.banking import (
    BankAccount,
    Customer,
    InsufficientFundsError,
)


def create_adult_birth_date() -> str:
    today = datetime.today()

    return today.replace(year=today.year - 25).strftime("%Y-%m-%d")


def test_create_checking_account() -> None:
    account = BankAccount(
        account_number="1234567890",
        initial_balance=500.0,
    )

    assert account.account_number == "1234567890"
    assert account.currency == "USD"
    assert account.account_type == "checking"
    assert account.balance == 500.0


def test_negative_initial_balance_raises_error() -> None:
    with pytest.raises(ValueError):
        BankAccount(
            account_number="1234567890",
            initial_balance=-100.0,
        )


def test_deposit_increases_balance() -> None:
    account = BankAccount(
        account_number="1234567890",
        initial_balance=100.0,
    )

    account.deposit(50.0)

    assert account.balance == 150.0


def test_negative_deposit_raises_error() -> None:
    account = BankAccount(
        account_number="1234567890",
        initial_balance=100.0,
    )

    with pytest.raises(ValueError):
        account.deposit(-50.0)


def test_withdraw_decreases_balance() -> None:
    account = BankAccount(
        account_number="1234567890",
        initial_balance=200.0,
    )

    account.withdraw(50.0)

    assert account.balance == 150.0


def test_withdraw_with_insufficient_funds() -> None:
    account = BankAccount(
        account_number="1234567890",
        initial_balance=100.0,
    )

    with pytest.raises(InsufficientFundsError):
        account.withdraw(150.0)


def test_savings_account_requires_minimum_opening_balance() -> None:
    with pytest.raises(ValueError):
        BankAccount.create_savings(
            account_number="1234567890",
            initial_balance=50.0,
        )


def test_savings_account_cannot_fall_below_minimum() -> None:
    account = BankAccount.create_savings(
        account_number="1234567890",
        initial_balance=200.0,
    )

    with pytest.raises(InsufficientFundsError):
        account.withdraw(150.0)


def test_create_savings_account() -> None:
    account = BankAccount.create_savings(
        account_number="1234567890",
        initial_balance=500.0,
    )

    assert account.account_type == "savings"
    assert account.balance == 500.0


@pytest.mark.parametrize(
    ("account_number", "expected"),
    [
        ("1234567890", True),
        ("12345", False),
        ("12345678901", False),
        ("123456789A", False),
        ("abcdefghij", False),
    ],
)
def test_account_number_validation(
    account_number: str,
    expected: bool,
) -> None:
    assert BankAccount.is_valid_account_number(account_number) is expected


def test_invalid_exchange_rate_raises_error() -> None:
    account = BankAccount(
        account_number="1234567890",
        initial_balance=500.0,
    )

    with pytest.raises(ValueError):
        account.convert_currency("EUR", 0)


def test_adult_customer_creation() -> None:
    customer = Customer(
        name="Test Customer",
        birth_date=create_adult_birth_date(),
    )

    assert customer.name == "Test Customer"
    assert customer.user_id > 0
    assert customer.accounts == []


def test_underage_customer_raises_error() -> None:
    underage_birth_date = (datetime.today() - timedelta(days=365 * 10)).strftime(
        "%Y-%m-%d"
    )

    with pytest.raises(ValueError):
        Customer(
            name="Underage Customer",
            birth_date=underage_birth_date,
        )


def test_add_valid_account() -> None:
    customer = Customer(
        name="Test Customer",
        birth_date=create_adult_birth_date(),
    )

    account = BankAccount(
        account_number="1234567890",
        initial_balance=100.0,
    )

    customer.add_account(account)

    assert account in customer.accounts


def test_invalid_account_is_not_added() -> None:
    customer = Customer(
        name="Test Customer",
        birth_date=create_adult_birth_date(),
    )

    account = BankAccount(
        account_number="12345",
        initial_balance=100.0,
    )

    customer.add_account(account)

    assert account not in customer.accounts


def test_get_total_balance() -> None:
    customer = Customer(
        name="Test Customer",
        birth_date=create_adult_birth_date(),
    )

    first_account = BankAccount(
        account_number="1234567890",
        initial_balance=300.0,
    )

    second_account = BankAccount(
        account_number="0987654321",
        initial_balance=200.0,
    )

    customer.add_account(first_account)
    customer.add_account(second_account)

    assert customer.get_total_balance() == 500.0


def test_transfer_between_accounts() -> None:
    customer = Customer(
        name="Test Customer",
        birth_date=create_adult_birth_date(),
    )

    source_account = BankAccount(
        account_number="1234567890",
        initial_balance=500.0,
    )

    target_account = BankAccount(
        account_number="0987654321",
        initial_balance=100.0,
    )

    customer.add_account(source_account)
    customer.add_account(target_account)

    customer.transfer(
        source_account=source_account,
        target_account=target_account,
        amount=200.0,
    )

    assert source_account.balance == 300.0
    assert target_account.balance == 300.0

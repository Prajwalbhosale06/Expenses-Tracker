
import json
import os
from datetime import datetime, date

FILE_NAME = "expenses.json"

expenses = []
monthly_limit = 0.0



def load_data():
    global expenses, monthly_limit

    if not os.path.exists(FILE_NAME):
        expenses = []
        monthly_limit = 0.0
        return

    try:
        with open(FILE_NAME, "r") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Invalid file structure.")

        records = data.get("expenses", [])
        limit = data.get("monthly_limit", 0)

        if not isinstance(records, list):
            raise ValueError("Expenses must be stored as a list.")

        if not isinstance(limit, (int, float)) or isinstance(limit, bool):
            raise ValueError("Invalid monthly limit.")

       
        required = {"id", "category", "amount", "date", "description"}
        seen_ids = set()

        for item in records:
            if not isinstance(item, dict) or not required.issubset(item):
                raise ValueError("Malformed expense record.")

            expense_id = item["id"]

            if not isinstance(expense_id, str) or not expense_id.strip():
                raise ValueError("Invalid expense ID.")

            if expense_id in seen_ids:
                raise ValueError("Duplicate expense ID in file.")

            if not isinstance(item["category"], str) or not item["category"].strip():
                raise ValueError("Invalid category.")

            if not isinstance(item["description"], str):
                raise ValueError("Invalid description.")

            amount = item["amount"]
            if (
                not isinstance(amount, (int, float))
                or isinstance(amount, bool)
                or not 0 < amount < float("inf")
            ):
                raise ValueError("Invalid expense amount.")

            datetime.strptime(item["date"], "%Y-%m-%d")
            seen_ids.add(expense_id)

        if limit < 0:
            raise ValueError("Monthly limit cannot be negative.")

        expenses = records
        monthly_limit = float(limit)

    except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
        print("Error loading data:", error)
        print("Starting with empty data. The original file is unchanged.")
        expenses = []
        monthly_limit = 0.0


def save_data():
    data = {
        "expenses": expenses,
        "monthly_limit": monthly_limit
    }

    temp_file = FILE_NAME + ".tmp"

    try:
        with open(temp_file, "w") as file:
            json.dump(data, file, indent=4)

        os.replace(temp_file, FILE_NAME)

    except (OSError, TypeError, ValueError) as error:
        print("Error saving data:", error)
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except OSError:
            pass



def get_amount(message):
    while True:
        try:
            amount = float(input(message))

            if amount <= 0 or amount == float("inf") or amount != amount:
                print("Amount must be a positive number.")
                continue

            return round(amount, 2)

        except ValueError:
            print("Please enter a valid number.")


def get_date(message):
    while True:
        date_text = input(message).strip()

        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return date_text
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD (example: 2026-10-12).")



def check_monthly_limit(month):
    if monthly_limit <= 0:
        return

    total = sum(
        item["amount"]
        for item in expenses
        if item["date"][:7] == month
    )

    print(f"Spending in {month}: Rs. {total:.2f}")
    print(f"Monthly limit: Rs. {monthly_limit:.2f}")

    if total > monthly_limit:
        print("WARNING: Monthly spending limit exceeded!")
    elif total == monthly_limit:
        print("You have reached your monthly spending limit.")
    else:
        print(f"Remaining budget: Rs. {monthly_limit - total:.2f}")



def add_expense():
    expense_id = input("Enter expense ID: ").strip()

    if not expense_id:
        print("Expense ID cannot be empty.")
        return

    if any(item["id"] == expense_id for item in expenses):
        print("This expense ID already exists.")
        return

    category = input("Enter category: ").strip()

    if not category:
        print("Category cannot be empty.")
        return

    amount = get_amount("Enter amount (Rs.): ")
    expense_date = get_date("Enter date (YYYY-MM-DD): ")
    description = input("Enter description: ").strip()

    expense = {
        "id": expense_id,
        "category": category,
        "amount": amount,
        "date": expense_date,
        "description": description
    }

    expenses.append(expense)
    save_data()

    print("Expense added successfully!")
    check_monthly_limit(expense_date[:7])



def view_expenses(records=None):
    if records is None:
        records = expenses

    if not records:
        print("No expenses found.")
        return

    print("\n" + "-" * 85)
    print(f"{'ID':<12}{'Category':<18}{'Amount':>12}  {'Date':<12}Description")
    print("-" * 85)

    for item in records:
        print(
            f"{item['id']:<12}"
            f"{item['category']:<18}"
            f"{item['amount']:>12.2f}  "
            f"{item['date']:<12}"
            f"{item['description']}"
        )

    print("-" * 85)



def search_expenses():
    category = input("Enter category to search: ").strip().casefold()

    if not category:
        print("Category cannot be empty.")
        return

    results = [
        item for item in expenses
        if item["category"].casefold() == category
    ]

    if results:
        view_expenses(results)
    else:
        print("No expenses found in this category.")


def calculate_total(records=None):
    if records is None:
        records = expenses

    return sum(item["amount"] for item in records)


def show_total():
    print(f"Total amount spent: Rs. {calculate_total():.2f}")



def category_analysis():
    if not expenses:
        print("No expenses available for analysis.")
        return

    totals = {}

    for item in expenses:
        category = item["category"]
        totals[category] = totals.get(category, 0) + item["amount"]

    print("\nCategory-wise Spending")
    print("-" * 35)

    for category, total in sorted(totals.items()):
        print(f"{category:<20} Rs. {total:.2f}")

    print("-" * 35)
    print(f"{'Grand Total':<20} Rs. {calculate_total():.2f}")



def highest_expense():
    if not expenses:
        print("No expenses available.")
        return

    highest = max(expenses, key=lambda item: item["amount"])

    print("\nHighest Expense")
    print(f"ID: {highest['id']}")
    print(f"Category: {highest['category']}")
    print(f"Amount: Rs. {highest['amount']:.2f}")
    print(f"Date: {highest['date']}")
    print(f"Description: {highest['description']}")



def filter_by_date():
    print("Enter dates in YYYY-MM-DD format.")
    start_date = get_date("Start date: ")
    end_date = get_date("End date: ")

    if start_date > end_date:
        print("Start date cannot be after end date.")
        return

    results = [
        item for item in expenses
        if start_date <= item["date"] <= end_date
    ]

    view_expenses(results)

    if results:
        print(f"Total for this period: Rs. {calculate_total(results):.2f}")



def top_three_expenses():
    if not expenses:
        print("No expenses available.")
        return

    largest = sorted(
        expenses,
        key=lambda item: item["amount"],
        reverse=True
    )[:3]

    print("\nThree Largest Expenses")
    view_expenses(largest)



def set_monthly_limit():
    global monthly_limit

    while True:
        try:
            limit = float(input("Enter monthly limit (Rs., 0 to disable): "))

            if limit < 0 or limit != limit or limit == float("inf"):
                print("Enter a valid non-negative amount.")
                continue

            monthly_limit = round(limit, 2)
            save_data()

            print(f"Monthly limit set to Rs. {monthly_limit:.2f}")

            current_month = date.today().strftime("%Y-%m")
            check_monthly_limit(current_month)
            return

        except ValueError:
            print("Please enter a valid number.")



def display_menu():
    print("\n========== PERSONAL EXPENSE TRACKER ==========")
    print("1.  Add Expense")
    print("2.  View All Expenses")
    print("3.  Search Expenses by Category")
    print("4.  Calculate Total Spending")
    print("5.  Category-wise Analysis")
    print("6.  View Highest Expense")
    print("7.  Filter Expenses by Date Range")
    print("8.  Display Three Largest Expenses")
    print("9.  Set Monthly Spending Limit")
    print("10. Exit")
    print("==============================================")



def main():
    load_data()

    print("Welcome to Personal Expense Tracker!")

    while True:
        display_menu()
        choice = input("Enter your choice (1-10): ").strip()

        try:
            if choice == "1":
                add_expense()
            elif choice == "2":
                view_expenses()
            elif choice == "3":
                search_expenses()
            elif choice == "4":
                show_total()
            elif choice == "5":
                category_analysis()
            elif choice == "6":
                highest_expense()
            elif choice == "7":
                filter_by_date()
            elif choice == "8":
                top_three_expenses()
            elif choice == "9":
                set_monthly_limit()
            elif choice == "10":
                save_data()
                print("Thank you for using Expense Tracker!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 10.")

        except (KeyboardInterrupt, EOFError):
            print("\nInput cancelled. Returning to the menu.")

        except Exception as error:
            print("An unexpected error occurred:", error)


if __name__ == "__main__":
    main()

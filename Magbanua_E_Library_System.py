import sqlite3
import datetime

# Connecting to SQLite database
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Create necessary tables if they do not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    member_id TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    date_registered TEXT,
                    password TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    category TEXT,
                    available INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS borrow_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT,
                    book_id INTEGER,
                    borrow_date TEXT,
                    return_date TEXT,
                    FOREIGN KEY(member_id) REFERENCES users(member_id),
                    FOREIGN KEY(book_id) REFERENCES books(book_id))''')

conn.commit()

def register():
    # Register a new user.
    print("\n--- Register a New Account ---")
    member_id = input("Enter Member ID: ")
    name = input("Enter Name: ")
    email = input("Enter Email Address: ")
    phone = input("Enter Phone Number: ")
    date_registered = datetime.date.today().isoformat()
    password = input("Enter Password: ")
    re_password = input("Re-Type Password: ")

    if password != re_password:
        print("Passwords do not match!")
        return

    try:
        cursor.execute(
            "INSERT INTO users (member_id, name, email, phone, date_registered, password) VALUES (?, ?, ?, ?, ?, ?)",
            (member_id, name, email, phone, date_registered, password))
        conn.commit()
        print("Account created successfully!")
    except sqlite3.IntegrityError:
        print("Member ID already exists. Try a different one.")

def login():
    # Log in an existing user.
    print("\n--- Login ---")
    member_id = input("Enter Member ID: ")
    password = input("Enter Password: ")

    cursor.execute("SELECT * FROM users WHERE member_id = ? AND password = ?", (member_id, password))
    user = cursor.fetchone()

    if user:
        print(f"Welcome, {user[1]}!")
        return member_id
    else:
        print("Invalid credentials.")
        return None

def admin_menu():
    # Display admin menu for managing books and users.
    while True:
        print("\n*********************************************************")
        print("|\t\t\t ADMIN MENU\t\t\t|")
        print("*********************************************************")
        print("=========================================================")
        print("|\t\t1. View All Books\t\t\t|")
        print("|\t\t2. Add a Book\t\t\t\t|")
        print("|\t\t3. Remove a Book\t\t\t|")
        print("|\t\t4. View All Users\t\t\t|")
        print("|\t\t5. Borrowing Summary\t\t\t|")
        print("|\t\t6. Exit Admin Menu\t\t\t|")
        print("=========================================================")
        choice = input("Choose an option: ")
        if choice == '1':
            view_books()
        elif choice == '2':
            add_book()
        elif choice == '3':
            remove_book()
        elif choice == '4':
            view_users()
        elif choice == '5':
            borrowing_summary()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Try again.")

def add_book():
    # Add a new book to the library.
    title = input("Enter Book Title: ")
    category = input("Enter Book Category: ")
    cursor.execute("INSERT INTO books (title, category, available) VALUES (?, ?, 1)", (title, category))
    conn.commit()
    print(f"Book '{title}' added successfully!")

def remove_book():
    # Remove a book from the library.
    book_id = input("Enter Book ID to Remove: ")
    cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    conn.commit()
    print("Book removed successfully!")

def view_users():
    # View all registered users.
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Phone: {user[3]}, Registered: {user[4]}")

def borrowing_summary():
    # Display borrowing statistics using SQL aggregate functions.
    print("\n--- Borrowing Summary ---")
    cursor.execute('''SELECT u.name, COUNT(br.record_id) AS books_borrowed
                      FROM users u
                      LEFT JOIN borrow_records br ON u.member_id = br.member_id
                      GROUP BY u.name
                      ORDER BY books_borrowed DESC''')
    results = cursor.fetchall()
    for row in results:
        print(f"Name: {row[0]}, Books Borrowed: {row[1]}")

def user_menu(member_id):
    # Display user menu for borrowing and returning books.
    while True:
        print("\n*********************************************************")
        print("|\t\t\t USER MENU\t\t\t|")
        print("*********************************************************")
        print("=========================================================")
        print("|\t\t1. View All Books\t\t\t|")
        print("|\t\t2. Search Book by Title\t\t\t|")
        print("|\t\t3. Borrow a Book\t\t\t|")
        print("|\t\t4. Return a Book\t\t\t|")
        print("|\t\t5. View Borrowing History\t\t|")
        print("|\t\t6. Exit User Menu\t\t\t|")
        print("=========================================================")
        choice = input("Choose an option: ")
        if choice == '1':
            view_books()
        elif choice == '2':
            search_book()
        elif choice == '3':
            borrow_book(member_id)
        elif choice == '4':
            return_book(member_id)
        elif choice == '5':
            view_borrowing_history(member_id)
        elif choice == '6':
            break
        else:
            print("Invalid choice. Try again.")

def view_books():
    # View all books in the library.
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    for book in books:
        status = "Available" if book[3] == 1 else "Borrowed"
        print(f"ID: {book[0]}, Title: {book[1]}, Category: {book[2]}, Status: {status}")

def search_book():
    # Search for a book by title.
    title = input("Enter Book Title to Search: ")
    cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + title + '%',))
    books = cursor.fetchall()
    if books:
        for book in books:
            status = "Available" if book[3] == 1 else "Borrowed"
            print(f"ID: {book[0]}, Title: {book[1]}, Category: {book[2]}, Status: {status}")
    else:
        print("No books found with that title.")

def borrow_book(member_id):
    # Borrow a book.
    book_id = input("Enter Book ID to Borrow: ")
    borrow_date = datetime.date.today().isoformat()
    cursor.execute("SELECT available FROM books WHERE book_id = ?", (book_id,))
    result = cursor.fetchone()

    if result and result[0] == 1:
        cursor.execute("INSERT INTO borrow_records (member_id, book_id, borrow_date) VALUES (?, ?, ?)",
                       (member_id, book_id, borrow_date))
        cursor.execute("UPDATE books SET available = 0 WHERE book_id = ?", (book_id,))
        conn.commit()
        print("Book borrowed successfully!")
    else:
        print("Book is currently unavailable.")

def return_book(member_id):
    # Return a borrowed book and calculate penalties.
    book_id = input("Enter Book ID to Return: ")
    return_date = datetime.date.today().isoformat()
    cursor.execute("SELECT borrow_date FROM borrow_records WHERE member_id = ? AND book_id = ? AND return_date IS NULL",
                   (member_id, book_id))
    borrow_date = cursor.fetchone()

    if borrow_date:
        days_borrowed = (datetime.date.fromisoformat(return_date) - datetime.date.fromisoformat(borrow_date[0])).days
        penalty = max(0, (days_borrowed - 14) * 10)
        cursor.execute("UPDATE borrow_records SET return_date = ? WHERE member_id = ? AND book_id = ?", 
                       (return_date, member_id, book_id))
        cursor.execute("UPDATE books SET available = 1 WHERE book_id = ?", (book_id,))
        conn.commit()
        print(f"Book returned successfully! Penalty: Php {penalty}")
    else:
        print("No borrowing record found.")

def view_borrowing_history(member_id):
    # View borrowing history for a user.
    print("\n--- Borrowing History ---")
    cursor.execute('''SELECT b.title, br.borrow_date, br.return_date
                      FROM borrow_records br
                      INNER JOIN books b ON br.book_id = b.book_id
                      WHERE br.member_id = ?''', (member_id,))
    records = cursor.fetchall()
    for record in records:
        status = "Returned" if record[2] else "Not Returned"
        print(f"Title: {record[0]}, Borrowed: {record[1]}, Returned: {record[2] or 'Pending'} ({status})")

def main():
    # Main menu.
    while True:
        print("\n*********************************************************")
        print("|\t\t WELCOME TO THE LIBRARY\t\t\t|")
        print("*********************************************************")
        print("=========================================================")
        print("|\t\t1. Register\t\t\t\t|")
        print("|\t\t2. Login\t\t\t\t|")
        print("|\t\t3. Admin Login\t\t\t\t|")
        print("|\t\t4. Exit\t\t\t\t\t|")
        print("=========================================================")
        choice = input("Choose an option: ")
        if choice == '1':
            register()
        elif choice == '2':
            member_id = login()
            if member_id:
                user_menu(member_id)
        elif choice == '3':
            admin_password = input("Enter Admin Password: ")
            if admin_password == "admin123":
                admin_menu()
            else:
                print("Invalid admin password.")
        elif choice == '4':
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()

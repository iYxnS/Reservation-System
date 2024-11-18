import pyodbc
import os
import re

# Database connection details
server = 'localhost'  
database = 'FinalProject'  
username = 'sa'  
password = 'sysadm' 

def connect_to_database():
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    return conn

def insert_customer(first_name, last_name, email, phone_number, cursor):
    insert_query = "INSERT INTO inn_customer (first_name, last_name, email, phone_number) VALUES (?, ?, ?, ?)"
    cursor.execute(insert_query, (first_name, last_name, email, phone_number))

    select_query = "SELECT @@IDENTITY"
    cursor.execute(select_query)
    result = cursor.fetchone()
    return result[0] if result else None


def insert_reservation(room_type, customer_id, accommodation_days, cost, cursor):
    query = "INSERT INTO inn_reservation (room_type, customer_id, accommodation_days, cost, checkout) VALUES (?, ?, ?, ?, 0)"
    cursor.execute(query, (room_type, customer_id, accommodation_days, cost))

def process_reservation_file():
    file_path = 'scripting/FinalProject/reservation_file.txt'  
    if os.path.exists('reservation_file.txt'):
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                with open('reservation_file.txt', 'r') as file:
                    for line in file:
                        first_name, last_name, email, phone_number, room_type, accommodation_days = line.strip().split(',')
                        customer_id = insert_customer(first_name, last_name, email, phone_number, cursor)
                        room_type_id = {'S': 1, 'P': 2, 'O': 3, 'E': 4}.get(room_type.strip().upper(), None)
                        if room_type_id:
                            cost = int(accommodation_days) * (100 if room_type_id == 1 else 150 if room_type_id == 2 else 200 if room_type_id == 3 else 50)
                            insert_reservation(room_type_id, customer_id, int(accommodation_days), cost, cursor)
                connection.commit()
        os.remove('reservation_file.txt')

if __name__ == "__main__":
    process_reservation_file()

def check_room_availability(room_type_id, cursor):
    query = "SELECT availability FROM inn_rooms WHERE id = ?"
    cursor.execute(query, (room_type_id,))
    result = cursor.fetchone()
    return result[0] > 0 if result else False

def check_in():
    with connect_to_database() as connection:
        with connection.cursor() as cursor:
            # Collect customer information
            print("***** Check-in Process *****")
            first_name = input("Enter first name: ")
            last_name = input("Enter last name: ")
            while True:
                email = input("Enter email: ")
                if is_valid_email(email):
                    break
                else:
                    print("Invalid email format. Please try again.")
            while True:
                phone_number = input("Enter phone number (10 digits): ")
                if is_valid_phone_number(phone_number):
                    break
                else:
                    print("Invalid phone number. Please enter a 10-digit phone number.")

            # Room selection
            print("Room types: 1. Standard, 2. Premium, 3. Ocean view, 4. Economy")
            room_type = input("Select room type (1-4): ")
            room_type_id = {'1': 1, '2': 2, '3': 3, '4': 4}.get(room_type, None)

            if room_type_id is None:
                print("Invalid room type selected.")
                return

            # Check room availability
            if not check_room_availability(room_type_id, cursor):
                print("Selected room type is not available.")
                return

            accommodation_days = input("Enter number of accommodation days: ")
            try:
                accommodation_days = int(accommodation_days)
            except ValueError:
                print("Invalid number of days.")
                return

            # Calculate cost based on room type
            room_prices = {1: 100, 2: 150, 3: 200, 4: 50}
            cost = room_prices[room_type_id] * accommodation_days

            # Insert customer and reservation
            customer_id = insert_customer(first_name, last_name, email, phone_number, cursor)
            insert_reservation(room_type_id, customer_id, accommodation_days, cost, cursor)

            # Update room availability
            update_query = "UPDATE inn_rooms SET availability = availability - 1 WHERE id = ?"
            cursor.execute(update_query, (room_type_id,))
            print("***** Check-in Process *****")
            connection.commit()

            print("Check-in successful. Enjoy your stay!")

def is_valid_email(email):
    # Regular expression for validating an email
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if re.match(regex, email):
        return True
    else:
        return False
    
def is_valid_phone_number(phone_number):
    pattern = r'^\d{10}$'
    return re.match(pattern, phone_number) is not None




def check_out():
    with connect_to_database() as connection:
        with connection.cursor() as cursor:
            print("***** Checkout Process *****")
            phone_number = input("Enter your phone number: ")
            print("checkout in progress.....")

            # Retrieve reservation based on phone number
            find_query = """
    SELECT inn_reservation.id, inn_customer.first_name, inn_customer.last_name, 
           inn_rooms.room_type, inn_reservation.accommodation_days, inn_reservation.cost
    FROM inn_reservation
    INNER JOIN inn_customer ON inn_reservation.customer_id = inn_customer.id
    INNER JOIN inn_rooms ON inn_reservation.room_type = inn_rooms.id
    WHERE inn_customer.phone_number = ? AND inn_reservation.checkout = 0
"""

            cursor.execute(find_query, (phone_number,))
            reservation = cursor.fetchone()

            if reservation is None:
                print("No active reservation found for this phone number.")
                return

            reservation_id, first_name, last_name, room_type, days, cost = reservation

            # Update reservation to mark as checked out
            update_query = "UPDATE inn_reservation SET checkout = 1 WHERE id = ?"
            cursor.execute(update_query, (reservation_id,))
            
            room_type_char = reservation[3]
            get_room_type_id_query = "SELECT id FROM inn_rooms WHERE room_type = ?"
            cursor.execute(get_room_type_id_query, (room_type_char,))
            room_type_id_result = cursor.fetchone()
            if room_type_id_result:
                    room_type_id = room_type_id_result[0]
                    room_update_query = "UPDATE inn_rooms SET availability = availability + 1 WHERE id = ?"
                    cursor.execute(room_update_query, (room_type_id,))
                    connection.commit()
            else:
                    print("Room type not found.")

        
            # Update room availability
            room_update_query = "UPDATE inn_rooms SET availability = availability + 1 WHERE id = ?"
            cursor.execute(room_update_query, (room_type_id,))

            connection.commit()

            # Display checkout information
        
            print(f"Pacific Inn\nYour invoice information is:\nName: {first_name} {last_name}\nAccommodation: {days} days Room type: {room_type}\nTotal Cost: ${cost:.2f} $\n-Thank you and See you next time")
            print("Thank you for staying with us!")
            
    
def is_any_room_available(cursor):
    query = "SELECT COUNT(*) FROM inn_rooms WHERE availability > 0"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0] > 0


def connect_to_database():
    try:
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        print("Connected to the database successfully.")
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def main():
    with connect_to_database() as connection:
        with connection.cursor() as cursor:
            process_reservation_file()

            while True:
                print("***** Welcome to the LIRS system *****")

                # Check room availability
                if is_any_room_available(cursor):
                    print("1. Check-out\n2. Check-in\n3. Exit")
                else:
                    print("1. Check-out\n3. Exit")
                    print("No available rooms for check-in.")

                choice = input("Please enter your option: ")

                if choice == '1':
                    check_out()
                elif choice == '2' and is_any_room_available(cursor):
                    check_in()
                elif choice == '3':
                    print("Exiting the system.")
                    break
                else:
                    print("Invalid option, please try again.")

if __name__ == "__main__":
    main()
    
    
import csv
import sqlite3

def load_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY, 
        name TEXT,
        country_code TEXT,
        city TEXT,
        address TEXT,
        locality TEXT,
        cuisines TEXT,
        average_cost_for_two REAL,
        currency TEXT,
        has_table_booking TEXT,
        has_online_delivery TEXT,
        is_delivering_now TEXT,
        price_range INTEGER,
        aggregate_rating REAL,
        rating_color TEXT,
        rating_text TEXT,
        votes INTEGER
    )
    ''')

    encodings = ['utf-8-sig', 'latin-1']

    for encoding in encodings:
        try:
            with open('Zomato.csv', 'r', encoding=encoding) as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    cursor.execute('''
                    INSERT OR IGNORE INTO restaurants (id, name, country_code, city, address, locality, cuisines,
                                                       average_cost_for_two, currency, has_table_booking, 
                                                       has_online_delivery, is_delivering_now, price_range,
                                                       aggregate_rating, rating_color, rating_text, votes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['Restaurant ID'], row['Restaurant Name'], row['Country Code'],
                        row['City'], row['Address'], row['Locality'], row['Cuisines'],
                        row['Average Cost for two'], row['Currency'], row['Has Table booking'],
                        row['Has Online delivery'], row['Is delivering now'], row['Price range'],
                        row['Aggregate rating'], row['Rating color'], row['Rating text'],
                        row['Votes']
                    ))
            print(f"Data loaded successfully using {encoding} encoding.")
            break  
        except UnicodeDecodeError:
           pass
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.close()
            return

    conn.commit()
    conn.close()

if __name__ == '__main__':
    load_data()
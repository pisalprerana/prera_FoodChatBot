import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='prabodh12',
    database='pandeyji_eatery'

)

def insert_order_item(food_item,quantity,number):
    try:
        cursor= cnx.cursor()

        cursor.callproc('insert_order_item', (food_item, quantity, number))

        cnx.commit()
        print("Order item inserted successfully")

        return 1
    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occuredL {e}")

        cnx.rollback()

        return -1

def get_total_order_price(number):
    cursor= cnx.cursor()

    query =f"SELECT get_total_order_price({number})"
    cursor.execute(query)

    result= cursor.fetchone()[0]

    cursor.close()

    return result

def get_next_order_id():
    cursor= cnx.cursor()

    query= "SELECT MAX(number) FROM orders"
    cursor.execute(query)

    result= cursor.fetchone()[0]

    cursor.close()

    if result is None:
        return 1
    else:
        return result + 1

def insert_order_tracking(number, status):
    cursor= cnx.cursor()

    insert_query= "INSERT INTO order_tracking (number, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (number, status))

    cnx.commit()

    cursor.close()

def get_order_status(number: int):
    cursor = cnx.cursor()

    query= ("SELECT status FROM order_tracking WHERE number = %s")

    cursor.execute(query, (number,))

    result = cursor.fetchone()

    cursor.close()


    if result is not None:
        return result[0]
    else:
        return None



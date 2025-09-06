import psycopg2



conn=psycopg2.connect(database='netology_db', user='postgres', password='*')


def create_table(conn_):
    with conn_.cursor() as cur:
        try:
            cur.execute("""
                        DROP TABLE IF EXISTS users CASCADE""")
            cur.execute("""
                        DROP TABLE IF EXISTS number_phone
                    """)
            cur.execute("""
                CREATE  TABLE users (
                ID SERIAL PRIMARY KEY,
                first_name VARCHAR(20) NOT NULL,
                last_name VARCHAR(30) NOT NULL,
                email VARCHAR(60) UNIQUE NOT NULL,
                CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
                );
            """)

            cur.execute("""
                CREATE TABLE number_phone(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                phone_number VARCHAR(15) NOT NULL,
                CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
                );
            """)
            conn_.commit()
        except Exception as err:
             conn_.rollback()
             print(f'Таблица не создана.ошибка {err}')

def add_users(conn_,first_name:str,last_name:str,email:str,phone_number:str=''):
    with conn_.cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO users(first_name,last_name,email)
                VALUES (%s,%s,%s)
                RETURNING id
            ;""",(first_name,last_name,email))
            new_user_id=cur.fetchone()[0]
            if phone_number=='':
                conn_.commit()
                print(f'добавлен новый пользователь с ID {new_user_id} без номера телефона')
                return True
            else:
                cur.execute("""
                            INSERT INTO number_phone(user_id,phone_number)
                            VALUES(%s,%s)
                        ;""", (new_user_id, phone_number))
                conn_.commit()
                print(f'добавлен новый пользователь с ID {new_user_id}')
                return True


        except Exception as err:
            conn_.rollback()
            print(f"Ошибка выполнения {err}")
            return False


def add_number_phone(conn_,user_id,phone_number):
        with conn_.cursor() as cur:
            try:
                cur.execute("""
                            INSERT INTO number_phone(user_id,phone_number)
                            VALUES(%s,%s)
                        ;""", (user_id, phone_number))
                conn_.commit()
                print(f'для пользователя с ID {user_id} добавлен номер {phone_number}')
                return True
            except Exception as err:
                print(f'завершение с ошибкой {err}')
                return False


def update_data_users(conn_,id_,table, column, new_data):
        with conn_.cursor() as cur:
            white_list_table = ['users', 'number_phone']
            white_list_column = ['first_name', 'last_name', 'email', 'phone_number']
            if table not in white_list_table:
                print('Неверное имя таблицы')
                return False
            if column not in white_list_column:
                print('Неверное имя столбца')
                return False
            try:
                fix_string = f"UPDATE {table} SET {column}= %s WHERE id= %s"
                cur.execute(fix_string, (new_data, id_))
                conn_.commit()
                print(f'успешное изменение столбца {column} в таблице {table}, присвоено значение {new_data}')
                return True


            except Exception as err:
                print(f'завершение с ошибкой {err}')
                return False


def delete_number_phone(conn_,phone_number):
    with conn_.cursor() as cur:
        try:
            cur.execute("""
            DELETE FROM number_phone
            WHERE phone_number = %s
            ;""",(phone_number,))
            if cur.rowcount == 0:
                print('Номера не существует')
                return False
            else:
                print(f'Номеров удалено {cur.rowcount}')
                conn_.commit()
                return True
        except Exception as err:
            conn_.rollback()
            print(f'Удаление не удалось. Ошибка {err}')
            return False


def delete_user_from_db(conn_,id_user):
    with conn_.cursor() as cur:
        try:
            cur.execute("""
            DELETE FROM users
            WHERE ID = %s
            ;""",(id_user,))
            if cur.rowcount == 0:
                print('Пользователя не существует')
                return False
            else:
                print(f'Пользователь с ID {id_user} удален из базы данных')
                conn_.commit()
                return True

        except Exception as err:
            conn_.rollback()
            print(f'удаление пользователя с ID {id_user} из базы данных не удалось.ошибка {err}')
            return False


def find_users(conn_,id_=None,first_name='',last_name='',email='',phone_number=''):
    with conn_.cursor() as cur:
        result=None
        if id_ is not None:
                try:
                    cur.execute("""SELECT users.id,users.first_name,users.last_name,users.email,number_phone.phone_number
                                            FROM users
                                            LEFT JOIN number_phone
                                            ON number_phone.user_id = users.id
                                            WHERE users.id = %s;""", (id_,))
                    result = cur.fetchall()

                except Exception as err:
                    print(f'Ошибка выполнения {err}')
                    return False
        elif phone_number=='':
            try:
                cur.execute("""SELECT users.id,users.first_name,users.last_name,users.email,number_phone.phone_number
                    FROM users
                    LEFT JOIN number_phone
                    ON number_phone.user_id = users.id
                    WHERE first_name = %s AND
                    last_name = %s AND
                    email= %s;""",(first_name,last_name,email))
                result=cur.fetchall()

            except Exception as err:
                print(f'Ошибка выполнения {err}')
                return False

        else:
            try:
                cur.execute("""SELECT users.id,users.first_name,users.last_name,users.email,number_phone.phone_number
                                    FROM users
                                    INNER JOIN number_phone
                                    ON number_phone.user_id = users.id
                                    WHERE number_phone.phone_number = %s;""", (phone_number,))
                result = cur.fetchall()

            except Exception as err:
                print(f'Ошибка выполнения {err}')
                return False

        if not result:
            print('Результат не найден')
            return False
        else:
            if result[0][4] is None:
                print(
                    f'ID пользователя {result[0][0]}, имя: {result[0][1]}, фамилия: {result[0][2]}, email: {result[0][3]}')
                return True
            else:
                phone_numbers=[]
                for row in result:
                    phone_numbers.append(row[4])
                print(
                    f'ID пользователя {result[0][0]}, имя: {result[0][1]}, фамилия: {result[0][2]}, email: {result[0][3]}, номера телефонов: {phone_numbers}')
                return True


conn.close()

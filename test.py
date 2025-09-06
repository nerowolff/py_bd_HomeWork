import psycopg2
from main import create_table,add_users,add_number_phone,update_data_users,find_users,delete_number_phone,delete_user_from_db

conn=psycopg2.connect(database='netology_db', user='postgres', password='*')

create_table(conn)

add_users(conn,'Alexey','S','orobas@mail.ru')

find_users(conn,1)

add_number_phone(conn,1,'89069817436')

find_users(conn,1)

update_data_users(conn,1,'users','last_name','Staros')

find_users(conn,1)

update_data_users(conn,1,'number_phone','phone_number','89069817401')

find_users(conn,1)

add_number_phone(conn,1,'89069817436')

delete_number_phone(conn,'89069817401')

find_users(conn,1)

delete_user_from_db(conn,1)

find_users(conn,1)

conn.close()




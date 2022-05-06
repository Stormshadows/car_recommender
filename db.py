import psycopg2

dbcon = psycopg2.connect(
        user='rwozksuc',
        password='3nv4b-4aaJb5bx0--2hIAZeoYVXateTm',
        database='rwozksuc',
        host='john.db.elephantsql.com')

cur = dbcon.cursor()
cur.execute("SELECT * FROM cars" )
car = cur.fetchone()
cur.close()

print(car[3][15])

dbcon.close()
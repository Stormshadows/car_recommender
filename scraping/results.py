import psycopg2

company = None
price_starting = 10.00
price_topend = 30.00
mileage_l = 10.00
mileage_u = 30.00
manual = None
automatic = True
petrol = True
diesel = True
cng = None
electric = None
seating_capacity = 5

SQL = """
    SELECT id, name, company, image, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating_capacity
    FROM cars
    WHERE price_starting > %s 
        AND price_topend < %s
        AND mileage_l > %s
        AND mileage_u < %s
        AND manual = COALESCE(%s, manual)
        AND automatic = COALESCE(%s, automatic)
        AND petrol = COALESCE(%s, petrol)
        AND diesel = COALESCE(%s, diesel)
        AND cng = COALESCE(%s, cng)
        AND electric = COALESCE(%s, electric)
        AND seating_capacity = %s;
        """

params = (price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating_capacity)

dbcon = psycopg2.connect(
        user='rwozksuc', 
        password='3nv4b-4aaJb5bx0--2hIAZeoYVXateTm',
        database='rwozksuc', 
        host='john.db.elephantsql.com')   

cur = dbcon.cursor()

cur.execute(SQL, params)

print(cur.fetchall())


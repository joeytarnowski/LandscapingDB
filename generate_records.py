import mysql.connector 
from mysql.connector import errorcode
import random_address as ra
import random
import names

try:
    connect = mysql.connector.connect(
        # Insert your own things here
        user = 'root',
        password = 'Samford99',
        host = 'localhost',
        database = 'landscapedb',
        port = '3306'
    )
except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
             print('Invalid credentials')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
             print('Database not found')
        else:
             print('Cannot connect to database:', err)
conn = connect.cursor()


def generate_phone_num():
    phone_num = ''
    phone_num += str(random.randint(1, 9))
    for i in range(2):
        phone_num += str(random.randint(0, 9))
    phone_num += '-'
    for i in range(3):
        phone_num += str(random.randint(0, 9))
    phone_num += '-'
    for i in range(4):
        phone_num += str(random.randint(0, 9))
    return phone_num
         
def create_customer():
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    phone_num = generate_phone_num()
    email = f'{first_name.lower()}{last_name.lower()}{random.randint(0,100)}@gmail.com'
    conn.execute('INSERT INTO Customer(first_name, last_name, email, phone_number) VALUES(%s,%s,%s,%s)', (first_name, last_name, email, phone_num))
    connect.commit()
    print(f'Customer {first_name} {last_name} added successfully\nPhone Number: {phone_num}\nEmail: {email}')

def create_location(street_addr, city, state, postal_code):
    try:
        conn.execute('INSERT INTO Location(street_address, city, state, zip) VALUES(%s,%s,%s,%s)', (street_addr, city, state, postal_code))
        connect.commit()
    except mysql.connector.errors.IntegrityError as err:
        print("skipping duplicate entry")
    print(f'Location {street_addr} added successfully\nCity: {city}\nState: {state}\nPostal Code: {postal_code}')
    
def create_employee():
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    phone_num = generate_phone_num()
    email = f'{first_name.lower()}{last_name.lower()}{random.randint(0,100)}@landscaping.com'
    hired_date = f'{random.randint(2000, 2021)}-{random.randint(1, 12)}-{random.randint(1, 28)}'
    conn.execute('INSERT INTO Employee(first_name, last_name, email, phone_number, hired_date) VALUES(%s,%s,%s,%s,%s)',\
                  (first_name, last_name, email, phone_num, hired_date))
    connect.commit()
    
    print(f'Employee {first_name} {last_name} added successfully\nPhone Number: {phone_num}\nEmail: {email}\nHired Date: {hired_date}')

def create_job():
    conn.execute('SELECT id FROM Location')
    locations = []
    for location in conn:
        locations.append(location[0])
    date = f'{random.randint(2023,2028)}-{random.randint(1, 12)}-{random.randint(1, 28)}'
    time = f'{random.randint(0, 23)}:{random.randint(0, 59)}'
    datetime = f'{date} {time}'
    location_id = locations[random.randint(0, len(locations)-1)]
    conn.execute('INSERT INTO Job(datetime, location_id) VALUES(%s, %s)', (datetime, location_id))
    connect.commit()

def create_service(name, price):
    conn.execute('INSERT INTO Service(name, price) VALUES(%s,%s)', (name, price))
    connect.commit()
    print(f'Service {name} added successfully\nPrice: {price}')

def connect_employee_job():
    # Create EmployeeJob table
    conn.execute('SELECT id FROM Employee')
    # Select all employees
    employees = []
    for employee in conn:
        employees.append(employee[0])
    # Select all jobs that don't have employees yet
    conn.execute('SELECT id FROM Job WHERE id NOT IN (SELECT job_id FROM EmployeeJob)')
    jobs = []
    for job in conn:
        jobs.append(job[0])
    for job in jobs:
        # Assign random number of employees to job
        for i in range(random.randint(1, 3)):          
            employee_id = employees[random.randint(0, len(employees)-1)]
            # Check if employee is already assigned to job
            try:
                conn.execute('INSERT INTO EmployeeJob(employee_id, job_id) VALUES(%s,%s)'\
                             , (employee_id, job))
                connect.commit()
            except mysql.connector.errors.IntegrityError:
                print("skipping duplicate entry")

def connect_service_job():
    conn.execute('SELECT name FROM Service')
    services = []
    for service in conn:
        services.append(service[0])
    # Select Jobs that don't have services yet
    conn.execute('SELECT id FROM Job WHERE id NOT IN (SELECT job_id FROM JobService)')
    jobs = []
    for job in conn:
        jobs.append(job[0])
    for job in jobs:
        for i in range(random.randint(1, 5)):
            service_id = services[random.randint(0, len(services)-1)]
            try:
                conn.execute('INSERT INTO JobService(job_id, service_name) VALUES(%s,%s)', (job, service_id))
                connect.commit()
            except mysql.connector.errors.IntegrityError:
                print("skipping duplicate entry")

def connect_customer_location():
    conn.execute('SELECT id FROM Customer')
    customers = []
    for customer in conn:
        customers.append(customer[0])
    conn.execute('SELECT id FROM Location')
    locations = []
    for location in conn:
        locations.append(location[0])
    for location in locations:
        customer_id = customers[random.randint(0, len(customers)-1)]
        try:
            conn.execute('INSERT INTO CustomerLocation(customer_id, location_id) VALUES(%s,%s)', (customer_id, location))
            connect.commit()
        except mysql.connector.errors.IntegrityError:
            print("skipping duplicate entry")

services = ['Hedge trimming', 'Garden maintenance', 'Weed control', 'Lawn care', 'Lawn aeration', 'Lawn fertilization', 'Lawn seeding', 'Lawn sodding', 'Lawn topdressing', 'Lawn dethatching', 'Lawn edging', 'Lawn irrigation', 'Lawn mulching', 'Lawn overseeding', 'Lawn renovation', 'Lawn rolling', 'Lawn watering', 'Lawn weed control', 'Lawn winterization', 'Patio installation', 'Fence installation', 'Fire pit installation', 'Gazebo installation', 'Retaining wall installation', 'Deck installation', 'Swimming pool installation']
prices = [50, 100, 75, 150, 200, 200, 250, 300, 150, 200, 100, 100, 150, 200, 250, 100, 50, 75, 100, 4000, 600, 700, 6000, 2000, 4000, 18000]

for i in range(len(services)):
    create_service(services[i], prices[i])

for i in range(500):
    address = ra.real_random_address()
    create_location(address['address1'], address['city'], address['state'], address['postalCode'])

for i in range(100):
    create_customer()

for i in range(20):
    create_employee()

for i in range(100):
    create_job()

connect_customer_location()
connect_employee_job()
connect_service_job()

     

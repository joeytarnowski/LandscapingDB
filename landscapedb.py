import mysql.connector 
from mysql.connector import errorcode

import tkinter as tk
from tkinter import font
from  tkinter import ttk
from tkinter import *
from tkinter import messagebox as mb

# Begin: Connection to Database ================

try:
    connect = mysql.connector.connect(
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

# End: Connection to Database =========================

# Begin: GUI Layout with table and buttons ===========
r = tk.Tk()
style = ttk.Style(r)
r.title("Landscaping")
r.geometry('1000x700')

# Create frame inside the main window to hold job information
display_frame = tk.Frame(r, width=780, height=600)
display_frame.pack(fill='both', expand=True, side=TOP, padx=10, pady=(40, 350))
tree = ttk.Treeview(display_frame)
conn = connect.cursor()

# Display functions (Joey)

# Begin: Display Jobs Function =======================
def display_jobs(search_criteria=None, search_value=None):
    style.configure("Treeview", rowheight=90)
    for item in tree.get_children():
        tree.delete(item)
    include_past = chk_var_jobs.get()

    # Create tree with necessary columns and headers
    tree['show'] = 'headings'

    tree['columns']  = ('id', 'datetime', 'location', 'customer', 'employees', 'services', 'totalcost')

    tree.column('id', width=50, minwidth=50, anchor=tk.CENTER)
    tree.column('datetime', width=100, minwidth=100, anchor=tk.CENTER)
    tree.column('location', minwidth=150, anchor=tk.W)
    tree.column('customer', width=100, minwidth=100, anchor=tk.W)
    tree.column('employees', width=150, minwidth=150, anchor=tk.W)
    tree.column('services', width=150, minwidth=150, anchor=tk.W)
    tree.column('totalcost', width=100, minwidth=100, anchor=tk.W)

    tree.heading('id', text='Job ID', anchor=tk.CENTER)
    tree.heading('datetime', text='Date/Time', anchor=tk.CENTER)
    tree.heading('location', text='Location', anchor=tk.CENTER)
    tree.heading('customer', text='Customer', anchor=tk.CENTER)
    tree.heading('employees', text='Employees', anchor=tk.CENTER)
    tree.heading('services', text='Services', anchor=tk.CENTER)
    tree.heading('totalcost', text='Total Cost', anchor=tk.CENTER)

    hsb = ttk.Scrollbar(r, orient='horizontal')
    hsb.configure(command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)
    hsb.pack(fill=X, side=BOTTOM)

    vsb = ttk.Scrollbar(r, orient='vertical')
    vsb.configure(command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(fill=Y, side=RIGHT, expand=False)

    # End: GUI Layout with table and buttons ===========

    # Begin: Select initial data and populate GUI Grid ========
    sql_query = construct_search_query(search_criteria, search_value, include_past=include_past)
    print(sql_query)
    conn.execute(sql_query)
    connres = conn.fetchall()

    i = 0
    for ro in connres:
        # Get id, datetime, location, customer, employees, services, and total cost
        datetime = ro[1]
        datetime = datetime.strftime('%m-%d-%Y\n%H:%M')
        # Get location
        conn.execute("select street_address, city, state, zip from Location where id = %s", (ro[2],))
        location_data = conn.fetchone()
        disp_location = f'{location_data[0]}\n{location_data[1]}, {location_data[2]} {location_data[3]}'

        # Get customer
        conn.execute("select first_name, last_name from Customer where id = \
                    (select customer_id from CustomerLocation where location_id = %s)", (ro[2],))
        customer_data = conn.fetchone()
        if customer_data is None:
            disp_customer = 'None'
        else:
            disp_customer = f'{customer_data[0]} {customer_data[1]}'

        # Get employees
        conn.execute("select employee_id from EmployeeJob where job_id = %s", (ro[0],))
        all_emps = conn.fetchall()
        disp_employees = ''
        for emp in all_emps:
            conn.execute("select first_name, last_name from Employee where id = %s", (emp[0],))
            emp_name = conn.fetchone()
            disp_employees += f'{emp_name[0]} {emp_name[1]}\n'

        # Get services
        conn.execute("select service_name from JobService where job_id = %s", (ro[0],))
        disp_services = ''
        for serv in conn:
            disp_services += f'{serv[0]}\n'

        # Get total cost
        disp_totalcost = 0
        conn.execute("select service_name from JobService where job_id = %s", (ro[0],))
        services = conn.fetchall()
        for serv in services:
            conn.execute("select price from Service where name = %s", (serv[0],))
            cost = conn.fetchone()
            disp_totalcost += cost[0]

        # display data in GUI
        tree.insert('', i, text="", values=(ro[0],datetime, disp_location, disp_customer, disp_employees, disp_services, disp_totalcost))
        i += 1
    tree.pack(expand=True, fill='both')
    # END: Select initial data and populate GUI Grid ========
# END: Display Jobs Function ========

# Begin: Display Employees Function =======================
def display_employees(search_criteria=None, search_value=None):
    style.configure("Treeview", rowheight=50)
    for item in tree.get_children():
        tree.delete(item)
    tree['show'] = 'headings'

    tree['columns']  = ('id', 'l_name', 'f_name', 'phone', 'email', 'jobs', 'hired_date')

    tree.column('id', width=50, minwidth=50, anchor=tk.CENTER)
    tree.column('l_name', width=70, minwidth=100, anchor=tk.W)
    tree.column('f_name', width=70, minwidth=10, anchor=tk.W)
    tree.column('phone', width=100, minwidth=100, anchor=tk.W)
    tree.column('email', width=230, minwidth=150, anchor=tk.W)
    tree.column('jobs', width=100, minwidth=100, anchor=tk.W)
    tree.column('hired_date', width=100, minwidth=100, anchor=tk.CENTER)

    tree.heading('id', text='Employee ID', anchor=tk.CENTER)
    tree.heading('l_name', text='Last Name', anchor=tk.CENTER)
    tree.heading('f_name', text='First Name', anchor=tk.CENTER)
    tree.heading('phone', text='Phone', anchor=tk.CENTER)
    tree.heading('email', text='Email', anchor=tk.CENTER)
    tree.heading('jobs', text='Jobs Worked (ID)', anchor=tk.CENTER)
    tree.heading('hired_date', text='Hired Date', anchor=tk.CENTER)

    hsb = ttk.Scrollbar(r, orient='horizontal')
    hsb.configure(command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)
    hsb.pack(fill=X, side=BOTTOM)

    vsb = ttk.Scrollbar(r, orient='vertical')
    vsb.configure(command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(fill=Y, side=RIGHT, expand=False)

    # End: GUI Layout with table and buttons ===========

    # Begin: Select initial data and populate GUI Grid ========
    sql_query = construct_search_query(search_criteria, search_value)
    conn.execute(sql_query)
    connres = conn.fetchall()

    i = 0
    for ro in connres:
        # Get id, last_name, first_name, phone, email, jobs, and hired_date
        # jobs
        conn.execute("select job_id from EmployeeJob where employee_id = %s", (ro[0],))
        all_jobs = conn.fetchall()
        disp_jobs = ''
        j = 0
        for job in all_jobs:
            if j % 5 == 0:
                disp_jobs += '\n'
            disp_jobs += f'{job[0]}, '
            j += 1
        disp_jobs = disp_jobs[:-2]
        disp_date = ro[5].strftime('%m-%d-%Y')

        # display data in GUI
        tree.insert('', i, text="", values=(ro[0],ro[2], ro[1], ro[4], ro[3], disp_jobs, disp_date))
        i += 1

    tree.pack(expand=True, fill='both')
# End: Display Employees Function =========================

# Begin: Display Customers Function =======================
def display_customers(search_criteria=None, search_value=None):
    style.configure("Treeview", rowheight=80)
    for item in tree.get_children():
        tree.delete(item)

    tree['show'] = 'headings'

    tree['columns']  = ('id', 'l_name', 'f_name', 'phone', 'email', 'locations')

    tree.column('id', width=50, minwidth=50, anchor=tk.CENTER)
    tree.column('l_name', width=70, minwidth=70, anchor=tk.W)
    tree.column('f_name', width=70, minwidth=70, anchor=tk.W)
    tree.column('phone', width=100, minwidth=100, anchor=tk.W)
    tree.column('email', width=160, minwidth=160, anchor=tk.W)
    tree.column('locations', width=150, minwidth=150, anchor=tk.W)

    tree.heading('id', text='Customer ID', anchor=tk.CENTER)
    tree.heading('l_name', text='Last Name', anchor=tk.CENTER)
    tree.heading('f_name', text='First Name', anchor=tk.CENTER)
    tree.heading('phone', text='Phone', anchor=tk.CENTER)
    tree.heading('email', text='Email', anchor=tk.CENTER)
    tree.heading('locations', text='Locations', anchor=tk.CENTER)

    hsb = ttk.Scrollbar(r, orient='horizontal')
    hsb.configure(command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)
    hsb.pack(fill=X, side=BOTTOM)

    vsb = ttk.Scrollbar(r, orient='vertical')
    vsb.configure(command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(fill=Y, side=RIGHT, expand=False)

    # End: GUI Layout with table and buttons ===========

    # Begin: Select initial data and populate GUI Grid ========
    sql_query = construct_search_query(search_criteria, search_value)
    conn.execute(sql_query)
    connres = conn.fetchall()

    i = 0
    for ro in connres:
        # Get id, last_name, first_name, phone, email, and locations
        # locations
        conn.execute("select location_id from CustomerLocation where customer_id = %s", (ro[0],))
        all_locs = conn.fetchall()
        disp_locs = ''
        for loc in all_locs:
            conn.execute("select street_address from Location where id = %s", (loc[0],))
            addr = conn.fetchone()
            disp_locs += f'{addr[0]}\n'
        
        # display data in GUI
        tree.insert('', i, text="", values=(ro[0],ro[2], ro[1], ro[4], ro[3], disp_locs))
        i += 1       
# End: Display Customers Function =========================

# Begin: Display Locations Function =======================
def display_locations(search_criteria=None, search_value=None):
    style.configure("Treeview", rowheight=50)
    for item in tree.get_children():
        tree.delete(item)

    tree['show'] = 'headings'

    tree['columns']  = ('id', 'street_addr', 'city', 'state', 'zip', 'customers', 'jobs')

    tree.column('id', width=50, minwidth=50, anchor=tk.CENTER)
    tree.column('street_addr', width=200, minwidth=200, anchor=tk.W)
    tree.column('city', width=70, minwidth=70, anchor=tk.W)
    tree.column('state', width=20, minwidth=20, anchor=tk.W)
    tree.column('zip', width=30, minwidth=30, anchor=tk.W)
    tree.column('customers', width=150, minwidth=150, anchor=tk.W)
    tree.column('jobs', width=100, minwidth=100, anchor=tk.W)

    tree.heading('id', text='Location ID', anchor=tk.CENTER)
    tree.heading('street_addr', text='Street Address', anchor=tk.CENTER)
    tree.heading('city', text='City', anchor=tk.CENTER)
    tree.heading('state', text='State', anchor=tk.CENTER)
    tree.heading('zip', text='Zip', anchor=tk.CENTER)
    tree.heading('customers', text='Customers', anchor=tk.CENTER)
    tree.heading('jobs', text='Jobs', anchor=tk.CENTER)

    hsb = ttk.Scrollbar(r, orient='horizontal')
    hsb.configure(command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)
    hsb.pack(fill=X, side=BOTTOM)

    vsb = ttk.Scrollbar(r, orient='vertical')
    vsb.configure(command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(fill=Y, side=RIGHT, expand=False)

    # End: GUI Layout with table and buttons ===========

    # Begin: Select initial data and populate GUI Grid ========
    sql_query = construct_search_query(search_criteria, search_value)
    conn.execute(sql_query)
    connres = conn.fetchall()

    i = 0
    for ro in connres:
        # Get id, street_addr, city, state, zip, customers, and jobs
        # customers
        conn.execute("select customer_id from CustomerLocation where location_id = %s", (ro[0],))
        all_custs = conn.fetchall()
        disp_custs = ''
        for cust in all_custs:
            conn.execute("select first_name, last_name from Customer where id = %s", (cust[0],))
            cust_name = conn.fetchone()
            disp_custs += f'{cust_name[0]} {cust_name[1]}\n'
        
        # jobs
        conn.execute("select id from Job where location_id = %s", (ro[0],))
        all_jobs = conn.fetchall()
        if len(all_jobs) == 0:
            disp_jobs = 'None'
        disp_jobs = ''
        j = 0
        for job in all_jobs:
            if j % 5 == 0:
                disp_jobs += '\n'
            disp_jobs += f'{job[0]}, '
            j += 1
        disp_jobs = disp_jobs[:-2]

        # display data in GUI
        if chk_var_locs.get() or len(all_jobs) > 0:
            tree.insert('', i, text="", values=(ro[0],ro[1], ro[2], ro[3], ro[4], disp_custs, disp_jobs))
            i += 1
# End: Display Locations Function =========================

# Begin: Display Services Function =======================
def display_services(search_criteria=None, search_value=None):
    style.configure("Treeview", rowheight=50)
    for item in tree.get_children():
        tree.delete(item)

    tree['show'] = 'headings'

    tree['columns']  = ('name', 'price')

    tree.column('name', width=150, minwidth=150, anchor=tk.W)
    tree.column('price', width=50, minwidth=50, anchor=tk.CENTER)

    tree.heading('name', text='Service Name', anchor=tk.CENTER)
    tree.heading('price', text='Price', anchor=tk.CENTER)

    hsb = ttk.Scrollbar(r, orient='horizontal')
    hsb.configure(command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)
    hsb.pack(fill=X, side=BOTTOM)

    vsb = ttk.Scrollbar(r, orient='vertical')
    vsb.configure(command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(fill=Y, side=RIGHT, expand=False)

    # End: GUI Layout with table and buttons ===========

    # Begin: Select initial data and populate GUI Grid ========
    sql_query = construct_search_query(search_criteria, search_value)
    conn.execute(sql_query)
    connres = conn.fetchall()

    i = 0
    for ro in connres:
        # Get name and price
        # display data in GUI
        tree.insert('', i, text="", values=(ro[0],ro[1]))
        i += 1
# End: Display Services Function =========================

# Begin: Construct Search Query Function (Joey) =======================
def construct_search_query(search_criteria, search_value, include_past=False):
    # Construct the search query based on the selected option and search criteria
    match selected_option.get():
        case 'Employees':
            if search_value is not None and search_value != '':
                search_value = f"'{search_value}'"
                match search_criteria:
                    case 'ID':
                        search_value = int(search_value[1:-1])
                        search_query = f"select * from Employee where id = {search_value} order by last_name, first_name desc"
                    case 'Last Name':
                        search_query = f"select * from Employee where last_name = {search_value} order by last_name, first_name desc"
                    case 'First Name':
                        search_query = f"select * from Employee where first_name = {search_value} order by last_name, first_name desc"
                    case 'Phone':
                        search_query = f"select * from Employee where phone = {search_value} order by last_name, first_name desc"
                    case 'Email':
                        search_query = f"select * from Employee where email = {search_value} order by last_name, first_name desc"
                    case 'Date Hired':
                        # Fix date formatting from MM-DD-YYYY to YYYY-MM-DD
                        search_value = f"'{search_value[6:]}-{search_value[:2]}-{search_value[3:5]}'"
                        search_query = f"select * from Employee where hired_date = {search_value} order by last_name, first_name desc"
            else:
                search_query = "select * from Employee order by last_name, first_name desc"
        case 'Customers':
            if search_value is not None and search_value != '':
                search_value = f"'{search_value}'"
                match search_criteria:
                    case 'ID':
                        search_value = int(search_value[1:-1])
                        search_query = f"select * from Customer where id = {search_value} order by last_name, first_name desc"
                    case 'Last Name':
                        search_query = f"select * from Customer where last_name = {search_value} order by last_name, first_name desc"
                    case 'First Name':
                        search_query = f"select * from Customer where first_name = {search_value} order by last_name, first_name desc"
                    case 'Phone':
                        search_query = f"select * from Customer where phone = {search_value} order by last_name, first_name desc"
                    case 'Email':
                        search_query = f"select * from Customer where email = {search_value} order by last_name, first_name desc"
            else:
                search_query = "select * from Customer order by last_name, first_name desc"
        case 'Locations':
            if search_value is not None and search_value != '':
                search_value = f"'{search_value}'"
                match search_criteria:
                    case 'ID':
                        search_value = int(search_value[1:-1])
                        search_query = f"select * from Location where id = {search_value} order by city, state, zip"
                    case 'Street Address':
                        search_query = f"select * from Location where street_address = {search_value} order by city, state, zip"
                    case 'City':
                        search_query = f"select * from Location where city = {search_value} order by city, state, zip"
                    case 'State':
                        search_query = f"select * from Location where state = {search_value} order by city, state, zip"
                    case 'Zip':
                        search_query = f"select * from Location where zip = {search_value} order by city, state, zip"
            else:
                search_query = "select * from Location"
        case 'Jobs':
            if search_value is not None and search_value != '':
                search_value = f"'{search_value}'"
                match search_criteria:
                    case 'ID':
                        search_value = int(search_value[1:-1])
                        search_query = f"select * from Job where id = {search_value} order by datetime asc"
                    case 'Date':
                        dates = search_value.split('_')
                        # Fix date formatting from MM-DD-YYYY to YYYY-MM-DD
                        dates[0] = f"'{dates[0][6:]}-{dates[0][:2]}-{dates[0][3:5]} 00:00:00'"
                        dates[1] = f"'{dates[1][6:]}-{dates[1][:2]}-{dates[1][3:5]} 23:59:59'"
                        search_query = f"select * from Job where datetime >= {dates[0]} and datetime <= {dates[1]} order by datetime asc"
                    case 'Start Date':
                        # Fix date formatting from MM-DD-YYYY to YYYY-MM-DD
                        search_value = f"'{search_value[6:]}-{search_value[:2]}-{search_value[3:5]} 00:00:00'"
                        search_query = f"select * from Job where datetime >= {search_value}"
                    case 'End Date':
                        # Fix date formatting from MM-DD-YYYY to YYYY-MM-DD
                        search_value = f"'{search_value[6:]}-{search_value[:2]}-{search_value[3:5]} 23:59:59'"
                        search_query = f"select * from Job where datetime <= {search_value} order by datetime asc"
                        if not include_past:
                            search_query = search_query[:-22] + " and datetime > now() order by datetime asc"
                    case 'Street Address':
                        search_query = f"select j.*\
                                        from Job j\
                                        join Location l on j.location_id = l.id\
                                        where l.street_address = {search_value} order by j.datetime asc"
                        if not include_past:
                            search_query = search_query[:-24] + " and j.datetime > now() order by datetime asc"
                    case 'City':
                        search_query = f"select j.*\
                                        from Job j\
                                        join Location l on j.location_id = l.id\
                                        where l.city = {search_value} order by j.datetime asc"
                        if not include_past:
                            search_query = search_query[:-24] + " and j.datetime > now() order by datetime asc"
                    case 'State':
                        search_query = f"select j.*\
                                        from Job j\
                                        join Location l on j.location_id = l.id\
                                        where l.state = {search_value} order by j.datetime asc"
                        if not include_past:
                            search_query = search_query[:-24] + " and j.datetime > now() order by datetime asc"
                    case 'Zip':
                        # Convert search value to integer
                        search_value = int(search_value[1:-1])
                        search_query = f"select j.*\
                                        from Job j\
                                        join Location l on j.location_id = l.id\
                                        where l.zip = {search_value} order by j.datetime asc"
                        if not include_past:
                            search_query = search_query[:-24] + " and j.datetime > now() order by datetime asc"
                    case 'Customer ID':
                        # Convert search value to integer
                        search_value = int(search_value[1:-1])
                        search_query = f"SELECT j.*\
                                        FROM Job j\
                                        JOIN CustomerLocation cl ON j.location_id = cl.location_id\
                                        WHERE cl.customer_id = {search_value} order by datetime asc"
                        if not include_past:
                            search_query = search_query[:-22] + " and datetime > now() order by datetime asc"
                    case 'Employee ID':
                        # Convert search value to integer
                        search_value = int(search_value[1:-1])
                        search_query = f"select j.* \
                                    from Job j\
                                    join EmployeeJob ej on j.id = ej.job_id\
                                    where ej.employee_id = {search_value} order by datetime asc"
                        if not include_past:
                            search_query = search_query[:-22] + " and datetime > now() order by datetime asc"
                    case 'Service':
                        search_query = f"select * from Job where id in \
                                            (select job_id from JobService where service_name = {search_value}) order by datetime asc"
                        if not include_past:
                            search_query = search_query[:-22] + " and datetime > now() order by datetime asc"
                    case 'Total Cost':
                        costs = search_value.split('_')
                        costs[0] = float(costs[0][1:])
                        costs[1] = float(costs[1][:-1])
                        search_query = f"select j.*\
                                            from Job j\
                                            join (\
                                                select js.job_id, sum(s.price) AS total_price\
                                                from JobService js\
                                                join Service s on js.service_name = s.name\
                                                group BY js.job_id\
                                            ) as service_totals on j.id = service_totals.job_id\
                                            where service_totals.total_price >= {costs[0]}\
                                            and service_totals.total_price <= {costs[1]} order by service_totals.total_price desc"
                        if not include_past:
                            search_query = search_query[:-41] + " and j.datetime > now() order by service_totals.total_price desc"
                    case 'Min Cost':
                        search_value = float(search_value[1:-1])
                        search_query = f"select j.*\
                                            from Job j\
                                            join (\
                                                select js.job_id, sum(s.price) AS total_price\
                                                from JobService js\
                                                join Service s on js.service_name = s.name\
                                                group BY js.job_id\
                                            ) as service_totals on j.id = service_totals.job_id\
                                            where service_totals.total_price >= {search_value} order by service_totals.total_price desc"
                        if not include_past:
                            search_query = search_query[:-41] + " and j.datetime > now() order by service_totals.total_price desc"
                    case 'Max Cost':
                        search_value = float(search_value[1:-1])
                        search_query = f"select j.*\
                                            from Job j\
                                            join (\
                                                select js.job_id, sum(s.price) AS total_price\
                                                from JobService js\
                                                join Service s on js.service_name = s.name\
                                                group BY js.job_id\
                                            ) as service_totals on j.id = service_totals.job_id\
                                            where service_totals.total_price <= {search_value} order by service_totals.total_price desc"
                        if not include_past:
                            search_query = search_query[:-41] + " and j.datetime > now() order by service_totals.total_price desc"
            else:
                search_query = "select * from Job order by datetime asc"
                if not include_past:
                    search_query = search_query[:-22] + " where datetime > now() order by datetime asc"
        case 'Services':
            if search_value is not None and search_value != '':
                search_value = f"'{search_value}'"
                match search_criteria:
                    case 'Name':
                        search_query = f"select * from Service where name = {search_value} order by name"
                    case 'Price':
                        search_query = f"select * from Service where price = {search_value} order by name"
            else:
                search_query = "select * from Service order by name"
                
    return search_query
# End: Construct Search Query Function =========================

# Helper function to manage cases of multiple search criteria
def perform_search(search_window, search_criteria, search_value=None, search_value2=None):
    search_window.destroy()
    # Perform the search based on the selected option and search criteria
    match selected_option.get():
        case 'Employees':
            display_employees(search_criteria, search_value)
        case 'Customers':
            display_customers(search_criteria, search_value)
        case 'Locations':
            display_locations(search_criteria, search_value)
        case 'Jobs':
            match search_criteria:
                case 'Date':
                    if search_value != '':
                        if search_value2 == '':
                            search_criteria = 'Start Date'
                            display_jobs(search_criteria, search_value)
                        else:
                            real_search_value = f'{search_value}_{search_value2}'
                            display_jobs(search_criteria, real_search_value)
                    else:
                        search_criteria = 'End Date'
                        display_jobs(search_criteria, search_value2)
                case 'Total Cost':
                    if search_value != '':
                        if search_value2 == '':
                            search_criteria = 'Min Cost'
                            display_jobs(search_criteria, search_value)
                        else:
                            real_search_value = f'{search_value}_{search_value2}'
                            display_jobs(search_criteria, real_search_value)
                    else:
                        search_criteria = 'Max Cost'
                        display_jobs(search_criteria, search_value2)
                case _:
                    display_jobs(search_criteria, search_value)


# Begin: Filter Info Function =======================
# Filters out all info except the search term
selected_search = tk.StringVar()
def filter_info():
    selected_menu = selected_option.get()
    # Create a new Toplevel window for the search
    search_window = tk.Toplevel(r)
    search_window.title("Search")
    search_window.geometry("300x200")
    top_frame = tk.Frame(search_window)
    bottom_frame = tk.Frame(search_window)
    top_frame.pack(side="top", fill="x")
    bottom_frame.pack(side="top", fill="x")

    def display_search():
        # Function to create search fields based on the selected option
        def create_search_fields():
            for widget in bottom_frame.winfo_children():
                widget.destroy()  # Clear previous search fields and buttons
            selected_search_option = selected_search.get()
            if selected_search_option == 'Date':
                date_label1 = tk.Label(bottom_frame, text="Start Date (MM-DD-YYYY):")
                date_label1.pack()
                search_entry = tk.Entry(bottom_frame)
                search_entry.pack()
                date_label2 = tk.Label(bottom_frame, text="End Date (MM-DD-YYYY):")
                date_label2.pack()
                search_entry2 = tk.Entry(bottom_frame)
                search_entry2.pack()
                search_button = tk.Button(bottom_frame, text="Search", command=lambda: perform_search(search_window, selected_search_option, search_entry.get(), search_entry2.get()))
                search_button.pack()
            elif selected_search_option == 'Total Cost':
                cost_label1 = tk.Label(bottom_frame, text="Minimum Cost:")
                cost_label1.pack()
                search_entry = tk.Entry(bottom_frame)
                search_entry.pack()
                cost_label2 = tk.Label(bottom_frame, text="Maximum Cost:")
                cost_label2.pack()
                search_entry2 = tk.Entry(bottom_frame)
                search_entry2.pack()
                search_button = tk.Button(bottom_frame, text="Search", command=lambda: perform_search(search_window, selected_search_option, search_entry.get(), search_entry2.get()))
                search_button.pack()
            else:
                search_label = tk.Label(bottom_frame, text=f"{selected_search_option}:")
                search_label.pack()
                search_entry = tk.Entry(bottom_frame)
                search_entry.pack()
                search_button = tk.Button(bottom_frame, text="Search", command=lambda: perform_search(search_window, selected_search_option, search_entry.get()))
                search_button.pack()


        # Add search fields and buttons to the search window
        search_label = tk.Label(top_frame, text=f"Search {selected_menu} by:")
        search_label.pack()

        # Create a dropdown menu
        search_options = []
        if selected_menu == 'Employees':
            search_options = ['ID', 'Last Name', 'First Name', 'Phone', 'Email', 'Date Hired']
        elif selected_menu == 'Customers':
            search_options = ['ID', 'Last Name', 'First Name', 'Phone', 'Email']
        elif selected_menu == 'Locations':
            search_options = ['ID', 'Street Address', 'City', 'State', 'Zip']
        elif selected_menu == 'Jobs':
            search_options = ['ID', 'Date', 'Street Address', 'City', 'State', 'Zip', 'Customer ID', 'Employee ID', 'Service', 'Total Cost']
        else:
            search_options = ['Search']

        selected_search.set(search_options[0])  # Set default option
        dropdown_menu = tk.OptionMenu(top_frame, selected_search, *search_options, command=lambda _: create_search_fields())
        dropdown_menu.pack(side='top')

        # Create search fields based on the selected option
        create_search_fields()

    display_search()  # Initial call to display search fields
# End: Filter Info Function =========================

# Begin: Get Receipt Function =======================
def get_receipt(tree):
    # Create a new Toplevel window for receipt
    receipt_window = tk.Toplevel(r)
    receipt_window.title("Receipt")
    receipt_window.geometry("300x600")

    # Get job from selected item
    selected_item = tree.selection()[0]
    uid=tree.item(selected_item)['values'][0]
    conn.execute("select * from Job where id = %s", (uid,))
    job = conn.fetchone()

    # Get customer
    conn.execute("select first_name, last_name from Customer where id = \
                (select customer_id from CustomerLocation where location_id = %s)", (job[2],))
    customer = conn.fetchone()
    cust_label = tk.Label(receipt_window, text=f'Customer: {customer[0]} {customer[1]}', anchor='w', justify='left')
    cust_label.place(x=10, y=10)

    # Get location
    conn.execute("select street_address, city, state, zip from Location where id = %s", (job[2],))
    location = conn.fetchone()
    loc_label = tk.Label(receipt_window, text=f'Address: \n{location[0]}\n{location[1]}, {location[2]} {location[3]}', anchor='w', justify='left')
    loc_label.place(x=10, y=40)

    # Get date and time
    date_time = job[1]
    date_time = date_time.strftime('%m-%d-%Y\n%H:%M')
    dt_label = tk.Label(receipt_window, text=f'Date/Time: \n{date_time}', anchor='w', justify='left')
    dt_label.place(x=10, y=100)

    # Get services
    conn.execute("select service_name from JobService where job_id = %s", (job[0],))
    services = conn.fetchall()
    serv_text = ''
    total_cost = 0
    for serv in services:
        conn.execute("select price from Service where name = %s", (serv[0],))
        cost = conn.fetchone()
        serv_text += f'{serv[0]}:         ${cost[0]}\n'
        total_cost += cost[0]
    serv_text += '-----------------------------------------------\n'
    serv_text += f'Total:         ${total_cost}'
    serv_label = tk.Label(receipt_window, text=serv_text, anchor='e', justify='right')
    serv_label.place(x=10, y=200)
# End: Get Receipt Function =========================

# Displays the selected option in the GUI and deletes unnecessary buttons and checkboxes
def display_info():
    match selected_option.get():
        case 'Employees':
            display_employees()
            checkbox_jobs.place_forget()
            checkbox_locs.place_forget()
            receiptbutton.place_forget()
        case 'Customers':
            display_customers()
            checkbox_jobs.place_forget()
            checkbox_locs.place_forget()
            receiptbutton.place_forget()
        case 'Locations':
            display_locations()
            checkbox_jobs.place_forget()
            checkbox_locs.place(x=150, y=10)
            receiptbutton.place_forget()
        case 'Jobs':
            display_jobs()
            checkbox_locs.place_forget()
            checkbox_jobs.place(x=150, y=10)
            receiptbutton.place(x=610, y=650)
        case 'Services':
            display_services()
            checkbox_jobs.place_forget()
            checkbox_locs.place_forget()
            receiptbutton.place_forget()


# Begin: Variables defined by data types to help with GUI =====
id=tk.StringVar()
date=tk.StringVar()
time=tk.StringVar()
street_addr=tk.StringVar()
city=tk.StringVar()
state=tk.StringVar()
zip=tk.StringVar()
f_name=tk.StringVar()
l_name=tk.StringVar()
phone=tk.StringVar()
email=tk.StringVar()
name=tk.StringVar()
price=tk.StringVar()
# End: Variables defined by data types to help with GUI =====


# Add functions (Tyler)

# Begin: Add Job function ===============
def add_job_data():
    # Create a new Toplevel window for adding a job
    add_job_window = tk.Toplevel(r)
    add_job_window.title("Add Job")
    add_job_window.geometry("600x400")
    f = Frame(add_job_window, width=600, height=400)
    f.pack()

    # Add labels and entry fields for date, time, street address, city, state, zip, and services
    l1=Label(f, text='Date (MM-DD-YYYY)', width=18, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=date, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)

    l2=Label(f, text='Time (HH:MM)', width=15, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=time, width=25)
    l2.place(x=50, y=70)
    e2.place(x=200, y=70)

    l3=Label(f, text='Street Address', width=15, font=('Calibri', 11, 'bold'))
    e3=Entry(f,textvariable=street_addr, width=25)
    l3.place(x=50, y=110)
    e3.place(x=200, y=110)

    l4=Label(f, text='City', width=15, font=('Calibri', 11, 'bold'))
    e4=Entry(f,textvariable=city, width=25)
    l4.place(x=50, y=150)
    e4.place(x=200, y=150)

    l5=Label(f, text='State', width=15, font=('Calibri', 11, 'bold'))
    e5=Entry(f,textvariable=state, width=25)
    l5.place(x=50, y=190)
    e5.place(x=200, y=190)

    l6=Label(f, text='Zip', width=15, font=('Calibri', 11, 'bold'))
    e6=Entry(f,textvariable=zip, width=25)
    l6.place(x=50, y=230)
    e6.place(x=200, y=230)

    l7=Label(f, text='Services', width=15, font=('Calibri', 11, 'bold'))
    e7=Entry(f, width=25)
    l7.place(x=50, y=270)
    e7.place(x=200, y=270)

    # Function to clear all entry fields and destroy the window
    def destroy_add_job():
        e1.delete(0, END)
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        e5.delete(0, END)
        e6.delete(0, END)
        e7.delete(0, END)
        f.destroy()
        add_job_window.destroy()

    # Function to add a job to the database
    def add_job():
        a_address = street_addr.get()
        a_city = city.get()
        a_state = state.get()
        a_zip = zip.get()
        a_date = date.get()
        a_time = time.get()
        a_date = f'{a_date[6:]}-{a_date[:2]}-{a_date[3:5]}'
        a_datetime = f'{a_date} {a_time}:00'
        a_services = e7.get().split(',')

        # Look up location id based on address
        conn.execute("select id from Location where street_address = %s and city = %s and state = %s and zip = %s",(a_address, a_city, a_state, a_zip))
        loc_id = conn.fetchone()
        # If location not found, ask user if they want to add it
        if loc_id is None:
            mb.askyesno("Location Not Found", "Location not found. Would you like to add it?")
            conn.execute("insert into Location (street_address, city, state, zip) values (%s, %s, %s, %s)", (a_address, a_city, a_state, a_zip))
            conn.execute("select last_insert_id()")
            loc_id = conn.fetchone()

        # Insert job into database
        conn.execute("insert into Job (datetime, location_id) values (%s, %s)", (a_datetime, loc_id[0]))
        conn.execute("select last_insert_id()")
        job_id = conn.fetchone()

        # Insert services into database
        for serv in a_services:
            conn.execute("insert into JobService (job_id, service_name) values (%s, %s)", (job_id[0], serv.strip()))

        connect.commit()
        destroy_add_job()
        display_info()

    add_button = Button(f, text="Add Job", command=add_job)
    add_button.place(x=250, y=320)

    cancel_button = Button(f, text="Cancel", command=destroy_add_job)
    cancel_button.place(x=350, y=320)
# End: Add Job function ============================

# Begin: Add Employee function (Tyler) =======================
def add_employee_data():
    # Create a new Toplevel window for adding an employee
    add_employee_window = tk.Toplevel(r)
    add_employee_window.title("Add Employee")
    add_employee_window.geometry("600x400")

    f = Frame(add_employee_window, width=600, height=400)
    f.pack()

    l1=Label(f, text='First Name', width=15, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=f_name, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)

    l2=Label(f, text='Last Name', width=15, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=l_name, width=25)
    l2.place(x=50, y=70)
    e2.place(x=200, y=70)

    l3=Label(f, text='Phone', width=15, font=('Calibri', 11, 'bold'))
    e3=Entry(f,textvariable=phone, width=25)
    l3.place(x=50, y=110)
    e3.place(x=200, y=110)

    l4=Label(f, text='Email', width=15, font=('Calibri', 11, 'bold'))
    e4=Entry(f,textvariable=email, width=25)
    l4.place(x=50, y=150)
    e4.place(x=200, y=150)

    l5=Label(f, text='Date Hired (MM-DD-YYYY)', width=20, font=('Calibri', 11, 'bold'))
    e5=Entry(f,textvariable=date, width=25)
    l5.place(x=50, y=190)
    e5.place(x=200, y=190)

    # Function to clear all entry fields and destroy the window
    def destroy_add_employee():
        e1.delete(0, END)
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        e5.delete(0, END)
        f.destroy()
        add_employee_window.destroy()

    # Function to add an employee to the database
    def add_employee():
        a_f_name = f_name.get()
        a_l_name = l_name.get()
        a_phone = phone.get()
        a_email = email.get()
        a_date = date.get()
        # Fix date formatting from MM-DD-YYYY to YYYY-MM-DD
        a_date = f'{a_date[6:]}-{a_date[:2]}-{a_date[3:5]}'

        # Insert employee into database
        conn.execute("insert into Employee (first_name, last_name, phone_number, email, hired_date) values (%s, %s, %s, %s, %s)",\
                      (a_f_name, a_l_name, a_phone, a_email, a_date))
        connect.commit()
        destroy_add_employee()
        display_info()

    add_button = Button(f, text="Add Employee", command=add_employee)
    add_button.place(x=200, y=250)

    cancel_button = Button(f, text="Cancel", command=destroy_add_employee)
    cancel_button.place(x=350, y=250)
# End: Add Employee function =========================

# Begin: Add Customer function =======================
def add_customer_data():
    # Create a new Toplevel window for adding a customer
    add_customer_window = tk.Toplevel(r)
    add_customer_window.title("Add Customer")
    add_customer_window.geometry("600x400")

    f = Frame(add_customer_window, width=600, height=400)
    f.pack()

    l1=Label(f, text='First Name', width=15, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=f_name, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)

    l2=Label(f, text='Last Name', width=15, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=l_name, width=25)
    l2.place(x=50, y=70)
    e2.place(x=200, y=70)

    l3=Label(f, text='Phone', width=15, font=('Calibri', 11, 'bold'))
    e3=Entry(f,textvariable=phone, width=25)
    l3.place(x=50, y=110)
    e3.place(x=200, y=110)

    l4=Label(f, text='Email', width=15, font=('Calibri', 11, 'bold'))
    e4=Entry(f,textvariable=email, width=25)
    l4.place(x=50, y=150)
    e4.place(x=200, y=150)

    def destroy_add_customer():
        e1.delete(0, END)
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        f.destroy()
        add_customer_window.destroy()

    def add_customer():
        a_f_name = f_name.get()
        a_l_name = l_name.get()
        a_phone = phone.get()
        a_email = email.get()

        # Insert customer into database
        conn.execute("insert into Customer (first_name, last_name, phone_number, email) values (%s, %s, %s, %s)", (a_f_name, a_l_name, a_phone, a_email))
        connect.commit()
        destroy_add_customer()
        display_info()

    add_button = Button(f, text="Add Customer", command=add_customer)
    add_button.place(x=250, y=200)
# End: Add Customer function =========================

# Begin: Add Location function =======================
def add_location_data():
    # Create a new Toplevel window for adding a location
    add_location_window = tk.Toplevel(r)
    add_location_window.title("Add Location")
    add_location_window.geometry("600x400")

    f = Frame(add_location_window, width=600, height=400)
    f.pack()

    l1=Label(f, text='Street Address', width=15, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=street_addr, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)

    l2=Label(f, text='City', width=8, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=city, width=25)
    l2.place(x=50, y=70)
    e2.place(x=200, y=70)

    l3=Label(f, text='State', width=8, font=('Calibri', 11, 'bold'))
    e3=Entry(f,textvariable=state, width=25)
    l3.place(x=50, y=110)
    e3.place(x=200, y=110)

    l4=Label(f, text='Zip', width=8, font=('Calibri', 11, 'bold'))
    e4=Entry(f,textvariable=zip, width=25)
    l4.place(x=50, y=150)
    e4.place(x=200, y=150)

    # Destroy the add location window
    def destroy_add_location():
        e1.delete(0, END)
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        f.destroy()
        add_location_window.destroy()

    # Add location to database
    def add_location():
        a_address = street_addr.get()
        a_city = city.get()
        a_state = state.get()
        a_zip = zip.get()

        # Insert location into database
        conn.execute("insert into Location (street_address, city, state, zip) values (%s, %s, %s, %s)", (a_address, a_city, a_state, a_zip))
        connect.commit()
        destroy_add_location()
        display_info()

    add_button = Button(f, text="Add Location", command=add_location)
    add_button.place(x=250, y=200)
# End: Add Location function =========================

# Begin: Add Service function =======================
def add_service_data():
    # Create a new Toplevel window for adding a service
    add_service_window = tk.Toplevel(r)
    add_service_window.title("Add Service")
    add_service_window.geometry("600x400")

    f = Frame(add_service_window, width=600, height=400)
    f.pack()

    l1=Label(f, text='Name', width=15, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=f_name, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)

    l2=Label(f, text='Price', width=15, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=phone, width=25)
    l2.place(x=50, y=70)
    e2.place(x=200, y=70)

    def destroy_add_service():
        e1.delete(0, END)
        e2.delete(0, END)
        f.destroy()
        add_service_window.destroy()

    def add_service():
        a_name = f_name.get()
        a_price = phone.get()

        # Insert service into database
        conn.execute("insert into Service (name, price) values (%s, %s)", (a_name, a_price))
        connect.commit()
        destroy_add_service()
        display_info()

    add_button = Button(f, text="Add Service", command=add_service)
    add_button.place(x=250, y=200)

# Begin: Add Data Function =======================
# Determines which add function to call based on the selected option
def add_data():
    match selected_option.get():
        case 'Employees':
            add_employee_data()
        case 'Customers':
            add_customer_data()
        case 'Locations':
            add_location_data()
        case 'Jobs':
            add_job_data()
        case 'Services':
            add_service_data()


# Update functions (Myles)

# Begin: Update Jobs Function =======================
def select_jobs(tree):
    curItem = tree.focus()
    values = tree.item(curItem, 'values')

    update_window = tk.Toplevel(r)
    update_window.title("Update")
    update_window.geometry("600x400")
   
    f = Frame(update_window, width=600, height=400)
    f.pack()
 

    l1=Label(f, text='ID', width=8, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=id, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)   
    
    l2=Label(f, text='Date (MM-DD-YYYY)', width=18, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=date, width=25)
    l2.place(x=50, y=70)
    e2.place(x=200, y=70)

    l3=Label(f, text='Time (HH:MM)', width=15, font=('Calibri', 11, 'bold'))
    e3=Entry(f,textvariable=time, width=25)
    l3.place(x=50, y=110)
    e3.place(x=200, y=110)
 
   
    l4=Label(f, text='Street Address', width=15, font=('Calibri', 11, 'bold'))
    e4=Entry(f,textvariable=street_addr, width=25)
    l4.place(x=50, y=150)
    e4.place(x=200, y=150)
 
   
    l5=Label(f, text='City', width=8, font=('Calibri', 11, 'bold'))
    e5=Entry(f,textvariable=city, width=25)
    l5.place(x=50, y=190)
    e5.place(x=200, y=190)
 

    l6=Label(f, text='State', width=8, font=('Calibri', 11, 'bold'))
    e6=Entry(f,textvariable=state, width=25)
    l6.place(x=50, y=230)
    e6.place(x=200, y=230)
 

    l7=Label(f, text='Zip', width=8, font=('Calibri', 11, 'bold'))
    e7=Entry(f,textvariable=zip, width=25)
    l7.place(x=50, y=270)
    e7.place(x=200, y=270)

    # Display current values in the entry fields
    temp_date = values[1].split('\n')[0]
    temp_time = values[1].split('\n')[1]
    temp_address = values[2].split('\n')
    temp_street_addr = temp_address[0]
    temp_city = temp_address[1].split(',')[0]
    temp_state = temp_address[1].split(',')[1][1:3]
    temp_zip = temp_address[1].split(',')[1][4:]
 
    e1.insert(0,values[0])
    e2.insert(0,temp_date)
    e3.insert(0,temp_time)
    e4.insert(0,temp_street_addr)
    e5.insert(0,temp_city)
    e6.insert(0,temp_state)
    e7.insert(0,temp_zip)
    def destroy_update():
        e1.delete(0,END)
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        e5.delete(0, END)
        e6.delete(0, END)
        e7.delete(0,END)
        f.destroy()
        update_window.destroy()
 
    def update_data():
        nonlocal e1, e2, e3, e4, e5, e6, e7, curItem, values
        a_id = id.get()
        a_address = street_addr.get()
        a_city = city.get()
        a_state = state.get()
        a_zip = zip.get()
        a_date = date.get()
        a_time = time.get()
        a_date = f'{a_date[6:]}-{a_date[:2]}-{a_date[3:5]}'
        a_datetime = f'{a_date} {a_time}:00'

        # Look up location id based on address
        conn.execute("select id from Location where street_address = %s and city = %s and state = %s and zip = %s",(a_address, a_city, a_state, a_zip))
        loc_id = conn.fetchone()
                
        conn.execute(
            'UPDATE Job SET id=%s, datetime=%s, location_id=%s WHERE id=%s',
                         (a_id, a_datetime, loc_id[0], values[0]))
 
        connect.commit()
        mb.showinfo('SUCCESS', 'Job data updated')
     
        destroy_update()
        display_info()

    def add_service():
        add_service_window = tk.Toplevel(r)
        add_service_window.title("Add Service")
        add_service_window.geometry("300x200")

        service_label = tk.Label(add_service_window, text="Service Name:")
        service_label.pack()
        service_entry = tk.Entry(add_service_window)
        service_entry.pack()

        def save_service():
            service_name = service_entry.get()
            conn.execute("select * from Service where name = %s", (service_name,))
            service = conn.fetchone()
            if service is None:
                mb.showerror("ERROR", "Service does not exist")
            else:
                conn.execute("select * from JobService where job_id = %s and service_name = %s", (values[0], service_name))
                job_service = conn.fetchone()
                if job_service is not None:
                    mb.showerror("ERROR", "Service already added")
                else:
                    conn.execute("insert into JobService (job_id, service_name) values (%s, %s)", (values[0], service_name))
                    connect.commit()
                    mb.showinfo("SUCCESS", "Service added")
                    add_service_window.destroy()
                    display_info()

        save_service_button = tk.Button(add_service_window, text="Save", command=lambda: save_service())
        save_service_button.pack()

    def remove_service():
        remove_service_window = tk.Toplevel(r)
        remove_service_window.title("Remove Service")
        remove_service_window.geometry("300x200")

        conn.execute("select service_name from JobService where job_id = %s", (values[0],))
        services = conn.fetchall()
        service_list = []
        for service in services:
            service_list.append(service[0])

        print(service_list)

        service_label = tk.Label(remove_service_window, text="Service Name:")
        service_label.pack()
        selected_service = tk.StringVar(remove_service_window)
        selected_service.set(service_list[0])
        service_menu = tk.OptionMenu(remove_service_window, selected_service, *service_list)
        service_menu.pack()

        def save_service():
            print("saving service")
            service_name = selected_service.get()
            conn.execute("delete from JobService where job_id = %s and service_name = %s", (values[0], service_name))
            connect.commit()
            mb.showinfo("SUCCESS", "Service removed")
            remove_service_window.destroy()
            destroy_update()
            display_info()

        save_service_button = tk.Button(remove_service_window, text="Save", command=lambda: save_service())
        save_service_button.pack()

    savebutton = tk.Button(f, text="Submit", command=update_data)
    savebutton.configure(font=('Calibri', 11, 'bold'))
    savebutton.place(x=100, y=360)

    cancelbutton = tk.Button(f, text="Cancel", command=destroy_update)
    cancelbutton.configure(font=('Calibri', 11, 'bold'))
    cancelbutton.place(x=200, y=360)

    add_servicebutton = tk.Button(f, text="Add Service", command=lambda: add_service())
    add_servicebutton.configure(font=('Calibri', 11, 'bold'))
    add_servicebutton.place(x=350, y=360)

    remove_servicebutton = tk.Button(f, text="Remove Service", command=lambda: remove_service())
    remove_servicebutton.configure(font=('Calibri', 11, 'bold'))
    remove_servicebutton.place(x=450, y=360)
# End: Update Jobs Function =============================

# Begin: Update Employees Function (Myles) =======================
def select_employees(tree):
    curItem = tree.focus()
    values = tree.item(curItem, 'values')

    update_window = tk.Toplevel(r)
    update_window.title("Update")
    update_window.geometry("600x400")
   
    f = Frame(update_window, width=600, height=400)
    f.pack()
 
    # Add labels and entry fields for ID, last name, first name, phone, email, and date hired
    l1=Label(f, text='ID', width=8, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=id, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)   
    
    l2=Label(f, text='Last Name', width=18, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=l_name, width=25)
    l2.place(x=50, y=70)
    e2.place(x=200, y=70)

    l3=Label(f, text='First Name', width=15, font=('Calibri', 11, 'bold'))
    e3=Entry(f,textvariable=f_name, width=25)
    l3.place(x=50, y=110)
    e3.place(x=200, y=110)
 
   
    l4=Label(f, text='Phone', width=15, font=('Calibri', 11, 'bold'))
    e4=Entry(f,textvariable=phone, width=25)
    l4.place(x=50, y=150)
    e4.place(x=200, y=150)
 
   
    l5=Label(f, text='Email', width=8, font=('Calibri', 11, 'bold'))
    e5=Entry(f,textvariable=email, width=25)
    l5.place(x=50, y=190)
    e5.place(x=200, y=190)
 

    l6=Label(f, text='Date Hired (MM-DD-YYYY)', width=18, font=('Calibri', 11, 'bold'))
    e6=Entry(f,textvariable=date, width=25)
    l6.place(x=50, y=230)
    e6.place(x=200, y=230)
 
    # Display current values in the entry fields
    e1.insert(0,values[0])
    e2.insert(0,values[1])
    e3.insert(0,values[2])
    e4.insert(0,values[3])
    e5.insert(0,values[4])
    e6.insert(0,values[6])

    # Function to clear all entry fields and destroy the window
    def destroy_update():
        e1.delete(0,END)
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        e5.delete(0, END)
        e6.delete(0,END)
        f.destroy()
        update_window.destroy()

    # Function to update employee data in the database
    def update_data():
        nonlocal e1, e2, e3, e4, e5, e6, curItem, values
        e_id = id.get()
        e_lname = l_name.get()
        e_fname = f_name.get()
        e_phone = phone.get()
        e_email = email.get()
        e_date = date.get()
        e_date = f'{e_date[6:]}-{e_date[:2]}-{e_date[3:5]}'

        conn.execute(
            'UPDATE Employee SET id=%s, last_name=%s, first_name=%s, phone_number=%s, email=%s, hired_date=%s WHERE id=%s',
                         (e_id, e_lname, e_fname, e_phone, e_email, e_date, values[0]))
 
        connect.commit()
        mb.showinfo('SUCCESS', 'Employee data updated')
     
        destroy_update()
        display_info()

    # Function to add a job to the employee
    def add_job():
        add_jobs_window = tk.Toplevel(r)
        add_jobs_window.title("Add Job")
        add_jobs_window.geometry("300x200")

        job_label = tk.Label(add_jobs_window, text="Job ID:")
        job_label.pack()
        job_entry = tk.Entry(add_jobs_window)
        job_entry.pack()

        def save_job():
            job_id = job_entry.get()
            conn.execute("select * from Job where id = %s", (job_id,))
            job = conn.fetchone()
            if job is None:
                mb.showerror("ERROR", "Job does not exist")
            else:
                conn.execute("select * from EmployeeJob where employee_id = %s and job_id = %s", (values[0], job_id))
                employee_job = conn.fetchone()
                if employee_job is not None:
                    mb.showerror("ERROR", "Job already added")
                else:
                    conn.execute("insert into EmployeeJob (employee_id, job_id) values (%s, %s)", (values[0], job_id))
                    connect.commit()
                    mb.showinfo("SUCCESS", "Job added")
                    add_jobs_window.destroy()
                    destroy_update()
                    display_info()

        save_job_button = tk.Button(add_jobs_window, text="Save", command=lambda: save_job())
        save_job_button.pack()

    # Function to remove a job from the employee
    def remove_job():
        remove_jobs_window = tk.Toplevel(r)
        remove_jobs_window.title("Remove Job")
        remove_jobs_window.geometry("300x200")

        conn.execute("select job_id from EmployeeJob where employee_id = %s", (values[0],))
        jobs = conn.fetchall()
        job_list = []
        for job in jobs:
            job_list.append(job[0])

        print(job_list)

        job_label = tk.Label(remove_jobs_window, text="Job ID:")
        job_label.pack()
        selected_job = tk.StringVar(remove_jobs_window)
        selected_job.set(job_list[0])
        job_menu = tk.OptionMenu(remove_jobs_window, selected_job, *job_list)
        job_menu.pack()

        # Function to save the job removal
        def save_job():
            print("saving job")
            job_id = selected_job.get()
            conn.execute("delete from EmployeeJob where employee_id = %s and job_id = %s", (values[0], job_id))
            connect.commit()
            mb.showinfo("SUCCESS", "Job removed")
            remove_jobs_window.destroy()
            destroy_update()
            display_info()

        save_job_button = tk.Button(remove_jobs_window, text="Save", command=lambda: save_job())
        save_job_button.pack()

    # Create all buttons for the update window
    savebutton = tk.Button(f, text="Submit", command=update_data)
    savebutton.configure(font=('Calibri', 11, 'bold'))
    savebutton.place(x=100, y=360)

    cancelbutton = tk.Button(f, text="Cancel", command=destroy_update)
    cancelbutton.configure(font=('Calibri', 11, 'bold'))
    cancelbutton.place(x=200, y=360)

    add_jobsbutton = tk.Button(f, text="Add Job", command=lambda: add_job())
    add_jobsbutton.configure(font=('Calibri', 11, 'bold'))
    add_jobsbutton.place(x=350, y=360)

    remove_jobsbutton = tk.Button(f, text="Remove Job", command=lambda: remove_job())
    remove_jobsbutton.configure(font=('Calibri', 11, 'bold'))
    remove_jobsbutton.place(x=450, y=360)
# End: Update Employees Function =========================
 
# Begin: Update Customers Function =======================
def select_customers(tree):
    curItem = tree.focus()
    values = tree.item(curItem, 'values')

    update_window = tk.Toplevel(r)
    update_window.title("Update")
    update_window.geometry("600x400")
   
    f = Frame(update_window, width=600, height=400)
    f.pack()
 

    l1=Label(f, text='ID', width=8, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=id, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)   
    
    l2=Label(f, text='Last Name', width=18, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=l_name, width=25)
    l2.place(x=50, y=70)
    e2.place(x=200, y=70)

    l3=Label(f, text='First Name', width=15, font=('Calibri', 11, 'bold'))
    e3=Entry(f,textvariable=f_name, width=25)
    l3.place(x=50, y=110)
    e3.place(x=200, y=110)
 
   
    l4=Label(f, text='Phone', width=15, font=('Calibri', 11, 'bold'))
    e4=Entry(f,textvariable=phone, width=25)
    l4.place(x=50, y=150)
    e4.place(x=200, y=150)
 
   
    l5=Label(f, text='Email', width=8, font=('Calibri', 11, 'bold'))
    e5=Entry(f,textvariable=email, width=25)
    l5.place(x=50, y=190)
    e5.place(x=200, y=190)
 

    # Display current values in the entry fields
    e1.insert(0,values[0])
    e2.insert(0,values[1])
    e3.insert(0,values[2])
    e4.insert(0,values[3])
    e5.insert(0,values[4])

    # Function to destroy the update window
    def destroy_update():
        e1.delete(0,END)
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        e5.delete(0, END)
        f.destroy()
        update_window.destroy()

    # Function to update the customer data
    def update_data():
        nonlocal e1, e2, e3, e4, e5, curItem, values
        c_id = id.get()
        c_lname = l_name.get()
        c_fname = f_name.get()
        c_phone = phone.get()
        c_email = email.get()

        conn.execute(
            'UPDATE Customer SET id=%s, last_name=%s, first_name=%s, phone=%s, email=%s WHERE id=%s',
                         (c_id, c_lname, c_fname, c_phone, c_email, values[0]))
 
        connect.commit()
        mb.showinfo('SUCCESS', 'Customer data updated')
     
        destroy_update()
        display_info()

    # Function to add a location to the customer
    def add_location():
        add_location_window = tk.Toplevel(r)
        add_location_window.title("Add Location")
        add_location_window.geometry("300x400")

        street_addr_label = tk.Label(add_location_window, text="Street Address:")
        street_addr_label.pack()
        street_addr_entry = tk.Entry(add_location_window)
        street_addr_entry.pack()
        city_label = tk.Label(add_location_window, text="City:")
        city_label.pack()
        city_entry = tk.Entry(add_location_window)
        city_entry.pack()
        state_label = tk.Label(add_location_window, text="State:")
        state_label.pack()
        state_entry = tk.Entry(add_location_window)
        state_entry.pack()
        zip_label = tk.Label(add_location_window, text="Zip:")
        zip_label.pack()
        zip_entry = tk.Entry(add_location_window)
        zip_entry.pack()

        # Function to save the location to the customer
        def save_location():
            
            conn.execute("select id from Location where street_address = %s and city = %s and state = %s and zip = %s", (street_addr_entry.get(), city_entry.get(), state_entry.get(), zip_entry.get()))
            location = conn.fetchone()
            if location is None:
                add_loc = mb.askyesno("ERROR", "Location does not exist. Add location first?")
                if add_loc == tk.YES:
                    conn.execute("insert into Location (street_address, city, state, zip) values (%s, %s, %s, %s)", (street_addr_entry.get(), city_entry.get(), state_entry.get(), zip_entry.get()))
                    connect.commit()
                    conn.execute("select id from Location where street_address = %s and city = %s and state = %s and zip = %s", (street_addr_entry.get(), city_entry.get(), state_entry.get(), zip_entry.get()))
                    location = conn.fetchone()
                    conn.execute("select * from CustomerLocation where customer_id = %s and location_id = %s", (values[0], location[0]))
                    customer_location = conn.fetchone()
                    if customer_location is not None:
                        mb.showerror("ERROR", "Location already added")
                    else:
                        conn.execute("insert into CustomerLocation (customer_id, location_id) values (%s, %s)", (values[0], location[0]))
                        connect.commit()
                        mb.showinfo("SUCCESS", "Location added")
                        add_location_window.destroy()
                        display_info()
                else:
                    add_location_window.destroy()
            else:
                conn.execute("select * from CustomerLocation where customer_id = %s and location_id = %s", (values[0], location[0]))
                customer_location = conn.fetchone()
                if customer_location is not None:
                    mb.showerror("ERROR", "Location already added")
                else:
                    conn.execute("insert into CustomerLocation (customer_id, location_id) values (%s, %s)", (values[0], location[0]))
                    connect.commit()
                    mb.showinfo("SUCCESS", "Location added")
                    add_location_window.destroy()
                    display_info()

        save_location_button = tk.Button(add_location_window, text="Save", command=lambda: save_location())
        save_location_button.pack()

    # Function to remove a location from the customer
    def remove_location():
        remove_location_window = tk.Toplevel(r)
        remove_location_window.title("Remove Location")
        remove_location_window.geometry("300x200")

        conn.execute("select location_id from CustomerLocation where customer_id = %s", (values[0],))
        locations = conn.fetchall()
        location_list = []
        display_list = []
        for location in locations:
            # Get the street address of the location
            conn.execute("select street_address from Location where id = %s", (location[0],))
            addr = conn.fetchone()
            display_list.append(addr[0])
            location_list.append(location[0])

        location_label = tk.Label(remove_location_window, text="Location:")
        location_label.pack()
        selected_location = tk.StringVar(remove_location_window)
        selected_location.set(display_list[0])
        location_menu = tk.OptionMenu(remove_location_window, selected_location, *display_list)
        location_menu.pack()

        # Function to save the location removal
        def save_location():
            print("saving location")
            addr_index = selected_location.get()[0]
            location_id = location_list[display_list.index(addr_index)]
            conn.execute("delete from CustomerLocation where customer_id = %s and location_id = %s", (values[0], location_id))
            connect.commit()
            mb.showinfo("SUCCESS", "Location removed")
            remove_location_window.destroy()
            display_info()

        save_location_button = tk.Button(remove_location_window, text="Save", command=lambda: save_location())
        save_location_button.pack()

    savebutton = tk.Button(f, text="Submit", command=update_data)
    savebutton.configure(font=('Calibri', 11, 'bold'))
    savebutton.place(x=50, y=360)

    cancelbutton = tk.Button(f, text="Cancel", command=destroy_update)
    cancelbutton.configure(font=('Calibri', 11, 'bold'))
    cancelbutton.place(x=150, y=360)

    add_locationbutton = tk.Button(f, text="Add Location", command=lambda: add_location())
    add_locationbutton.configure(font=('Calibri', 11, 'bold'))
    add_locationbutton.place(x=300, y=360)

    remove_locationbutton = tk.Button(f, text="Remove Location", command=lambda: remove_location())
    remove_locationbutton.configure(font=('Calibri', 11, 'bold'))
    remove_locationbutton.place(x=450, y=360)
# End: Update Customers Function =========================

# Begin: Update Locations Function =======================
def select_locations(tree):
    curItem = tree.focus()
    values = tree.item(curItem, 'values')

    update_window = tk.Toplevel(r)
    update_window.title("Update")
    update_window.geometry("600x400")
   
    f = Frame(update_window, width=600, height=400)
    f.pack()
 
    # Create labels and entry fields for the location data
    l1=Label(f, text='ID', width=8, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=id, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)   
    
    l2=Label(f, text='Street Address', width=18, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=street_addr, width=25)
    l2.place(x=50, y=70)
    e2.place(x=200, y=70)

    l3=Label(f, text='City', width=15, font=('Calibri', 11, 'bold'))
    e3=Entry(f,textvariable=city, width=25)
    l3.place(x=50, y=110)
    e3.place(x=200, y=110)
 
   
    l4=Label(f, text='State', width=15, font=('Calibri', 11, 'bold'))
    e4=Entry(f,textvariable=state, width=25)
    l4.place(x=50, y=150)
    e4.place(x=200, y=150)
 
   
    l5=Label(f, text='Zip', width=8, font=('Calibri', 11, 'bold'))
    e5=Entry(f,textvariable=zip, width=25)
    l5.place(x=50, y=190)
    e5.place(x=200, y=190)
 

    # Display current values in the entry fields
    e1.insert(0,values[0])
    e2.insert(0,values[1])
    e3.insert(0,values[2])
    e4.insert(0,values[3])
    e5.insert(0,values[4])

    def destroy_update():
        e1.delete(0,END)
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        e5.delete(0, END)
        f.destroy()
        update_window.destroy()

    def update_data():
        nonlocal e1, e2, e3, e4, e5, curItem, values
        l_id = id.get()
        l_address = street_addr.get()
        l_city = city.get()
        l_state = state.get()
        l_zip = zip.get()

        conn.execute(
            'UPDATE Location SET id=%s, street_address=%s, city=%s, state=%s, zip=%s WHERE id=%s',
                         (l_id, l_address, l_city, l_state, l_zip, values[0]))
 
        connect.commit()
        mb.showinfo('SUCCESS', 'Location data updated')
     
        destroy_update()
        display_info()

    # Function to add a customer to the location
    def add_customer():
        add_customer_window = tk.Toplevel(r)
        add_customer_window.title("Add Customer")
        add_customer_window.geometry("300x200")

        customer_label = tk.Label(add_customer_window, text="Customer ID:")
        customer_label.pack()
        customer_entry = tk.Entry(add_customer_window)
        customer_entry.pack()

        # Function to save the customer to the location
        def save_customer():
            customer_id = customer_entry.get()
            conn.execute("select * from Customer where id = %s", (customer_id,))
            customer = conn.fetchone()
            if customer is None:
                mb.showerror("ERROR", "Customer does not exist")
            else:
                conn.execute("select * from CustomerLocation where location_id = %s and customer_id = %s", (values[0], customer_id))
                customer_location = conn.fetchone()
                if customer_location is not None:
                    mb.showerror("ERROR", "Customer already added")
                else:
                    conn.execute("insert into CustomerLocation (location_id, customer_id) values (%s, %s)", (values[0], customer_id))
                    connect.commit()
                    mb.showinfo("SUCCESS", "Customer added")
                    add_customer_window.destroy()
                    destroy_update()
                    display_info()

        save_customer_button = tk.Button(add_customer_window, text="Save", command=lambda: save_customer())
        save_customer_button.pack()

    # Function to remove a customer from the location
    def remove_customer():
        remove_customer_window = tk.Toplevel(r)
        remove_customer_window.title("Remove Customer")
        remove_customer_window.geometry("300x200")

        conn.execute("select customer_id from CustomerLocation where location_id = %s", (values[0],))
        customers = conn.fetchall()
        customer_list = []
        for customer in customers:
            customer_list.append(customer[0])

        print(customer_list)

        customer_label = tk.Label(remove_customer_window, text="Customer ID:")
        customer_label.pack()
        selected_customer = tk.StringVar(remove_customer_window)
        selected_customer.set(customer_list[0])
        customer_menu = tk.OptionMenu(remove_customer_window, selected_customer, *customer_list)
        customer_menu.pack()

        # Function to save the customer removal
        def save_customer():
            print("saving customer")
            customer_id = selected_customer.get()
            conn.execute("delete from CustomerLocation where location_id = %s and customer_id = %s", (values[0], customer_id))
            connect.commit()
            mb.showinfo("SUCCESS", "Customer removed")
            remove_customer_window.destroy()
            destroy_update()
            display_info()

        save_customer_button = tk.Button(remove_customer_window, text="Save", command=lambda: save_customer())
        save_customer_button.pack()

    savebutton = tk.Button(f, text="Submit", command=update_data)
    savebutton.configure(font=('Calibri', 11, 'bold'))
    savebutton.place(x=50, y=360)

    cancelbutton = tk.Button(f, text="Cancel", command=destroy_update)
    cancelbutton.configure(font=('Calibri', 11, 'bold'))
    cancelbutton.place(x=150, y=360)

    add_customerbutton = tk.Button(f, text="Add Customer", command=lambda: add_customer())
    add_customerbutton.configure(font=('Calibri', 11, 'bold'))
    add_customerbutton.place(x=300, y=360)

    remove_customerbutton = tk.Button(f, text="Remove Customer", command=lambda: remove_customer())
    remove_customerbutton.configure(font=('Calibri', 11, 'bold'))
    remove_customerbutton.place(x=450, y=360)
# End: Update Locations Function =========================

# Begin: Update Services Function =======================
def select_services(tree):
    curItem = tree.focus()
    values = tree.item(curItem, 'values')

    update_window = tk.Toplevel(r)
    update_window.title("Update")
    update_window.geometry("600x400")
   
    f = Frame(update_window, width=600, height=400)
    f.pack()
 
    # Create labels and entry fields for the service data
    l1=Label(f, text='Name', width=8, font=('Calibri', 11, 'bold'))
    e1=Entry(f,textvariable=name, width=25)
    l1.place(x=50, y=30)
    e1.place(x=200, y=30)   

    l2=Label(f, text='Price', width=15, font=('Calibri', 11, 'bold'))
    e2=Entry(f,textvariable=price, width=25)
    l2.place(x=50, y=110)
    e2.place(x=200, y=110)
 
    # Display current values in the entry fields
    e1.insert(0,values[0])
    e2.insert(0,values[1])

    def destroy_update():
        e1.delete(0,END)
        e2.delete(0, END)
        f.destroy()
        update_window.destroy()

    def update_data():
        nonlocal e1, e2, curItem, values
        s_name = name.get()
        s_price = price.get()

        conn.execute(
            'UPDATE Service SET name=%s, price=%s WHERE name=%s',
                         (s_name, s_price, values[0]))
 
        connect.commit()
        mb.showinfo('SUCCESS', 'Service data updated')
     
        destroy_update()
        display_info()

    savebutton = tk.Button(f, text="Submit", command=update_data)
    savebutton.configure(font=('Calibri', 11, 'bold'))
    savebutton.place(x=50, y=360)

    cancelbutton = tk.Button(f, text="Cancel", command=destroy_update)
    cancelbutton.configure(font=('Calibri', 11, 'bold'))
    cancelbutton.place(x=150, y=360)
# End: Update Services Function =========================

# Select which update function to call based on the selected option
def select_update(tree):
    selected_menu = selected_option.get()
    if selected_menu == 'Employees':
        select_employees(tree)
    elif selected_menu == 'Jobs':
        select_jobs(tree)
    elif selected_menu == 'Customers':
        select_customers(tree)
    elif selected_menu == 'Locations':
        select_locations(tree)
    elif selected_menu == 'Services':
        select_services(tree)
    else:
        mb.showerror("ERROR", "Update not available for selected option")

# Begin: Delete function (Tyler) =======================
def delete_data(tree, selection):
    # Delete record after confirmation
    def confirm_delete():
        selected_item = tree.selection()[0]
        uid=tree.item(selected_item)['values'][0]
        del_query = f'DELETE from {selection} where id = %s'
        sel_data=(uid,)
        conn.execute(del_query, sel_data)
        connect.commit()
        tree.delete(selected_item)
        mb.showinfo("SUCCESS",f'{selection} data deleted')

    # Display a confirmation dialog box
    response = mb.askyesno("Confirmation", f"Are you sure you want to delete this {selection} data?")

    if response:
        # If user confirms deletion, call the confirm_delete function
        confirm_delete()
# End: Delete Function====================


# GUI Layout with table and buttons

# Checkbox variables
chk_var_jobs = tk.BooleanVar()
chk_var_locs = tk.BooleanVar()

# Create checkboxes
checkbox_jobs = tk.Checkbutton(r, text="Include Past Jobs", variable=chk_var_jobs, command=lambda:display_info())
checkbox_jobs.place(x=150, y=10)
checkbox_locs = tk.Checkbutton(r, text="Include Locations with no Jobs", variable=chk_var_locs, command=lambda:display_info())
# checkbox_locs is placed when Locations is selected in the dropdown menu

# Create buttons
insertbutton = tk.Button(r,text='Insert', command=lambda:add_data())
insertbutton.configure(font=('calibri', 14, 'bold'), highlightbackground='#3E4149')
insertbutton.place(x=160, y=650)

updatebutton = tk.Button(r,text='Update', command=lambda:select_update(tree))
updatebutton.configure(font=('calibri', 14, 'bold'), highlightbackground='#3E4149')
updatebutton.place(x=310, y=650)

deletebutton = tk.Button(r,text='Delete', command=lambda:delete_data(tree, selected_option.get()[:-1]))
deletebutton.configure(font=('calibri', 14, 'bold'), highlightbackground='#3E4149')
deletebutton.place(x=460, y=650)

receiptbutton = tk.Button(r,text='Get Receipt', command=lambda:get_receipt(tree))
receiptbutton.configure(font=('calibri', 14, 'bold'), highlightbackground='#3E4149')
receiptbutton.place(x=610, y=650)

# Create a dropdown menu
options = ['Jobs', 'Employees', 'Customers', 'Locations', 'Services']
selected_option = tk.StringVar(r)
selected_option.set(options[0])  # Set default option
dropdown_menu = tk.OptionMenu(r, selected_option, *options, command=display_info()) 
dropdown_menu.place(x=30, y=10)

# Add filter button
filter_button = tk.Button(r, text='Filter', command=lambda:filter_info())
filter_button.configure(font=('calibri', 14, 'bold'), highlightbackground='#3E4149')
filter_button.place(x=900, y=10)

# Whenever a display setting changes, update the display
chk_var_jobs.trace_add("write", lambda *args: display_info())
chk_var_locs.trace_add("write", lambda *args: display_info())
selected_option.trace_add("write", lambda *args: display_info())

r.mainloop()
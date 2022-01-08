### BANK MANAGEMENT SYSTEM CODE ###
## Team: Mohamed Firas Adil, Goppinath Saravnan, George V
## 12 A
import mysql.connector as ms
import tkinter as tk
from sys import exit

mysqlpassword = 'firas123'  # enter your password here
mydb = ms.connect(host='localhost', user='root', password=mysqlpassword)

#  checking connection status
if mydb.is_connected():
    print('Connection established')
else:
    print('Unable to establish a connection with mysql')
    exit()

# initiation - table creation
cursor = mydb.cursor()
cursor.execute('create database if not exists bankdata')
cursor.execute('use bankdata')
cursor.execute('create table if not exists accountdata(accno int(4) primary key, password varchar(70), name varchar(30), balance int)')
cursor.execute('create table if not exists transactiondata(accno int(4), amount int, category varchar(35))')
mydb.commit()

# declaring some important variables
userdata = []
starting_accno = 1000
salt = '@#xqd#$'
x = 4

# basic functions
def encode(word, x):  #  encoding inputted password so that databse doesnt store plain text passwords
        encoded = ''
        for i in word:
            encoded += str(ord(i)+x)
        return encoded

def passwordcheck(passw, store):  #  checks if password entry is correct - used for chenging password
    if encode(passw+salt, x) == store:
        return True
    else:
        return False

def assignbankno():  #  assigns the next available bank account number by scanning the database
    cursor.execute('select max(accno) from accountdata')
    num = cursor.fetchone()
    if num[0] is None:
        return 1001
    else:
        return num[0]+1

def endpgm(n=None):  #  Ends the program
    master.destroy()
    try:
        popup.destroy()
    except NameError:
        None
    mydb.close()
    exit()

# general tkinter functions
def clearscreen():  # clears the tkinter window
    itemlist = master.winfo_children()
    for item in itemlist:
        if isinstance(item, tk.Menu):  # checking if widget is the top menubar to avoid removal
            continue
        else:
            item.destroy()

def popupmsg(msg):  #  Reusable tkinter messagebox for error warnings
    popup = tk.Tk()
    popup.wm_title("Warning Message")
    tk.Label(popup, text=msg).grid(sticky=tk.N, pady=10)
    tk.Button(popup, text="Ok", command=popup.destroy).grid(pady=10, padx=5)
    popup.mainloop()

# menu creation
def menu():
    if userdata == []:
        popupmsg('Invalid details, account not found\n  Log in.')
    else:
        clearscreen()
        pdx = 245
        w = 18
        pdy = (8, 0)
        tk.Button(master, text='Log Out', command=logout).grid(padx=10, pady=10, sticky=tk.W)
        tk.Button(master, text='Deposit money', width=w, command=depositgrid).grid(padx=pdx, pady=(50, 0))
        tk.Button(master, text='Withdraw money', width=w, command=withdrawgrid).grid(padx=pdx, pady=pdy)
        tk.Button(master, text='Money transfer', width=w, command=transfergrid).grid(padx=pdx, pady=pdy)
        tk.Button(master, text='View account details', width=w, command=accountdetailsgrid).grid(padx=pdx, pady=pdy)
        tk.Button(master, text='Transaction history', width=w, command=historygrid).grid(padx=pdx, pady=pdy)
        tk.Button(master, text='Change account details', width=w, command=editdetailsgrid).grid(padx=pdx, pady=pdy)
        tk.Button(master, text='Loan', width=w, command=loanmenu).grid(padx=pdx, pady=pdy)


# LOG OUT
def logout():
    global userdata
    userdata = []
    initialize()


# DEPOSIT
def deposit(amount):
    if amount.strip().isdigit():
        amount = int(amount)
        cursor.execute(f'update accountdata set balance=balance+ {amount} where accno = {userdata[0]} ')
        cursor.execute(f'insert into transactiondata values( {userdata[0]}, {amount} ,  "deposit" )')
        mydb.commit()
        userdata[3] += amount
        depositgrid()
        return True
    else:
        popupmsg('Enter a valid number')
        return False

def depositgrid():
    clearscreen()
    pdx = 270
    tk.Button(master, text='Back', command=menu).grid(padx=10, pady=10, sticky=tk.W)
    tk.Label(master, text=f'Balance: \n{userdata[3]:,} ').grid(padx=pdx, pady=(75, 0))
    tk.Label(master, text='Deposit amount: ').grid(padx=pdx, pady=(25, 0))
    amt = tk.Entry(master, width=20)
    amt.grid(padx=pdx)
    amt.bind('<Return>', (lambda function: deposit(amt.get())))
    tk.Button(master, text='Deposit', command=lambda: deposit(amt.get())).grid(padx=pdx, pady=(5, 0))


# WITHDRAW
def withdraw(amount):
    if amount.strip().isdigit():
        amount = int(amount)
        if userdata[3] < amount:
            return False
        cursor.execute(f'select balance from accountdata where accno={userdata[0]}')
        if cursor.fetchone()[0] < amount:
            popupmsg('Error you do not have enough balance to complete this transaction')
            return False
        cursor.execute(f'update accountdata set balance=balance - {amount} where accno = {userdata[0]} ')
        amount = amount - (2 * (amount))
        cursor.execute(f'insert into transactiondata values({userdata[0]}, {amount} ,  "withdrawal" )')
        mydb.commit()
        userdata[3] += amount
        withdrawgrid()
        return True
    else:
        popupmsg('Enter a valid number')
        return False

def withdrawgrid():
    clearscreen()
    pdx = 270
    tk.Button(master, text='Back', command=menu).grid(padx=10, pady=10, sticky=tk.W)
    tk.Label(master, text=f'Balance: \n{userdata[3]:,} ').grid(padx=pdx, pady=(75, 0))
    tk.Label(master, text='Withdraw amount: ').grid(padx=pdx, pady=(25, 0))
    amt = tk.Entry(master,width=20)
    amt.grid(padx=pdx)
    amt.bind('<Return>', (lambda function: withdraw(amt.get())))
    tk.Button(master, text='Withdraw', command=lambda: withdraw(amt.get())).grid(padx=pdx, pady=(5, 0))


# MONEY TRANSFER
def moneytransfer(acc2no, amount):
    if amount.strip().isdigit() and acc2no.strip().isdigit() and amount.strip()!='0':
        amount, acc2no = int(amount), int(acc2no)
        cursor.execute(f'select balance from accountdata where accno={userdata[0]}')
        if cursor.fetchone()[0] < amount:
            popupmsg('Error you do not have enough balance to complete this transaction')
            return False
        cursor.execute(f'select name from accountdata where accno={acc2no}')
        if cursor.fetchone() is None:
            popupmsg('Account doesnt exist')
            return False
        cursor.execute(f'update accountdata set balance=balance + {amount} where accno = {acc2no} ')
        cursor.execute(f'insert into transactiondata values( {acc2no}, {amount} ,  "money transfer" )')
        cursor.execute(f'update accountdata set balance=balance - {amount} where accno = {userdata[0]} ')
        amount = amount - (2 * (amount))
        cursor.execute(f'insert into transactiondata values( {userdata[0]}, {amount} ,  "money transfer" )')
        mydb.commit()
        userdata[3] += amount
        menu()
        return True
    else:
        popupmsg('Enter a valid number')
        return False

def transfergrid():
    clearscreen()
    pdx = 260
    tk.Button(master, text='Back', command=menu).grid(padx=10, pady=10, sticky=tk.W)
    tk.Label(master, text='Transfer to an existing account').grid(padx=pdx, pady=(75, 0))
    tk.Label(master, text='Recipient account number: ').grid(padx=pdx, pady=(25, 0))
    acc2no = tk.Entry(master, width=20)
    acc2no.grid(padx=pdx)
    tk.Label(master,text='Amount: ').grid(padx=pdx, pady=(25, 0))
    amt = tk.Entry(master, width=20)
    amt.grid(padx=pdx)
    amt.bind('<Return>', (lambda function: moneytransfer(acc2no.get(), amt.get())))
    tk.Button(master, text='Transfer', command=lambda: moneytransfer(acc2no.get(), amt.get())).grid(padx=pdx, pady=(5, 0))


# TRANSACTION HISTORY
def transactionhistory():
    cursor.execute(f'select * from transactiondata where accno = {userdata[0]}')
    return cursor.fetchall()

def historygrid():
    clearscreen()
    tk.Button(master, text='Back', command=menu).grid(padx=10, pady=10, sticky=tk.W)
    data = transactionhistory()
    limit = len(data)
    if limit > 12:
        limit -= 12
        data = data[limit:]
    data.insert(0, (1001, 'Amount', 'Reason'))
    for i in data:
        tk.Label(master, text=f'{i[1]} \t\t\t {i[2].title()}').grid(pady=(5, 0), sticky=tk.W, padx=210)


# ACCOUNT DETAILS
def accountdetailsgrid():
    clearscreen()
    pdx = 240
    tk.Button(master, text='Back', command=menu).grid(padx=10, pady=10, sticky=tk.W)
    tk.Label(master, text=f'Name: {userdata[2].title()}').grid(padx = pdx, pady = (135, 0), sticky=tk.W)
    tk.Label(master, text=f'Account Number: {userdata[0]}').grid(padx=pdx, pady=(2, 0), sticky=tk.W)
    tk.Label(master, text=f'Balance: {userdata[3]:,}').grid(padx=pdx, pady=(2, 0), sticky=tk.W)


# LOAN SCREENS #
# loan menu
def loanmenu():
    clearscreen()
    pdx = 260
    tk.Button(master, text='Back', command=menu).grid(padx=10, pady=10, sticky=tk.W)
    tk.Button(master, text='Loan Application', command=loanapp).grid(padx=pdx, pady=(150, 20))
    tk.Button(master, text='Loan Repayment', command=loanrepayment).grid(padx=pdx)

def unpaidloan():  #  checks if there is an unpaid loan in this account by going through the transaction history
    cursor.execute(f'select sum(amount) from transactiondata where accno={userdata[0]} and category="loan" ')
    total = cursor.fetchone()[0]
    if total is None or int(total) == 0:
        return 'No existing loans'
    cursor.execute(f'select sum(amount) from transactiondata where accno={userdata[0]} and category="loan repayment" ')
    repaid = cursor.fetchone()[0]
    if repaid == None or int(repaid) == 0:
        return int(total)
    return int(total) + int(repaid)

# loan application
def sqlapp(amt):
    if amt.strip().isdigit() and amt.strip() != '0':
        amt = int(amt)
        if amt > userdata[3]:
            popupmsg('The bank does not approve loans larger\n than the bank account balance.')
            return False
        loanstatus = unpaidloan()
        if loanstatus == 0 or loanstatus == 'No existing loans':
            cursor.execute(f'update accountdata set balance=balance+ {amt} where accno = {userdata[0]} ')
            cursor.execute(f'insert into transactiondata values( {userdata[0]}, {amt} ,  "loan" )')
            mydb.commit()
            userdata[3] += amt
            menu()
            popupmsg('LOAN APPROVED!')
            return True
        else:
            popupmsg('The bank does not approve new loans\n when there is already an active loan.')
    else:
        popupmsg('Enter a valid amount')
        return False

def loanapp():
    clearscreen()
    pdx = 240
    tk.Button(master, text='Back', command=loanmenu).grid(padx=10, pady=10, sticky=tk.W)
    tk.Label(master, text='LOAN APPLICATION').grid(padx=pdx, pady=(60, 40))
    tk.Label(master, text=f'Name: {userdata[2]}').grid(padx=pdx)
    tk.Label(master, text='Amount:').grid(padx=pdx, pady=(5, 0))
    amt = tk.Entry(master, width=20)
    amt.grid(padx=pdx)
    amt.bind('<Return>', (lambda function: sqlapp(amt.get())))
    tk.Button(master, text='Submit request', command=lambda: sqlapp(amt.get())).grid(padx=pdx, pady=(30, 0))

# loan repayment
def sqlrepay(amt, status):
    if amt.strip().isdigit() and amt.strip() != '0':
        amt = int(amt)
        if amt > status:
            popupmsg('You cannot repay more than amount owed to bank')
            return False
        elif amt > userdata[3]:
            popupmsg('You do not have enough money in your account')
            return False
        else:
            cursor.execute(f'update accountdata set balance=balance- {amt} where accno = {userdata[0]} ')
            amt = amt - (2 * (amt))
            cursor.execute(f'insert into transactiondata values( {userdata[0]}, {amt} ,  "loan repayment" )')
            mydb.commit()
            userdata[3] += amt
            loanrepayment()
            return True
    else:
        popupmsg('Enter a valid amount')
        return False

def loanrepayment():
    clearscreen()
    pdx = 240
    tk.Button(master, text='Back', command=loanmenu).grid(padx=10, pady=10, sticky=tk.W)
    tk.Label(master, text='LOAN REPAYMENT SCREEN').grid(padx=pdx, pady=(60, 40))
    tk.Label(master, text=f'Name: {userdata[2]}').grid(padx=pdx)
    status = unpaidloan()
    if status == 'No existing loans' or status == 0:
        tk.Label(master, text='No unpaid loans').grid(padx=pdx, pady=(35, 0))
        None
    else:
        tk.Label(master, text=f'Loan status: {status:,} unpaid').grid(padx=pdx, pady=(5, 0))
        tk.Label(master, text='Amount:').grid(padx=pdx, pady=(5, 0))
        amt=tk.Entry(master, width=20)
        amt.grid(padx=pdx)
        amt.bind('<Return>', (lambda function: sqlrepay(amt.get(), status)))
        tk.Button(master, text='Repay specific amount', command=lambda:sqlrepay(amt.get(), status)).grid(padx=pdx, pady=(5, 0))
        tk.Button(master, text='Repay full amount', command=lambda:sqlrepay(str(status), status)).grid(padx=pdx, pady=(30, 0))


# EDIT ACCOUT DETAILS
def delacc():
    global userdata
    loanstatus = unpaidloan()
    if loanstatus == 0 or loanstatus == 'No existing loans':
        cursor.execute(f'delete from accountdata where accno={userdata[0]}')
        cursor.execute(f'delete from transactiondata where accno={userdata[0]}')
        mydb.commit()
        userdata = []
        initialize()
        return True
    else:
        popupmsg('You cannot delete an account under an active loan.')
        return False

def editname(name):
    if len(name) > 30:
        popupmsg('Name is a maximum of 30 characters')
        return False
    cursor.execute(f'update accountdata set name="{name}" where accno={userdata[0]}')
    mydb.commit()
    userdata[2] = name
    return True

def editpass(newpass):
    if password.find(' ') == -1 and len(password) <= 16:
        finalpass = encode(newpass + salt, x)
        if passwordcheck(newpass, userdata[1]):
            popupmsg('Cannot be the same as old password')
        else:
            cursor.execute(f'update accountdata set password="{finalpass}" where accno={userdata[0]} ')
            mydb.commit()
            userdata[1] = finalpass
            menu()
            return True
    else:
        popupmsg('Password cannot contain spaces\nand must be a maximum of 16 characters')
        return False

def editdetailsgrid():
    clearscreen()
    pdx = 260
    tk.Button(master, text='Back', command=menu).grid(padx=10, pady=10, sticky=tk.W)
    tk.Label(master, text='Edit name: ').grid(padx=pdx, pady=(85, 0))
    name = tk.Entry(master, width=20)
    name.grid(padx=pdx)
    tk.Button(master, text='Change name', command=lambda:[editname(name.get()), menu()]).grid(padx=pdx, pady=(5, 0))
    tk.Label(master, text='Edit password: ').grid(padx=pdx, pady=(20, 0))
    passw = tk.Entry(master, width=20)
    passw.grid(padx = pdx)
    tk.Button(master, text='Change password', command=lambda:editpass(passw.get())).grid(padx=pdx, pady=(5,0))
    tk.Button(master, text='Delete this account', command=lambda:delacc()).grid(padx=pdx, pady=(75, 0))


# LOGIN
def sqllogin(accno, password, encoded=False):
    if not encoded:
        password = encode(password + salt, x)
    if accno.strip().isdigit() and len(accno) == 4:
        cursor.execute(f'select * from accountdata where accno = {accno} and password = "{password}" ')
        data = cursor.fetchone()
        if data is not None:
            global userdata
            userdata = list(data)
        menu()
    else:
        popupmsg('Invalid account number')
        return False

def login():
    clearscreen()
    pdx = 280
    tk.Button(master, text='Back', command=initialize).grid(padx=10, pady=10, sticky=tk.W)
    tk.Label(master, text='Account Number').grid(padx=pdx, pady=(100, 0))
    accno = tk.Entry(master, width=20)
    accno.grid(padx=pdx)
    tk.Label(master, text='Password').grid(padx=pdx)
    password = tk.Entry(master, width=20)
    password.grid(padx=pdx)
    password.bind('<Return>', (lambda function: sqllogin(accno.get(), str(password.get()))))
    tk.Button(master, text='Login', command=lambda: sqllogin(accno.get(), str(password.get()))).grid(padx=pdx, pady=(5, 0))


# SIGNUP
def sqlsignup(accno, password, name):
    if password.find(' ') == -1 and len(password) <= 16:
        if len(name) > 30:
            popupmsg('Name is a maximum of 30 characters')
            return False
        password = encode(password + salt, x)
        cursor.execute(f'insert into accountdata values({accno} , "{password}" , "{name}" , 0 )')
        cursor.execute(f'insert into transactiondata values( {accno}, 0 , "account creation")')
        mydb.commit()
        global userdata
        userdata = [accno, password , name , 0]
        menu()
        popupmsg('Account created')
        return True
    else:
        popupmsg('Password cannot contain spaces\nand must be a maximum of 16 characters')
        return False

def signup():
    clearscreen()
    pdx = 280
    accno = assignbankno()
    tk.Button(master, text='Back', command=initialize).grid(padx=10, pady=10, sticky=tk.W)
    tk.Label(master, text=f'Account Number: {accno}').grid(padx=pdx, pady=(100, 0))
    tk.Label(master, text='Name').grid(padx=pdx)
    name = tk.Entry(master, width=20)
    name.grid(padx=pdx)
    tk.Label(master, text='Password').grid(padx=pdx)
    password = tk.Entry(master, width=20)
    password.grid(padx=pdx)
    password.bind('<Return>', (lambda function: sqlsignup(accno, password.get(), name.get())))
    tk.Button(master, text='Create account', command=lambda:sqlsignup(accno, password.get(), name.get())).grid(padx=pdx, pady=(5, 0))

def default():
    clearscreen()
    cursor.execute(f'select * from accountdata where accno = {starting_accno}')
    data = cursor.fetchone()
    if data is None:
        cursor.execute(f'insert into accountdata values({starting_accno}, {encode("password"+salt, x)} , "admin", 0)')
        cursor.execute(f'insert into transactiondata values({starting_accno} , 0 , "account creation")')
        mydb.commit()
        global userdata
        userdata =  [starting_accno, encode('password'+salt, x) , 'admin' , 0]
        menu()
    else:
        password = data[1]
        sqllogin(str(starting_accno), data[1], True)


# OPENING SCREEN
def initialize():
    pdx = 260
    clearscreen()
    tk.Button(master, text='Log in', command=login, width=10).grid(padx=pdx, pady=(135, 10))
    tk.Button(master, text='Sign Up', command=signup, width=10).grid(padx=pdx, pady=(0, 160))
    tk.Button(master, text='Use default account', command=default, width = 15).grid(padx=pdx)
    tk.Label(master, text='Only for trial purposes', font=("Helvetica", 7)).grid(padx=pdx)


# tknter window creation
master=tk.Tk()
master.title('Bank Account Manager')
master.geometry('670x440')
master.resizable(width=False, height=False)  # fixing window size
master.option_add("*font", "lucida 10")
master.configure(bg='#EEEEEE')

# Menubar for navigation
menubar = tk.Menu(master)
optionsmenu = tk.Menu(menubar, tearoff=0)
# Defining first dropdown
optionsmenu.add_command(label="Home", command=menu, accelerator="Ctrl+H")
optionsmenu.add_separator()
optionsmenu.add_command(label = "Exit", command=endpgm, accelerator="Ctrl+W")

menubar.add_cascade(label="Options", menu=optionsmenu)
master.config(menu=menubar)
# Defining keyboard shortcuts
master.bind('<Control-h>', (lambda function: menu()))
master.bind('<Control-H>', (lambda function: menu()))
master.bind('<Control-w>', endpgm)
master.bind('<Control-W>', endpgm)

if __name__ == '__main__':
    # starting the interface
    initialize()
    master.mainloop()

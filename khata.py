import platform
import tkinter as tk
from tkinter import ttk, filedialog as fd, messagebox as mb
import sqlite3
import time
import pyperclip
from fpdf import FPDF


class Khata(object):
    def __init__(self, win):
        self.win = win
        self.win.state('zoomed')
        self.idvar = tk.StringVar()
        self.idvar.trace('w', self.findcus)
        self.namevar = tk.StringVar()
        self.paymentvar = tk.StringVar()
        self.creditvar = tk.StringVar()

        self.cusidvar = tk.StringVar()
        self.cusidvar.trace('w', self.findcustomer)
        self.cusnamevar = tk.StringVar()
        self.cusaddressvar = tk.StringVar()
        self.cusphonevar = tk.StringVar()

        self.win.title("Khata by MAKS")

        self.conn = sqlite3.connect("./database.db")
        self.c = self.conn.cursor()
        self.win.bind("<Control-r>", self.mkreport)
        self.win.bind("<Control-R>", self.mkreport)

        self.treeframe = tk.Frame(self.win)
        self.treeframe.pack(fill='both', expand=1)
        self.treecol = ['Sr', 'ID', 'Date', 'Person Name', 'Phone',
                        'Address', 'Debit(Payment)', 'Credit', 'Balance']
        self.tree = ScrolledTreeView(
            self.treeframe, columns=self.treecol, show="headings", selectmode='browse')
        self.tree.pack(fill='both', expand=1)
        for col in self.treecol:
            self.tree.heading(col, text=col
                              )

        self.tree.column('Sr', width=50)
        self.tree.column('ID', width=50)
        self.tree.column('Date', width=70)
        self.tree.column('Phone', width=100)
        self.tree.column('Address', width=150)
        self.tree.column('Debit(Payment)', anchor='e')
        self.tree.column('Credit', anchor='e')
        self.tree.column('Balance', anchor='e')
        self.setDataInTree()
        self.tree.bind("<Double-Button-1>", self.doubleClickOnTree)
        self.tree.bind("<Button-3>", self.openmenu)
        self.mkmenu()

    def mkreport(self, e):
        pdf = FPDF(format='a4', unit='in')
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18.0)
        th = pdf.font_size
        pdf.ln(2*th)
        pdf.set_font('Arial', 'B', 18.0)
        pdf.text(3.1, 0.5, "Khata by MAKS")
        pdf.ln(th)
        pdf.set_font('Arial', '', 10.0)
        pdf.text(2.99, 0.7, "Publish on "+time.strftime("%d-%h-%Y | %I:%M %p"))
        pdf.set_font('Arial', 'B', 10.0)
        th = pdf.font_size
        pdf.cell(0.4, 2*th, "ID", border=1, align='C')
        pdf.cell(0.8, 2*th, "Date", border=1, align='C')
        pdf.cell(1.5, 2*th, "Name", border=1, align='C')
        pdf.cell(0.9, 2*th, "Phone", border=1, align='C')
        # pdf.cell(1.5, 2*th, "Address", border=1,align ='C')
        pdf.cell(1.3, 2*th, "Debit", border=1, align='C')
        pdf.cell(1.3, 2*th, "Credit", border=1, align='C')
        pdf.cell(1.3, 2*th, "Balance", border=1, align='C')
        pdf.ln(2*th)
        data = [self.tree.item(i, 'values') for i in self.tree.get_children()]
        if data:
            pdf.set_font('Arial', '', 9.0)
            for row in data:
                # Enter data in colums
                pdf.cell(0.4, 2*th, row[1], border=1)
                pdf.cell(0.8, 2*th, row[2], border=1)
                pdf.cell(1.5, 2*th, row[3], border=1)
                pdf.cell(0.9, 2*th, row[4], border=1)
                # pdf.cell(1.5, 2*th, row[5], border=1)
                pdf.cell(1.3, 2*th, row[6], border=1, align='R')
                pdf.cell(1.3, 2*th, row[7], border=1, align='R')
                pdf.cell(1.3, 2*th, row[8], border=1, align='R')
                pdf.ln(2*th)
            url = fd.asksaveasfile(mode='w', defaultextension='.pdf', filetypes=(
                ('PDF File', '*.pdf'), ('All files', '*.*')))
            if url:
                pdf.output(url.name, 'F')
                mb.showinfo("Success", "Report created successfully.")
                url.close()

    def findcustomer(self, *args):
        cusid = self.cusidvar.get()
        if cusid:
            self.c.execute(
                f"SELECT name,phone,address FROM customers WHERE id={cusid}")
            data = self.c.fetchall()
            if data:
                self.cusnamevar.set(data[-1][0])
                self.cusphonevar.set(data[-1][1])
                self.cusaddressvar.set(data[-1][2])
                self.submitbtn.config(state='disabled')
                self.cusupdatebtn.config(state='normal')
                self.cusdeletebtn.config(state='normal')
            else:
                self.submitbtn.config(state='normal')
                self.cusupdatebtn.config(state='disabled')
                self.cusdeletebtn.config(state='disabled')
                self.cusnamevar.set('')
                self.cusphonevar.set('')
                self.cusaddressvar.set('')
        else:
            self.submitbtn.config(state='normal')
            self.cusupdatebtn.config(state='disabled')
            self.cusdeletebtn.config(state='disabled')
            self.cusnamevar.set('')
            self.cusphonevar.set('')
            self.cusaddressvar.set('')

    def mkmenu(self):
        self.aMenu = tk.Menu(self.win, tearoff=0)
        self.aMenu.add_command(
            label='Remove selection', command=lambda: self.tree.selection_remove(self.tree.selection()))
        self.aMenu.add_command(
            label='Delete selected row', command=self.deleteRow)
        self.aMenu.add_command(label='Copy ID', command=lambda: pyperclip.copy(
            self.tree.item(self.tree.selection(), 'values')[1]))
        self.aMenu.add_command(label='Copy Date', command=lambda: pyperclip.copy(
            self.tree.item(self.tree.selection(), 'values')[2]))
        self.aMenu.add_command(label='Copy Name', command=lambda: pyperclip.copy(
            self.tree.item(self.tree.selection(), 'values')[3]))
        self.aMenu.add_command(label='Copy Phone', command=lambda: pyperclip.copy(
            self.tree.item(self.tree.selection(), 'values')[4]))
        self.aMenu.add_command(label='Copy Address', command=lambda: pyperclip.copy(
            self.tree.item(self.tree.selection(), 'values')[5]))
        self.aMenu.add_command(label='Copy Debit', command=lambda: pyperclip.copy(
            self.tree.item(self.tree.selection(), 'values')[6]))
        self.aMenu.add_command(label='Copy Credit', command=lambda: pyperclip.copy(
            self.tree.item(self.tree.selection(), 'values')[7]))
        self.aMenu.add_command(label='Copy Balance', command=lambda: pyperclip.copy(
            self.tree.item(self.tree.selection(), 'values')[8]))

    def openmenu(self, event):
        if self.tree.selection():
            self.aMenu.post(event.x_root, event.y_root)
            self.tree.focus()

    def doubleClickOnTree(self, event):
        select = self.tree.selection()
        if select:
            rowdata = self.tree.item(select, 'values')
            self.idvar.set(rowdata[1])
            self.payent.focus()

    def deleteRow(self):
        select = self.tree.selection()
        if select and mb.askyesno("Delete this row", "Do you want to delete selected row from the table?"):
            rowdata = self.tree.item(select, 'values')
            self.c.execute(f"DELETE FROM payments WHERE payid={rowdata[0]}")
            self.conn.commit()
            self.setDataInTree(self.cusidvar.get())

    def findcus(self, *a):
        ids = self.idvar.get()
        if ids:
            self.c.execute(f"SELECT name FROM customers WHERE id={ids}")
            name = self.c.fetchall()
            if name:
                self.namevar.set(name[-1][-1])
            else:
                self.namevar.set("")
        else:
            self.namevar.set("")

        self.setDataInTree(ids)

    def mktables(self):
        self.c.execute(
            "CREATE TABLE customers(id INTEGER PRIMARY KEY,cusdate TEXT,name TEXT, phone TEXT,address TEXT)")
        self.c.execute(
            "CREATE TABLE payments(payid INTEGER PRIMARY KEY,id TEXT,paydate TEXT,payments TEXT,credit TEXT)")
        self.conn.commit()

    def setDataInTree(self, cusid=""):
        [self.tree.delete(i) for i in self.tree.get_children()]
        try:
            if cusid:
                self.c.execute(f"""SELECT payments.payid,payments.id, payments.paydate, customers.name, customers.phone, customers.address, payments.payments, payments.credit
            FROM payments
            INNER JOIN customers ON payments.id=customers.id WHERE payments.id='{cusid}' AND customers.id='{cusid}';
                """)
            else:
                self.c.execute(f"""SELECT payments.payid,payments.id, payments.paydate, customers.name, customers.phone, customers.address, payments.payments, payments.credit
            FROM payments
            INNER JOIN customers ON payments.id=customers.id;
                """)

            data = self.c.fetchall()
            if data:
                bal = 0
                data2 = []
                for i in data:
                    bal = float(i[6])-float(i[7])+float(bal)
                    data2.append([i[0], i[1], i[2], i[3], i[4], i[5], "{:,.2f}".format(
                        float(i[6])), "{:,.2f}".format(float(i[7])), "{:,.2f}".format(bal)])
                for i in data2:
                    self.tree.insert('', 'end', values=i)
        except:
            self.mktables()

    def submit(self):
        ids = self.idvar.get()
        pay = self.paymentvar.get()
        name = self.namevar.get()
        cre = self.creditvar.get()
        date = time.strftime('%Y-%m-%d')

        if not name:
            mb.showerror(
                "ERROR", "Cannot find a customer.\nPlease select customer first.")
            return
        if not pay and cre:
            pay = 0
        elif not cre and pay:
            cre = 0
        elif not pay and not cre:
            mb.showerror(
                "ERROR", "Please type payment or credit before try again.")
            return
        if pay:
            try:
                int(pay)
            except ValueError:
                mb.showerror("ERROR", "Payment must be a number.")
                return
        if cre:
            try:
                int(cre)
            except ValueError:
                mb.showerror("ERROR", "Credit must be a number.")
                return
        self.c.execute(
            f"INSERT INTO payments(id,paydate,payments,credit) VALUES('{ids}','{date}','{pay}','{cre}')")
        self.conn.commit()
        mb.showinfo("Success", "Payment or Credit added successfully.")
        self.paymentvar.set('')
        self.creditvar.set('')
        self.setDataInTree(self.idvar.get())

    def submitcustomer(self):
        name = self.cusnamevar.get()
        if not name:
            mb.showerror("ERROR", "Please type the name of Customer.")
            self.custop.focus_set()
            return
        phone = self.cusphonevar.get()
        if not phone:
            mb.showerror("ERROR", "Please type the phone number of Customer.")
            self.custop.focus_set()
            return
        address = self.cusaddressvar.get()
        if not address:
            mb.showerror("ERROR", "Please type the address of Customer.")
            self.custop.focus_set()
            return
        date = time.strftime('%Y-%m-%d')
        self.c.execute(
            f"INSERT INTO customers(cusdate,name, phone,address) VALUES('{date}','{name}','{phone}','{address}')")
        self.conn.commit()
        mb.showinfo("Success", "Customer added successfully.")
        self.cusphonevar.set('')
        self.cusaddressvar.set('')
        self.cusnamevar.set('')
        self.cusidvar.set(int(self.cusidvar.get())+1)
        self.custop.focus_set()

    def addcus(self):
        self.custop = tk.Toplevel(self.win)
        self.custop.update_idletasks()
        self.custop.title("Add Customers")
        width = 350
        height = 200
        x = (self.custop.winfo_screenwidth() // 2) - (width // 2)
        y = (self.custop.winfo_screenheight() // 2) - (height // 2)
        self.custop.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        self.cusframe = tk.Frame(self.custop)
        self.cusframe.pack(fill='both', expand=1)
        tk.Label(self.cusframe, font='arial 11', text='Customer ID: ').grid(
            column=1, row=1, sticky='w', pady=(10, 0), padx=(10, 0))
        tk.Label(self.cusframe, font='arial 11', text='Customer Name: ').grid(
            column=1, row=2, sticky='w', pady=(10, 0), padx=(10, 0))
        tk.Label(self.cusframe, font='arial 11', text='Address: ').grid(
            column=1, row=3, sticky='w', pady=(10, 0), padx=(10, 0))
        tk.Label(self.cusframe, font='arial 11', text='Phone: ').grid(
            column=1, row=4, sticky='w', pady=(10, 0), padx=(10, 0))
        ttk.Entry(self.cusframe, textvariable=self.cusidvar, font='arial 12').grid(
            column=2, row=1, sticky='w', pady=(10, 0), padx=(10, 0))

        ttk.Entry(self.cusframe, textvariable=self.cusnamevar, font='arial 12').grid(
            column=2, row=2, sticky='w', pady=(10, 0), padx=(10, 0))
        ttk.Entry(self.cusframe, textvariable=self.cusaddressvar, font='arial 12').grid(
            column=2, row=3, sticky='w', pady=(10, 0), padx=(10, 0))
        ttk.Entry(self.cusframe, textvariable=self.cusphonevar, font='arial 12').grid(
            column=2, row=4, sticky='w', pady=(10, 0), padx=(10, 0))
        self.cusupdatebtn = ttk.Button(
            self.cusframe, state='disabled', text='Update', command=self.updatecus)
        self.cusdeletebtn = ttk.Button(
            self.cusframe, text='Delete', state='disabled', command=self.deletecus)
        self.submitbtn = ttk.Button(
            self.cusframe, text='Submit', command=self.submitcustomer)
        self.cusupdatebtn.grid(column=1, row=5, sticky='w',
                               pady=(10, 0), padx=(10, 0))
        self.cusdeletebtn.grid(column=2, row=5, sticky='e',
                               pady=(10, 0), padx=(10, 0))
        self.submitbtn.grid(column=2, row=5, sticky='w',
                            pady=(10, 0), padx=(10, 0))
        self.custop.resizable(False, False)

        self.c.execute("SELECT MAX(id) FROM customers")
        cusid = self.c.fetchall()
        if cusid[-1][-1]:
            self.cusidvar.set(int(cusid[-1][-1])+1)
        else:
            self.cusidvar.set(1)

    def updatecus(self):
        cusid = self.cusidvar.get()
        cusaddress = self.cusaddressvar.get()
        cusphone = self.cusphonevar.get()
        cusname = self.cusnamevar.get()
        if mb.askyesno("Update Customer", "Do you want to Update this customer?"):
            self.c.execute(
                f"UPDATE customers SET name='{cusname}',phone='{cusphone}',address='{cusaddress}' WHERE id={cusid}")
            self.conn.commit()
            self.idvar.set(self.idvar.get())
            self.custop.focus()

    def deletecus(self):
        cusid = self.cusidvar.get()
        if mb.askyesno("Delete Customer", "Do you want to delete this customer?"):
            self.c.execute(f"DELETE FROM customers WHERE id={cusid}")
            self.conn.commit()
            self.idvar.set(self.idvar.get())
            self.custop.focus()

    def findCustomerByView(self, value, data):
        if value and data:
            if value == 'id':
                self.c.execute(
                    f"SELECT id,cusdate,name,phone,address FROM customers WHERE {value}={data}")
            else:
                self.c.execute(
                    f"SELECT id,cusdate,name,phone,address FROM customers WHERE {value} LIKE '{data}%'")
        else:
            self.c.execute(
                f"SELECT id,cusdate,name,phone,address FROM customers")

        data = self.c.fetchall()
        [self.custree.delete(i) for i in self.custree.get_children()]
        [self.custree.insert('', 'end', value=i) for i in data]

    def viewcustomer(self):
        self.vidvar = tk.StringVar()
        self.vidvar.trace(
            'w', lambda *args: self.findCustomerByView('id', self.vidvar.get()))
        self.vnamevar = tk.StringVar()
        self.vnamevar.trace(
            'w', lambda *args: self.findCustomerByView('name', self.vnamevar.get()))
        self.vphonevar = tk.StringVar()
        self.vphonevar.trace(
            'w', lambda *args: self.findCustomerByView('phone', self.vphonevar.get()))
        self.vaddress = tk.StringVar()
        self.vaddress.trace(
            'w', lambda *args: self.findCustomerByView('address', self.vaddress.get()))
        viewcustop = tk.Toplevel(self.win)
        viewcustop.update_idletasks()
        viewcustop.title("View Customers")
        width = 650
        height = 400
        x = (viewcustop.winfo_screenwidth() // 2) - (width // 2)
        y = (viewcustop.winfo_screenheight() // 2) - (height // 2)
        viewcustop.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        viewcustop.resizable(False, False)
        viewCusEntFrame = tk.Frame(viewcustop)
        tk.Label(viewCusEntFrame, text="ID :").grid(
            column=1, row=1, sticky='w')
        ttk.Entry(viewCusEntFrame, textvariable=self.vidvar).grid(
            column=2, row=1, sticky='w')
        tk.Label(viewCusEntFrame, text="Name :").grid(
            column=3, row=1, sticky='w')
        ttk.Entry(viewCusEntFrame, textvariable=self.vnamevar).grid(
            column=4, row=1, sticky='w')
        tk.Label(viewCusEntFrame, text="Phone :").grid(
            column=1, row=2, sticky='w')
        ttk.Entry(viewCusEntFrame, textvariable=self.vphonevar).grid(
            column=2, row=2, sticky='w')
        tk.Label(viewCusEntFrame, text="Address :").grid(
            column=3, row=2, sticky='w')
        ttk.Entry(viewCusEntFrame, textvariable=self.vaddress).grid(
            column=4, row=2, sticky='w')
        viewCusEntFrame.pack(side='bottom')
        viewCusTreeFrame = tk.Frame(viewcustop)

        viewCusTreeFrame.pack(fill='both', expand=1)
        custreecol = ['ID', 'Date', 'Person Name', 'Phone', 'Address']
        self.custree = ScrolledTreeView(
            viewCusTreeFrame, columns=custreecol, show="headings", selectmode='browse')
        self.custree.pack(fill='both', expand=1)
        for col in custreecol:
            self.custree.heading(col, text=col
                                 )
        self.custree.column('ID', width=50)
        self.custree.column('Date', width=70)
        self.custree.column('Phone', width=100)
        self.c.execute(f"SELECT id,cusdate,name,phone,address FROM customers")
        data = self.c.fetchall()
        [self.custree.insert('', 'end', value=i) for i in data]

    def mkent(self):
        self.entframe = tk.Frame(self.win)
        self.win.bind('<Return>', lambda e: self.submit())
        self.entframe.pack(side='bottom')
        tk.Label(self.entframe, font='arial 11', text='Enter Customer ID: ').grid(
            column=1, row=1, sticky='w', pady=(10, 0))
        tk.Label(self.entframe, font='arial 11', text='Customer Name: ').grid(
            column=3, row=1, sticky='w', padx=(10, 0), pady=(10, 0))
        tk.Label(self.entframe, font='arial 11', text='Payment: ').grid(
            column=1, row=2, sticky='w', pady=10)
        tk.Label(self.entframe, font='arial 11', text='Credit: ').grid(
            column=3, row=2, sticky='w', pady=10, padx=(10, 0))
        ttk.Entry(self.entframe, textvariable=self.idvar, font='arial 12').grid(
            column=2, row=1, sticky='w', pady=(10, 0))
        ttk.Entry(self.entframe, textvariable=self.namevar, font='arial 12',
                  state='readonly').grid(column=4, row=1, sticky='w', pady=(10, 0))
        self.payent = ttk.Entry(
            self.entframe, textvariable=self.paymentvar, font='arial 12')
        self.payent.grid(column=2, row=2, sticky='w', pady=10)
        ttk.Entry(self.entframe, textvariable=self.creditvar, font='arial 12').grid(
            column=4, row=2, sticky='w', pady=10)
        ttk.Button(self.entframe, text='Submit', command=self.submit).grid(
            column=2, row=3, sticky='w')
        ttk.Button(self.entframe, text='Add Customer',
                   command=self.addcus).grid(column=4, row=3, sticky='w')
        ttk.Button(self.entframe, text='View Customer',
                   command=self.viewcustomer).grid(column=4, row=3, sticky='e')


py3 = True
# The following code is added to facilitate the Scrolled widgets you specified.


class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''
    # ttk.Style().layout("scrollbarStyle",{'background':'blue'})

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)

        # self.configure(yscrollcommand=_autoscroll(vsb),
        #    xscrollcommand=_autoscroll(hsb))
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Copy geometry methods of master  (taken from ScrolledText.py)
        if py3:
            methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
                | tk.Place.__dict__.keys()
        else:
            methods = tk.Pack.__dict__.keys() + tk.Grid.__dict__.keys() \
                + tk.Place.__dict__.keys()

        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)


def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
        container.bind(
            '<Leave>', lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)
    return wrapped


class ScrolledTreeView(AutoScroll, ttk.Treeview):
    '''A standard ttk Treeview widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        ttk.Treeview.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)


operatingSystem = platform.system()


def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    if operatingSystem == 'Windows' or operatingSystem == 'Darwin':
        child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-MouseWheel>',
                       lambda e: _on_shiftmouse(e, child))
    else:
        child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
        child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))


def _unbound_to_mousewheel(event, widget):
    if operatingSystem == 'Windows' or operatingSystem == 'Darwin':
        widget.unbind_all('<MouseWheel>')
        widget.unbind_all('<Shift-MouseWheel>')
    else:
        widget.unbind_all('<Button-4>')
        widget.unbind_all('<Button-5>')
        widget.unbind_all('<Shift-Button-4>')
        widget.unbind_all('<Shift-Button-5>')


def _on_mousewheel(event, widget):
    if operatingSystem == 'Windows':
        widget.yview_scroll(-1*int(event.delta/120), 'units')
    elif operatingSystem == 'Darwin':
        widget.yview_scroll(-1*int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.yview_scroll(-1, 'units')
        elif event.num == 5:
            widget.yview_scroll(1, 'units')


def _on_shiftmouse(event, widget):
    if operatingSystem == 'Windows':
        widget.xview_scroll(-1*int(event.delta/120), 'units')
    elif operatingSystem == 'Darwin':
        widget.xview_scroll(-1*int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.xview_scroll(-1, 'units')
        elif event.num == 5:
            widget.xview_scroll(1, 'units')


if __name__ == "__main__":
    win = tk.Tk()
    k = Khata(win)
    k.mkent()
    win.mainloop()

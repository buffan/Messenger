import fbchat
from tkinter import *
from tkinter import ttk

#email = input('Enter email associated with Facebook account: ')
#password = input('Enter password associated with Facebook account: ')

def SendMessage(*args):
    client = fbchat.Client(email.get(), password.get())
    friend = client.getUsers('Oriana Hollingsworth')[0]
    message = "You've been nominated for the position of 'Git rekt scrub' - Greg Harrison"
    sent = client.send(friend.uid, message)


root = Tk()
root.title('Messenger')

mainframe = ttk.Frame(root, padding='3 3 12 12')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

email = StringVar()
password = StringVar()

email_entry = ttk.Entry(mainframe, width=7, textvariable=email)
email.entry.grid(column=0, row=1, sticky=(W, E))
passsword_entry = ttk.Entry(mainframe, width=7, textvariable=password)
password_entry.grid(column=0, row=2, sticky=(W, E))

ttk.Button(mainframe, text='Send message', command=SendMessage).grid(column=0, row=2, sticky=(W, E))

ttk.Label(mainframe, textvariable=email).grid(column=1, row=1, sticky=(E))
ttk.Label(mainframe, textvariable=password).grid(column=1, row=2, sticky=(E))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

email_entry.focus()
root.bind('<Return>', SendMessage)

root.mainloop()


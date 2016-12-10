import fbchat
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from collections import defaultdict


def SendMessage(*args):
    email_str = email.get()
    password_str = password.get()
    client = fbchat.Client(email_str, password_str, debug=False)
    noms = CompileNominations()
    for person in noms.keys():
        message = boilerplate_entry.get('1.0', 'end-1c').replace('{positions}', '- ' + '\n- '.join(noms[person]))
        print('{}: {}'.format(person, message))
        if person == 'Oriana Hollingsworth':
            fb_friend = client.getUsers(person)[0]
            sent = client.send(fb_friend.uid, message)


def CompileNominations():
    with open(path_field.get('1.0', 'end-1c')) as f:
        f.readline() #Eliminate headers
        d = defaultdict(set)
        for line in f:
            _, person, position = line.split(',')
            d[person].add(position[:-1]) #-1 to eliminate endline from cell
    return d
            

def SetPath(*args):
    extensions = [('CSV', '*.csv'), ('All files', '*')]
    dlg = filedialog.Open(mainframe, filetypes=extensions)
    result = dlg.show()

    if result:
        path_field['state'] = 'normal'
        path_field.insert('1.0', result)
        path_field['state'] = 'disabled'
 

root = Tk()
root.title('Messenger')

mainframe = ttk.Frame(root, padding='3 3 12 12')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

file_selector = ttk.Button(mainframe, text='Select nominations CSV', command=SetPath).grid(column=1, row=1, sticky=(W, E))
path_field = Text(mainframe, width=30, height=1)
path_field.grid(column=1, row=2, sticky=(W, E))
path_field['state'] = 'disabled'

email = StringVar()
email_entry = ttk.Entry(mainframe, width=20, textvariable=email)
email_entry.grid(column=1, row=3, sticky=(W, E))

password = StringVar()
password_entry = ttk.Entry(mainframe, width=20, show='*', textvariable=password)
password_entry.grid(column=1, row=4, sticky=(W, E))

ttk.Label(mainframe, text='Path').grid(column=2, row=2, sticky=(W, E))
ttk.Label(mainframe, text='Email').grid(column=2, row=3, sticky=(W, E))
ttk.Label(mainframe, text='Password').grid(column=2, row=4, sticky=(W, E))

bp_dims = (30, 10) #width by height
boilerplate_entry = Text(mainframe, width=bp_dims[0], height=bp_dims[1])
boilerplate_entry.grid(column=3, row=1, sticky=(W, E, N, S), columnspan=1, rowspan=4)


ttk.Button(mainframe, text='Send message', command=SendMessage).grid(column=3, row=5, sticky=(W, E))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

email_entry.focus()

root.mainloop()


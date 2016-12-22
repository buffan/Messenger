import fbchat
import requests
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import BitmapImage
from collections import defaultdict
from math import ceil
import base64


def SendMessage(*args):
    #TODO: finish implementation
    """
    if '{positions}' not in boilerplate_entry.get('1.0', 'end-1c'):
        if not messagebox.askyesno(title='Send message?', 
            message='{positions} not found in boilerplate text. Still send message?'):
            return
    """
    email_str = email.get()
    password_str = password.get()
    client = fbchat.Client(email_str, password_str, debug=False)
    noms = CompileNominations()
    for person in noms.keys():
        message = boilerplate_entry.get('1.0', 'end-1c').replace('{positions}', '- ' + '\n- '.join(noms[person]))
        print('{}: {}'.format(person, message))
        possible_friends = client.getUsers(person)
        # Filter out people not on friends list
        possible_friends = list(filter(lambda x: client.getUserInfo(x.uid)['is_friend'], possible_friends))
        # If no matches found on friends list
        if not possible_friends:
            print('{} not found on friends list'.format(person))
            continue
        # If multiple matches found on friends list
        elif len(possible_friends) > 1:
            friend = DisambiguateFriends(client, possible_friends, person)
        # If only 1 match found on friends list
        else:
            friend = possible_friends[0]
        #sent = client.send(friend.uid, message)
    print('All messages sent. Can safely exit program.')


#TODO: Implement
def DisambiguateFriends(client, possibilities, person):
    window = Toplevel(mainframe)
    window.title('Multiple results found')

    num_possibilities = len(possibilities)
    poss_index = 0
    for r in range(2):
        for c in range(int(ceil(len(possibilities)/2))):
            uid = possibilities[poss_index].uid
            img = str(base64.standard_b64encode(requests.get(client.getUserInfo(uid)['thumbSrc']).content))
            print(type(img))
            img = PhotoImage(img)
            b = ttk.Button(window, text=uid, image=img)
            b.configure(command=lambda: print(b.cget('text')))
            b.grid(column=c, row=r)
            b.image = img
            print('Button with id {} created at {}, {}'.format(uid, r, c))
            poss_index += 1

    for child in window.winfo_children():
        child.grid_configure(padx=2, pady=2)
            
    


def CompileNominations():
    with open(path_field.get('1.0', 'end-1c')) as f:
        # Eliminate headers
        f.readline() 
        d = defaultdict(set)
        for line in f:
            _, person, position = map(str.strip, line.split(','))
            d[person].add(position)
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


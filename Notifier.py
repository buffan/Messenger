import fbchat
import requests
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import BitmapImage
from collections import defaultdict
from math import ceil
from io import BytesIO
from PIL import ImageTk, Image


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
            friend_uid = DisambiguateFriends(client, possible_friends, person)
            print(friend_uid)
            print('Cats')
        # If only 1 match found on friends list
        else:
            friend_uid = possible_friends[0].uid
        #sent = client.send(friend.uid, message)
    print('All messages sent. Can safely exit program.')


#TODO: Return uid to calling method
def DisambiguateFriends(client, possibilities, person):
    window = Toplevel(mainframe)
    window.title('Multiple results found')

    num_possibilities = len(possibilities)
    poss_index = 0
    # Create max of 2 rows
    for r in range(2):
        for c in range(int(ceil(len(possibilities)/2))):
            uid = possibilities[poss_index].uid

            content = requests.get(client.getUserInfo(uid)['thumbSrc']).content
            resized_image = ResizeImage(Image.open(BytesIO(content)))
            img = ImageTk.PhotoImage(resized_image)

            # I have no idea why this works. The internet provided this magical lambda answer.
            b = ttk.Button(window, command=lambda uid=uid: uid, image=img)
            b.grid(column=c, row=r, sticky=(N, S, E, W))
            b.image = img
            poss_index += 1

    for child in window.winfo_children():
        child.grid_configure(padx=2, pady=2)


def ResizeImage(img):
    '''
    Rescales given image to match end_width
    '''
    end_width = 75
    percentage_resize = end_width/float(img.size[0])
    end_height = int(img.size[1]*percentage_resize)
    return img.resize((end_width, end_height), Image.ANTIALIAS)
    


def CompileNominations():
    '''
    Opens nominations csv, creates dictionary {person: list of positions}
    Return: {person: positions} dictionary
    '''
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


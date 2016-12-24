import fbchat
import requests
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from collections import defaultdict
from math import ceil
from io import BytesIO
from PIL import ImageTk, Image
from os import path


class AutoHideScrollbar(Scrollbar):
    '''
    Scrollbar that automatically hides when needed.
    Taken from effbot.org
    '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError("cannot use pack with this widget")
    def place(self, **kw):
        raise TclError("cannot use place with this widget")



def ProcessNominations(*args):
    # Ask user if they still want to send message without {positions} key
    if '{positions}' not in boilerplate_entry.get('1.0', 'end-1c'):
        check = '{positions} not found in boilerplate text. Still send message?'
        # Return if user does not want to send message
        if not messagebox.askyesno(title='Send message?', message=check):
            return
   
    # Attempt login
    email_str = email.get()
    password_str = password.get()
    try:
        client = fbchat.Client(email_str, password_str, debug=False)
    except:
        messagebox.showerror('Error', message='Incorrect username or password. Try again.')
        return

    nominations = CompileNominations()

    # Progress window setup
    progress_window = Toplevel()
    progress_window.title('Progress')
    progress = StringVar()
    progress.set('Processed 0/{}'.format(len(nominations.keys())))
    ttk.Label(progress_window, textvar=progress).grid(row=0, column=0)
    for child in progress_window.winfo_children():
        child.grid_configure(padx=2, pady=2)

    not_found = []
    for counter, person in enumerate(nominations.keys()):
        # Update process window
        progress.set('Processed {}/{}'.format(counter, len(nominations.keys())))
        progress_window.update()

        possible_friends = client.getUsers(person)
        # Filter out people not on friends list
        possible_friends = list(filter(lambda x: client.getUserInfo(x.uid)['is_friend'], possible_friends))
        # If no matches found on friends list
        if not possible_friends:
            print('{} not found on friends list\n'.format(person))
            not_found.append(person)
            continue
        # If multiple matches found on friends list
        elif len(possible_friends) > 1:
            DisambiguateFriends(possible_friends, person, nominations, client)
        # If only 1 match found on friends list
        else:
            friend_uid = possible_friends[0].uid
            SendMessage(person, friend_uid, nominations, client)
    progress_window.destroy()

    # If some users were not found on friends list, display warning box with their names and positions
    if not_found:
        DisplayNotFound(not_found, nominations)

    messagebox.showinfo('Done!', message='All messages sent. Program will now exit.')
    root.destroy()


def DisplayNotFound(not_found, nominations):
        '''
        Displays a window with all names not found
        '''
        not_found_window = Toplevel(mainframe)
        not_found_window.geometry(CalcWindowDimensions(not_found, nominations))
        not_found_window.title('User{} not found'.format('s' if len(not_found) > 1 else ''))
        # Canvas and frame both required for scrollbar
        canvas = Canvas(not_found_window, borderwidth=0)
        frame = Frame(canvas)

        vscrollbar = AutoHideScrollbar(not_found_window, orient='vertical', command=canvas.yview)
        vscrollbar.grid(row=0, column=1, sticky=(N, S))
        hscrollbar = AutoHideScrollbar(not_found_window, orient='horizontal', command=canvas.xview)
        hscrollbar.grid(row=1, column=0, sticky=(E, W))

        canvas.configure(yscrollcommand=vscrollbar.set)
        canvas.configure(xscrollcommand=hscrollbar.set)
        canvas.grid(row=0, column=0, sticky=(N, S, E, W))
        # Allow the frame to expand
        not_found_window.grid_rowconfigure(0, weight=1)
        not_found_window.grid_columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)

        canvas.create_window((0, 0), window=frame, anchor='nw')
        frame.bind('<Configure>', lambda event, canvas=canvas: OnFrameConfigure(canvas))

        # Display list of names not found and associated positions
        message = 'The following not found. Please send their messages manually.\n\n'
        names_and_positions = '\n\n'.join(['{} - {}'.format(person, ', '.join(nominations[person])) for person in not_found])
        Label(frame, text=message, font='Helvetica 14 bold').grid(row=0, column=0, sticky=(E, W))
        Label(frame, text=names_and_positions, anchor='w', justify='left').grid(row=1, column=0, sticky=(W, E))

        ttk.Button(frame, text='Ok', command=not_found_window.destroy).grid(row=2, column=0, sticky=(S))

        mainframe.wait_window(not_found_window)


def CalcWindowDimensions(not_found, nominations):
    '''
    Calculates max window dimensions required constrained by screen dimensions
    '''
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Values determined by experimentation
    pixels_per_char = 10
    pixels_per_col = 31
    nominations_width = pixels_per_char * max([len(', '.join(positions) + name) for name, positions in nominations.items() if name in not_found])
    # 2 lines per entry, 1 line of boilerplate, 1 button
    nominations_height = pixels_per_col *(2*len(not_found)+2)

    width = min(screen_width, nominations_width)
    height = min(screen_height, nominations_height)
    x_coord = screen_width//2
    y_coord = screen_height//2

    print(screen_width, nominations_width, screen_height, nominations_height)

    #return '{}x{}+{}+{}'.format(width, height, x_coord, y_coord)
    return '{}x{}+0+0'.format(width, height)

def OnFrameConfigure(canvas):
    '''
    Event handler for scrollbar move
    '''
    canvas.configure(scrollregion=canvas.bbox("all"))

def DisambiguateFriends(possibilities, person, nominations, client):
    '''
    Displays box of profile pictures. User clicks picture of intended recipient. Message is sent to associated user.
    '''
    window = Toplevel(mainframe)
    window.title('Multiple results found')

    l = ttk.Label(window, text='Multiple {}s found. Select the profile picture of the intended user.'.format(person))
    num_columns = ceil(len(possibilities)/2)
    l.grid(row=0, column=0, columnspan=num_columns)

    poss_index = 0
    # Create max of 2 rows of pictures
    for r in range(1, 3):
        for c in range(num_columns):
            uid = possibilities[poss_index].uid

            # Get and rescale thumbnail of profile picture. Would like to figure out how to get full sized picture
            content = requests.get(client.getUserInfo(uid)['thumbSrc']).content
            resized_image = RescaleImage(Image.open(BytesIO(content)))
            img = ImageTk.PhotoImage(resized_image)

            # I have no idea why this command works. The internet provided the magical lambda uid=uid answer.
            b = ttk.Button(window, image=img, command=lambda uid=uid: SendAndClose(person, uid, nominations, client, window))
            b.grid(column=c, row=r, sticky=(N, S, E, W))
            # Save image reference to prevent garbage collection!
            b.image = img
            poss_index += 1

    for child in window.winfo_children():
        child.grid_configure(padx=2, pady=2)
    # Wait for window to close before continuing
    mainframe.wait_window(window)


def SendAndClose(name, uid, nominations, client, window):
    '''
    Destroys window, then calls SendMessage
    '''
    window.destroy()
    SendMessage(name, uid, nominations, client)


def SendMessage(name, uid, nominations, client):
    '''
    Sends a message to the user with uid containing their nominations.
    '''
    message = boilerplate_entry.get('1.0', 'end-1c').replace('{positions}', '- ' + '\n- '.join(nominations[name]))
    print('{}: {}\n'.format(name, message))
    #client.send(uid, message)


def RescaleImage(img):
    '''
    Rescales given image
    '''
    scale_value = 2.0
    width, height = [int(scale_value*dim) for dim in img.size]
    return img.resize((width, height), Image.ANTIALIAS)    


def CompileNominations():
    '''
    Opens nominations csv, creates dictionary {person: list of positions}
    Return: {person: positions} dictionary
    '''
    d = defaultdict(set)
    with open(path_field.get('1.0', 'end-1c')) as f:
        # Eliminate headers
        f.readline() 
        for line in f:
            _, person, position = map(str.strip, line.split(','))
            # Use title to register the same name regardless of capitalization
            d[person.title()].add(position)
    WriteToFile(d)
    return d


def WriteToFile(d):
    '''
    Writes names and associated positions to log file on Desktop
    '''
    file_path = path.join(path.expanduser('~'), path.join('Desktop', 'log.txt'))
    with open(file_path, 'w') as f:
        for k, v in d.items():
            s = '{}: {}\n'.format(k, ', '.join(v))
            f.write(s)
        
            
def SetPath(*args):
    extensions = [('CSV', '*.csv'), ('All files', '*')]
    dlg = filedialog.Open(mainframe, filetypes=extensions)
    result = dlg.show()

    if result:
        path_field['state'] = 'normal'
        path_field.delete('1.0', END)
        path_field.insert('1.0', result)
        path_field['state'] = 'disabled'
 

# GUI setup
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
boilerplate_entry = Text(mainframe, width=bp_dims[0], height=bp_dims[1], wrap='word')
boilerplate_entry.grid(column=3, row=1, sticky=(W, E, N, S), columnspan=1, rowspan=3)
ttk.Label(mainframe, text='Message body').grid(column=3, row=4)

ttk.Button(mainframe, text='Send message', command=ProcessNominations).grid(column=3, row=5, sticky=(W, E))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

email_entry.focus()

root.mainloop()


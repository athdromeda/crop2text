from tkinter import Checkbutton, Entry, IntVar, Tk, Menu, Frame, Label, Canvas, Text, Scrollbar, SEL, INSERT, END, filedialog
from PIL import Image, ImageTk
import pytesseract
import threading

root = Tk()
root.title('crop2text')

WIDTH = 560
HEIGHT = 560
file_path = ""
aspect_ratio = 0
start_x = 0
start_y = 0
end_x = 0
end_y = 0
scanned_text = ''
rect = ''
tesseract_cfg = {}
whitelistOption = IntVar()
blacklistOption = IntVar()


def open_image():
    global file_path, HEIGHT, aspect_ratio
    file_path = filedialog.askopenfilename(title="Open Image File", filetypes=[(
        "All files", "*.*"), ("Image Files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")])
    if file_path:
        global image, photo_image
        image = Image.open(file_path)
        original_width, original_height = image.size

        aspect_ratio = HEIGHT / original_height
        new_width = int(original_width * aspect_ratio)
        resized_image = image.resize((new_width, HEIGHT), Image.LANCZOS)

        image = ImageTk.PhotoImage(resized_image)
        canvas.config(width=new_width)
        canvas.create_image(0, 0, anchor="nw", image=image)

        filepath_label.config(text=file_path)


def start_rectangle(event):
    global start_x, start_y, rect
    canvas.delete(rect)
    start_x = event.x
    start_y = event.y


def end_rectangle(event):
    global end_x, end_y, file_path
    end_x = event.x
    end_y = event.y
    if file_path:
        draw_rectangle()


def draw_rectangle():
    global start_x, start_y, end_x, end_y, rect
    perform_ocr()

    rect = canvas.create_rectangle(
        start_x, start_y, end_x, end_y, outline="red", fill="", width=2)

    filepath_label.config(text='Loading...')
    thread = threading.Thread(target=perform_ocr)
    thread.start()

def perform_ocr():
    global HEIGHT, WIDTH, aspect_ratio, scanned_text, start_x, start_y, end_x, end_y, tesseract_cfg
    image = Image.open(file_path)

    rect_points = (start_x, start_y, end_x, end_y)
    original_rect_coords = tuple(point / aspect_ratio for point in rect_points)

    croppedImage = image.crop(original_rect_coords)
    croppedImage.save(file_path[:file_path.rfind('/') + 1] + 'result.jpg')

    tesseract_cfg_str = ' '.join([f'-c {key}={value}' for key, value in tesseract_cfg.items()])
    scanned_text = pytesseract.image_to_string(croppedImage, config=tesseract_cfg_str)
    filepath_label.config(text=file_path)
    update_scanned_text()

def update_scanned_text():
    global scanned_text
    editor.delete('1.0', 'end')
    editor.insert('1.0', scanned_text)


def update_coordinate_text(event):
    x = event.x
    y = event.y
    cursor_coordinate.config(text=f"({x}, {y})")


def select_all(event):
    editor.tag_add(SEL, '1.0', END)
    editor.mark_set(INSERT, '1.0')
    editor.see(INSERT)
    return 'break'


def save_to_file(event):
    global scanned_text
    file_path = filedialog.asksaveasfilename(defaultextension='.txt')
    if file_path:
        with open(file_path, 'w') as file:
            file.write(scanned_text)
    print(f"Scanned text saved to {file_path}")


def delete_word_backspace(event):
    editor.delete("insert-1c wordstart", "insert")


def delete_word_delete(event):
    editor.delete("insert", "insert + 1c wordend")


def handle_whitelist():
    global tesseract_cfg, whitelistOption
    if whitelistOption.get()==1:
        tesseract_cfg['tessedit_char_whitelist'] = whitelist.get()
    else:
        del tesseract_cfg['tessedit_char_whitelist']


def handle_blacklist():
    global tesseract_cfg, blacklistOption
    if blacklistOption.get()==1:
        tesseract_cfg['tessedit_char_blacklist'] = blacklist.get()
    else:
        del tesseract_cfg['tessedit_char_blacklist']


# Menu bar
menubar = Menu(root, background='#3c87f4', foreground='white',
               activebackground='#39627d', activeforeground='white')
filemenu = Menu(menubar, tearoff=0, background='#3c87f4', foreground='white',
                activebackground='#39627d', activeforeground='white')
filemenu.add_command(label="Open", command=open_image)
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

# main frame
main_frame = Frame(root, background='blue')
main_frame.pack(fill='both', expand=True)

# canvas_frame
canvas_frame = Frame(main_frame, background='#273148')
canvas_frame.pack(side="left", fill='both', expand=True)

# canvas
canvas = Canvas(canvas_frame, width=WIDTH, height=HEIGHT,
                background='#333b55', cursor='cross')
canvas.pack(expand=True, anchor='center')

# canvas bind
canvas.bind("<Motion>", update_coordinate_text)
canvas.bind("<ButtonPress-1>", start_rectangle)
canvas.bind("<ButtonRelease-1>", end_rectangle)

tesseract_configs = Frame(canvas_frame, background='#333b55')
tesseract_configs.pack(side="bottom", fill='x', expand=True, anchor='s')

whitelist_option = Checkbutton(tesseract_configs, background='#333b55', fg='#6372a2', text='Whitelist', variable=whitelistOption, command=handle_whitelist, borderwidth=0, highlightthickness=0)
whitelist_option.pack(side="left")
whitelist = Entry(tesseract_configs, background='#4a567c', foreground='white', borderwidth=0, highlightthickness=0, insertbackground='white')
whitelist.pack(side="left", pady=3, padx=3)

blacklist_option = Checkbutton(tesseract_configs, background='#333b55', fg='#6372a2', text='Blacklist', variable=blacklistOption, command=handle_blacklist, borderwidth=0, highlightthickness=0)
blacklist_option.pack(side="left")
blacklist = Entry(tesseract_configs, background='#4a567c', foreground='white', borderwidth=0, highlightthickness=0, insertbackground='white')
blacklist.pack(side="left", pady=3, padx=3)

# text_frame
editor_frame = Frame(main_frame, background='#1c2435', width=600)
editor_frame.place(relx=1.0, rely=0.0, anchor='ne')
editor_frame.pack_propagate(False)
editor_frame.pack(fill='y', expand=True)

# scrollbar
scrollbar = Scrollbar(editor_frame)
scrollbar.pack(side='right', fill='y')

editor = Text(editor_frame, yscrollcommand=scrollbar.set, background='#1c2435', fg="#c1e2ff",
              insertbackground='white', borderwidth=0, highlightthickness=0, highlightbackground=root.cget("bg"))
editor.tag_configure('sel', background='#273148', foreground='white')
editor.pack(side='bottom', fill='both', expand=True, padx=12, pady=6)
editor.bind('<Control-a>', select_all)
editor.bind('<Control-s>', save_to_file)
editor.bind('<Control-BackSpace>', delete_word_backspace)
editor.bind('<Control-Delete>', delete_word_delete)

scrollbar.config(command=editor.yview)

# Bottom Frame
bottom_frame = Frame(root, background='#3c87f4')
bottom_frame.pack(side='bottom', fill='x')

filepath_label = Label(bottom_frame, text="Open an image first",
                       background=bottom_frame['background'], fg='white')
filepath_label.pack(side='left')

cursor_coordinate = Label(bottom_frame, text="(0,0)",
                          background=bottom_frame['background'], fg='white')
cursor_coordinate.pack(side='right')

# shortcut
root.bind('<Control-o>', lambda event: open_image())

root.mainloop()

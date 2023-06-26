import ttkbootstrap as ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import pytesseract

# defining global variables
WIDTH = 750
HEIGHT = 560
file_path = ""
aspect_ratio = 0
start_x = 0
start_y = 0
end_x = 0
end_y = 0

# function to open the image file
def open_image():
    global file_path, HEIGHT, aspect_ratio
    file_path = filedialog.askopenfilename(title="Open Image File", filetypes=[("All files", "*.*"), ("Image Files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")])
    if file_path:
        global image, photo_image
        image = Image.open(file_path)
        original_width, original_height = image.size

        aspect_ratio = HEIGHT / original_height
        new_width = int(original_width * aspect_ratio)
        resized_image = image.resize((new_width, HEIGHT), Image.LANCZOS)

        image = ImageTk.PhotoImage(resized_image)
        canvas.create_image(0, 0, anchor="nw", image=image)

# Function to handle the mouse button press event
def start_rectangle(event):
    global start_x, start_y
    start_x = event.x
    start_y = event.y

# Function to handle the mouse button release event
def end_rectangle(event):
    global end_x, end_y
    end_x = event.x
    end_y = event.y
    draw_rectangle()

# Function to draw the rectangle on the canvas
def draw_rectangle():
    global HEIGHT, WIDTH, aspect_ratio
    image = Image.open(file_path)

    # Rectangle coordinates on the canvas
    canvas_rect_coords = (start_x, start_y, end_x, end_y)

    # Calculate rectangle coordinates in the original image
    original_rect_coords = (
        (canvas_rect_coords[0] / aspect_ratio),
        (canvas_rect_coords[1] / aspect_ratio),
        (canvas_rect_coords[2] / aspect_ratio),
        (canvas_rect_coords[3] / aspect_ratio)
    )

    croppedImage  = image.crop(original_rect_coords)
    croppedImage.save(file_path[:file_path.rfind('/') + 1] + 'result.jpg')
    text = pytesseract.image_to_string(croppedImage)
    output_path = file_path[:file_path.rfind('/') + 1] + 'result.txt'
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(text)

    print(f"Scanned text saved to {output_path}")
    canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="yellow", fill="", width=2)

def update_coordinate_text(event):
    x = event.x
    y = event.y
    canvas.itemconfig(coord_text, text=f"({x}, {y})")

root = ttk.Window(themename="vapor")
root.title("Image Editor")
root.geometry("510x580+300+110")
root.resizable(0,0)
root.resizable(True,True)
icon = ttk.PhotoImage(file='icon.png')
root.iconphoto(False, icon)

# the left frame to contain the 4 buttons
left_frame = ttk.Frame(root, width=200, height=600)
left_frame.pack(side="left", fill="y")

# Create a Canvas widget
# the right canvas for displaying the image
canvas = ttk.Canvas(root, width=WIDTH, height=HEIGHT, background="blue")
canvas.pack()

canvas.bind("<ButtonPress-1>", start_rectangle)
canvas.bind("<ButtonRelease-1>", end_rectangle)

# Create a text item to display the coordinates
coord_text = canvas.create_text(540, 540, anchor="nw", text="(0, 0)", fill="white")

# Bind the motion event to update the coordinate text
canvas.bind("<Motion>", update_coordinate_text)

# loading the icons for the 4 buttons
image_icon = ttk.PhotoImage(file = 'add.png').subsample(12, 12)

# button for adding/opening the image file
image_button = ttk.Button(left_frame, image=image_icon, bootstyle="light", command=open_image)
image_button.pack(pady=5)

root.mainloop()

# https://www.thepythoncode.com/article/make-an-image-editor-in-tkinter-python#environment-set-up
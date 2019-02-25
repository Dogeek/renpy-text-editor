import tkinter as tk
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk


class ImageLayer:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.path = ""
        self.img = None
        self.reference = None
        self.mouse_pos = (0, 0)

    def hitbox(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def move(self, x, y):
        self.x = x - self.mouse_pos[0]
        self.y = y - self.mouse_pos[1]

    @property
    def rect(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)


class LayeredImageBuilderGUI(tk.Frame):
    def __init__(self, master=None):
        super(LayeredImageBuilderGUI, self).__init__()
        self.master = master
        self.init_contextual()
        self.canvas = tk.Canvas(self, width=1024, height=768)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.master.bind('<Button-3>', self.display_contextual)
        self.master.bind('<Button-1>', self.select_image)
        self.master.bind('<B1-Motion>', self.move_selection)
        self.images = []
        self.selected = None
        self.selection_rect = None
        self.loop()

    def init_contextual(self):
        self.contextual_menu = tk.Menu(self, tearoff=0)
        self.contextual_menu.add_command(label='Add Image',
                                         command=self.add_image)

    def display_contextual(self, event):
        try:
            self.contextual_menu.tk_popup(event.x_root, event.y_root, 0)
        except Exception:
            pass
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.contextual_menu.grab_release()

    def select_image(self, event):
        for img in reversed(self.images):
            if img.hitbox(event.x_root, event.y_root):
                self.selected = img
                self.selected.mouse_pos = (event.x_root, event.y_root)
                self.selection_rect = self.canvas.create_rectangle(self.selected.x, self.selected.y,
                                         self.selected.width, self.selected.height)
                return
        self.selected = None
        self.remove_selection_rect()
        return

    def remove_selection_rect(self):
        self.canvas.delete(self.selection_rect)
        self.selection_rect = None

    def move_selection(self, event):
        self.remove_selection_rect()
        if self.selected is not None:
            self.selected.move(event.x_root, event.y_root)
            self.canvas.coords(self.selected.reference, (self.selected.x, self.selected.y))
        if self.selection_rect is not None:
            self.canvas.coords(self.selection_rect, self.selected.rect)

    def add_image(self):
        img_path = filedialog.askopenfilename()
        if not img_path:
            return
        im = ImageTk.PhotoImage(file=img_path)
        layer = ImageLayer()
        layer.width = im.width()
        layer.height = im.height()
        layer.path = img_path
        layer.img = im
        layer.reference = self.canvas.create_image((0, 0), image=im, anchor="nw")
        self.images.append(layer)
        return

    def loop(self):
        if self.selection_rect is not None and self.selected is not None:
            self.canvas.delete(self.selection_rect)
            self.selection_rect = self.canvas.create_rectangle(self.selected.x, self.selected.y,
                                                               self.selected.width, self.selected.height)
        self.canvas.update_idletasks()
        self.after(5, self.loop)
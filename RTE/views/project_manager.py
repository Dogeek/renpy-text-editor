import tkinter as tk
import tkinter.ttk as ttk
import os
import glob
from RTE.constants import assets
from RTE.config import config
from RTE.utils import autoscroll


class ProjectManagerView(tk.Frame):
    def __init__(self, master=None, project_path=None):
        super(ProjectManagerView, self).__init__(master)
        self._project_path = project_path
        self.init_treeview()

    def _get_project_path(self):
        return self._project_path

    def _set_project_path(self, ppath):
        self._project_path = ppath
        self.project_name = ppath.split("\\")[-1]

    project_path = property(_get_project_path, _set_project_path)

    def init_treeview(self):
        global config
        self.vsb = ttk.Scrollbar(orient="vertical")
        self.hsb = ttk.Scrollbar(orient="horizontal")
        self.tree = ttk.Treeview(self,
                                 columns=("fullpath", "type", "size"),
                                 displaycolumns=(),
                                 height=config.wm_height // 20,
                                 selectmode="browse",
                                 yscrollcommand=lambda f, l: autoscroll(self.vsb, f, l),
                                 xscrollcommand=lambda f, l: autoscroll(self.hsb, f, l),
                                 )

        self.tree.heading("#0", text="Directory Structure", anchor='w')
        self.tree.heading("size", text="File Size", anchor='w')
        self.tree.column("size", stretch=0, width=100)

        self.vsb['command'] = self.tree.yview
        self.hsb['command'] = self.tree.xview

        self.tree.grid(row=0, column=0)
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ns")
        self.tree.bind('<<TreeviewOpen>>', self.update_tree)
        self.tree.bind('<Double-Button-1>', self.change_dir)

    def build_tree(self, rootdir=None):  # old code
        if rootdir is None:
            rootdir = self.project_path
        for root, dirs, files in os.walk(rootdir):
            if dirs:
                for directory in dirs:
                    item_options = {"text": directory,
                                    "image": assets.get_icon_by_extension("folder"),
                                    "values": (directory, os.path.join(root, directory)),
                                    "open": True}
                    self.tree.insert("", "end", **item_options)
                    self.build_tree(os.path.join(root, directory))
            for filename in files:
                item_options = {"text": filename,
                                "image": assets.get_icon_by_extension(filename.split(".")[-1]),
                                "values": (filename, os.path.join(root, filename)),
                                "open": True}
                self.tree.insert("", "end", **item_options)

    def populate_tree(self, node=""):
        if self.tree.set(node, "type") != 'directory':
            return

        path = self.tree.set(node, "fullpath")
        # path = self.project_path
        self.tree.delete(*self.tree.get_children(node))

        #parent = self.tree.parent(node)
        special_dirs = [] #if parent else glob.glob('.') + glob.glob('..')

        for p in special_dirs + os.listdir(path):
            ptype = None
            p = os.path.join(path, p).replace('\\', '/')
            if os.path.isdir(p):
                ptype = "directory"
            elif os.path.isfile(p):
                ptype = "file"

            fname = os.path.split(p)[1]
            id_ = self.tree.insert(node, "end", text=fname, values=[p, ptype])

            if ptype == 'directory':
                if fname not in ('.', '..'):
                    self.tree.insert(id_, 0, text="dummy")
                    self.tree.item(id_, text=fname,
                                   image=assets.get_icon_by_extension("folder"))
            elif ptype == 'file':
                size = os.stat(p).st_size
                self.tree.item(id_, image=assets.get_icon_by_extension(fname.split(".")[-1]))
                #self.tree.set(id_, "size", "%d bytes" % size)

    def populate_roots(self):
        dir_ = os.path.abspath(self.project_path).replace('\\', '/')
        node = self.tree.insert('', 'end', text=self.project_name, values=[dir_, "directory"])
        self.populate_tree(node)

    def update_tree(self, event):
        tree = event.widget
        self.populate_tree(tree.focus())

    def change_dir(self, event):
        tree = event.widget
        node = tree.focus()
        print(tree.item(node))
        if tree.parent(node):
            path = os.path.abspath(tree.set(node, "fullpath"))
            if os.path.isdir(path):
                os.chdir(path)
                tree.delete(tree.get_children(''))
                self.populate_roots()

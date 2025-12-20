from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
import json
import os
import sys
import webbrowser

# tags
SEARCH_HIGHLIGHT_TAG = "search_highlight"

# global constants
APP_NAME = "JON - Just another notepad"
DEFAULT_TITLE = "Untitled"
DEFAULT_WINDOW_SIZE = "800x600"
IS_BUILD = False                  # declare true while editing code, declare false when not changing code
IS_DEBUG = False                  # need to add debug features for this one
helpurl = "https://www.youtube.com/watch?v=My0lzMuNcHI"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# runtime state
currentFilePath = None                  # keeps track of file path for memory on open/save logic
unsavedChanges = False                  # keeps track of any unsaved changes

# important functions
def resource_path(*parts):
    return os.path.join(ROOT_DIR, *parts)


def fileCheck(filename):
    return os.path.exists(resource_path(filename))

def updateVersion(file_path="np_settings.json"):
    # load or initialize version data
    if not os.path.exists(file_path):
        versionData = {"major": 1, "minor": 0, "build": 0}
    else:
        with open(file_path, "r") as json_file:
            versionData = json.load(json_file)

    #increment build number
    if IS_BUILD:
        versionData["build"] += 1

    #save updated version
    with open(file_path, "w") as json_file:
        json.dump(versionData, json_file, indent=4)

    #create version string
    versionString = f"v{versionData['major']}.{versionData['minor']} build {versionData['build']}"
    return versionString

def updateTitle():
    # creates an asterisk next to the filename in the title bar if unsaved changes exist
    base_name = os.path.basename(currentFilePath) if currentFilePath else DEFAULT_TITLE
    dirty_marker = "*" if unsavedChanges else ""
    mainWindow.title(f"{dirty_marker}{base_name} - {APP_NAME}")

def on_edit(event=None):
    # checks to see if text has been edited to change unsavedChange flag to true
    global unsavedChanges
    if mainTextField.edit_modified():
        unsavedChanges = True
        updateTitle()
        update_cursor_position()
        # print("Text has been edited") # debug
        mainTextField.edit_modified(False)

def rcPopup(event):
    try:
        rcMenu.tk_popup(event.x_root, event.y_root)
    finally:
        rcMenu.grab_release()

def prompt_unsaved_changes():
    global unsavedChanges
    if not unsavedChanges:
        return True

    display_name = currentFilePath if currentFilePath else DEFAULT_TITLE
    unsavedChangesWarning = messagebox.askyesnocancel(
        "Unsaved Changes",
        f"Do you want to save changes to {display_name}?")
    if unsavedChangesWarning:
        return saveFile()
    if unsavedChangesWarning is None:
        return False
    return True

def load_content(text, path=None):
    global currentFilePath, unsavedChanges
    currentFilePath = path
    mainTextField.delete("1.0", END)
    mainTextField.insert("1.0", text)
    mainTextField.tag_remove(SEARCH_HIGHLIGHT_TAG, "1.0", END)
    unsavedChanges = False
    mainTextField.edit_modified(False)
    updateTitle()
    update_cursor_position()


# Function to update cursor position and document statistics
def update_cursor_position(event=None):
    try:
        index = mainTextField.index("insert")
        line, col = map(int, index.split("."))
        cursor_label.config(text=f"Ln {line}, Col {col + 1}")
        text_content = mainTextField.get("1.0", "end-1c")
        char_count = len(text_content)
        word_count = len(text_content.split()) if text_content.strip() else 0
        document_stats_label.config(text=f"{char_count} chars | {word_count} words")
    except Exception:
        cursor_label.config(text="Ln -, Col -")
        document_stats_label.config(text="0 chars | 0 words")

def fileExit():
    # on exit, if unsaved changes prompts user to save, not save or cancel w/ messagebox
    if prompt_unsaved_changes():
        mainWindow.destroy()

def newFile():
    if not prompt_unsaved_changes():
        return
    load_content("", None)

def openFile():
    # opens a file starting at data folder
    if not prompt_unsaved_changes():
        return

    # sets the context window to default to .txt or an option for all files
    initial_directory = os.path.dirname(currentFilePath) if currentFilePath else ROOT_DIR
    filepath = filedialog.askopenfilename(
        title="Open file...",
        initialdir=initial_directory,
        filetypes=[("Text Files","*.txt"),
                   ("All Files","*.*")])

    # if filepath is true, start the openFile process
    # global currentFilePath
    if filepath:
        try:
            with open(filepath, "r", encoding="utf-8") as openFileHandler:
                openFileData = openFileHandler.read()
                load_content(openFileData, filepath)

        except FileNotFoundError:
            messagebox.showerror("Open Error", "File not found, it might have been moved or deleted.")

        except Exception as e:
            messagebox.showerror("Open Error", f"An unexpected error occurred:\n{e}")

def saveFile():
    global currentFilePath, unsavedChanges
    if currentFilePath:
        try:
            content = mainTextField.get("1.0", "end-1c")
            with open(currentFilePath, "w", encoding="utf-8") as saveFileHandler:
                saveFileHandler.write(content)
                unsavedChanges = False
                updateTitle()
            mainTextField.edit_modified(False)
            return True

        except OSError as e:
            messagebox.showerror("Save Error", f"Could not save the file:\n{e}")
            return False
        except Exception as e:
            messagebox.showerror("Save Error", f"Save file error:\n{e}")
            return False
    else:
        return saveAsFile()

def saveAsFile():
    global currentFilePath, unsavedChanges
    initial_directory = os.path.dirname(currentFilePath) if currentFilePath else ROOT_DIR
    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialdir=initial_directory,
        filetypes=[
            ("Text File", "*.txt"),
            ("Python File", "*.py"),
            ("All Files","*.*")
        ])
    if filepath:
        try:
            fileText = str(mainTextField.get("1.0", "end-1c"))
            with open(filepath, "w", encoding="utf-8") as fileHandler:
                fileHandler.write(fileText)
            currentFilePath = filepath
            unsavedChanges = False
            updateTitle()
            mainTextField.edit_modified(False)
            update_cursor_position()
            return True

        except FileNotFoundError:
            messagebox.showerror("Save Error", "File not found, it might have been moved or deleted.")
            return False
        except Exception as e:
            messagebox.showerror("Save Error", f"An unexpected error occurred:\n{e}")
            return False
    return False

def undoEdit():
    try:
        mainTextField.edit_undo()
    except TclError:
        pass

def cutEdit():
    copyEdit()
    try:
        mainTextField.delete(SEL_FIRST, SEL_LAST)
    except TclError:
        pass

def copyEdit():
    try:
        selected_text = mainTextField.get(SEL_FIRST, SEL_LAST)
        mainTextField.clipboard_clear()
        mainTextField.clipboard_append(selected_text)
    except TclError:
        pass

def pasteEdit():
    try:
        clippaste = mainWindow.clipboard_get()
        mainTextField.insert(INSERT, clippaste)
    except TclError:
        pass

def fontFormat():

    def fontChange(event):
        selected_font = fontListbox.get(fontListbox.curselection())
        currentFont.config(family=selected_font)

    def fontSizeChange(event):
        selected_fontSize = sizeListbox.get(sizeListbox.curselection())
        currentFont.config(size=selected_fontSize)

    def fontStyleChange(event):
        # there is probably an easier and faster way to handle this :)
        # changes font style based on selection

        selected_fontStyle = styleListbox.get(styleListbox.curselection())

        if selected_fontStyle == "Regular":
            currentFont.config(weight="normal", slant="roman",underline=False, overstrike=False)
        elif selected_fontStyle == "Bold":
            currentFont.config(weight="bold", slant="roman",underline=False,overstrike=False)
        elif selected_fontStyle == "Italic":
            currentFont.config(weight="normal", slant="italic",underline=False,overstrike=False)
        elif selected_fontStyle == "Bold/Italic":
            currentFont.config(weight="bold", slant="italic",underline=False,overstrike=False)
        elif selected_fontStyle == "Underline":
            currentFont.config(weight="normal", slant="italic", underline=True,overstrike=False)
        elif selected_fontStyle == "Strike":
            currentFont.config(weight="normal", slant="italic", underline=False,overstrike=True)
        else:
            print("How did you select something that's not in the box?")

    # messagebox.showerror(title="Under construction", message="Under Construction - For now") # debug
    fontWindow = Toplevel(mainWindow)
    fontWindow.title("Font")
    fontWindow.resizable(FALSE, FALSE)
    # Center the window on screen
    window_width = 400
    window_height = 400
    screen_width = fontWindow.winfo_screenwidth()
    screen_height = fontWindow.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    fontWindow.geometry(f"{window_width}x{window_height}+{x}+{y}")

    #label generation
    fontLabel = Label(fontWindow, text="Font:", font=("Segoe UI", 9))
    fontLabel.grid(row=0, column=0, padx=10, pady=10)

    sizeLabel = Label(fontWindow, text="Font Size:", font=("Segoe UI", 9))
    sizeLabel.grid(row=0, column=1)

    styleLabel = Label(fontWindow, text="Font Style:", font=("Segoe UI", 9))
    styleLabel.grid(row=0, column=2)

    # add listboxes
    fontListbox = Listbox(fontWindow, selectmode=SINGLE, width=30)
    fontListbox.grid(row=1, column=0)

    sizeListbox = Listbox(fontWindow, selectmode=SINGLE, width=10)
    sizeListbox.grid(row=1, column=1)

    styleListbox = Listbox(fontWindow, selectmode=SINGLE, width=30)
    styleListbox.grid(row=1, column=2)

    # add preview frame with sample text inside of the frame
    # need to fix somewhat, at larger fonts there is not enough space even with clipping
    previewFrame = LabelFrame(fontWindow, text="Sample",padx=10, pady=10,width=100,height=70)
    previewFrame.grid(row=4, column=0, columnspan=1,padx=10, pady=10, sticky="nsew")
    previewFrame.rowconfigure(0, weight=1)
    previewFrame.columnconfigure(0, weight=1)
    previewFrame.grid_propagate(False)

    # creates the sample text

    previewCanvas = Canvas(previewFrame,width=100,height=70)
    previewCanvas.grid(row=0, column=0, sticky="nsew")
    previewCanvas.create_text(
        60, 10,  # center coordinates
        text="AaBbYyZz",
        font=currentFont,
        anchor="center"
    )

    # add font families to fontListbox
    for f in font.families():
        fontListbox.insert(END, f)

    # add sizes to size listbox (can create more sizes if so desired)
    font_sizes = [8,10,12,14,16,18,20,36,48,72]
    for size in font_sizes:
        sizeListbox.insert(END, size)

    # add styles to styleBox
    font_styles = ["Regular","Bold","Italic","Bold/Italic","Underline", "Strike"]
    for style in font_styles:
        styleListbox.insert(END, style)

    # bind listboxes to keys
    fontListbox.bind("<ButtonRelease-1>", fontChange)
    sizeListbox.bind("<ButtonRelease-1>", fontSizeChange)
    styleListbox.bind("<ButtonRelease-1>", fontStyleChange)

def toggleWordWrap():
    if wordWrapVar.get():
        mainTextField.config(wrap="word")
    else:
        mainTextField.config(wrap="none")

def findAndReplace():
    def highlight_all():
        mainTextField.tag_remove(SEARCH_HIGHLIGHT_TAG, "1.0", END)
        query = find_entry.get()
        if not query:
            matches_label.config(text="")
            return

        start_pos = "1.0"
        matches = 0
        first_match = None
        nocase = bool(ignore_case_var.get())
        while True:
            start_pos = mainTextField.search(query, start_pos, nocase=nocase, stopindex=END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(query)}c"
            mainTextField.tag_add(SEARCH_HIGHLIGHT_TAG, start_pos, end_pos)
            if not first_match:
                first_match = start_pos
            start_pos = end_pos
            matches += 1

        if matches:
            matches_label.config(text=f"{matches} match(es)")
            mainTextField.see(first_match)
        else:
            matches_label.config(text="No matches found")

    def replace_next():
        global unsavedChanges
        query = find_entry.get()
        replacement = replace_entry.get()
        if not query:
            return

        start_pos = mainTextField.search(query, mainTextField.index(INSERT), nocase=bool(ignore_case_var.get()), stopindex=END)
        if not start_pos:
            matches_label.config(text="No further matches")
            return

        end_pos = f"{start_pos}+{len(query)}c"
        mainTextField.delete(start_pos, end_pos)
        mainTextField.insert(start_pos, replacement)
        mainTextField.mark_set(INSERT, f"{start_pos}+{len(replacement)}c")
        highlight_all()
        update_cursor_position()
        unsavedChanges = True
        updateTitle()

    def replace_all():
        query = find_entry.get()
        replacement = replace_entry.get()
        if not query:
            return

        text = mainTextField.get("1.0", END)
        nocase = bool(ignore_case_var.get())
        comparison_text = text.lower() if nocase else text
        target = query.lower() if nocase else query
        occurrences = comparison_text.count(target)
        if not occurrences:
            matches_label.config(text="No matches found")
            return

        if nocase:
            start = 0
            result = ""
            while True:
                idx = comparison_text.find(target, start)
                if idx == -1:
                    result += text[start:]
                    break
                result += text[start:idx] + replacement
                start = idx + len(query)
            mainTextField.delete("1.0", END)
            mainTextField.insert("1.0", result)
        else:
            mainTextField.delete("1.0", END)
            mainTextField.insert("1.0", text.replace(query, replacement))

        mainTextField.edit_modified(True)
        on_edit()
        highlight_all()
        matches_label.config(text=f"Replaced {occurrences} occurrence(s)")

    findWindow = Toplevel(mainWindow)
    findWindow.title("Find / Replace")
    findWindow.resizable(FALSE, FALSE)

    Label(findWindow, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    find_entry = Entry(findWindow, width=30)
    find_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    Label(findWindow, text="Replace:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    replace_entry = Entry(findWindow, width=30)
    replace_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ignore_case_var = BooleanVar(value=True)
    Checkbutton(findWindow, text="Ignore case", variable=ignore_case_var, command=highlight_all).grid(row=2, column=1, sticky="w", padx=5, pady=2)

    button_frame = Frame(findWindow)
    button_frame.grid(row=3, column=0, columnspan=2, pady=5)

    Button(button_frame, text="Find All", command=highlight_all, width=10).grid(row=0, column=0, padx=5)
    Button(button_frame, text="Replace", command=replace_next, width=10).grid(row=0, column=1, padx=5)
    Button(button_frame, text="Replace All", command=replace_all, width=10).grid(row=0, column=2, padx=5)

    matches_label = Label(findWindow, text="", anchor="w")
    matches_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=2)

    find_entry.focus_set()
    findWindow.transient(mainWindow)
    findWindow.grab_set()

def helpView():
    webbrowser.open(helpurl)

def about():
    # create a child window (top level) and disable all buttons at the top
    aboutWindow = Toplevel(mainWindow)
    aboutWindow.title(f"About {APP_NAME}")
    aboutWindow.overrideredirect(False) # make true to remove min/max/close buttons

    # Center the window on screen
    window_width = 400
    window_height = 250
    screen_width = aboutWindow.winfo_screenwidth()
    screen_height = aboutWindow.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    aboutWindow.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # bulk of about window text
    aboutPynote = f"""{APP_NAME} is a project notepad app coded entirely in Python utilizing TKinter to get back into programming with python. 
    \nThank you to Bro Code and chatGPT (lol) for helping me practice my programming skills and giving me the resources and tips to help build this tool!
    \n
    \n\n Created by Jake Evans"""

    # add content to actual window

    aboutWindowLabel = Label(aboutWindow,text=f"{APP_NAME} version {version}", font=("Arial",14,"bold"))
    aboutWindowLabel.pack(side=TOP,pady=10)
    aboutWindowText = Label(aboutWindow,text=aboutPynote,font=("Arial",10),wraplength=380, justify="center")
    aboutWindowText.pack(side=TOP)



    awButtonClose = Button(aboutWindow, text="OK",
                           height=1, width=2,
                           padx=20,
                           command=aboutWindow.destroy)
    awButtonClose.place(relx=0.95, rely=0.95, anchor="se")

def initialize_window():
    global mainWindow, currentFont, wordWrapVar, rcMenu, menubar, fileMenu, editMenu, formatMenu, helpMenu
    global xScrollbar, yScrollbar, mainTextField, status_frame, cursor_label, document_stats_label, version

    mainWindow = Tk()
    mainWindow.geometry(DEFAULT_WINDOW_SIZE)
    version = updateVersion()
    mainWindow.title(f"{DEFAULT_TITLE} - {APP_NAME}")

    #########DEFAULT VALUES FOR WINDOW################
    currentFont = font.Font(family="consolas", size=13)
    if fileCheck("pynote_icon.ico"):
        icon_path = resource_path("pynote_icon.ico")
        try:
            mainWindow.iconbitmap(icon_path)
        except Exception:
            # icon bitmap fails silently on platforms that do not support .ico
            pass
    wordWrapVar = BooleanVar(value=True)
    ##################################################

    # Right Click (rc) context menu generation
    rcMenu = Menu(mainWindow, tearoff=0)
    rcMenu.add_command(label="Undo", command=undoEdit)
    rcMenu.add_separator()
    rcMenu.add_command(label="Cut", command=cutEdit)
    rcMenu.add_command(label="Copy", command=copyEdit)
    rcMenu.add_command(label="Paste", command=pasteEdit)
    rcMenu.add_separator()
    rcMenu.add_command(label="Select All", command=lambda: mainTextField.tag_add(SEL, "1.0", END))
    rcMenu.bind("<Button-3>", rcPopup)

    # menubar generation
    menubar = Menu(mainWindow)
    mainWindow.config(menu=menubar)

    # file context menu in menu bar
    fileMenu = Menu(menubar,tearoff=False)
    menubar.add_cascade(label="File", menu=fileMenu)
    fileMenu.add_command(label="New", command=newFile)
    fileMenu.add_command(label="Open", command=openFile)
    fileMenu.add_command(label="Save", command=saveFile)
    fileMenu.add_command(label="Save As...", command=saveAsFile)
    fileMenu.add_separator()
    fileMenu.add_command(label="Exit", command=fileExit)

    # edit context menu in menu bar
    editMenu = Menu(menubar,tearoff=False)
    menubar.add_cascade(label="Edit", menu=editMenu)
    editMenu.add_command(label="Undo", accelerator="Ctrl+Z", command=undoEdit)
    editMenu.add_separator()
    editMenu.add_command(label="Cut", accelerator="Ctrl+X", command=cutEdit)
    editMenu.add_command(label="Copy", accelerator="Ctrl+C", command=copyEdit)
    editMenu.add_command(label="Paste", accelerator="Ctrl+V", command=pasteEdit)
    editMenu.add_separator()
    editMenu.add_command(label="Find / Replace", accelerator="Ctrl+F", command=findAndReplace)
    editMenu.add_command(label="Select All", accelerator="Ctrl+A", command=lambda: mainTextField.tag_add(SEL, "1.0", END))

    # format context menu in menu bar
    formatMenu = Menu(menubar,tearoff=False)
    menubar.add_cascade(label="Format", menu=formatMenu)
    formatMenu.add_checkbutton(label="Word Wrap", variable=wordWrapVar, command=toggleWordWrap)
    formatMenu.add_command(label="Font...", command=fontFormat)

    # help context menu in menu bar
    helpMenu = Menu(menubar,tearoff=False)
    menubar.add_cascade(label="Help", menu=helpMenu)
    helpMenu.add_command(label="View Help", command=helpView)
    helpMenu.add_separator()
    helpMenu.add_command(label=f"About {APP_NAME}", command=about)

    # text window scrollbar
    xScrollbar = Scrollbar(mainWindow, orient="horizontal")
    xScrollbar.pack(side="bottom", fill="x")

    yScrollbar = Scrollbar(mainWindow, orient="vertical")
    yScrollbar.pack(side="right", fill="y")

    # text window
    mainTextField = Text(mainWindow, font=currentFont, wrap="word", undo=True, yscrollcommand=yScrollbar.set, xscrollcommand=xScrollbar.set)
    mainTextField.pack(side="top", expand=True, fill="both")
    mainTextField.bind("<<Modified>>", on_edit)
    mainTextField.bind("<Control-z>", lambda e: undoEdit())
    mainTextField.bind("<Control-f>", lambda e: (findAndReplace(), "break"))
    mainTextField.bind("<Control-a>", lambda e: (mainTextField.tag_add(SEL, "1.0", END), "break"))
    mainTextField.bind("<Button-3>", rcPopup)
    mainTextField.tag_config(SEARCH_HIGHLIGHT_TAG, background="yellow")
    mainWindow.protocol("WM_DELETE_WINDOW", fileExit)

    # Status bar frame
    status_frame = Frame(mainWindow, relief="sunken", bd=1)
    status_frame.pack(side="bottom", fill="x")

    # Label to hold line/column display
    cursor_label = Label(status_frame, text="Ln 1, Col 1", anchor="e")
    cursor_label.pack(side="right", padx=5)

    document_stats_label = Label(status_frame, text="0 chars | 0 words", anchor="w")
    document_stats_label.pack(side="left", padx=5)

    # Bind typing and mouse release to update function
    mainTextField.bind("<KeyRelease>", update_cursor_position)
    mainTextField.bind("<ButtonRelease>", update_cursor_position)
    mainTextField.bind("<MouseWheel>", update_cursor_position)

    xScrollbar.config(command=mainTextField.xview)
    yScrollbar.config(command=mainTextField.yview)


def open_startup_file():
    if len(sys.argv) < 2:
        return

    candidate = os.path.abspath(sys.argv[1])
    if not os.path.isfile(candidate):
        messagebox.showerror("Open Error", f"Startup file not found:\n{candidate}")
        return

    try:
        with open(candidate, "r", encoding="utf-8") as openFileHandler:
            openFileData = openFileHandler.read()
            load_content(openFileData, candidate)
    except Exception as e:
        messagebox.showerror("Open Error", f"Could not open startup file:\n{e}")


def main():
    initialize_window()
    open_startup_file()
    update_cursor_position()
    mainWindow.mainloop()


if __name__ == "__main__":
    main()

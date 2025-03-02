import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyfiglet
from PIL import Image, ImageDraw, ImageFont
import pyperclip
import os
import requests
import threading
import json

# Initialize main window with professional hacker-style black theme
root = tk.Tk()
root.title("ASCII Art Generator")
root.configure(bg="#000000")  # Pure black background
root.geometry("1200x700")  # Wider to accommodate the chatbot sidebar

# Color palette
BG_BLACK = "#000000"        # Main background
DARK_GRAY = "#111111"       # Secondary background
LIGHT_GRAY = "#CCCCCC"      # Text color
BLUE_PRIMARY = "#3B82F6"    # Primary blue for ASCII art
BLUE_SECONDARY = "#1E40AF"  # Secondary blue for ASCII shadow
BLUE_HIGHLIGHT = "#60A5FA"  # Highlight blue

# Create a custom dark theme
style = ttk.Style()
style.theme_use('default')

# Configure custom styles
style.configure("Hacker.TFrame", background=BG_BLACK)
style.configure("Sidebar.TFrame", background=DARK_GRAY)

style.configure("Hacker.TLabel", 
                background=BG_BLACK, 
                foreground=LIGHT_GRAY,
                font=("Consolas", 10))

style.configure("Title.TLabel", 
                background=BG_BLACK, 
                foreground=LIGHT_GRAY,
                font=("Consolas", 16, "bold"))

style.configure("Status.TLabel", 
                background=BG_BLACK, 
                foreground=LIGHT_GRAY,
                font=("Consolas", 9))

style.configure("Hacker.TButton",
                background=DARK_GRAY,
                foreground=LIGHT_GRAY,
                font=("Consolas", 9),
                relief="flat",
                borderwidth=1)

style.map("Hacker.TButton",
          background=[('active', "#333333")],
          foreground=[('active', LIGHT_GRAY)])

# Custom combobox
style.configure("Hacker.TCombobox",
                fieldbackground=DARK_GRAY,
                background=DARK_GRAY,
                foreground=LIGHT_GRAY,
                selectbackground="#333333",
                selectforeground=LIGHT_GRAY)

# Retrieve available fonts from pyfiglet and sort them
available_fonts = sorted(pyfiglet.FigletFont.getFonts())

# Global variables
shadow_text_id = None
current_ascii_art = ""
animation_running = True
sidebar_visible = True
ollama_models = []

# Ollama API setup
OLLAMA_API_URL = "http://localhost:11434/api/"

def fetch_ollama_models():
    """Fetch available models from the Ollama API."""
    global ollama_models
    try:
        response = requests.get(OLLAMA_API_URL + "tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            ollama_models = [model["name"] for model in models]
            if ollama_model_selector:
                ollama_model_selector['values'] = ollama_models
                if ollama_models:
                    ollama_model_selector.set(ollama_models[0])
        else:
            append_to_chat("Failed to connect to Ollama API. Is Ollama running?")
    except Exception as e:
        append_to_chat(f"Error connecting to Ollama: {str(e)}")

def generate_from_ollama(model, prompt):
    """Generate text using Ollama API."""
    try:
        payload = {"model": model, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_API_URL + "generate", json=payload)
        if response.status_code == 200:
            return response.json().get("response", "No response")
        return f"Error in generation. Status code: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def generate_art():
    """Convert input text to ASCII art and display with a 3D effect."""
    global current_ascii_art
    text = entry.get()
    # Get the font selected from the drop-down (default to "standard" if nothing selected)
    font_choice = font_var.get().strip() or "standard"
    if text:
        # Generate ASCII art using pyfiglet
        ascii_art = pyfiglet.figlet_format(text, font=font_choice)
        current_ascii_art = ascii_art  # Store for copying later
        display_art(ascii_art)
        # Update status with message
        status_var.set(f"Generated with {font_choice} font")
    else:
        messagebox.showerror("Error", "Please enter some text first.")

def display_art(ascii_art):
    """Display the ASCII art on the canvas with a shadow for 3D effect."""
    canvas.delete("all")
    x_offset, y_offset = 2, 2  # Shadow offset
    global shadow_text_id
    
    # Draw shadow text (the "3D" layer) with a darker blue
    shadow_text_id = canvas.create_text(
        10 + x_offset, 10 + y_offset, 
        anchor="nw", text=ascii_art,
        font=("Consolas", 12), fill=BLUE_SECONDARY  # Dark blue shadow
    )
    
    # Draw the main ASCII art text over the shadow
    canvas.create_text(
        10, 10, anchor="nw", text=ascii_art,
        font=("Consolas", 12), fill=BLUE_PRIMARY  # Light blue
    )
    
    # Start animating the shadow if enabled
    if animation_toggle_var.get():
        animate_shadow(shadow_text_id)

def copy_to_clipboard():
    """Copy the current ASCII art to clipboard."""
    if current_ascii_art:
        pyperclip.copy(current_ascii_art)
        status_var.set("Copied to clipboard")
    else:
        status_var.set("No art to copy")

def toggle_animation():
    """Toggle the shadow animation on/off."""
    global animation_running
    animation_running = animation_toggle_var.get()
    if current_ascii_art and animation_running:
        # Restart animation if it was turned back on
        animate_shadow(shadow_text_id)
    status_var.set("Animation " + ("on" if animation_running else "off"))

def animate_shadow(item):
    """Cycle through blue shades to animate the shadow text."""
    if not animation_running:
        return  # Stop if animation toggle is off
        
    # Blue shades for subtle shadow pulsing
    colors = [BLUE_SECONDARY, "#2563EB", "#1D4ED8", "#2563EB"]
    
    def update_color(i=0):
        if animation_running and item:
            try:
                canvas.itemconfig(item, fill=colors[i % len(colors)])
                root.after(400, update_color, i + 1)  # Slower pulse
            except:
                pass  # In case the item doesn't exist anymore
    
    update_color()

def save_animated_gif():
    """Generate and save an animated GIF of the ASCII art with a subtle shadow."""
    text = entry.get()
    font_choice = font_var.get().strip() or "standard"
    if not text:
        messagebox.showerror("Error", "Please enter text first.")
        return

    # Generate the ASCII art
    ascii_art = pyfiglet.figlet_format(text, font=font_choice)
    
    try:
        # Try to use Consolas font for consistency with display
        font_path = os.path.join(os.environ.get('WINDIR', ''), 'Fonts', 'consola.ttf')
        if os.path.exists(font_path):
            pil_font = ImageFont.truetype(font_path, 12)
        else:
            pil_font = ImageFont.truetype("cour.ttf", 12)
    except Exception:
        pil_font = ImageFont.load_default()

    # Calculate the size needed for the image
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.multiline_textbbox((0, 0), ascii_art, font=pil_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    margin = 10
    x_offset, y_offset = 2, 2  # Shadow offset
    img_width = text_width + margin * 2 + x_offset
    img_height = text_height + margin * 2 + y_offset

    # Define colors for the subtle shadow animation
    colors = [BLUE_SECONDARY, "#2563EB", "#1D4ED8", "#2563EB"]
    frames = []
    
    for color in colors:
        frame = Image.new("RGB", (img_width, img_height), BG_BLACK)
        draw = ImageDraw.Draw(frame)
        # Draw shadow text (offset by (x_offset, y_offset))
        draw.multiline_text((margin + x_offset, margin + y_offset), ascii_art, font=pil_font, fill=color)
        # Draw main text in blue
        draw.multiline_text((margin, margin), ascii_art, font=pil_font, fill=BLUE_PRIMARY)
        frames.append(frame)

    # Prompt the user to choose a folder and filename
    file_path = filedialog.asksaveasfilename(
        defaultextension=".gif",
        filetypes=[("GIF Files", "*.gif")],
        title="Save Animated GIF",
        initialfile="ascii_art.gif"
    )
    
    if not file_path:
        return  # User canceled the dialog

    # Save the frames as an animated GIF
    frames[0].save(file_path, save_all=True, append_images=frames[1:], duration=400, loop=0)
    status_var.set(f"GIF saved: {os.path.basename(file_path)}")

def clear_text():
    """Clear the input field and reset the canvas."""
    entry.delete(0, tk.END)
    canvas.delete("all")
    status_var.set("Ready")

def show_font_preview():
    """Show a preview of the selected font."""
    font_choice = font_var.get().strip() or "standard"
    preview_text = "Preview"
    preview_art = pyfiglet.figlet_format(preview_text, font=font_choice)
    display_art(preview_art)
    status_var.set(f"Font preview: {font_choice}")

def toggle_sidebar():
    """Toggle the left sidebar visibility."""
    global sidebar_visible
    sidebar_visible = not sidebar_visible
    
    if sidebar_visible:
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        toggle_sidebar_button.config(text="◀")
    else:
        sidebar.pack_forget()
        toggle_sidebar_button.config(text="▶")

def send_message():
    """Send a message to the Ollama chatbot."""
    message = chat_input.get()
    if not message.strip():
        return
    
    model = ollama_model_selector.get()
    if not model:
        append_to_chat("Please select a model first")
        return
        
    # Display user message
    append_to_chat(f"You: {message}")
    chat_input.delete(0, tk.END)
    
    # Get response in a separate thread
    def get_response():
        response = generate_from_ollama(model, message)
        root.after(0, lambda: append_to_chat(f"AI: {response}"))
    
    threading.Thread(target=get_response).start()

def append_to_chat(message):
    """Append a message to the chat history."""
    chat_history.config(state=tk.NORMAL)
    chat_history.insert(tk.END, message + "\n\n")
    chat_history.see(tk.END)
    chat_history.config(state=tk.DISABLED)

# Create main container
main_container = tk.Frame(root, bg=BG_BLACK)
main_container.pack(fill=tk.BOTH, expand=True)

# Create toggle sidebar button (fixed position)
toggle_sidebar_button = tk.Button(main_container, text="◀", font=("Consolas", 10), 
                                bg=DARK_GRAY, fg=LIGHT_GRAY, bd=0,
                                command=toggle_sidebar)
toggle_sidebar_button.place(x=5, y=5, width=20, height=20)

# Create left sidebar (collapsible)
sidebar = ttk.Frame(main_container, style="Sidebar.TFrame", width=250)
sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
sidebar.pack_propagate(False)  # Don't shrink

# Add title to sidebar
title_label = ttk.Label(sidebar, text="ASCII Art Generator", style="Title.TLabel")
title_label.pack(pady=(25, 25))  # Extra padding at top for toggle button

# Input section
input_section = ttk.Frame(sidebar, style="Sidebar.TFrame")
input_section.pack(fill=tk.X, pady=5, padx=10)

# Text input
entry_label = ttk.Label(input_section, text="Text:", style="Hacker.TLabel")
entry_label.pack(anchor=tk.W, pady=(0, 5))

entry = tk.Entry(input_section, width=25, font=("Consolas", 10), 
                bg=DARK_GRAY, fg=LIGHT_GRAY, insertbackground=LIGHT_GRAY)
entry.pack(fill=tk.X, pady=(0, 15))

# Font selection
font_var = tk.StringVar(value="standard")
font_label = ttk.Label(input_section, text="Font:", style="Hacker.TLabel")
font_label.pack(anchor=tk.W, pady=(0, 5))

font_combobox = ttk.Combobox(input_section, textvariable=font_var, values=available_fonts, 
                           state="readonly", style="Hacker.TCombobox", width=23)
font_combobox.pack(fill=tk.X, pady=(0, 5))
font_combobox.set("standard")

# Preview font button
preview_button = ttk.Button(input_section, text="Preview Font", command=show_font_preview, style="Hacker.TButton")
preview_button.pack(fill=tk.X, pady=(5, 15))

# Actions section
action_section = ttk.Frame(sidebar, style="Sidebar.TFrame")
action_section.pack(fill=tk.X, pady=5, padx=10)

# Button to generate ASCII art
generate_button = ttk.Button(action_section, text="Generate", command=generate_art, style="Hacker.TButton")
generate_button.pack(fill=tk.X, pady=5)

# Button to clear input
clear_button = ttk.Button(action_section, text="Clear", command=clear_text, style="Hacker.TButton")
clear_button.pack(fill=tk.X, pady=5)

# Button to copy to clipboard
copy_button = ttk.Button(action_section, text="Copy to Clipboard", command=copy_to_clipboard, style="Hacker.TButton")
copy_button.pack(fill=tk.X, pady=5)

# Button to save as GIF
save_button = ttk.Button(action_section, text="Save as GIF", command=save_animated_gif, style="Hacker.TButton")
save_button.pack(fill=tk.X, pady=5)

# Animation toggle
animation_frame = ttk.Frame(action_section, style="Sidebar.TFrame")
animation_frame.pack(fill=tk.X, pady=10)

animation_toggle_var = tk.BooleanVar(value=True)
animation_toggle = ttk.Checkbutton(animation_frame, text="Enable Animation", variable=animation_toggle_var, 
                                 command=toggle_animation, style="Hacker.TButton")
animation_toggle.pack(side=tk.LEFT)

# Main content area in the center
main_content = ttk.Frame(main_container, style="Hacker.TFrame")
main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

# Canvas with a subtle border
canvas = tk.Canvas(main_content, bg=BG_BLACK, highlightbackground=DARK_GRAY, highlightthickness=1)
canvas.pack(fill=tk.BOTH, expand=True)

# Right sidebar for Ollama chatbot
chat_sidebar = ttk.Frame(main_container, style="Sidebar.TFrame", width=300)
chat_sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
chat_sidebar.pack_propagate(False)  # Don't shrink

# Chatbot section
chat_title = ttk.Label(chat_sidebar, text="Ollama Chatbot", style="Title.TLabel")
chat_title.pack(pady=(15, 10))

# Model selector for chatbot
model_frame = ttk.Frame(chat_sidebar, style="Sidebar.TFrame")
model_frame.pack(fill=tk.X, padx=10, pady=5)

model_label = ttk.Label(model_frame, text="Select Model:", style="Hacker.TLabel")
model_label.pack(anchor=tk.W)

ollama_model_var = tk.StringVar()
ollama_model_selector = ttk.Combobox(model_frame, textvariable=ollama_model_var, values=ollama_models,
                                   state="readonly", style="Hacker.TCombobox")
ollama_model_selector.pack(fill=tk.X, pady=5)

refresh_button = ttk.Button(model_frame, text="Refresh Models", command=fetch_ollama_models, style="Hacker.TButton")
refresh_button.pack(fill=tk.X, pady=5)

# Chat history display
chat_history = tk.Text(chat_sidebar, bg=DARK_GRAY, fg=LIGHT_GRAY, font=("Consolas", 9),
                     wrap=tk.WORD, state=tk.DISABLED, height=20)
chat_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Chat input
input_frame = ttk.Frame(chat_sidebar, style="Sidebar.TFrame")
input_frame.pack(fill=tk.X, padx=10, pady=10)

chat_input = tk.Entry(input_frame, bg=DARK_GRAY, fg=LIGHT_GRAY, font=("Consolas", 9),
                    insertbackground=LIGHT_GRAY)
chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
chat_input.bind("<Return>", lambda event: send_message())

send_button = ttk.Button(input_frame, text="Send", command=send_message, style="Hacker.TButton", width=8)
send_button.pack(side=tk.RIGHT)

# Status bar for feedback
status_var = tk.StringVar(value="Ready")
status_bar = ttk.Label(root, textvariable=status_var, style="Status.TLabel", anchor=tk.W)
status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)

# Initialize with welcome message
welcome_message = pyfiglet.figlet_format("ASCII Art", font="standard")
display_art(welcome_message)
current_ascii_art = welcome_message

# Initialize chat with welcome message
append_to_chat("Welcome to the Ollama chatbot! Select a model and start chatting.")

# Try to fetch Ollama models on startup
threading.Thread(target=fetch_ollama_models).start()

# Center the window on the screen
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")

root.mainloop()

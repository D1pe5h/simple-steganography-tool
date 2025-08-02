import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import numpy as np
import os

# --- Core Functions ---
def text_to_bits(text):
    return ''.join(format(ord(char), '08b') for char in text)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

def encode(image_path, message, password, output_path):
    try:
        img = Image.open(image_path)
        pixels = np.array(img)

        if img.mode != 'RGB':
            pixels = np.array(img.convert('RGB'))
            img = Image.fromarray(pixels, 'RGB')

        flat = pixels.flatten()
        full_text = password + "::" + message + "\x00"
        data = text_to_bits(full_text)

        if len(data) > len(flat):
            return False, "Message too long for this image."

        for i in range(len(data)):
            flat[i] = flat[i] & ~1 | int(data[i])

        encoded_img = flat.reshape(pixels.shape)
        result_img = Image.fromarray(encoded_img.astype('uint8'), 'RGB')
        result_img.save(output_path)
        return True, "Message encoded successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def decode(image_path, password):
    try:
        img = Image.open(image_path)
        pixels = np.array(img)
        flat = pixels.flatten()
        bits = ""

        for i in range(len(flat)):
            bits += str(flat[i] & 1)
            if len(bits) % 8 == 0:
                byte = bits[-8:]
                if byte == "00000000":
                    break

        full_text = bits_to_text(bits)
        if "::" not in full_text:
            return "Error: No hidden data found or corrupted."

        parts = full_text.split("::", 1)
        pass_check, message = parts[0], parts[1].rstrip("\x00")

        if pass_check == password:
            return message
        else:
            return "Access Denied"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Dark Theme GUI Application ---
class StegoTool:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 StegoTool - Secure Image Steganography")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#121212")  # Dark background

        # Custom Styles
        style = ttk.Style()
        style.theme_use("clam")  # Better control over styling

        # Dark colors
        bg_color = "#121212"
        fg_color = "#FFFFFF"
        accent_color = "#008CBA"
        entry_bg = "#1E1E1E"
        button_hover = "#006F8F"

        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color,
                        padding=(20, 8), font=("Arial", 10))
        style.map("TNotebook.Tab", background=[("selected", accent_color)], 
                  foreground=[("selected", "white")])

        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Arial", 10))
        style.configure("TButton", background=accent_color, foreground=fg_color, font=("Arial", 10, "bold"))
        style.map("TButton", background=[("active", button_hover)])

        # Tab control
        self.tab_control = ttk.Notebook(root)
        self.encode_tab = ttk.Frame(self.tab_control)
        self.decode_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.encode_tab, text="Encode Message")
        self.tab_control.add(self.decode_tab, text="Decode Message")
        self.tab_control.pack(expand=1, fill="both", padx=20, pady=20)

        # Apply dark style to all widgets manually
        self.setup_encode_tab()
        self.setup_decode_tab()

    def setup_encode_tab(self):
        frame = self.encode_tab
        frame.configure(style="TLabel")

        # Title
        title = tk.Label(frame, text="Hide Your Message", font=("Arial", 14, "bold"), bg="#121212", fg="#00BFFF")
        title.grid(row=0, column=0, columnspan=3, pady=(10, 20))

        # Image Path
        tk.Label(frame, text="Image Path:", bg="#121212", fg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        self.image_path_encode = tk.Entry(frame, width=50, bg="#1E1E1E", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#333")
        self.image_path_encode.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(frame, text="Browse", bg="#008CBA", fg="white", font=("Arial", 9), relief="flat", cursor="hand2", command=self.browse_image_encode).grid(row=1, column=2, padx=10)

        # Password
        tk.Label(frame, text="Password:", bg="#121212", fg="white", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        self.password_encode = tk.Entry(frame, width=50, show="*", bg="#1E1E1E", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#333")
        self.password_encode.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

        # Message
        tk.Label(frame, text="Secret Message:", bg="#121212", fg="white", font=("Arial", 10)).grid(row=3, column=0, sticky="nw", padx=20, pady=10)
        self.message_text = tk.Text(frame, height=6, width=50, bg="#1E1E1E", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#333", font=("Arial", 9))
        self.message_text.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

        # Encode Button
        tk.Button(frame, text="🔐 Encode & Save", bg="#00A86B", fg="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", height=2, command=self.encode_message).grid(row=4, column=1, columnspan=2, pady=20)

        # Status
        self.status_encode = tk.Label(frame, text="", fg="#00BFFF", bg="#121212", font=("Arial", 9))
        self.status_encode.grid(row=5, column=1, columnspan=2, pady=5)

    def setup_decode_tab(self):
        frame = self.decode_tab
        frame.configure(style="TLabel")

        # Title
        title = tk.Label(frame, text="Extract Hidden Message", font=("Arial", 14, "bold"), bg="#121212", fg="#FF6347")
        title.grid(row=0, column=0, columnspan=3, pady=(10, 20))

        # Image Path
        tk.Label(frame, text="Image Path:", bg="#121212", fg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        self.image_path_decode = tk.Entry(frame, width=50, bg="#1E1E1E", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#333")
        self.image_path_decode.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(frame, text="Browse", bg="#008CBA", fg="white", font=("Arial", 9), relief="flat", cursor="hand2", command=self.browse_image_decode).grid(row=1, column=2, padx=10)

        # Password
        tk.Label(frame, text="Password:", bg="#121212", fg="white", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        self.password_decode = tk.Entry(frame, width=50, show="*", bg="#1E1E1E", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#333")
        self.password_decode.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

        # Decode Button
        tk.Button(frame, text="🔓 Decode Message", bg="#FF6347", fg="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", height=2, command=self.decode_message).grid(row=3, column=1, columnspan=2, pady=20)

        # Result
        tk.Label(frame, text="Extracted Message:", bg="#121212", fg="white", font=("Arial", 10)).grid(row=4, column=0, sticky="nw", padx=20, pady=10)
        self.result_text = tk.Text(frame, height=6, width=50, bg="#1E1E1E", fg="white", relief="flat", highlightthickness=1, highlightbackground="#333", font=("Arial", 9))
        self.result_text.grid(row=4, column=1, columnspan=2, padx=10, pady=10)

        # Status
        self.status_decode = tk.Label(frame, text="", fg="#00BFFF", bg="#121212", font=("Arial", 9))
        self.status_decode.grid(row=5, column=1, columnspan=2, pady=5)

    def browse_image_encode(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.bmp;*.tiff;*.jpg;*.jpeg")])
        if path:
            self.image_path_encode.delete(0, tk.END)
            self.image_path_encode.insert(0, path)

    def browse_image_decode(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.bmp;*.tiff;*.jpg;*.jpeg")])
        if path:
            self.image_path_decode.delete(0, tk.END)
            self.image_path_decode.insert(0, path)

    def encode_message(self):
        image_path = self.image_path_encode.get().strip()
        password = self.password_encode.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()

        if not image_path or not password or not message:
            messagebox.showerror("⚠ Input Error", "All fields are required!")
            return

        if not os.path.exists(image_path):
            messagebox.showerror("⚠ File Error", "Image file not found!")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                   filetypes=[("PNG Files", "*.png")],
                                                   title="Save Encoded Image As")
        if not output_path:
            return

        success, msg = encode(image_path, message, password, output_path)
        self.status_encode.config(text=msg)
        self.status_encode.config(fg="lightgreen" if success else "red")
        if success:
            messagebox.showinfo("✅ Success", msg)
        else:
            messagebox.showerror("❌ Error", msg)

    def decode_message(self):
        image_path = self.image_path_decode.get().strip()
        password = self.password_decode.get().strip()

        if not image_path or not password:
            messagebox.showerror("⚠ Input Error", "Image path and password are required!")
            return

        if not os.path.exists(image_path):
            messagebox.showerror("⚠ File Error", "Image file not found!")
            return

        result = decode(image_path, password)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)
        self.status_decode.config(text="Decoding completed.", fg="lightgreen")

# --- Run Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = StegoTool(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import hashlib
import time
import csv
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw  # pyright: ignore[reportMissingImports]
import qrcode # type: ignore
import os
import sys
import math
from pyzbar import pyzbar   # type: ignore
import cv2  # pyright: ignore[reportMissingImports]
import geocoder  # type: ignore
import socket
import requests # type: ignore
# from pyzbar.pyzbar import decode


class DiamondBackground(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.diamonds = []
        self.bind("<Configure>", self.redraw)
        
    def redraw(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Diamond pattern parameters
        size = 40
        cols = width // size + 2
        rows = height // size + 2
        
        # Create diamond pattern
        for row in range(rows):
            for col in range(cols):
                x = col * size
                y = row * size
                
                # Offset every other column
                if col % 2 == 1:
                    y += size // 2
                
                # Draw diamond
                points = [
                    x + size//2, y,
                    x + size, y + size//2,
                    x + size//2, y + size,
                    x, y + size//2
                ]
                
                self.create_polygon(points, 
                                   fill="#e6f3ff",  # Light blue fill
                                   outline="#b3d9ff",  # Lighter blue outline
                                   width=1,
                                   tags="diamond")

class VenusAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Venus Attendance System")
        self.root.geometry("1300x800")
        self.current_user = None  # Initialize current_user
        
        # Set application icon
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, 'logo.png')
            self.root.iconbitmap(icon_path)
        except:
            pass  # Continue without icon if there's an error

        # Theme configuration with diamond theme
        self.themes = {
             "venus_jewel": {
        "bg": "#0A1A44",               # Dark royal blue background
        "fg": "#ffffff",               # White text
        "button_bg": "#FFFFFF",        # Soft blue button
        "button_fg": "#001548",        # White button text
        "entry_fg": "#1B2B65",         # Darker entry field
        "entry_bg": "#ffffff",         # White text in entry
        "highlight": "#FFFFFF",        # Light blue border / focus
        "error": "#FF6B6B",            # Red for errors
        "success": "#28C76F",          # Green for success
        "font": ("Segoe UI", 10),      # Clean modern font
        "heading_font": ("Segoe UI", 18, "bold"),
        "hover": "#000000"          # Light gray on hover
        },
            # "Light": {
            #     "fg": "#000000",
            #     "bg": "#FFFFFF",
            #     "button_bg": "#ffffff",
            #     "button_fg": "#000000",
            #     "highlight": "#4CAF50",
            #     "entry_bg": "#3d3d3d"
            # },
            "Dark": {
                "bg": "#000000",
                "fg": "#FFFFFF",
                "button_bg": "#fefefe",
                "button_fg": "#000000",
                "highlight": "#FFFFFF",
                "entry_bg": "#ffffff"
            }
        }
        self.current_theme = "venus_jewel"
        
        # Create diamond background
        self.background = DiamondBackground(self.root)
        self.background.pack(fill="both", expand=True)
        
        # Main container frame
        self.main_container = tk.Frame(self.background, bg=self.themes[self.current_theme]["bg"])
        self.main_container.place(relwidth=0.95, relheight=0.95, relx=0.025, rely=0.025)
        
        # Load logo image
        self.load_logo()
        
        # Initialize database
        self.init_db()
        
        # Show splash screen first
        self.show_splash()
    
    def load_logo(self):
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            logo_path = os.path.join(application_path, 'logo.png')
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(logo_img)
        except:
            self.logo_img = None
    
    def create_header(self, parent_frame):
        """Create consistent header with logo for all screens"""
        header_frame = tk.Frame(parent_frame, bg=self.themes[self.current_theme]["bg"])
        header_frame.pack(fill='x', padx=10, pady=5)
        
        if self.logo_img:
            logo_label = tk.Label(header_frame, image=self.logo_img, 
                                bg=self.themes[self.current_theme]["bg"])
            logo_label.pack(side='left', padx=5)
        
        tk.Label(header_frame, text="Venus Attendance System", 
                font=('Arial', 20, 'bold'),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side='left', padx=10)
        
        return header_frame
    
    def init_db(self):
        self.conn = sqlite3.connect('attendance.db')
        self.c = self.conn.cursor()
        
        # Create users table if not exists
        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         username TEXT UNIQUE,
                         password TEXT,
                         full_name TEXT,
                         contact TEXT,
                         organization TEXT,
                         department TEXT,
                         position TEXT,
                         role TEXT DEFAULT 'user')''')
        
        # Create admin user if not exists
        self.c.execute("SELECT id FROM users WHERE username='admin'")
        if not self.c.fetchone():
            hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
            self.c.execute('''INSERT INTO users 
                            (username, password, full_name, role) 
                            VALUES (?, ?, ?, ?)''',
                          ('admin', hashed_password, 'Administrator', 'admin'))
        
        # Create attendance table with location fields
        self.c.execute('''CREATE TABLE IF NOT EXISTS attendance
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         user_id INTEGER,
                         action TEXT,
                         timestamp DATETIME,
                         latitude REAL,
                         longitude REAL,
                         address TEXT,
                         ip_address TEXT,
                         device_info TEXT,
                         FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        self.conn.commit()

    
    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.main_container.config(bg=theme["bg"])
        
        for widget in self.main_container.winfo_children():
            self._apply_theme_to_widget(widget, theme)
    
    def _apply_theme_to_widget(self, widget, theme):
        if isinstance(widget, (tk.Frame, tk.LabelFrame)):
            widget.config(bg=theme["bg"])
        elif isinstance(widget, tk.Label):
            widget.config(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, tk.Button):
            widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                        activebackground=theme["highlight"])
        elif isinstance(widget, tk.Entry):
            widget.config(bg=theme["entry_bg"], fg="black", insertbackground="black")
        elif isinstance(widget, ttk.Widget):
            style = ttk.Style()
            style.configure("TFrame", background=theme["bg"])
            style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
            style.configure("TButton", 
                          background=theme["button_bg"], 
                          foreground=theme["button_fg"])
            style.configure("TEntry", 
                          fieldbackground=theme["entry_bg"], 
                          foreground="black")
            style.configure("Treeview", 
                          background=theme["bg"],
                          foreground=theme["fg"],
                          fieldbackground=theme["bg"])
            style.configure("Treeview.Heading",
                          background=theme["button_bg"],
                          foreground=theme["button_fg"])
        
        for child in widget.winfo_children():
            self._apply_theme_to_widget(child, theme)
    
    def show_splash(self):
        self.clear_window()
        
        splash_frame = tk.Frame(self.main_container, bg=self.themes[self.current_theme]["bg"])
        splash_frame.pack(expand=True, fill='both')
        
        if self.logo_img:
            logo_label = tk.Label(splash_frame, image=self.logo_img, 
                                bg=self.themes[self.current_theme]["bg"])
            logo_label.pack(pady=20)
        
        tk.Label(splash_frame, text="Venus Attendance System", 
                font=('Arial', 24, 'bold'), bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(pady=10)
        
        self.spinner_canvas = tk.Canvas(splash_frame, width=50, height=50,
                                       bg=self.themes[self.current_theme]["bg"],
                                       highlightthickness=0)
        self.spinner_canvas.pack()
        self.spinner_id = self.spinner_canvas.create_arc(5, 5, 45, 45, start=0, extent=20, 
                                                        style='arc', width=3,
                                                        outline=self.themes[self.current_theme]["highlight"])
        
        self.root.after(3000, self.show_login)
        self.animate_spinner()
    
    def animate_spinner(self, angle=0):
        try:
            self.spinner_canvas.itemconfig(self.spinner_id, start=angle)
            angle = (angle + 10) % 360
            self.root.after(50, lambda: self.animate_spinner(angle))
        except tk.TclError:
            pass
    
    def show_login(self):
        self.clear_window()
        
        # Main login container
        login_container = tk.Frame(self.main_container, 
                                bg=self.themes[self.current_theme]["bg"],
                                bd=0, highlightthickness=0)
        login_container.pack(expand=True, fill='both')
        
        # Logo and title frame
        logo_frame = tk.Frame(login_container, bg=self.themes[self.current_theme]["bg"])
        logo_frame.pack(pady=(50, 20))
        
        if self.logo_img:
            logo_label = tk.Label(logo_frame, image=self.logo_img, 
                                bg=self.themes[self.current_theme]["bg"])
            logo_label.pack()
        
        tk.Label(logo_frame, text="Venus Attendance System", 
                font=('Arial', 14),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack()
        
        # Login form frame
        form_frame = tk.Frame(login_container, 
                            bg=self.themes[self.current_theme]["bg"],
                            padx=30, pady=20)
        form_frame.pack()
        
        # Login title
        tk.Label(form_frame, text="Login", 
                font=('Arial', 18, 'bold'),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Form fields
        tk.Label(form_frame, text="Username:", 
                font=('Arial', 12),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=1, column=0, sticky='w', pady=5)
        self.username_entry = tk.Entry(form_frame, 
                                    font=('Arial', 12),
                                    bg=self.themes[self.current_theme]["entry_bg"],
                                    fg="black",
                                    width=25,
                                    bd=1,
                                    relief='solid')
        self.username_entry.grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Password:", 
                font=('Arial', 12),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=2, column=0, sticky='w', pady=5)
        self.password_entry = tk.Entry(form_frame, 
                                    font=('Arial', 12),
                                    show="*", 
                                    bg=self.themes[self.current_theme]["entry_bg"],
                                    fg="black",
                                    width=25,
                                    bd=1,
                                    relief='solid')
        self.password_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Login as radio buttons
        tk.Label(form_frame, text="Login as:", 
                font=('Arial', 12),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=3, column=0, sticky='w', pady=5)
        
        radio_frame = tk.Frame(form_frame, bg=self.themes[self.current_theme]["bg"])
        radio_frame.grid(row=3, column=1, sticky='w', padx=10)
        
        self.role_var = tk.StringVar(value="user")
        tk.Radiobutton(radio_frame, text="User", 
                    variable=self.role_var, 
                    value="user",
                    font=('Arial', 11),
                    bg=self.themes[self.current_theme]["bg"],
                    fg=self.themes[self.current_theme]["fg"],
                    selectcolor=self.themes[self.current_theme]["bg"]).pack(side='left')
        tk.Radiobutton(radio_frame, text="Admin", 
                    variable=self.role_var, 
                    value="admin",
                    font=('Arial', 11),
                    bg=self.themes[self.current_theme]["bg"],
                    fg=self.themes[self.current_theme]["fg"],
                    selectcolor=self.themes[self.current_theme]["bg"]).pack(side='left', padx=10)
        
        # Button frame
        button_frame = tk.Frame(form_frame, bg=self.themes[self.current_theme]["bg"])
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Login Button - Solid Style
        login_btn = tk.Button(button_frame,
                            text="LOGIN",
                            command=self.login,
                            font=('Arial', 12, 'bold'),
                            bg="#4CAF50",  # Green color
                            fg="white",
                            activebackground="#45a049",
                            activeforeground="white",
                            width=15,
                            bd=4,
                            relief='flat',
                            padx=10,
                            pady=5,
                            cursor="hand2")
        login_btn.pack(pady=5)
        
        # Hover effects for login button
        def on_enter_login(e):
            login_btn['bg'] = "#45a049"  # Darker green on hover
        
        def on_leave_login(e):
            login_btn['bg'] = "#FEFFFE"  # Original green
        
        login_btn.bind("<Enter>", on_enter_login)
        login_btn.bind("<Leave>", on_leave_login)
        
        # Options frame for Register/Forgot Password
        options_frame = tk.Frame(form_frame, bg=self.themes[self.current_theme]["bg"])
        options_frame.grid(row=5, column=0, columnspan=2)
        
        # Register Button - Text Link Style
        register_btn = tk.Button(options_frame,
                                text="Register",
                                command=self.show_register,
                                font=('Arial', 10, 'underline'),
                                bg=self.themes[self.current_theme]["bg"],
                                fg=self.themes[self.current_theme]["highlight"],
                                activebackground=self.themes[self.current_theme]["bg"],
                                activeforeground=self.themes[self.current_theme]["button_fg"],
                                bd=2,
                                width=15,
                                relief='flat',
                                padx=10,
                                cursor="hand2")
        register_btn.pack(side='left', padx=5)
        
        # Hover effects for register button
        def on_enter_register(e):
            register_btn['bg'] = "#45a049" 
            register_btn['fg'] = self.themes[self.current_theme]["hover"]
        
        def on_leave_register(e):
            register_btn['bg'] = "#fefffe" 
            register_btn['fg'] = self.themes[self.current_theme]["hover"]
        
        register_btn.bind("<Enter>", on_enter_register)
        register_btn.bind("<Leave>", on_leave_register)
        
        # Separator
        tk.Label(options_frame,
                text="|",
                font=('Arial', 10),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side='left', padx=5)
        
        # Forgot Password Button - Text Link Style
        forgot_btn = tk.Button(options_frame,
                            text="Forgot Password",
                            command=self.forgot_password,
                            font=('Arial', 10, 'underline'),
                            bg=self.themes[self.current_theme]["bg"],
                            fg=self.themes[self.current_theme]["highlight"],
                            activebackground=self.themes[self.current_theme]["bg"],
                            activeforeground=self.themes[self.current_theme]["button_fg"],
                            bd=2,
                            width=15,
                            relief='flat',
                            cursor="hand2")
        forgot_btn.pack(side='left', padx=5)
        
        # Hover effects for forgot password button
        def on_enter_forgot(e):
            forgot_btn['bg'] = "#45a049" 
            forgot_btn['fg'] = self.themes[self.current_theme]["hover"]
        
        def on_leave_forgot(e):
            forgot_btn['bg'] = "#ffffff" 
            forgot_btn['fg'] = self.themes[self.current_theme]["hover"]
        
        forgot_btn.bind("<Enter>", on_enter_forgot)
        forgot_btn.bind("<Leave>", on_leave_forgot)
        
        # Center all widgets
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        
        self.apply_theme()


    def get_location_data(self):
        """Get current location data using geocoder"""
        try:
            # Get IP-based location
            ip_info = requests.get('https://ipinfo.io/json').json()
            ip = ip_info.get('ip', '')
            loc = ip_info.get('loc', '').split(',')
            city = ip_info.get('city', '')
            region = ip_info.get('region', '')
            country = ip_info.get('country', '')
            
            latitude, longitude = 0.0, 0.0
            if len(loc) == 2:
                latitude, longitude = float(loc[0]), float(loc[1])
            
            address = f"{city}, {region}, {country}"
            
            # Get device hostname
            device = socket.gethostname()
            
            return {
                'latitude': latitude,
                'longitude': longitude,
                'address': address,
                'ip_address': ip,
                'device_info': device
            }
        except Exception as e:
            print(f"Error getting location: {e}")
            return {
                'latitude': 0.0,
                'longitude': 0.0,
                'address': "Location unavailable",
                'ip_address': "Unknown",
                'device_info': "Unknown"
            }


    def show_register(self):
        self.clear_window()
        
        # Main register container
        register_container = tk.Frame(self.main_container, 
                                    bg=self.themes[self.current_theme]["bg"],
                                    bd=0, highlightthickness=0)
        register_container.pack(expand=True, fill='both')
        
        # Logo and title frame
        logo_frame = tk.Frame(register_container, bg=self.themes[self.current_theme]["bg"])
        logo_frame.pack(pady=(30, 10))
        
        if self.logo_img:
            logo_label = tk.Label(logo_frame, image=self.logo_img, 
                                bg=self.themes[self.current_theme]["bg"])
            logo_label.pack()
        
        tk.Label(logo_frame, text="Venus Attendance System", 
                font=('Arial', 14),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack()
        
        tk.Label(logo_frame, text="Create New Account", 
                font=('Arial', 16, 'bold'),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(pady=(10, 0))
        
        # Register form frame
        form_frame = tk.Frame(register_container, 
                            bg=self.themes[self.current_theme]["bg"],
                            padx=30, pady=20)
        form_frame.pack()
        
        # Form fields
        fields = [
            ("Full Name:", "full_name_entry"),
            ("Username:", "username_entry"),
            ("Password:", "password_entry"),
            ("Contact No:", "contact_entry"),
            ("Organization:", "org_entry"),
            ("Department:", "dept_entry"),
            ("Position:", "position_entry")
        ]
        
        self.entries = {}
        for i, (label, name) in enumerate(fields):
            # Label
            tk.Label(form_frame, text=label,
                    font=('Arial', 12),
                    bg=self.themes[self.current_theme]["bg"],
                    fg=self.themes[self.current_theme]["fg"]).grid(row=i, column=0, sticky='w', pady=5)
            
            # Entry field
            entry = tk.Entry(form_frame, 
                            font=('Arial', 12),
                            show="*" if "password" in name else "",
                            bg=self.themes[self.current_theme]["entry_bg"],
                            fg="black",
                            width=25,
                            bd=1,
                            relief='solid')
            entry.grid(row=i, column=1, pady=5, padx=10, sticky='w')
            self.entries[name] = entry
        
        # Button frame
        button_frame = tk.Frame(form_frame, bg=self.themes[self.current_theme]["bg"])
        button_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        # Register Button - Solid Style
        register_btn = tk.Button(button_frame,
                            text="REGISTER",
                            command=self.register,
                            font=('Arial', 12, 'bold'),
                            bg="#4CAF50",  # Green color
                            fg="white",
                            activebackground="#45a049",
                            activeforeground="white",
                            width=15,
                            bd=0,
                            relief='flat',
                            padx=10,
                            pady=5,
                            cursor="hand2")
        register_btn.pack(side='left', padx=10)
        
        # Back to Login Button - Outline Style
        back_btn = tk.Button(button_frame,
                            text="BACK TO LOGIN",
                            command=self.show_login,
                            font=('Arial', 12, 'bold'),
                            bg=self.themes[self.current_theme]["bg"],
                            fg=self.themes[self.current_theme]["highlight"],
                            activebackground="#f0f0f0",
                            activeforeground=self.themes[self.current_theme]["highlight"],
                            width=15,
                            bd=1,
                            relief='solid',
                            padx=10,
                            pady=5,
                            cursor="hand2")
        back_btn.pack(side='left', padx=10)
        
        # Hover effects for register button
        def on_enter_register(e):
            register_btn['bg'] = "#45a049"  # Darker green on hover
        
        def on_leave_register(e):
            register_btn['bg'] = "#FFFFFF"  # Original green
        
        register_btn.bind("<Enter>", on_enter_register)
        register_btn.bind("<Leave>", on_leave_register)
        
        # Hover effects for back button
        def on_enter_back(e):
            back_btn['bg'] = "#45a049"  # Light gray on hover
        
        def on_leave_back(e):
            back_btn['bg'] = "#f0f0f0" # Original background
        
        back_btn.bind("<Enter>", on_enter_back)
        back_btn.bind("<Leave>", on_leave_back)
        
        # Center all widgets in the form
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        
        self.apply_theme()
        
    def show_dashboard(self):
        if not self.current_user:
            self.show_login()
            return
            
        self.clear_window()
        
        self.create_header(self.main_container)
        
        menubar = tk.Menu(self.root)
        
        attendance_menu = tk.Menu(menubar, tearoff=0)
        attendance_menu.add_command(label="Check In", command=lambda: self.show_qr_scanner("in"))
        attendance_menu.add_command(label="Check Out", command=lambda: self.show_qr_scanner("out"))
        menubar.add_cascade(label="Attendance", menu=attendance_menu)
        
        profile_menu = tk.Menu(menubar, tearoff=0)
        profile_menu.add_command(label="View Profile", command=self.show_profile)
        menubar.add_cascade(label="Profile", menu=profile_menu)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        for theme_name in self.themes.keys():
            theme_menu.add_command(label=theme_name, 
                                 command=lambda t=theme_name: self.change_theme(t))
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        settings_menu.add_command(label="Change Password", command=self.change_password)
        settings_menu.add_separator()
        settings_menu.add_command(label="Logout", command=self.logout)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        history_menu = tk.Menu(menubar, tearoff=0)
        history_menu.add_command(label="Daily", command=lambda: self.show_attendance_history("daily"))
        history_menu.add_command(label="Monthly", command=lambda: self.show_attendance_history("monthly"))
        history_menu.add_command(label="All", command=lambda: self.show_attendance_history("all"))
        history_menu.add_separator()
        history_menu.add_command(label="Export History", command=self.export_attendance_history)
        menubar.add_cascade(label="Attendance History", menu=history_menu)
        
        if self.current_user[8] == 'admin':
            admin_menu = tk.Menu(menubar, tearoff=0)
            admin_menu.add_command(label="Manage Users", command=self.manage_users)
            admin_menu.add_command(label="View All Attendance", command=self.view_all_attendance)
            admin_menu.add_command(label="Generate Reports", command=self.generate_reports)
            menubar.add_cascade(label="Admin", menu=admin_menu)
        
        self.root.config(menu=menubar)
        
        main_frame = tk.Frame(self.main_container, bg=self.themes[self.current_theme]["bg"])
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        welcome_frame = tk.Frame(main_frame, bg=self.themes[self.current_theme]["bg"])
        welcome_frame.pack(fill='x', pady=10)
        
        role = "Administrator" if self.current_user[8] == 'admin' else "User"
        tk.Label(welcome_frame, text=f"Welcome, {self.current_user[3]}! ({role})", 
                font=('Arial', 16),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side='left')
        
        actions_frame = tk.Frame(main_frame, bg=self.themes[self.current_theme]["bg"])
        actions_frame.pack(fill='x', pady=20)
        
        tk.Button(actions_frame, text="Check In", command=lambda: self.show_qr_scanner("in"), 
                 width=15, height=3,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).grid(row=0, column=0, padx=10)
        tk.Button(actions_frame, text="Check Out", command=lambda: self.show_qr_scanner("out"), 
                 width=15, height=3,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).grid(row=0, column=1, padx=10)
        tk.Button(actions_frame, text="Attendance History", command=lambda: self.show_attendance_history("daily"), 
                 width=15, height=3,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).grid(row=0, column=2, padx=10)
        tk.Button(actions_frame, text="Profile", command=self.show_profile, 
                 width=15, height=3,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).grid(row=0, column=3, padx=10)
        
        if self.current_user[8] == 'admin':
            tk.Button(actions_frame, text="Manage Users", command=self.manage_users, 
                     width=15, height=3,
                     bg="#ff9999",
                     fg="black").grid(row=0, column=4, padx=10)
            tk.Button(actions_frame, text="View All Attendance", command=self.view_all_attendance, 
                     width=15, height=3,
                     bg="#ff9999",
                     fg="black").grid(row=0, column=5, padx=10)
        
        form_frame = tk.LabelFrame(main_frame, text="Employee Information", 
                                 bg=self.themes[self.current_theme]["bg"],
                                 fg=self.themes[self.current_theme]["fg"],
                                 font=('Arial', 12, 'bold'))
        form_frame.pack(fill='both', expand=True, pady=20)
        
        details = [
            ("Employee ID:", self.current_user[0]),
            ("Full Name:", self.current_user[3]),
            ("Username:", self.current_user[1]),
            ("Contact:", self.current_user[4]),
            ("Organization:", self.current_user[5]),
            ("Department:", self.current_user[6] if len(self.current_user) > 6 else "N/A"),
            ("Position:", self.current_user[7] if len(self.current_user) > 7 else "N/A"),
            ("Role:", self.current_user[8] if len(self.current_user) > 8 else "user")
        ]
        
        for i, (label, value) in enumerate(details):
            tk.Label(form_frame, text=label, font=('Arial', 11),
                    bg=self.themes[self.current_theme]["bg"],
                    fg=self.themes[self.current_theme]["fg"]).grid(row=i, column=0, sticky='e', padx=10, pady=5)
            tk.Label(form_frame, text=value, font=('Arial', 11),
                    bg=self.themes[self.current_theme]["bg"],
                    fg=self.themes[self.current_theme]["fg"]).grid(row=i, column=1, sticky='w', padx=10, pady=5)
        
        recent_frame = tk.LabelFrame(main_frame, text="Recent Attendance", 
                                   bg=self.themes[self.current_theme]["bg"],
                                   fg=self.themes[self.current_theme]["fg"],
                                   font=('Arial', 12, 'bold'))
        recent_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        style = ttk.Style()
        style.configure("Treeview", 
                       background=self.themes[self.current_theme]["bg"],
                       foreground=self.themes[self.current_theme]["fg"],
                       fieldbackground=self.themes[self.current_theme]["fg"])
        style.configure("Treeview.Heading",
                       background=self.themes[self.current_theme]["button_fg"],
                       foreground=self.themes[self.current_theme]["button_bg"])
        
        tree = ttk.Treeview(recent_frame, columns=('Date', 'Check In', 'Check Out'), show='headings', height=5)
        tree.heading('Date', text='Date')
        tree.heading('Check In', text='First Check In')
        tree.heading('Check Out', text='Last Check Out')
        
        scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.c.execute("""
            SELECT date(timestamp) as date, 
                   time(min(timestamp)) as first_in, 
                   time(max(case when action='out' then timestamp end)) as last_out
            FROM attendance 
            WHERE user_id=?
            GROUP BY date(timestamp)
            ORDER BY date(timestamp) DESC
            LIMIT 5
        """, (self.current_user[0],))
        
        records = self.c.fetchall()
        for record in records:
            tree.insert('', 'end', values=record)
        
        self.apply_theme()
    
    def manage_users(self):
        if not self.current_user or self.current_user[8] != 'admin':
            messagebox.showerror("Error", "You don't have permission to access this feature")
            return
        
        self.clear_window()
        
        self.create_header(self.main_container)
        
        users_frame = tk.Frame(self.main_container, bg=self.themes[self.current_theme]["bg"])
        users_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(users_frame, text="User Management", 
                font=('Arial', 16),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(pady=10)
        
        buttons_frame = tk.Frame(users_frame, bg=self.themes[self.current_theme]["bg"])
        buttons_frame.pack(fill='x', pady=10)
        
        tk.Button(buttons_frame, text="Add New User", command=self.add_new_user,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Back to Dashboard", command=self.show_dashboard,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).pack(side='right', padx=5)
        
        style = ttk.Style()
        style.configure("Treeview", 
                       background=self.themes[self.current_theme]["bg"],
                       foreground=self.themes[self.current_theme]["fg"],
                       fieldbackground=self.themes[self.current_theme]["bg"])
        style.configure("Treeview.Heading",
                       background=self.themes[self.current_theme]["button_bg"],
                       foreground=self.themes[self.current_theme]["button_fg"])
        
        tree = ttk.Treeview(users_frame, columns=('ID', 'Username', 'Full Name', 'Role'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Username', text='Username')
        tree.heading('Full Name', text='Full Name')
        tree.heading('Role', text='Role')
        
        scrollbar = ttk.Scrollbar(users_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        context_menu = tk.Menu(tree, tearoff=0)
        context_menu.add_command(label="Edit User", command=lambda: self.edit_user(tree))
        context_menu.add_command(label="Delete User", command=lambda: self.delete_user(tree))
        context_menu.add_command(label="Reset Password", command=lambda: self.reset_user_password(tree))
        
        def show_context_menu(event):
            item = tree.identify_row(event.y)
            if item:
                tree.selection_set(item)
                context_menu.post(event.x_root, event.y_root)
        
        tree.bind("<Button-3>", show_context_menu)
        
        self.c.execute("SELECT id, username, full_name, role FROM users ORDER BY id")
        users = self.c.fetchall()
        
        for user in users:
            tree.insert('', 'end', values=user)
        
        self.apply_theme()
    
    def add_new_user(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New User")
        add_window.geometry("400x500")
        
        theme = self.themes[self.current_theme]
        add_window.config(bg=theme["bg"])
        
        main_frame = tk.Frame(add_window, bg=theme["bg"])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Add New User", font=('Arial', 14),
                bg=theme["bg"], fg=theme["fg"]).pack(pady=10)
        
        form_frame = tk.Frame(main_frame, bg=theme["bg"])
        form_frame.pack(fill='both', expand=True)
        
        fields = [
            ("Full Name:", "full_name"),
            ("Username:", "username"),
            ("Password:", "password"),
            ("Contact No:", "contact"),
            ("Organization:", "org"),
            ("Department:", "dept"),
            ("Position:", "position"),
            ("Role:", "role")
        ]
        
        self.new_user_entries = {}
        self.role_var = tk.StringVar(value="user")
        
        for i, (label, name) in enumerate(fields):
            tk.Label(form_frame, text=label, bg=theme["bg"], fg=theme["fg"]).grid(
                row=i, column=0, sticky='e', padx=5, pady=5)
            
            if name == "password":
                entry = tk.Entry(form_frame, show="*", bg=theme["entry_bg"])
            elif name == "role":
                role_menu = tk.OptionMenu(form_frame, self.role_var, "user", "admin")
                role_menu.config(bg=theme["button_bg"], fg=theme["button_fg"])
                role_menu.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                continue
            else:
                entry = tk.Entry(form_frame, bg=theme["entry_bg"])
            
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
            self.new_user_entries[name] = entry
        
        button_frame = tk.Frame(main_frame, bg=theme["bg"])
        button_frame.pack(fill='x', pady=10)
        
        tk.Button(button_frame, text="Save", command=self.save_new_user,
                 bg=theme["button_bg"], fg=theme["button_fg"]).pack(
                 side='right', padx=5)
        
        tk.Button(button_frame, text="Cancel", command=add_window.destroy,
                 bg=theme["button_bg"], fg=theme["button_fg"]).pack(
                 side='right', padx=5)
        
        form_frame.grid_columnconfigure(1, weight=1)
    
    def save_new_user(self):
        data = {
            'full_name': self.new_user_entries['full_name'].get(),
            'username': self.new_user_entries['username'].get(),
            'password': self.new_user_entries['password'].get(),
            'contact': self.new_user_entries['contact'].get(),
            'org': self.new_user_entries['org'].get(),
            'dept': self.new_user_entries['dept'].get(),
            'position': self.new_user_entries['position'].get(),
            'role': self.role_var.get()
        }
        
        if not data['username'] or not data['password'] or not data['full_name']:
            messagebox.showerror("Error", "Username, password and full name are required")
            return
        
        try:
            hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
            
            self.c.execute("""INSERT INTO users 
                           (username, password, full_name, contact, organization, department, position, role) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           (data['username'], hashed_password, data['full_name'], 
                            data['contact'], data['org'], data['dept'], 
                            data['position'], data['role']))
            self.conn.commit()
            
            messagebox.showinfo("Success", "User added successfully")
            self.root.focus_get().destroy()
            self.manage_users()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
    
    def edit_user(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a user to edit")
            return
        
        user_data = tree.item(selected_item)['values']
        user_id = user_data[0]
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit User")
        edit_window.geometry("400x400")
        
        theme = self.themes[self.current_theme]
        edit_window.config(bg=theme["bg"])
        
        self.c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = self.c.fetchone()
        
        fields = [
            ("Full Name:", "full_name", user[3]),
            ("Username:", "username", user[1]),
            ("Contact No:", "contact", user[4]),
            ("Organization:", "org", user[5]),
            ("Department:", "dept", user[6]),
            ("Position:", "position", user[7]),
            ("Role:", "role", user[8])
        ]
        
        entries = {}
        role_var = tk.StringVar(value=user[8])
        
        for i, (label, name, value) in enumerate(fields):
            tk.Label(edit_window, text=label, bg=theme["bg"], fg=theme["fg"]).grid(
                row=i, column=0, sticky='e', padx=5, pady=5)
            
            if name == "role":
                entry = tk.OptionMenu(edit_window, role_var, "user", "admin")
                entry.config(bg=theme["button_bg"], fg=theme["button_fg"])
            else:
                entry = tk.Entry(edit_window, bg=theme["entry_bg"])
                entry.insert(0, value if value else "")
            
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[name] = entry
        
        def update_user():
            data = {
                'full_name': entries['full_name'].get(),
                'username': entries['username'].get(),
                'contact': entries['contact'].get(),
                'org': entries['org'].get(),
                'dept': entries['dept'].get(),
                'position': entries['position'].get(),
                'role': role_var.get()
            }
            
            if not data['username'] or not data['full_name']:
                messagebox.showerror("Error", "Username and full name are required")
                return
            
            try:
                self.c.execute("UPDATE users SET username=?, full_name=?, contact=?, organization=?, department=?, position=?, role=? WHERE id=?",
                             (data['username'], data['full_name'], data['contact'], data['org'], data['dept'], data['position'], data['role'], user_id))
                self.conn.commit()
                messagebox.showinfo("Success", "User updated successfully")
                edit_window.destroy()
                self.manage_users()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists")
        
        tk.Button(edit_window, text="Update", command=update_user,
                bg=theme["button_bg"], fg=theme["button_fg"]).grid(
                row=len(fields)+1, column=1, pady=10)
    
    def delete_user(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a user to delete")
            return
        
        user_data = tree.item(selected_item)['values']
        user_id = user_data[0]
        username = user_data[1]
        
        if user_id == self.current_user[0]:
            messagebox.showerror("Error", "You cannot delete your own account")
            return
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete user {username}?"):
            self.c.execute("DELETE FROM users WHERE id=?", (user_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "User deleted successfully")
            self.manage_users()
    
    def reset_user_password(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a user to reset password")
            return
        
        user_data = tree.item(selected_item)['values']
        user_id = user_data[0]
        username = user_data[1]
        
        new_password = tk.simpledialog.askstring("Reset Password", 
                                               f"Enter new password for {username}:",
                                               show='*')
        if new_password:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            self.c.execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Password reset successfully")
    
    def view_all_attendance(self):
        if not self.current_user or self.current_user[8] != 'admin':
            messagebox.showerror("Error", "You don't have permission to access this feature")
            return
        
        self.clear_window()
        
        self.create_header(self.main_container)
        
        attendance_frame = tk.Frame(self.main_container, bg=self.themes[self.current_theme]["bg"])
        attendance_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(attendance_frame, text="All Attendance Records", 
                font=('Arial', 16),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(pady=10)
        
        filter_frame = tk.Frame(attendance_frame, bg=self.themes[self.current_theme]["bg"])
        filter_frame.pack(fill='x', pady=10)
        
        tk.Label(filter_frame, text="From:", 
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side='left', padx=5)
        self.from_date_entry = tk.Entry(filter_frame, bg=self.themes[self.current_theme]["entry_bg"])
        self.from_date_entry.pack(side='left', padx=5)
        
        tk.Label(filter_frame, text="To:", 
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side='left', padx=5)
        self.to_date_entry = tk.Entry(filter_frame, bg=self.themes[self.current_theme]["entry_bg"])
        self.to_date_entry.pack(side='left', padx=5)
        
        tk.Label(filter_frame, text="User:", 
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side='left', padx=5)
        
        self.user_var = tk.StringVar()
        self.user_dropdown = ttk.Combobox(filter_frame, textvariable=self.user_var, state='readonly')
        self.user_dropdown.pack(side='left', padx=5)
        
        self.c.execute("SELECT id, username FROM users ORDER BY username")
        users = self.c.fetchall()
        user_dict = {user[0]: user[1] for user in users}
        self.user_dropdown['values'] = ["All Users"] + [f"{user[0]} - {user[1]}" for user in users]
        self.user_dropdown.current(0)
        
        buttons_frame = tk.Frame(attendance_frame, bg=self.themes[self.current_theme]["bg"])
        buttons_frame.pack(fill='x', pady=10)
        
        tk.Button(buttons_frame, text="Filter", command=self.apply_attendance_filters,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Export to CSV", command=self.export_all_attendance,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="View Map", command=self.show_attendance_map,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Back to Dashboard", command=self.show_dashboard,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).pack(side='right', padx=5)
        
        style = ttk.Style()
        style.configure("Treeview", 
                       background=self.themes[self.current_theme]["bg"],
                       foreground=self.themes[self.current_theme]["fg"],
                       fieldbackground=self.themes[self.current_theme]["bg"])
        style.configure("Treeview.Heading",
                       background=self.themes[self.current_theme]["button_bg"],
                       foreground=self.themes[self.current_theme]["button_fg"])
        
        self.attendance_tree = ttk.Treeview(attendance_frame, 
                                          columns=('ID', 'User', 'Action', 'Timestamp', 'Location', 'Device'), 
                                          show='headings')
        self.attendance_tree.heading('ID', text='ID')
        self.attendance_tree.heading('User', text='User')
        self.attendance_tree.heading('Action', text='Action')
        self.attendance_tree.heading('Timestamp', text='Timestamp')
        self.attendance_tree.heading('Location', text='Location')
        self.attendance_tree.heading('Device', text='Device')
        
        self.attendance_tree.column('ID', width=50, anchor='center')
        self.attendance_tree.column('User', width=150)
        self.attendance_tree.column('Action', width=80, anchor='center')
        self.attendance_tree.column('Timestamp', width=150, anchor='center')
        self.attendance_tree.column('Location', width=200)
        self.attendance_tree.column('Device', width=150)
        
        scrollbar = ttk.Scrollbar(attendance_frame, orient="vertical", command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        
        self.attendance_tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        self.load_all_attendance()
        
        self.apply_theme()

    
    def load_all_attendance(self, user_id=None, from_date=None, to_date=None):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        query = """
            SELECT a.id, u.username, a.action, a.timestamp, 
                   CASE WHEN a.address IS NOT NULL THEN a.address ELSE 'Unknown' END as location,
                   a.device_info
            FROM attendance a
            JOIN users u ON a.user_id = u.id
        """
        params = []
        
        conditions = []
        if user_id:
            conditions.append("a.user_id=?")
            params.append(user_id)
        
        if from_date:
            conditions.append("date(a.timestamp) >= ?")
            params.append(from_date)
        
        if to_date:
            conditions.append("date(a.timestamp) <= ?")
            params.append(to_date)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY a.timestamp DESC"
        
        self.c.execute(query, params)
        records = self.c.fetchall()
        
        for record in records:
            self.attendance_tree.insert('', 'end', values=record)

    def apply_attendance_filters(self):
        user_filter = self.user_var.get()
        from_date = self.from_date_entry.get()
        to_date = self.to_date_entry.get()
        
        user_id = None
        if user_filter and user_filter != "All Users":
            user_id = int(user_filter.split(' - ')[0])
        
        if from_date and to_date:
            try:
                datetime.strptime(from_date, '%Y-%m-%d')
                datetime.strptime(to_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
        
        self.load_all_attendance(user_id, from_date, to_date)
    

    def show_attendance_map(self):
        """Show a map with attendance locations (placeholder implementation)"""
        try:
            # Get all attendance records with location data
            self.c.execute("""
                SELECT u.username, a.latitude, a.longitude, a.timestamp, a.action 
                FROM attendance a
                JOIN users u ON a.user_id = u.id
                WHERE a.latitude != 0 AND a.longitude != 0
                ORDER BY a.timestamp DESC
                LIMIT 100
            """)
            records = self.c.fetchall()
            
            if not records:
                messagebox.showinfo("Info", "No location data available to display on map")
                return
            
            # In a real implementation, you would use a mapping library like folium
            # Here we'll just show the coordinates in a messagebox
            map_info = "Attendance Locations:\n\n"
            for record in records:
                username, lat, lon, timestamp, action = record
                map_info += f"{username} checked {action} at {timestamp}\n"
                map_info += f"Location: {lat}, {lon}\n\n"
            
            # Create a scrollable text window to display the locations
            map_window = tk.Toplevel(self.root)
            map_window.title("Attendance Locations")
            map_window.geometry("600x400")
            
            text_frame = tk.Frame(map_window)
            text_frame.pack(fill='both', expand=True)
            
            text_widget = tk.Text(text_frame, wrap='word')
            scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side='right', fill='y')
            text_widget.pack(side='left', fill='both', expand=True)
            
            text_widget.insert('1.0', map_info)
            text_widget.configure(state='disabled')
            
            # In a production app, you would:
            # 1. Use folium to create an interactive map
            # 2. Add markers for each attendance record
            # 3. Display the map in a webview or export as HTML
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show map: {str(e)}")



    def export_all_attendance(self):
        items = self.attendance_tree.get_children()
        if not items:
            messagebox.showinfo("Info", "No attendance records found to export")
            return
        
        data = []
        for item in items:
            values = self.attendance_tree.item(item)['values']
            data.append(values)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Attendance Data As"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Username', 'Action', 'Timestamp', 'Location', 'Device'])
                writer.writerows(data)
            
            messagebox.showinfo("Success", f"Attendance data exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export attendance data:\n{str(e)}")

    def generate_reports(self):
        if not self.current_user or self.current_user[8] != 'admin':
            messagebox.showerror("Error", "You don't have permission to access this feature")
            return
        
        report_window = tk.Toplevel(self.root)
        report_window.title("Generate Reports")
        report_window.geometry("500x300")
        
        theme = self.themes[self.current_theme]
        report_window.config(bg=theme["bg"])
        
        tk.Label(report_window, text="Generate Attendance Report", 
                font=('Arial', 14),
                bg=theme["bg"], fg=theme["fg"]).pack(pady=10)
        
        tk.Label(report_window, text="Report Type:",
                bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
        self.report_type = tk.StringVar(value="daily")
        tk.Radiobutton(report_window, text="Daily Summary", variable=self.report_type, value="daily",
                      bg=theme["bg"], fg=theme["fg"]).pack()
        tk.Radiobutton(report_window, text="Monthly Summary", variable=self.report_type, value="monthly",
                      bg=theme["bg"], fg=theme["fg"]).pack()
        tk.Radiobutton(report_window, text="User Activity", variable=self.report_type, value="user",
                      bg=theme["bg"], fg=theme["fg"]).pack()
        
        tk.Label(report_window, text="Date Range:",
                bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
        
        date_frame = tk.Frame(report_window, bg=theme["bg"])
        date_frame.pack()
        
        tk.Label(date_frame, text="From:",
                bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=0, padx=5)
        self.report_from_date = tk.Entry(date_frame, bg=theme["entry_bg"])
        self.report_from_date.grid(row=0, column=1, padx=5)
        
        tk.Label(date_frame, text="To:",
                bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=2, padx=5)
        self.report_to_date = tk.Entry(date_frame, bg=theme["entry_bg"])
        self.report_to_date.grid(row=0, column=3, padx=5)
        
        tk.Button(report_window, text="Generate Report", 
                 command=self.generate_report_data,
                 bg=theme["button_bg"], fg=theme["button_fg"]).pack(pady=20)
    
    def generate_report_data(self):
        report_type = self.report_type.get()
        from_date = self.report_from_date.get()
        to_date = self.report_to_date.get()
        
        if from_date and to_date:
            try:
                datetime.strptime(from_date, '%Y-%m-%d')
                datetime.strptime(to_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
        
        if report_type == "daily":
            self.generate_daily_report(from_date, to_date)
        elif report_type == "monthly":
            self.generate_monthly_report(from_date, to_date)
        elif report_type == "user":
            self.generate_user_activity_report(from_date, to_date)
    
    def generate_daily_report(self, from_date=None, to_date=None):
        query = """
            SELECT date(timestamp) as date, 
                   COUNT(DISTINCT user_id) as users,
                   SUM(CASE WHEN action='in' THEN 1 ELSE 0 END) as check_ins,
                   SUM(CASE WHEN action='out' THEN 1 ELSE 0 END) as check_outs
            FROM attendance
        """
        
        params = []
        conditions = []
        
        if from_date:
            conditions.append("date(timestamp) >= ?")
            params.append(from_date)
        
        if to_date:
            conditions.append("date(timestamp) <= ?")
            params.append(to_date)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY date(timestamp) ORDER BY date(timestamp) DESC"
        
        self.c.execute(query, params)
        records = self.c.fetchall()
        
        if not records:
            messagebox.showinfo("Info", "No attendance data found for the selected period")
            return
        
        headers = ["Date", "Unique Users", "Check-Ins", "Check-Outs"]
        data = [headers] + [list(record) for record in records]
        
        self.save_report_data(data, "daily_attendance_report")
    
    def generate_monthly_report(self, from_date=None, to_date=None):
        query = """
            SELECT strftime('%Y-%m', timestamp) as month,
                   COUNT(DISTINCT user_id) as users,
                   SUM(CASE WHEN action='in' THEN 1 ELSE 0 END) as check_ins,
                   SUM(CASE WHEN action='out' THEN 1 ELSE 0 END) as check_outs
            FROM attendance
        """
        
        params = []
        conditions = []
        
        if from_date:
            conditions.append("date(timestamp) >= ?")
            params.append(from_date)
        
        if to_date:
            conditions.append("date(timestamp) <= ?")
            params.append(to_date)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY strftime('%Y-%m', timestamp) ORDER BY month DESC"
        
        self.c.execute(query, params)
        records = self.c.fetchall()
        
        if not records:
            messagebox.showinfo("Info", "No attendance data found for the selected period")
            return
        
        headers = ["Month", "Unique Users", "Check-Ins", "Check-Outs"]
        data = [headers] + [list(record) for record in records]
        
        self.save_report_data(data, "monthly_attendance_report")
    
    def generate_user_activity_report(self, from_date=None, to_date=None):
        query = """
            SELECT u.id, u.username, u.full_name,
                   COUNT(CASE WHEN a.action='in' THEN 1 END) as check_ins,
                   COUNT(CASE WHEN a.action='out' THEN 1 END) as check_outs,
                   MIN(a.timestamp) as first_activity,
                   MAX(a.timestamp) as last_activity
            FROM users u
            LEFT JOIN attendance a ON u.id = a.user_id
        """
        
        params = []
        conditions = []
        
        if from_date or to_date:
            if from_date:
                conditions.append("date(a.timestamp) >= ?")
                params.append(from_date)
            
            if to_date:
                conditions.append("date(a.timestamp) <= ?")
                params.append(to_date)
            
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY u.id ORDER BY u.username"
        
        self.c.execute(query, params)
        records = self.c.fetchall()
        
        if not records:
            messagebox.showinfo("Info", "No user activity data found for the selected period")
            return
        
        headers = ["User ID", "Username", "Full Name", "Check-Ins", "Check-Outs", "First Activity", "Last Activity"]
        data = [headers] + [list(record) for record in records]
        
        self.save_report_data(data, "user_activity_report")
    
    def save_report_data(self, data, default_filename):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Report As",
            initialfile=default_filename
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)
            
            messagebox.showinfo("Success", f"Report generated successfully:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def show_attendance_history(self, period):
        self.clear_window()
        
        self.create_header(self.main_container)
        
        history_frame = tk.Frame(self.main_container, bg=self.themes[self.current_theme]["bg"])
        history_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(history_frame, text=f"Attendance History ({period})", 
                font=('Arial', 16),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(pady=10)
        
        buttons_frame = tk.Frame(history_frame, bg=self.themes[self.current_theme]["bg"])
        buttons_frame.pack(fill='x', pady=10)
        
        tk.Button(buttons_frame, text="Export to CSV", command=self.export_attendance_history,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Back to Dashboard", command=self.show_dashboard,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).pack(side='right', padx=5)
        
        style = ttk.Style()
        style.configure("Treeview", 
                       background=self.themes[self.current_theme]["bg"],
                       foreground=self.themes[self.current_theme]["fg"],
                       fieldbackground=self.themes[self.current_theme]["bg"])
        style.configure("Treeview.Heading",
                       background=self.themes[self.current_theme]["button_bg"],
                       foreground=self.themes[self.current_theme]["button_fg"])
        
        tree = ttk.Treeview(history_frame, columns=('Date', 'Check In', 'Check Out'), show='headings')
        tree.heading('Date', text='Date')
        tree.heading('Check In', text='First Check In')
        tree.heading('Check Out', text='Last Check Out')
        
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        if period == "daily":
            query = """
                SELECT date(timestamp) as date, 
                       time(min(timestamp)) as first_in, 
                       time(max(case when action='out' then timestamp end)) as last_out
                FROM attendance 
                WHERE user_id=?
                GROUP BY date(timestamp)
                ORDER BY date(timestamp) DESC
                LIMIT 30
            """
        elif period == "monthly":
            query = """
                SELECT strftime('%Y-%m', timestamp) as month,
                       min(time(timestamp)) as earliest_checkin,
                       max(time(case when action='out' then timestamp end)) as latest_checkout
                FROM attendance
                WHERE user_id=?
                GROUP BY strftime('%Y-%m', timestamp)
                ORDER BY month DESC
            """
        else:
            query = """
                SELECT date(timestamp) as date, 
                       time(min(timestamp)) as first_in, 
                       time(max(case when action='out' then timestamp end)) as last_out
                FROM attendance 
                WHERE user_id=?
                GROUP BY date(timestamp)
                ORDER BY date(timestamp) DESC
            """
        
        self.c.execute(query, (self.current_user[0],))
        records = self.c.fetchall()
        
        for record in records:
            tree.insert('', 'end', values=record)
        
        self.apply_theme()
    
    def export_attendance_history(self):
        self.c.execute("""
            SELECT date(timestamp) as date, 
                   time(min(timestamp)) as first_in, 
                   time(max(case when action='out' then timestamp end)) as last_out
            FROM attendance 
            WHERE user_id=?
            GROUP BY date(timestamp)
            ORDER BY date(timestamp)
        """, (self.current_user[0],))
        
        records = self.c.fetchall()
        
        if not records:
            messagebox.showinfo("Info", "No attendance records found to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Attendance History As"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "First Check-In", "Last Check-Out", "Employee Name", "Employee ID"])
                
                for record in records:
                    writer.writerow([
                        record[0],
                        record[1],
                        record[2],
                        self.current_user[3],
                        self.current_user[0]
                    ])
            
            messagebox.showinfo("Success", f"Attendance history exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export attendance history:\n{str(e)}")
    
    def show_qr_scanner(self, action):
        def scan_qr_code():
            cap = cv2.VideoCapture(0)
            found = False

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                decoded_objects = pyzbar.decode(frame)
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    cap.release()
                    cv2.destroyAllWindows()
                    found = True
                    self.process_attendance(qr_data)
                    return

                cv2.imshow("Scan QR Code - Press 'q' to Quit", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            if not found:
                messagebox.showwarning("QR Scanner", "No QR code detected.")

        self.clear_window()
        self.create_header(self.main_container)

        # Get location data
        location_data = self.get_location_data()
        
        # Include location in QR data
        qr_data = f"{self.current_user[0]}_{action}_{time.time()}_" \
                  f"{location_data['latitude']}_{location_data['longitude']}_" \
                  f"{location_data['ip_address']}"
        
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_tk = ImageTk.PhotoImage(img)

        img_label = tk.Label(self.main_container, image=img_tk,
                            bg=self.themes[self.current_theme]["bg"])
        img_label.image = img_tk
        img_label.pack(pady=10)

        # Show location information
        loc_frame = tk.Frame(self.main_container, bg=self.themes[self.current_theme]["bg"])
        loc_frame.pack(pady=10)
        
        tk.Label(loc_frame, text="Current Location:", 
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=0, sticky='e')
        tk.Label(loc_frame, text=location_data['address'], 
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=1, sticky='w')
        
        tk.Label(loc_frame, text="Coordinates:", 
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=1, column=0, sticky='e')
        tk.Label(loc_frame, text=f"{location_data['latitude']}, {location_data['longitude']}", 
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=1, column=1, sticky='w')
        
        tk.Label(loc_frame, text="Device:", 
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=2, column=0, sticky='e')
        tk.Label(loc_frame, text=location_data['device_info'], 
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).grid(row=2, column=1, sticky='w')

        scan_btn = tk.Button(self.main_container, text="Start QR Scanner", command=scan_qr_code,
                            bg=self.themes[self.current_theme]["button_bg"],
                            fg=self.themes[self.current_theme]["button_fg"])
        scan_btn.pack(pady=10)

        back_btn = tk.Button(self.main_container, text="Back to Dashboard", command=self.show_dashboard,
                            bg=self.themes[self.current_theme]["button_bg"],
                            fg=self.themes[self.current_theme]["button_fg"])
        back_btn.pack(pady=10)

        self.apply_theme()

    
    def show_profile(self):
        self.clear_window()
        
        self.create_header(self.main_container)
        
        profile_frame = tk.Frame(self.main_container, bg=self.themes[self.current_theme]["bg"])
        profile_frame.pack(expand=True, padx=50, pady=20)
        
        tk.Label(profile_frame, text="Your Profile", 
                font=('Arial', 18),
                bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(pady=20)
        
        details_frame = tk.Frame(profile_frame, bg=self.themes[self.current_theme]["bg"])
        details_frame.pack()
        
        details = [
            ("Employee ID:", self.current_user[0]),
            ("Full Name:", self.current_user[3]),
            ("Username:", self.current_user[1]),
            ("Contact:", self.current_user[4]),
            ("Organization:", self.current_user[5]),
            ("Department:", self.current_user[6] if len(self.current_user) > 6 else "N/A"),
            ("Position:", self.current_user[7] if len(self.current_user) > 7 else "N/A"),
            ("Role:", self.current_user[8] if len(self.current_user) > 8 else "user")
        ]
        
        for i, (label, value) in enumerate(details):
            tk.Label(details_frame, text=label, font=('Arial', 12),
                    bg=self.themes[self.current_theme]["bg"],
                    fg=self.themes[self.current_theme]["fg"]).grid(row=i, column=0, sticky='e', pady=5)
            tk.Label(details_frame, text=value, font=('Arial', 12),
                    bg=self.themes[self.current_theme]["bg"],
                    fg=self.themes[self.current_theme]["fg"]).grid(row=i, column=1, sticky='w', pady=5)
        
        tk.Button(profile_frame, text="Back to Dashboard", command=self.show_dashboard,
                 bg=self.themes[self.current_theme]["button_bg"],
                 fg=self.themes[self.current_theme]["button_fg"]).pack(pady=20)
        
        self.apply_theme()
    
    def process_attendance(self, qr_data):
        try:
            parts = qr_data.split('_')
            user_id = int(parts[0])
            action = parts[1]
            timestamp = parts[2]
            latitude = float(parts[3]) if len(parts) > 3 else 0.0
            longitude = float(parts[4]) if len(parts) > 4 else 0.0
            ip_address = parts[5] if len(parts) > 5 else "Unknown"
            
            if user_id != self.current_user[0]:
                messagebox.showerror("Error", "Invalid QR code")
                return
            
            # Get more detailed location info
            location_data = self.get_location_data()
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.c.execute("""INSERT INTO attendance 
                           (user_id, action, timestamp, latitude, longitude, address, ip_address, device_info) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                          (user_id, action, now, latitude, longitude, 
                           location_data['address'], ip_address, location_data['device_info']))
            self.conn.commit()
            
            messagebox.showinfo("Success", f"Successfully checked {action} at {now}\nLocation: {location_data['address']}")
            self.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_window(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        self.c.execute("SELECT * FROM users WHERE username=? AND password=?", 
                      (username, hashed_password))
        user = self.c.fetchone()
        
        if user:
            if role and user[8] != role:
                messagebox.showerror("Error", f"You don't have permission to login as {role}")
                return
            
            self.current_user = user
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def register(self):
        data = {
            'full_name': self.entries['full_name_entry'].get(),
            'username': self.entries['username_entry'].get(),
            'password': self.entries['password_entry'].get(),
            'contact': self.entries['contact_entry'].get(),
            'org': self.entries['org_entry'].get(),
            'dept': self.entries['dept_entry'].get(),
            'position': self.entries['position_entry'].get()
        }
        
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required")
            return
        
        self.c.execute("SELECT id FROM users WHERE username=?", (data['username'],))
        if self.c.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return
        
        hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
        
        self.c.execute("INSERT INTO users (username, password, full_name, contact, organization, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (data['username'], hashed_password, data['full_name'], data['contact'], data['org'], data['dept'], data['position']))
        self.conn.commit()
        
        messagebox.showinfo("Success", "Registration successful! Please login.")
        self.show_login()
    
    def logout(self):
        self.current_user = None
        self.show_login()
    
    def forgot_password(self):
        messagebox.showinfo("Info", "Please contact your administrator to reset your password")
    
    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme()
        
        if theme_name == "Diamond":
            self.background.delete("all")
            self.background.redraw()
    
    def change_password(self):
        pass_window = tk.Toplevel(self.root)
        pass_window.title("Change Password")
        pass_window.geometry("400x200")
        
        theme = self.themes[self.current_theme]
        pass_window.config(bg=theme["bg"])
        
        tk.Label(pass_window, text="Current Password:",
                bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
        current_pass = tk.Entry(pass_window, show="*", bg=theme["entry_bg"])
        current_pass.pack(pady=5)
        
        tk.Label(pass_window, text="New Password:",
                bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
        new_pass = tk.Entry(pass_window, show="*", bg=theme["entry_bg"])
        new_pass.pack(pady=5)
        
        tk.Label(pass_window, text="Confirm New Password:",
                bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
        confirm_pass = tk.Entry(pass_window, show="*", bg=theme["entry_bg"])
        confirm_pass.pack(pady=5)
        
        def update_password():
            current = current_pass.get()
            new = new_pass.get()
            confirm = confirm_pass.get()
            
            if not current or not new or not confirm:
                messagebox.showerror("Error", "All fields are required")
                return
            
            if new != confirm:
                messagebox.showerror("Error", "New passwords don't match")
                return
            
            hashed_current = hashlib.sha256(current.encode()).hexdigest()
            self.c.execute("SELECT password FROM users WHERE id=?", (self.current_user[0],))
            db_password = self.c.fetchone()[0]
            
            if hashed_current != db_password:
                messagebox.showerror("Error", "Current password is incorrect")
                return
            
            hashed_new = hashlib.sha256(new.encode()).hexdigest()
            self.c.execute("UPDATE users SET password=? WHERE id=?", 
                         (hashed_new, self.current_user[0]))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Password updated successfully")
            pass_window.destroy()
        
        tk.Button(pass_window, text="Update Password", command=update_password,
                bg=theme["button_bg"], fg=theme["button_fg"]).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = VenusAttendanceSystem(root)
    root.mainloop()
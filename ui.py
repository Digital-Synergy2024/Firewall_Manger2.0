import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from firewall import FirewallManager
from utils import log_action, log_error, download_image_from_url
import bcrypt
import json
import subprocess
import time
import os
from PIL import Image, ImageTk


class FirewallManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("N3xG3n Firewall Manager")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1E1E2E")
        self.root.attributes("-alpha", 1.0)  # Set transparency
        self.root.resizable(True, True)
        self.firewall_manager = FirewallManager()
        self.users_file = "users.json"
        self.session_timeout = 300  # 5 minutes
        self.last_activity = time.time()
        self.admin_username = "admin"
        self.admin_password = bcrypt.hashpw(
            "admin123".encode(), bcrypt.gensalt()
        ).decode()
        self.users = {}
        self.load_users()
        self.authenticate_user()
        self.start_session_monitor()
        self.root.bind("<Configure>", self.on_resize)
        self.background_image = None
        self.background_label = None
        self.current_image_path = None
        self.current_image_url = None
        self.set_background_image(image_path="Wolf.jpg")  # Set initial background image
        self.default_log_path = (
            "C:\\xampp\\apache\\logs\\access.log"  # Default for VPS hosting
        )
        self.custom_log_paths = []  # List to store custom log paths

    def load_users(self):
        """Load user credentials from a file."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r") as file:
                    self.users = json.load(file)
            except Exception as e:
                log_error(f"Failed to load users: {e}")
                self.users = {self.admin_username: self.admin_password}
        else:
            self.users = {self.admin_username: self.admin_password}
            self.save_users()

    def save_users(self):
        """Save user credentials to a file."""
        try:
            with open(self.users_file, "w") as file:
                json.dump(self.users, file)
        except Exception as e:
            log_error(f"Failed to save users: {e}")

    def authenticate_user(self):
        """Authenticate the user with a login system."""
        while True:
            choice = self.show_auth_dialog()
            if choice == "cancel":
                self.show_message_dialog(
                    "Exiting",
                    "You have canceled the login process. Exiting the application.",
                )
                self.root.quit()
                return
            elif choice == "login":
                username = self.show_input_dialog("Login", "Enter your username:")
                if not username:
                    self.show_message_dialog("Error", "Username cannot be empty!")
                    continue

                password = self.show_input_dialog(
                    "Login", "Enter your password:", is_password=True
                )
                if not password:
                    self.show_message_dialog("Error", "Password cannot be empty!")
                    continue

                if username in self.users and bcrypt.checkpw(
                    password.encode(), self.users[username].encode()
                ):
                    self.show_message_dialog("Success", "Login successful!")
                    self.create_main_menu()  # Ensure this is called after successful login
                    break
                else:
                    self.show_message_dialog(
                        "Error", "Invalid credentials. Please try again."
                    )
            elif choice == "register":
                username = self.show_input_dialog("Register", "Enter a new username:")
                if not username:
                    self.show_message_dialog("Error", "Username cannot be empty!")
                    continue

                if username in self.users:
                    self.show_message_dialog(
                        "Error",
                        "Username already exists. Please choose a different username.",
                    )
                    continue

                password = self.show_input_dialog(
                    "Register", "Enter a new password:", is_password=True
                )
                if not password:
                    self.show_message_dialog("Error", "Password cannot be empty!")
                    continue

                hashed_password = bcrypt.hashpw(
                    password.encode(), bcrypt.gensalt()
                ).decode()
                self.users[username] = hashed_password
                self.save_users()
                self.show_message_dialog(
                    "Success", "Registration successful! You can now log in."
                )

    def show_auth_dialog(self):
        """Show a dialog to ask the user if they want to log in or register."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Authentication")
        dialog.geometry("400x200")
        dialog.configure(bg="#1E1E2E")
        dialog.resizable(False, False)

        tk.Label(
            dialog,
            text="Do you have an account?",
            font=("Segoe UI", 12),
            fg="#FFFFFF",
            bg="#1E1E2E",
        ).pack(pady=20)

        result = {"choice": None}

        def on_login():
            result["choice"] = "login"
            dialog.destroy()

        def on_register():
            result["choice"] = "register"
            dialog.destroy()

        def on_cancel():
            result["choice"] = "cancel"
            dialog.destroy()

        button_frame = tk.Frame(dialog, bg="#1E1E2E")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Login",
            command=on_login,
            font=("Segoe UI", 12),
            bg="#2E2E3E",
            fg="#FFFFFF",
            activebackground="#3E3E4E",
            activeforeground="#FFFFFF",
            width=10,
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame,
            text="Register",
            command=on_register,
            font=("Segoe UI", 12),
            bg="#2E2E3E",
            fg="#FFFFFF",
            activebackground="#3E3E4E",
            activeforeground="#FFFFFF",
            width=10,
        ).pack(side="left", padx=10)

        tk.Button(
            dialog,
            text="Cancel",
            command=on_cancel,
            font=("Segoe UI", 12),
            bg="#E74C3C",
            fg="#FFFFFF",
            activebackground="#C0392B",
            activeforeground="#FFFFFF",
            width=10,
        ).pack(pady=10)

        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

        return result["choice"]

    def create_scrollable_window(parent, title, width=1000, height=600):
        """Create a scrollable Toplevel window."""
        window = tk.Toplevel(parent)
        window.title(title)
        window.geometry(f"{width}x{height}")
        window.configure(bg="#1E1E2E")

        # Create a canvas and scrollbar
        canvas = tk.Canvas(window, bg="#1E1E2E", highlightthickness=0)
        scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1E1E2E")

        # Configure the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Update scroll region when content changes
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        return window, scrollable_frame

    def create_main_menu(self):
        """Create the main menu with a grid layout, scrollable content, and live data viewing."""
        self.clear_window()

        # Header
        header_frame = tk.Frame(self.root, bg="#1E1E2E", pady=10)
        header_frame.pack(fill="x")
        tk.Label(
            header_frame,
            text="N3xG3n Firewall Manager",
            font=("Segoe UI", 24, "bold"),
            fg="#FFFFFF",
            bg="#1E1E2E",
        ).pack()

        # Main Content
        main_content_frame = tk.Frame(self.root, bg="#1E1E2E")
        main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Scrollable Firewall Section
        firewall_canvas = tk.Canvas(
            main_content_frame, bg="#1E1E2E", highlightthickness=0, width=250
        )
        firewall_scrollbar = tk.Scrollbar(
            main_content_frame, orient="vertical", command=firewall_canvas.yview
        )
        firewall_frame = tk.Frame(firewall_canvas, bg="#1E1E2E")

        firewall_canvas.create_window((0, 0), window=firewall_frame, anchor="nw")
        firewall_canvas.configure(yscrollcommand=firewall_scrollbar.set)

        firewall_canvas.pack(side="left", fill="y", expand=True, padx=10, pady=10)
        firewall_scrollbar.pack(side="left", fill="y")

        tk.Label(
            firewall_frame,
            text="Firewall Controls",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg="#1E1E2E"
        ).pack(side="top", pady=10)

        firewall_buttons = [
            ("Enable Firewall", self.firewall_manager.enable_firewall),
            ("Disable Firewall", self.firewall_manager.disable_firewall),
            (
                "Open Ports",
                lambda: self.show_input_and_execute(self.firewall_manager.open_ports),
            ),
            (
                "Close Ports",
                lambda: self.show_input_and_execute(self.firewall_manager.close_ports),
            ),
            (
                "List Active Rules",
                lambda: self.show_output(self.firewall_manager.list_active_rules),
            ),
            (
                "Search Rule",
                lambda: self.show_input_and_execute(
                    self.firewall_manager.search_firewall_rule
                ),
            ),
            (
                "Delete Rule",
                lambda: self.show_input_and_execute(
                    self.firewall_manager.delete_firewall_rule
                ),
            ),
            (
                "Detect Port Conflicts",
                lambda: self.show_input_and_execute(
                    self.firewall_manager.detect_port_conflicts
                ),
            ),
            ("Firewall Rule Simulator", self.show_firewall_rule_simulator),
            ("Backup Rules", self.firewall_manager.backup_firewall_rules),
            ("Restore Rules", self.firewall_manager.restore_firewall_rules),
            ("Reset Firewall", self.firewall_manager.reset_firewall),
            ("Optimize Rules", self.firewall_manager.optimize_rules),
            (
                "Validate Rule",
                lambda: self.show_input_and_execute(
                    self.firewall_manager.validate_firewall_rule
                ),
            ),
            ("Advanced Rule Management", self.advanced_rule_management),
            ("View Firewall Activity", self.view_firewall_activity),
            ("Generate Security Audit Report", self.generate_security_audit_report),
            (
                "View Statistics",
                lambda: self.show_output(self.firewall_manager.view_statistics),
            ),
        ]

        for text, command in firewall_buttons:
            tk.Button(
                firewall_frame,
                text=text,
                command=command,
                font=("Segoe UI", 10, "bold"),
                bg="#2E2E3E",
                fg="#FFFFFF",
                activebackground="#3E3E4E",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=5,
                pady=5,
            ).pack(fill="x", pady=5, padx=10)

        firewall_frame.update_idletasks()
        firewall_canvas.config(scrollregion=firewall_canvas.bbox("all"))

        # Scrollable Networking Section
        networking_canvas = tk.Canvas(
            main_content_frame, bg="#1E1E2E", highlightthickness=0, width=250
        )
        networking_scrollbar = tk.Scrollbar(
            main_content_frame, orient="vertical", command=networking_canvas.yview
        )
        networking_frame = tk.Frame(networking_canvas, bg="#1E1E2E")

        networking_canvas.create_window((0, 0), window=networking_frame, anchor="nw")
        networking_canvas.configure(yscrollcommand=networking_scrollbar.set)

        networking_canvas.pack(side="right", fill="y", expand=True, padx=10, pady=10)
        networking_scrollbar.pack(side="right", fill="y")

        tk.Label(
            networking_frame,
            text="Networking Tools",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg="#1E1E2E"
        ).pack(side="top", pady=10)

        networking_buttons = [
            (
                "Query Port Status",
                lambda: self.show_input_and_execute(
                    self.firewall_manager.query_port_status
                ),
            ),
            ("Predefined Port Profiles", self.show_predefined_port_profiles),
            ("Network Monitoring", self.show_network_monitoring),
            ("Geo-IP Blocking", self.show_geo_ip_blocking),
            (
                "Malware Detection",
                lambda: self.show_input_and_execute(
                    self.firewall_manager.malware_detection
                ),
            ),
            (
                "View Network Profile",
                lambda: self.show_output(self.firewall_manager.view_network_profile),
            ),
            ("Ping and Traceroute", self.ping_and_traceroute),
            ("Port Scanning", self.port_scanning),
            ("Windows Commands", self.open_windows_commands),
            ("View Logs", self.view_logs),
            ("View Network Traffic", self.view_network_traffic),
            ("View Network Connections", self.view_network_connections),
            ("View Network Statistics", self.view_network_statistics),
            ("View Network Devices", self.view_network_devices),
            ("View Network Shares", self.view_network_shares),
            ("View Network Services", self.view_network_services),
            ("View Network Protocols", self.view_network_protocols),
            ("View Network Interfaces", self.view_network_interfaces),
            ("View Network Routes", self.view_network_routes),
            ("View Network Topology", self.view_network_topology),
            ("View Network Performance", self.view_network_performance),
            ("View Network Security", self.view_network_security),
            ("View Network Configuration", self.view_network_configuration),
            ("View Network Policies", self.view_network_policies),
            (
                "Clear Browser Cache",
                lambda: self.safe_execute(self.clear_browser_cache),
            ),
            ("Defragment Drives", lambda: self.safe_execute(self.defragment_drives)),
        ]

        for text, command in networking_buttons:
            tk.Button(
                networking_frame,
                text=text,
                command=command,
                font=("Segoe UI", 10, "bold"),
                bg="#2E2E3E",
                fg="#FFFFFF",
                activebackground="#3E3E4E",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=5,
                pady=5,
            ).pack(fill="x", pady=5, padx=10)

        networking_frame.update_idletasks()
        networking_canvas.config(scrollregion=networking_canvas.bbox("all"))

        # Bottom Section: General Buttons
        general_frame_container = tk.Frame(main_content_frame, bg="#1E1E2E", width=1500, height=50)
        general_frame_container.pack(fill="x", pady=5)

        canvas = tk.Canvas(general_frame_container, bg="#1E1E2E", highlightthickness=0)
        scrollbar = tk.Scrollbar(
            general_frame_container, orient="horizontal", command=canvas.xview
        )
        general_frame = tk.Frame(canvas, bg="#1E1E2E")

        canvas.create_window((0, 0), window=general_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side="top", fill="both")
        scrollbar.pack(side="bottom", fill="x")

        general_buttons = [
            ("Generate Reports", self.show_generate_reports),
            ("Export Reports", self.show_export_reports),
            ("Logs Manager", self.manage_log_paths),
            ("Set Color Theme", self.set_color_theme),
            ("Malware Detection", self.show_malware_detection_dialog),
            ("Customizable Dashboard", self.customizable_dashboard),
            ("Admin Panel", self.create_admin_panel),
            ("Help Menu", self.show_help_menu),
            ("Exit", self.root.quit),
        ]

        for i, (text, command) in enumerate(general_buttons):
            row = i // 3  # 3 buttons per row
            col = i % 3   # Column index
            tk.Button(
                general_frame,
                text=text,
                command=command,
                font=("Segoe UI", 10, "bold"),
                bg="#2E2E3E",
                fg="#FFFFFF",
                activebackground="#3E3E4E",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=10,
                width=20  # Set a fixed width for buttons
            ).grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Make the columns expand evenly
        general_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        for col in range(3):  # Adjust the range based on the number of columns
            general_frame.grid_columnconfigure(col, weight=1)

        # for text, command in general_buttons:
        #     tk.Button(
        #         general_frame,
        #         text=text,
        #         command=command,
        #         font=("Segoe UI", 10, "bold"),
        #         bg="#2E2E3E",
        #         fg="#FFFFFF",
        #         activebackground="#3E3E4E",
        #         activeforeground="#FFFFFF",
        #         relief="flat",
        #         bd=0,
        #         padx=5,
        #         pady=5,
        #     ).pack(side="left", padx=10, pady=5)

        # general_frame.update_idletasks()
        # canvas.config(scrollregion=canvas.bbox("all"))

        # Right Section: Live Data Viewer
        right_frame = tk.Frame(main_content_frame, bg="#1E1E2E", width=1500)
        right_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=5)

        tk.Label(
            right_frame,
            text="Live Network Traffic",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg="#1E1E2E",
        ).pack(pady=10)

        self.traffic_viewer = tk.Text(
            right_frame,
            font=("Courier", 10),
            bg="#2E2E3E",
            fg="#FFFFFF",
            wrap="none",
            state="disabled",
            height=20,
        )
        self.traffic_viewer.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_traffic_viewer()

    def show_malware_detection_dialog(self):
        """Show a dialog to select a file for malware detection."""
        file_path = filedialog.askopenfilename(
            title="Select File for Malware Detection",
            filetypes=[("All Files", "*.*")]
        )
        if file_path:
            result = self.firewall_manager.malware_detection(file_path)
            self.show_message_dialog("Malware Detection Result", result)

    def set_background_image(self, image_path=None, url=None):
        """Set the background image from a file or URL."""
        try:
            print("Setting background image...")
            print(f"Image path: {image_path}, URL: {url}")

            # Load the image from URL or file
            if url:
                image = download_image_from_url(url)
                self.current_image_url = url
                self.current_image_path = None
            elif image_path:
                if not os.path.exists(image_path):
                    raise FileNotFoundError(f"Image file not found: {image_path}")
                image = Image.open(image_path)
                self.current_image_path = image_path
                self.current_image_url = None
            else:
                return

            # Ensure the image format is supported
            if image.format not in ["PNG", "JPEG", "BMP", "GIF"]:
                raise ValueError("Unsupported image format. Please use PNG, JPG, BMP, or GIF.")

            # Resize the image to fit the window
            image = image.resize(
                (self.root.winfo_width(), self.root.winfo_height()),
                Image.Resampling.LANCZOS  # Use LANCZOS for high-quality resizing
            )
            self.background_image = ImageTk.PhotoImage(image)

            # Create or update the background label
            if self.background_label:
                self.background_label.destroy()
            self.background_label = tk.Label(self.root, image=self.background_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Lower the background label to ensure it is behind all other widgets
            self.background_label.lower()

            print(f"Image loaded successfully from {'URL' if url else 'file'}: {url or image_path}")

        except Exception as e:
            print(f"Failed to set background image: {e}")
            

    def set_background_from_url(self):
        """Prompt the user to enter a URL for the background image."""
        url_window = tk.Toplevel(self.root)
        url_window.title("Enter Image URL")
        url_window.geometry("400x150")
        url_window.configure(bg="#1E1E2E")

        tk.Label(
            url_window,
            text="Enter the URL of the background image:",
            font=("Segoe UI", 10),
            fg="#FFFFFF",
            bg="#1E1E2E"
        ).pack(pady=10)

        url_entry = tk.Entry(url_window, font=("Segoe UI", 10), width=50)
        url_entry.pack(pady=5)

        def apply_url():
            url = url_entry.get()
            if url:
                self.set_background_image(url=url)
            url_window.destroy()

        tk.Button(
            url_window,
            text="Set Background",
            command=apply_url,
            font=("Segoe UI", 10),
            bg="#1ABC9C",
            fg="#FFFFFF",
            activebackground="#16A085",
            activeforeground="#FFFFFF"
        ).pack(pady=10)

    def on_resize(self, event):
        """Resize the background image when the window is resized."""
        if self.background_image and self.current_image_path:
            try:
                # Check if the background_label exists
                if not self.background_label or not self.background_label.winfo_exists():
                    print("Background label does not exist. Recreating it.")
                    self.set_background_image(image_path=self.current_image_path)
                    return

                # Load the image again and resize it to fit the new window dimensions
                image = Image.open(self.current_image_path)
                image = image.resize(
                    (self.root.winfo_width(), self.root.winfo_height()),
                    Image.Resampling.LANCZOS
                )
                self.background_image = ImageTk.PhotoImage(image)

                # Update the background label with the resized image
                self.background_label.config(image=self.background_image)
            except Exception as e:
                print(f"Failed to resize background image: {e}")

    def show_apache_logs(self):
        """Open a CMD window to display Apache web server logs."""
        if not self.custom_log_paths:
            log_file_path = self.default_log_path
        else:
            log_file_path = self.select_log_path()

        if not log_file_path:
            self.show_message_dialog("Error", "No log file path selected!")
            return

        try:
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"Get-Content '{log_file_path}' -Tail 10 -Wait",
                ],
                shell=True,
            )
        except Exception as e:
            log_error(f"Failed to display Apache logs: {e}")
            self.show_message_dialog("Error", f"Failed to display Apache logs: {e}")

    def select_log_path(self):
        """Allow the user to select a log path."""

        dialog = tk.Toplevel(self.root)
        dialog.title("Select Log Path")
        dialog.geometry("400x300")
        dialog.configure(bg="#1E1E2E")

        tk.Label(
            dialog,
            text="Select a Log Path",
            font=("Segoe UI", 12),
            fg="#FFFFFF",
            bg="#1E1E2E",
        ).pack(pady=10)

        log_path_var = tk.StringVar(value=self.default_log_path)

        # Add default log path
        tk.Radiobutton(
            dialog,
            text=f"Default: {self.default_log_path}",
            variable=log_path_var,
            value=self.default_log_path,
            font=("Segoe UI", 10),
            bg="#1E1E2E",
            fg="#FFFFFF",
            selectcolor="#2E2E3E",
        ).pack(anchor="w", padx=20)

        # Add custom log paths
        for path in self.custom_log_paths:
            tk.Radiobutton(
                dialog,
                text=path,
                variable=log_path_var,
                value=path,
                font=("Segoe UI", 10),
                bg="#1E1E2E",
                fg="#FFFFFF",
                selectcolor="#2E2E3E",
            ).pack(anchor="w", padx=20)

        def on_select():
            dialog.destroy()

        tk.Button(
            dialog,
            text="Select",
            command=on_select,
            font=("Segoe UI", 10),
            bg="#1ABC9C",
            fg="#FFFFFF",
            activebackground="#16A085",
            activeforeground="#FFFFFF",
        ).pack(pady=10)

        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

        return log_path_var.get()
    
    def manage_log_paths(self):
        """Manage custom log paths and allow viewing logs."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Log Paths")
        dialog.geometry("400x400")
        dialog.configure(bg="#1E1E2E")

        tk.Label(
            dialog,
            text="Manage Log Paths",
            font=("Segoe UI", 12),
            fg="#FFFFFF",
            bg="#1E1E2E"
        ).pack(pady=10)

        listbox = tk.Listbox(dialog, font=("Segoe UI", 10), bg="#2E2E3E", fg="#FFFFFF")
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Populate the listbox with custom log paths
        for path in self.custom_log_paths:
            listbox.insert("end", path)

        def add_path():
            path = filedialog.askopenfilename(title="Select Log File")
            if path and path not in self.custom_log_paths:
                self.custom_log_paths.append(path)
                listbox.insert("end", path)

        def remove_path():
            selected = listbox.curselection()
            if selected:
                path = listbox.get(selected)
                self.custom_log_paths.remove(path)
                listbox.delete(selected)

        def view_log(event):
            selected = listbox.curselection()
            if selected:
                log_file_path = listbox.get(selected)
                self.display_log_file(log_file_path)

        listbox.bind("<Double-Button-1>", view_log)

        tk.Button(
            dialog,
            text="Add Path",
            command=add_path,
            font=("Segoe UI", 10),
            bg="#1ABC9C",
            fg="#FFFFFF",
            activebackground="#16A085",
            activeforeground="#FFFFFF"
        ).pack(side="left", padx=10, pady=10)

        tk.Button(
            dialog,
            text="Remove Path",
            command=remove_path,
            font=("Segoe UI", 10),
            bg="#E74C3C",
           fg="#FFFFFF",
            activebackground="#C0392B",
            activeforeground="#FFFFFF"
        ).pack(side="right", padx=10, pady=10)

        tk.Button(
            dialog,
            text="Close",
            command=dialog.destroy,
            font=("Segoe UI", 10),
            bg="#2E2E3E",
            fg="#FFFFFF",
            activebackground="#3E3E4E",
            activeforeground="#FFFFFF"
        ).pack(pady=10)

        tk.Button(
            dialog,
            text="VPS Apache Logs",
            command=self.show_apache_logs,
            font=("Segoe UI", 10),
            bg="#1ABC9C",
            fg="#FFFFFF",
            activebackground="#16A085",
            activeforeground="#FFFFFF"
        ).pack(pady=10)

    def display_log_file(self, log_file_path):
        """Display the contents of a log file in a scrollable widget."""
        try:
            with open(log_file_path, "r") as file:
                log_content = file.read()
        except Exception as e:
            log_error(f"Failed to read log file: {e}")
            self.show_message_dialog("Error", f"Failed to read log file: {e}")
            return

        log_window = tk.Toplevel(self.root)
        log_window.title(f"Viewing Log: {log_file_path}")
        log_window.geometry("800x600")
        log_window.configure(bg="#1E1E2E")

        text_widget = tk.Text(
            log_window,
            font=("Courier", 10),
            bg="#2E2E3E",
            fg="#FFFFFF",
            wrap="none",
            state="normal",
        )
        text_widget.insert("1.0", log_content)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(
            log_window,
            text="Close",
            command=log_window.destroy,
            font=("Segoe UI", 10),
            bg="#E74C3C",
            fg="#FFFFFF",
            activebackground="#C0392B",
            activeforeground="#FFFFFF"
        ).pack(pady=10)

    def advanced_rule_management(self):
        """Provide advanced management options for firewall rules."""
        try:
            management_window = tk.Toplevel(self.root)
            management_window.title("Advanced Rule Management")
            management_window.geometry("800x600")
            management_window.configure(bg="#1E1E2E")

            tk.Label(
                management_window,
                text="Advanced Rule Management",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            # Add options for advanced rule management
            options = [
                (
                    "List All Rules",
                    lambda: self.show_output(self.firewall_manager.list_active_rules),
                ),
                (
                    "Search Rule",
                    lambda: self.show_input_and_execute(
                        self.firewall_manager.search_firewall_rule
                    ),
                ),
                (
                    "Delete Rule",
                    lambda: self.show_input_and_execute(
                        self.firewall_manager.delete_firewall_rule
                    ),
                ),
                (
                    "Validate Rule",
                    lambda: self.show_input_and_execute(
                        self.firewall_manager.validate_firewall_rule
                    ),
                ),
                ("Optimize Rules", self.firewall_manager.optimize_rules),
            ]

            for text, command in options:
                tk.Button(
                    management_window,
                    text=text,
                    command=command,
                    font=("Segoe UI", 12),
                    bg="#2E2E3E",
                    fg="#FFFFFF",
                    activebackground="#3E3E4E",
                    activeforeground="#FFFFFF",
                    relief="flat",
                    bd=0,
                    padx=10,
                    pady=5,
                ).pack(fill="x", pady=5, padx=20)

            tk.Button(
                management_window,
                text="Close",
                command=management_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=20)

        except Exception as e:
            log_error(f"Failed to open Advanced Rule Management: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Advanced Rule Management: {e}"
            )

    def create_admin_panel(self):
        """Create an admin panel for managing advanced settings."""
        try:
            admin_window = tk.Toplevel(self.root)
            admin_window.title("Admin Panel")
            admin_window.geometry("800x600")
            admin_window.configure(bg="#1E1E2E")

            tk.Label(
                admin_window,
                text="Admin Panel",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            tk.Label(
                admin_window,
                text="Manage advanced settings and configurations.",
                font=("Segoe UI", 12),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            # Placeholder for admin panel options
            options = [
                ("Manage Users", self.manage_users),
                ("View Logs", self.view_logs),
                ("Schedule Tasks", self.schedule_tasks),
                ("Optimize Firewall Rules", self.firewall_manager.optimize_rules),
                ("Reset Firewall", self.firewall_manager.reset_firewall),
            ]

            for text, command in options:
                tk.Button(
                    admin_window,
                    text=text,
                    command=command,
                    font=("Segoe UI", 12),
                    bg="#2E2E3E",
                    fg="#FFFFFF",
                    activebackground="#3E3E4E",
                    activeforeground="#FFFFFF",
                    relief="flat",
                    bd=0,
                    padx=10,
                    pady=5,
                ).pack(fill="x", pady=5, padx=20)

            tk.Button(
                admin_window,
                text="Close",
                command=admin_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=20)

        except Exception as e:
            log_error(f"Failed to open Admin Panel: {e}")
            self.show_message_dialog("Error", f"Failed to open Admin Panel: {e}")

    def ping_and_traceroute(self):
        """Perform a ping and traceroute to a specified host."""
        host = self.show_input_dialog(
            "Ping and Traceroute", "Enter the host (e.g., google.com):"
        )
        if not host:
            self.show_message_dialog("Error", "Host cannot be empty!")
            return
        try:
            ping_result = subprocess.run(
                ["ping", host], capture_output=True, text=True, check=True
            ).stdout
            traceroute_result = subprocess.run(
                ["tracert", host], capture_output=True, text=True, check=True
            ).stdout
            self.show_output(
                lambda: f"Ping Results:\n{ping_result}\n\nTraceroute Results:\n{traceroute_result}"
            )
        except Exception as e:
            log_error(f"Failed to perform ping and traceroute: {e}")
            self.show_message_dialog(
                "Error", f"Failed to perform ping and traceroute: {e}"
            )

    def port_scanning(self):
        """Perform a basic port scan on a specified host."""
        host = self.show_input_dialog(
            "Port Scanning", "Enter the host (e.g., 192.168.1.1):"
        )
        if not host:
            self.show_message_dialog("Error", "Host cannot be empty!")
            return
        try:
            result = subprocess.run(
                ["nmap", host], capture_output=True, text=True, check=True
            ).stdout
            self.show_output(lambda: f"Port Scanning Results:\n{result}")
        except Exception as e:
            log_error(f"Failed to perform port scanning: {e}")
            self.show_message_dialog("Error", f"Failed to perform port scanning: {e}")

    def clear_browser_cache(self):
        """Clear browser cache for common browsers."""
        try:
            cache_paths = [
                os.path.expanduser(
                    "~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache"
                ),
                os.path.expanduser("~\\AppData\\Local\\Mozilla\\Firefox\\Profiles"),
            ]
            for path in cache_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            os.remove(os.path.join(root, file))
            log_action("Cleared browser cache.")
            self.show_message_dialog("Success", "Browser cache cleared successfully!")
        except Exception as e:
            log_error(f"Failed to clear browser cache: {e}")
            self.show_message_dialog("Error", f"Failed to clear browser cache: {e}")

    def defragment_drives(self):
        """Defragment drives on the system."""
        try:
            result = subprocess.run(
                ["defrag", "C:"], capture_output=True, text=True, check=True
            ).stdout
            log_action("Defragmented drive C.")
            self.show_output(lambda: f"Defragmentation Results:\n{result}")
        except Exception as e:
            log_error(f"Failed to defragment drives: {e}")
            self.show_message_dialog("Error", f"Failed to defragment drives: {e}")

    def show_input_and_execute(self, func):
        """Prompt the user for input and execute the given function."""
        input_value = self.show_input_dialog(
            "Input Required", "Enter the required value:"
        )
        if input_value:
            func(input_value)

    def show_output(self, func):
        """Display the output of a function in a new window."""
        output = func()
        output_window = tk.Toplevel(self.root)
        output_window.title("Output")
        output_window.geometry("800x600")
        output_window.configure(bg="#1E1E2E")

        text_widget = tk.Text(
            output_window,
            font=("Courier", 10),
            bg="#2E2E3E",
            fg="#FFFFFF",
            wrap="none",
            state="normal",
        )
        text_widget.insert("1.0", output)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

    def update_traffic_viewer(self):
        """Update the live network traffic viewer with real-time data."""
        try:
            result = subprocess.run(
                ["netstat", "-an"], capture_output=True, text=True, shell=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            # Filter and format the output to show only active connections
            filtered_lines = []
            for line in output.splitlines():
                if "ESTABLISHED" in line or "CLOSE_WAIT" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        protocol = parts[0]
                        local_address = parts[1]
                        remote_address = parts[2]
                        filtered_lines.append(
                            f"{protocol} | Local: {local_address} | Remote: {remote_address}"
                        )

            # Update the traffic viewer
            self.traffic_viewer.config(state="normal")
            self.traffic_viewer.delete("1.0", "end")
            self.traffic_viewer.insert("1.0", "\n".join(filtered_lines))
            self.traffic_viewer.see("end")
            self.traffic_viewer.config(state="disabled")

            # Schedule the next update
            self.root.after(5000, self.update_traffic_viewer)
        except Exception as e:
            log_error(f"Failed to update traffic viewer: {e}")

    def show_help_menu(self):
        """Display the updated help menu."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help Menu")
        help_window.geometry("800x600")
        help_window.configure(bg="#1E1E2E")
        help_window.resizable(True, True)

        help_text = """
        Welcome to the N3xG3n Firewall Manager Help Menu!

        Below is a list of features and how to use them:

        1. **Open Specific Ports**
           - Opens a specific port or range of ports for inbound traffic.
           - **How to Use**: Enter the port number (e.g., 80) or range (e.g., 1000-2000) and select the protocol (TCP/UDP).
           - **Example**: To allow HTTP traffic, enter port 80 and select TCP.

        2. **Close Specific Ports**
           - Closes a specific port or range of ports.
           - **How to Use**: Enter the port number (e.g., 80) or range (e.g., 1000-2000) and select the protocol (TCP/UDP).
           - **Example**: To block HTTP traffic, enter port 80 and select TCP.

        3. **Query Port Status**
           - Checks if a specific port is open or closed.
           - **How to Use**: Enter the port number (e.g., 80) to check its status.
           - **Example**: To check if port 80 is open, enter 80.

        4. **Reset Firewall to Default**
           - Resets the firewall to its default configuration, removing all custom rules.
           - **How to Use**: Click the button and confirm the action when prompted.
           - **Warning**: This will erase all custom rules.

        5. **Predefined Port Profiles**
           - Provides predefined configurations for common applications and services.
           - **How to Use**: Select a category (e.g., Communication Tools, Game Servers) to view available profiles.
           - **Example**: To view ports for Minecraft, select "Game Servers".

        6. **Backup Firewall Rules**
           - Saves the current firewall rules to a file.
           - **How to Use**: Choose a location to save the backup file.
           - **Example**: Save the rules to "firewall_backup.wfw".

        7. **Restore Firewall Rules**
           - Restores firewall rules from a backup file.
           - **How to Use**: Select a previously saved backup file to restore the rules.
           - **Example**: Restore rules from "firewall_backup.wfw".

        8. **Enable/Disable Firewall**
           - Toggles the firewall state (on/off) for all profiles.
           - **How to Use**: Select "Yes" to enable or "No" to disable the firewall.
           - **Example**: To disable the firewall, select "No".

        9. **List Active Rules**
            - Displays all active firewall rules.
            - **How to Use**: Click the button to view the list of rules.
            - **Example**: Use this to review all currently active rules.

        10. **Search Firewall Rule**
            - Searches for a specific firewall rule by name.
            - **How to Use**: Enter the rule name to search for it.
            - **Example**: To find a rule named "Open Port 80", enter "Open Port 80".

        11. **Delete Firewall Rule**
            - Deletes a specific firewall rule by name.
            - **How to Use**: Enter the rule name to delete it.
            - **Example**: To delete a rule named "Open Port 80", enter "Open Port 80".

        12. **Export Logs**
            - Exports the log file to a user-specified location.
            - **How to Use**: Choose a location to save the log file.
            - **Example**: Save the logs to "firewall_logs.log".

        13. **View Statistics**
            - Displays statistics about the current firewall rules.
            - **Details**: Shows the total number of rules, allow rules, and block rules.
            - **How to Use**: Click the button to view the statistics.

        14. **Detect Port Conflicts**
            - Checks if a specific port is already in use.
            - **How to Use**: Enter the port number to check for conflicts.
            - **Example**: To check if port 80 is in use, enter 80.

        15. **View Network Profile**
            - Displays the current network profile (e.g., Public, Private, Domain).
            - **How to Use**: Click the button to view the profile.

        16. **Windows Commands**
            - Provides a list of helpful Windows commands and allows you to execute them.
            - **How to Use**: Click the "Windows Commands" button to open the commands window. Select a predefined command or enter a custom command to execute.
            - **Examples**:
              - Predefined Commands:
                - "Ping Google": Tests connectivity to Google.
                - "Run SFC Scan": Scans and repairs system files.
                - "Flush DNS Cache": Clears the DNS cache.
              - Custom Commands:
                - Enter any valid Windows command in the input field and click "Run Command".

        17. **Execute Custom Command**
            - Allows you to manually execute any Windows command.
            - **How to Use**: Enter the command in the input field in the "Windows Commands" window and click "Run Command".
            - **Example**: To check disk space, enter `dir` and click "Run Command".

        18. **Set Color Theme**
           - Changes the application's background color for a personalized experience.
           - **How to Use**: Select a color theme from the list of available options.
           - **Example**: To set the background to blue, select "Blue".

        19. **Exit**
            - Closes the application.
            - **How to Use**: Click the "Exit" button to close the application.

        If you have any questions or need further assistance, feel free to email me at jarrodz@digital-synergy.org.
        """

        text_widget = tk.Text(
            help_window,
            font=("Segoe UI", 12),
            bg="#1E1E2E",
            fg="#FFFFFF",
            wrap="word",
            state="normal",
        )
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

    def show_input_dialog(self, title, prompt, is_password=False):
        """Show a custom input dialog for user input."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.configure(bg="#1E1E2E")
        dialog.resizable(False, False)

        tk.Label(
            dialog, text=prompt, font=("Segoe UI", 12), fg="#FFFFFF", bg="#1E1E2E"
        ).pack(pady=10)

        entry_var = tk.StringVar()
        entry = tk.Entry(
            dialog, textvariable=entry_var, show="*" if is_password else ""
        )
        entry.pack(pady=10, padx=20, fill="x")
        entry.focus()

        def on_submit():
            dialog.destroy()

        tk.Button(
            dialog,
            text="Submit",
            command=on_submit,
            font=("Segoe UI", 12),
            bg="#2E2E3E",
            fg="#FFFFFF",
            activebackground="#3E3E4E",
            activeforeground="#FFFFFF",
        ).pack(pady=10)

        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

        return entry_var.get()

    def show_message_dialog(self, title, message):
        """Show an informational message dialog."""
        messagebox.showinfo(title, message)

    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_session_monitor(self):
        """Monitor user activity and enforce session timeout."""
        # Removed session timeout logic to make the session indefinite.
        pass

    def reset_activity_timer(self):
        """Reset the activity timer to prevent session timeout."""
        # Removed activity timer reset logic as session timeout is now indefinite.
        pass

    def manage_users(self):
        """Manage user accounts."""
        try:
            users_window = tk.Toplevel(self.root)
            users_window.title("Manage Users")
            users_window.geometry("800x600")
            users_window.configure(bg="#1E1E2E")

            tk.Label(
                users_window,
                text="Manage Users",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                users_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            user_list = "\n".join([f"Username: {user}" for user in self.users.keys()])
            text_widget.insert("1.0", user_list)
            text_widget.config(state="disabled")

            tk.Button(
                users_window,
                text="Close",
                command=users_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Manage Users window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Manage Users window: {e}"
            )

    def view_logs(self):
        """View action and error logs in a scrollable window."""
        log_window = tk.Toplevel(self.root)
        log_window.title("View Logs")
        log_window.geometry("800x600")
        log_window.configure(bg="#1E1E2E")

        text_widget = tk.Text(
            log_window,
            font=("Courier", 10),
            bg="#2E2E3E",
            fg="#FFFFFF",
            wrap="none",
            state="normal",
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            with open("action_log.txt", "r") as log_file:
                logs = log_file.read()
            text_widget.insert("1.0", logs)
        except Exception as e:
            log_error(f"Failed to load logs: {e}")
            text_widget.insert("1.0", "Failed to load logs.")

        text_widget.config(state="disabled")

    def schedule_tasks(self):
        """Schedule tasks for the firewall."""
        try:
            tasks_window = tk.Toplevel(self.root)
            tasks_window.title("Schedule Tasks")
            tasks_window.geometry("800x600")
            tasks_window.configure(bg="#1E1E2E")

            tk.Label(
                tasks_window,
                text="Schedule Tasks",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            tk.Label(
                tasks_window,
                text="Feature to schedule firewall tasks is under development.",
                font=("Segoe UI", 12),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=20)

            tk.Button(
                tasks_window,
                text="Close",
                command=tasks_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Schedule Tasks window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Schedule Tasks window: {e}"
            )

    def set_color_theme(self):
        """Allow users to change the application's color theme."""
        try:
            theme_window = tk.Toplevel(self.root)
            theme_window.title("Set Color Theme")
            theme_window.geometry("400x300")
            theme_window.configure(bg="#1E1E2E")

            tk.Label(
                theme_window,
                text="Select a Color Theme",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            themes = {
                "Default": "#1E1E2E",
                "Light": "#FFFFFF",
                "Dark Blue": "#0A0A23",
                "Green": "#0A230A",
            }

            def apply_theme(color):
                self.root.configure(bg=color)
                theme_window.destroy()

            for theme_name, color in themes.items():
                tk.Button(
                    theme_window,
                    text=theme_name,
                    command=lambda c=color: apply_theme(c),
                    font=("Segoe UI", 12),
                    bg="#2E2E3E",
                    fg="#FFFFFF",
                    activebackground="#3E3E4E",
                    activeforeground="#FFFFFF",
                    relief="flat",
                    bd=0,
                    padx=10,
                    pady=5,
                ).pack(fill="x", pady=5, padx=10)

        except Exception as e:
            log_error(f"Failed to open Set Color Theme window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Set Color Theme window: {e}"
            )

    def customizable_dashboard(self):
        """Allow users to rearrange or hide sections of the main menu."""
        try:
            dashboard_window = tk.Toplevel(self.root)
            dashboard_window.title("Customizable Dashboard")
            dashboard_window.geometry("800x600")
            dashboard_window.configure(bg="#1E1E2E")

            tk.Label(
                dashboard_window,
                text="Customizable Dashboard",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            tk.Label(
                dashboard_window,
                text="Drag and drop to rearrange sections or toggle visibility.",
                font=("Segoe UI", 12),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            # Frame for sections
            sections_frame = tk.Frame(dashboard_window, bg="#1E1E2E")
            sections_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # List of sections with their visibility state
            sections = [
                {"name": "Firewall Section", "visible": True},
                {"name": "Networking Section", "visible": True},
                {"name": "General Buttons", "visible": True},
                {"name": "Live Data Viewer", "visible": True},
            ]

            # Function to toggle visibility
            def toggle_visibility(section, button):
                section["visible"] = not section["visible"]
                button.config(text="Hide" if section["visible"] else "Show")

            # Create draggable section items
            for section in sections:
                section_frame = tk.Frame(sections_frame, bg="#2E2E3E", pady=5)
                section_frame.pack(fill="x", pady=5)

                tk.Label(
                    section_frame,
                    text=section["name"],
                    font=("Segoe UI", 12),
                    fg="#FFFFFF",
                    bg="#2E2E3E",
                ).pack(side="left", padx=10)

                toggle_button = tk.Button(
                    section_frame,
                    text="Hide" if section["visible"] else "Show",
                    font=("Segoe UI", 10),
                    bg="#1ABC9C",
                    fg="#FFFFFF",
                    activebackground="#16A085",
                    activeforeground="#FFFFFF",
                    relief="flat",
                    bd=0,
                    padx=10,
                    pady=5,
                )
                toggle_button.config(
                    command=lambda s=section, b=toggle_button: toggle_visibility(s, b)
                )
                toggle_button.pack(side="right", padx=10)

            tk.Button(
                sections_frame,
                text="Upload Background",
                command=self.upload_background_image,
                font=("Segoe UI", 12),
                bg="#1ABC9C",
                fg="#FFFFFF",
                activebackground="#16A085",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(fill="x", pady=5)

            tk.Button(
                sections_frame,
                text="Set Background URL",
                command=self.set_background_from_url,
                font=("Segoe UI", 12),
                bg="#1ABC9C",
                fg="#FFFFFF",
                activebackground="#16A085",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(fill="x", pady=5)

            # Save changes button
            tk.Button(
                dashboard_window,
                text="Save Changes",
                command=lambda: self.apply_dashboard_changes([]),  # Placeholder
                font=("Segoe UI", 12),
                bg="#1ABC9C",
                fg="#FFFFFF",
                activebackground="#16A085",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

            # Close button
            tk.Button(
                dashboard_window,
                text="Close",
                command=dashboard_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Customizable Dashboard window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Customizable Dashboard window: {e}"
            )

    def apply_dashboard_changes(self, sections):
        """Apply changes to the main menu based on user customization."""
        # Example logic to apply visibility changes
        for section in sections:
            if section["name"] == "Firewall Section":
                # Apply visibility to the firewall section
                # self.firewall_section_frame.pack_forget() or .pack()
                pass
            elif section["name"] == "Networking Section":
                # Apply visibility to the networking section
                pass
            elif section["name"] == "General Buttons":
                # Apply visibility to the general buttons
                pass
            elif section["name"] == "Live Data Viewer":
                # Apply visibility to the live data viewer
                pass

        self.show_message_dialog(
            "Success", "Dashboard customization applied successfully!"
        )

    def upload_background_image(self):
        """Allow the user to upload a background image."""
        file_path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
       )
        if file_path:
            self.set_background_image(image_path=file_path)

    def show_predefined_port_profiles(self):
        """Display predefined port profiles with scrollable content, toggle buttons, and state labels."""
        profiles = self.firewall_manager.predefined_port_profiles()
        profile_window = tk.Toplevel(self.root)
        profile_window.title("Predefined Port Profiles")
        profile_window.geometry("600x400")
        profile_window.configure(bg="#1E1E2E")

        # Create a scrollable frame
        canvas = tk.Canvas(profile_window, bg="#1E1E2E", highlightthickness=0)
        scrollbar = tk.Scrollbar(
            profile_window, orient="vertical", command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas, bg="#1E1E2E")

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Update scroll region when content changes
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Add profiles with toggle buttons and state labels
        for category, ports in profiles.items():
            tk.Label(
                scrollable_frame,
                text=category,
                font=("Segoe UI", 14, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=5)

            for port in ports:
                frame = tk.Frame(scrollable_frame, bg="#1E1E2E")
                frame.pack(fill="x", pady=2, padx=10)

                tk.Label(
                    frame,
                    text=f"{port['name']}: {port['ports']}",
                    font=("Segoe UI", 12),
                    fg="#FFFFFF",
                    bg="#1E1E2E",
                ).pack(side="left", padx=5)

                state_label = tk.Label(
                    frame,
                    text=(
                        "Enabled"
                        if self.firewall_manager.is_profile_enabled(port["name"])
                        else "Disabled"
                    ),
                    font=("Segoe UI", 10),
                    fg="#FFFFFF",
                    bg="#1E1E2E",
                )
                state_label.pack(side="right", padx=5)

                def toggle_profile(port_name=port["name"], label=state_label):
                    if self.firewall_manager.is_profile_enabled(port_name):
                        self.firewall_manager.disable_profile(port_name)
                        log_action(f"Disabled profile: {port_name}")
                        label.config(text="Disabled")
                    else:
                        self.firewall_manager.enable_profile(port_name)
                        log_action(f"Enabled profile: {port_name}")
                        label.config(text="Enabled")
                    self.show_message_dialog("Success", f"Toggled profile: {port_name}")

                tk.Button(
                    frame,
                    text="Toggle",
                    command=toggle_profile,
                    font=("Segoe UI", 10),
                    bg="#2E2E3E",
                    fg="#FFFFFF",
                    activebackground="#3E3E4E",
                    activeforeground="#FFFFFF",
                    relief="flat",
                    bd=0,
                    padx=5,
                    pady=2,
                ).pack(side="right", padx=5)

    def show_network_monitoring(self):
        """Display network monitoring tools."""
        monitoring_window = tk.Toplevel(self.root)
        monitoring_window.title("Network Monitoring")
        monitoring_window.geometry("800x600")
        monitoring_window.configure(bg="#1E1E2E")

        tk.Label(
            monitoring_window,
            text="Network Monitoring (Live Connections)",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg="#1E1E2E",
        ).pack(pady=10)

        text_widget = tk.Text(
            monitoring_window,
            font=("Courier", 10),
            bg="#2E2E3E",
            fg="#FFFFFF",
            wrap="none",
            state="normal",
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            result = subprocess.run(
                ["netstat", "-an"], capture_output=True, text=True, shell=True
            )
            text_widget.insert("1.0", result.stdout)
        except Exception as e:
            log_error(f"Failed to display network monitoring: {e}")
            text_widget.insert("1.0", "Failed to load network monitoring data.")

    def show_geo_ip_blocking(self):
        """Display Geo-IP blocking tools."""
        self.show_message_dialog(
            "Feature Coming Soon", "Geo-IP Blocking is under development."
        )

    def show_firewall_rule_simulator(self):
        """Display the firewall rule simulator."""
        try:
            # Create a new window for the simulator
            simulator_window = tk.Toplevel(self.root)
            simulator_window.title("Firewall Rule Simulator")
            simulator_window.geometry("800x600")
            simulator_window.configure(bg="#1E1E2E")

            # Title Label
            tk.Label(
                simulator_window,
                text="Firewall Rule Simulator",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            # Input Frame
            input_frame = tk.Frame(simulator_window, bg="#1E1E2E")
            input_frame.pack(fill="x", padx=20, pady=10)

            # Rule Name Input
            tk.Label(
                input_frame,
                text="Rule Name:",
                font=("Segoe UI", 12),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
            rule_name_var = tk.StringVar()
            tk.Entry(
                input_frame,
                textvariable=rule_name_var,
                font=("Segoe UI", 12),
                bg="#2E2E3E",
                fg="#FFFFFF",
                relief="flat",
            ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

            # Port Input
            tk.Label(
                input_frame,
                text="Port:",
                font=("Segoe UI", 12),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
            port_var = tk.StringVar()
            tk.Entry(
                input_frame,
                textvariable=port_var,
                font=("Segoe UI", 12),
                bg="#2E2E3E",
                fg="#FFFFFF",
                relief="flat",
            ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

            # Protocol Dropdown
            tk.Label(
                input_frame,
                text="Protocol:",
                font=("Segoe UI", 12),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).grid(row=2, column=0, sticky="w", padx=5, pady=5)
            protocol_var = tk.StringVar(value="TCP")
            protocol_dropdown = ttk.Combobox(
                input_frame,
                textvariable=protocol_var,
                values=["TCP", "UDP"],
                font=("Segoe UI", 12),
                state="readonly",
            )
            protocol_dropdown.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

            # Action Dropdown
            tk.Label(
                input_frame,
                text="Action:",
                font=("Segoe UI", 12),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).grid(row=3, column=0, sticky="w", padx=5, pady=5)
            action_var = tk.StringVar(value="Allow")
            action_dropdown = ttk.Combobox(
            input_frame,
                textvariable=action_var,
                values=["Allow", "Block"],
                font=("Segoe UI", 12),
                state="readonly",
            )
            action_dropdown.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

            # Configure grid weights for input frame
            input_frame.grid_columnconfigure(1, weight=1)

            # Output Frame
            output_frame = tk.Frame(simulator_window, bg="#1E1E2E")
            output_frame.pack(fill="both", expand=True, padx=20, pady=10)

            tk.Label(
                output_frame,
                text="Simulation Results:",
                font=("Segoe UI", 12, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(anchor="w", pady=5)

            result_text = tk.Text(
                output_frame,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="word",
                state="normal",
            )
            result_text.pack(fill="both", expand=True, padx=5, pady=5)

            # Simulate Button
            def simulate_rule():
                rule_name = rule_name_var.get()
                port = port_var.get()
                protocol = protocol_var.get()
                action = action_var.get()

                if not rule_name or not port or not protocol or not action:
                    self.show_message_dialog("Error", "All fields are required!")
                    return

                try:
                    port = int(port)
                    if port < 1 or port > 65535:
                        raise ValueError("Port must be between 1 and 65535.")
                except ValueError as e:
                    self.show_message_dialog("Error", f"Invalid port: {e}")
                    return

                # Simulate the rule (this is a placeholder for actual simulation logic)
                result_text.config(state="normal")
                result_text.insert(
                    "end",
                    f"Simulating Rule:\n"
                    f"Name: {rule_name}\n"
                    f"Port: {port}\n"
                    f"Protocol: {protocol}\n"
                    f"Action: {action}\n\n"
                    f"Result: Rule simulated successfully!\n\n",
                )
                result_text.config(state="disabled")
                result_text.see("end")

            tk.Button(
                simulator_window,
                text="Simulate Rule",
                command=simulate_rule,
                font=("Segoe UI", 12),
                bg="#1ABC9C",
                fg="#FFFFFF",
                activebackground="#16A085",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

            # Close Button
            tk.Button(
                simulator_window,
                text="Close",
                command=simulator_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Firewall Rule Simulator: {e}")
            self.show_message_dialog("Error", f"Failed to open Firewall Rule Simulator: {e}")

    def show_generate_reports(self):
        """Generate reports for firewall activity."""
        try:
            report_file = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            )
            if report_file:
                with open(report_file, "w") as file:
                    file.write("Firewall Activity Report\n")
                    file.write("========================\n")
                    file.write(self.firewall_manager.view_statistics())
                self.show_message_dialog("Success", "Report generated successfully!")
        except Exception as e:
            log_error(f"Failed to generate report: {e}")
            self.show_message_dialog("Error", "Failed to generate report.")

    def show_export_reports(self):
        """Export reports for firewall activity."""
        try:
            export_window = tk.Toplevel(self.root)
            export_window.title("Export Reports")
            export_window.geometry("800x600")
            export_window.configure(bg="#1E1E2E")

            tk.Label(
                export_window,
                text="Export Reports",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            tk.Label(
                export_window,
                text="Feature to export reports is under development.",
                font=("Segoe UI", 12),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=20)

            tk.Button(
                export_window,
                text="Close",
                command=export_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Export Reports window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Export Reports window: {e}"
            )

    def export_logs(self):
        """Export logs to a user-specified location."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("All Files", "*.*")],
        )
        if file_path:
            try:
                with open("action_log.txt", "r") as log_file:
                    logs = log_file.read()
                with open(file_path, "w") as export_file:
                    export_file.write(logs)
                self.show_message_dialog("Success", "Logs exported successfully!")
            except Exception as e:
                log_error(f"Failed to export logs: {e}")
                self.show_message_dialog("Error", "Failed to export logs.")

    def open_windows_commands(self):
        """Open a window with helpful Windows commands."""
        commands_window = tk.Toplevel(self.root)
        commands_window.title("Windows Commands")
        commands_window.geometry("800x600")
        commands_window.configure(bg="#1E1E2E")  # Match the main UI background color

        canvas = tk.Canvas(commands_window, bg="#1E1E2E", highlightthickness=0)
        scrollbar = tk.Scrollbar(
            commands_window, orient="vertical", command=canvas.yview
        )
        scrollable_frame = tk.Frame(
            canvas, bg="#1E1E2E"
        )  # Match the main UI background color

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(
            scrollable_frame,
            text="Helpful Windows Commands",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",  # Match the text color of the main UI
            bg="#1E1E2E",  # Match the background color of the main UI
        ).grid(row=0, column=0, columnspan=3, pady=10)

        # Updated commands dictionary
        commands = {
            "Check Disk Space": "dir",
            "List Running Processes": "tasklist",
            "Ping Google": "ping google.com -n 4",
            "IP Configuration": "ipconfig",
            "Flush DNS Cache": "ipconfig /flushdns",
            "System Information": "systeminfo",
            "Check Network Connections": "netstat -an",
            "Restart Network Adapter": "ipconfig /release && ipconfig /renew",
            "Run SFC Scan (Check Files)": "sfc /scannow",
            "Verify SFC Integrity": "sfc /verifyonly",
            "Repair Network Issues": "netsh int ip reset && netsh winsock reset",
            "View Active Network Adapters": "ipconfig /all",
            "Test Connectivity to Host": "tracert google.com",
            "Display Routing Table": "route print",
            "Enable Firewall Logging": "netsh advfirewall set currentprofile logging filename log.txt",
            "Disable Firewall Logging": "netsh advfirewall set currentprofile logging disabled",
            "Check Open Ports": "netstat -an | findstr LISTENING",
            "View ARP Cache": "arp -a",
            "Clear ARP Cache": "arp -d *",
            "Check DNS Servers": "nslookup google.com",
            "Test SMB Connectivity": "net use \\\\hostname\\share",
        }

        row = 1
        col = 0
        for command_name, command in commands.items():
            tk.Button(
                scrollable_frame,
                text=command_name,
                command=lambda cmd=command: self.execute_command(cmd),
                font=("Segoe UI", 12),
                bg="#2E2E3E",  # Match button background color of the main UI
                fg="#FFFFFF",  # Match button text color of the main UI
                activebackground="#3E3E4E",  # Match active button background color of the main UI
                activeforeground="#FFFFFF",  # Match active button text color of the main UI
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
                cursor="hand2",
            ).grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            col += 1
            if col > 2:
                col = 0
                row += 1

        tk.Label(
            scrollable_frame,
            text="Execute Custom Command",
            font=("Segoe UI", 14, "bold"),
            fg="#FFFFFF",  # Match the text color of the main UI
            bg="#1E1E2E",  # Match the background color of the main UI
        ).grid(row=row + 1, column=0, columnspan=3, pady=10)

        custom_command_var = tk.StringVar()
        custom_command_entry = tk.Entry(
            scrollable_frame,
            textvariable=custom_command_var,
            font=("Segoe UI", 12),
            bg="#2E2E3E",  # Match entry background color of the main UI
            fg="#FFFFFF",  # Match entry text color of the main UI
            relief="flat",
        )
        custom_command_entry.grid(
            row=row + 2, column=0, columnspan=2, padx=20, pady=5, sticky="ew"
        )

        tk.Button(
            scrollable_frame,
            text="Run Command",
            command=lambda: self.execute_command(custom_command_var.get()),
            font=("Segoe UI", 12),
            bg="#1ABC9C",  # Match button background color for success actions
            fg="#FFFFFF",  # Match button text color
            activebackground="#16A085",  # Match active button background color for success actions
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
        ).grid(row=row + 2, column=2, padx=20, pady=5, sticky="ew")

        tk.Button(
            scrollable_frame,
            text="Return to Main Page",
            command=commands_window.destroy,
            font=("Segoe UI", 12),
            bg="#E74C3C",  # Match button background color for danger actions
            fg="#FFFFFF",  # Match button text color
            activebackground="#C0392B",  # Match active button background color for danger actions
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
        ).grid(row=row + 3, column=0, columnspan=3, pady=20)

    def execute_command(self, command):
        """Execute a Windows command and display the output."""
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            output = result.stdout if result.returncode == 0 else result.stderr
            self.show_output(lambda: output)
        except Exception as e:
            log_error(f"Failed to execute command '{command}': {e}")
            self.show_message_dialog("Error", f"Failed to execute command: {e}")

    def view_firewall_activity(self):
        """Display recent firewall activity logs."""
        try:
            activity_window = tk.Toplevel(self.root)
            activity_window.title("Firewall Activity")
            activity_window.geometry("800x600")
            activity_window.configure(bg="#1E1E2E")

            tk.Label(
                activity_window,
                text="Firewall Activity Logs",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                activity_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            try:
                with open("action_log.txt", "r") as log_file:
                    logs = log_file.read()
                text_widget.insert("1.0", logs)
            except FileNotFoundError:
                text_widget.insert("1.0", "No firewall activity logs found.")
            except Exception as e:
                log_error(f"Failed to load firewall activity logs: {e}")
                text_widget.insert("1.0", "Failed to load firewall activity logs.")

            text_widget.config(state="disabled")

            tk.Button(
                activity_window,
                text="Close",
                command=activity_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Firewall Activity window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Firewall Activity window: {e}"
            )

    def generate_security_audit_report(self):
        """Generate a detailed security audit report for the firewall."""
        try:
            report_file = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Save Security Audit Report",
            )
            if not report_file:
                self.show_message_dialog("Cancelled", "Report generation cancelled.")
                return

            # Collect firewall statistics
            statistics = self.firewall_manager.view_statistics()

            # Collect active rules
            active_rules = self.firewall_manager.list_active_rules()

            # Generate the report content
            report_content = (
                "N3xG3n Firewall Manager - Security Audit Report\n"
                "=================================================\n\n"
                "Firewall Statistics:\n"
                f"{statistics}\n\n"
                "Active Firewall Rules:\n"
                f"{active_rules}\n\n"
                "Audit Summary:\n"
                "- Ensure all open ports are necessary.\n"
                "- Review rules for potential misconfigurations.\n"
                "- Regularly update firewall rules to match security policies.\n"
            )

            # Save the report to the specified file
            with open(report_file, "w") as file:
                file.write(report_content)

            log_action(f"Security audit report generated and saved to {report_file}")
            self.show_message_dialog(
                "Success", f"Security audit report saved to {report_file}"
            )
        except Exception as e:
            log_error(f"Failed to generate security audit report: {e}")
            self.show_message_dialog(
                "Error", f"Failed to generate security audit report: {e}"
            )

    def view_network_traffic(self):
        """Display live network traffic statistics."""
        try:
            traffic_window = tk.Toplevel(self.root)
            traffic_window.title("Network Traffic")
            traffic_window.geometry("800x600")
            traffic_window.configure(bg="#1E1E2E")

            tk.Label(
                traffic_window,
                text="Live Network Traffic",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                traffic_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            def update_traffic():
                try:
                    result = subprocess.run(
                        ["netstat", "-e"], capture_output=True, text=True, shell=True
                    )
                    output = result.stdout if result.returncode == 0 else result.stderr

                    text_widget.config(state="normal")
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", output)
                    text_widget.config(state="disabled")

                    # Schedule the next update
                    traffic_window.after(5000, update_traffic)
                except Exception as e:
                    log_error(f"Failed to update network traffic: {e}")
                    text_widget.config(state="normal")
                    text_widget.insert("1.0", "Failed to load network traffic data.")
                    text_widget.config(state="disabled")

            update_traffic()

            tk.Button(
                traffic_window,
                text="Close",
                command=traffic_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Traffic window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Traffic window: {e}"
            )

    def view_network_connections(self):
        """Display active network connections."""
        try:
            connections_window = tk.Toplevel(self.root)
            connections_window.title("Network Connections")
            connections_window.geometry("800x600")
            connections_window.configure(bg="#1E1E2E")

            tk.Label(
                connections_window,
                text="Active Network Connections",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                connections_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            def update_connections():
                try:
                    result = subprocess.run(
                        ["netstat", "-an"], capture_output=True, text=True, shell=True
                    )
                    output = result.stdout if result.returncode == 0 else result.stderr

                    text_widget.config(state="normal")
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", output)
                    text_widget.config(state="disabled")

                    # Schedule the next update
                    connections_window.after(5000, update_connections)
                except Exception as e:
                    log_error(f"Failed to update network connections: {e}")
                    text_widget.config(state="normal")
                    text_widget.insert(
                        "1.0", "Failed to load network connections data."
                    )
                    text_widget.config(state="disabled")

            update_connections()

            tk.Button(
                connections_window,
                text="Close",
                command=connections_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Connections window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Connections window: {e}"
            )

    def view_network_statistics(self):
        """Display network statistics such as sent/received packets and errors."""
        try:
            statistics_window = tk.Toplevel(self.root)
            statistics_window.title("Network Statistics")
            statistics_window.geometry("800x600")
            statistics_window.configure(bg="#1E1E2E")

            tk.Label(
                statistics_window,
                text="Network Statistics",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                statistics_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            def update_statistics():
                try:
                    result = subprocess.run(
                        ["netstat", "-e"], capture_output=True, text=True, shell=True
                    )
                    output = result.stdout if result.returncode == 0 else result.stderr

                    text_widget.config(state="normal")
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", output)
                    text_widget.config(state="disabled")

                    # Schedule the next update
                    statistics_window.after(5000, update_statistics)
                except Exception as e:
                    log_error(f"Failed to update network statistics: {e}")
                    text_widget.config(state="normal")
                    text_widget.insert("1.0", "Failed to load network statistics.")
                    text_widget.config(state="disabled")

            update_statistics()

            tk.Button(
                statistics_window,
                text="Close",
                command=statistics_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Statistics window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Statistics window: {e}"
            )

    def view_network_devices(self):
        """Display a list of network devices and their statuses."""
        try:
            devices_window = tk.Toplevel(self.root)
            devices_window.title("Network Devices")
            devices_window.geometry("800x600")
            devices_window.configure(bg="#1E1E2E")

            tk.Label(
                devices_window,
                text="Network Devices",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                devices_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            def update_devices():
                try:
                    result = subprocess.run(
                        ["ipconfig", "/all"], capture_output=True, text=True, shell=True
                    )
                    output = result.stdout if result.returncode == 0 else result.stderr

                    text_widget.config(state="normal")
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", output)
                    text_widget.config(state="disabled")

                    # Schedule the next update
                    devices_window.after(5000, update_devices)
                except Exception as e:
                    log_error(f"Failed to update network devices: {e}")
                    text_widget.config(state="normal")
                    text_widget.insert("1.0", "Failed to load network devices data.")
                    text_widget.config(state="disabled")

            update_devices()

            tk.Button(
                devices_window,
                text="Close",
                command=devices_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Devices window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Devices window: {e}"
            )

    def view_network_shares(self):
        """Display shared network resources."""
        try:
            shares_window = tk.Toplevel(self.root)
            shares_window.title("Network Shares")
            shares_window.geometry("800x600")
            shares_window.configure(bg="#1E1E2E")

            tk.Label(
                shares_window,
                text="Network Shares",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                shares_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["net", "view"], capture_output=True, text=True, shell=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                shares_window,
                text="Close",
                command=shares_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Shares window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Shares window: {e}"
            )

    def view_network_services(self):
        """Display active network services."""
        try:
            services_window = tk.Toplevel(self.root)
            services_window.title("Network Services")
            services_window.geometry("800x600")
            services_window.configure(bg="#1E1E2E")

            tk.Label(
                services_window,
                text="Network Services",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                services_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["sc", "query"], capture_output=True, text=True, shell=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                services_window,
                text="Close",
                command=services_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Services window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Services window: {e}"
            )

    def view_network_protocols(self):
        """Display network protocols in use."""
        try:
            protocols_window = tk.Toplevel(self.root)
            protocols_window.title("Network Protocols")
            protocols_window.geometry("800x600")
            protocols_window.configure(bg="#1E1E2E")

            tk.Label(
                protocols_window,
                text="Network Protocols",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                protocols_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["netsh", "interface", "ipv4", "show", "config"],
                capture_output=True,
                text=True,
                shell=True,
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                protocols_window,
                text="Close",
                command=protocols_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Protocols window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Protocols window: {e}"
            )

    def view_network_interfaces(self):
        """Display network interfaces."""
        try:
            interfaces_window = tk.Toplevel(self.root)
            interfaces_window.title("Network Interfaces")
            interfaces_window.geometry("800x600")
            interfaces_window.configure(bg="#1E1E2E")

            tk.Label(
                interfaces_window,
                text="Network Interfaces",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                interfaces_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["ipconfig"], capture_output=True, text=True, shell=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                interfaces_window,
                text="Close",
                command=interfaces_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Interfaces window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Interfaces window: {e}"
            )

    def view_network_routes(self):
        """Display network routing table."""
        try:
            routes_window = tk.Toplevel(self.root)
            routes_window.title("Network Routes")
            routes_window.geometry("800x600")
            routes_window.configure(bg="#1E1E2E")

            tk.Label(
                routes_window,
                text="Network Routes",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                routes_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["route", "print"], capture_output=True, text=True, shell=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                routes_window,
                text="Close",
                command=routes_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Routes window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Routes window: {e}"
            )

    def view_network_topology(self):
        """Display network topology."""
        try:
            topology_window = tk.Toplevel(self.root)
            topology_window.title("Network Topology")
            topology_window.geometry("800x600")
            topology_window.configure(bg="#1E1E2E")

            tk.Label(
                topology_window,
                text="Network Topology",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                topology_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["tracert", "google.com"], capture_output=True, text=True, shell=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                topology_window,
                text="Close",
                command=topology_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Topology window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Topology window: {e}"
            )

    def view_network_performance(self):
        """Display network performance metrics."""
        try:
            performance_window = tk.Toplevel(self.root)
            performance_window.title("Network Performance")
            performance_window.geometry("800x600")
            performance_window.configure(bg="#1E1E2E")

            tk.Label(
                performance_window,
                text="Network Performance",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                performance_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["netstat", "-e"], capture_output=True, text=True, shell=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                performance_window,
                text="Close",
                command=performance_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Performance window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Performance window: {e}"
            )

    def view_network_security(self):
        """Display network security settings."""
        try:
            security_window = tk.Toplevel(self.root)
            security_window.title("Network Security")
            security_window.geometry("800x600")
            security_window.configure(bg="#1E1E2E")

            tk.Label(
                security_window,
                text="Network Security",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                security_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["netsh", "advfirewall", "show", "currentprofile"],
                capture_output=True,
                text=True,
                shell=True,
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                security_window,
                text="Close",
                command=security_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Security window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Security window: {e}"
            )

    def view_network_configuration(self):
        """Display network configuration details."""
        try:
            config_window = tk.Toplevel(self.root)
            config_window.title("Network Configuration")
            config_window.geometry("800x600")
            config_window.configure(bg="#1E1E2E")

            tk.Label(
                config_window,
                text="Network Configuration",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                config_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["ipconfig", "/all"], capture_output=True, text=True, shell=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                config_window,
                text="Close",
                command=config_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Configuration window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Configuration window: {e}"
            )

    def view_network_policies(self):
        """Display network policies."""
        try:
            policies_window = tk.Toplevel(self.root)
            policies_window.title("Network Policies")
            policies_window.geometry("800x600")
            policies_window.configure(bg="#1E1E2E")

            tk.Label(
                policies_window,
                text="Network Policies",
                font=("Segoe UI", 16, "bold"),
                fg="#FFFFFF",
                bg="#1E1E2E",
            ).pack(pady=10)

            text_widget = tk.Text(
                policies_window,
                font=("Courier", 10),
                bg="#2E2E3E",
                fg="#FFFFFF",
                wrap="none",
                state="normal",
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            result = subprocess.run(
                ["gpresult", "/R"], capture_output=True, text=True, shell=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr

            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")

            tk.Button(
                policies_window,
                text="Close",
                command=policies_window.destroy,
                font=("Segoe UI", 12),
                bg="#E74C3C",
                fg="#FFFFFF",
                activebackground="#C0392B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
            ).pack(pady=10)

        except Exception as e:
            log_error(f"Failed to open Network Policies window: {e}")
            self.show_message_dialog(
                "Error", f"Failed to open Network Policies window: {e}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallManagerApp(root)
    root.mainloop()

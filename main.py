import tkinter as tk
from ui import FirewallManagerApp

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.resizable(True, True)  # Make the main window resizable
        app = FirewallManagerApp(root)
        app.create_main_menu()  # Ensure the main menu reflects the dashboard configuration
        root.mainloop()
    except Exception as e:
        with open("error_log.txt", "w") as error_file:
            error_file.write(f"An unexpected error occurred:\n{str(e)}\n")
        print(f"An unexpected error occurred: {e}")


from file_organizer import FileOrganizer
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time

# Add parent directory to path to import FileOrganizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer & Cleaner")
        self.root.geometry("600x600")
        self.root.resizable(True, True)

        # Set icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Initialize FileOrganizer
        self.organizer = FileOrganizer()

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create title
        title_label = ttk.Label(
            main_frame, text="File Organizer & Cleaner", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create tabs
        self.quick_clean_tab = ttk.Frame(self.notebook)
        self.organize_tab = ttk.Frame(self.notebook)
        self.custom_tab = ttk.Frame(self.notebook)
        self.logs_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.quick_clean_tab, text="Quick Clean")
        self.notebook.add(self.organize_tab, text="Organize Files")
        self.notebook.add(self.custom_tab, text="Custom Cleanup")
        self.notebook.add(self.logs_tab, text="Logs")

        # Set up tabs
        self._setup_quick_clean_tab()
        self._setup_organize_tab()
        self._setup_custom_tab()
        self._setup_logs_tab()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL,
                                        length=100, mode='determinate',
                                        variable=self.progress_var)
        self.progress.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def _setup_quick_clean_tab(self):
        # Quick Clean Options
        frame = ttk.LabelFrame(self.quick_clean_tab,
                               text="Quick Clean Options", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Checkboxes for cleanup options
        self.clean_temp_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Clean Temporary Files",
                        variable=self.clean_temp_var).pack(anchor=tk.W, pady=5)

        self.clean_browser_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Clean Browser Cache",
                        variable=self.clean_browser_var).pack(anchor=tk.W, pady=5)

        self.organize_desktop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Organize Desktop",
                        variable=self.organize_desktop_var).pack(anchor=tk.W, pady=5)

        self.organize_downloads_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Organize Downloads Folder",
                        variable=self.organize_downloads_var).pack(anchor=tk.W, pady=5)

        self.empty_recycle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Empty Recycle Bin",
                        variable=self.empty_recycle_var).pack(anchor=tk.W, pady=5)

        # Advanced options
        advanced_frame = ttk.LabelFrame(
            frame, text="Advanced Options", padding=5)
        advanced_frame.pack(fill=tk.X, expand=False, pady=5)

        self.check_running_apps_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="Check for running applications before cleaning",
                        variable=self.check_running_apps_var).pack(anchor=tk.W, pady=2)

        # Run Button
        ttk.Button(frame, text="Start Quick Clean",
                   command=self.start_quick_clean).pack(pady=20)

        # Results frame
        results_frame = ttk.LabelFrame(
            self.quick_clean_tab, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.results_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.config(state=tk.DISABLED)

    def _setup_organize_tab(self):
        frame = ttk.Frame(self.organize_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Directory selection
        ttk.Label(frame, text="Select a directory to organize:").pack(
            anchor=tk.W, pady=5)

        dir_frame = ttk.Frame(frame)
        dir_frame.pack(fill=tk.X, pady=5)

        self.dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.dir_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse...",
                   command=self.browse_directory).pack(side=tk.RIGHT, padx=5)

        # Organize button
        ttk.Button(frame, text="Organize Files",
                   command=self.organize_selected_dir).pack(pady=20)

        # Preview frame
        preview_frame = ttk.LabelFrame(frame, text="Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.preview_text = tk.Text(preview_frame, height=10, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)

    def _setup_custom_tab(self):
        frame = ttk.Frame(self.custom_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # File Types
        types_frame = ttk.LabelFrame(frame, text="File Types", padding=10)
        types_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Show current file type mappings
        self.file_types_text = tk.Text(types_frame, height=15, wrap=tk.WORD)
        self.file_types_text.pack(fill=tk.BOTH, expand=True)

        for category, extensions in self.organizer.file_types.items():
            if extensions:
                self.file_types_text.insert(
                    tk.END, f"{category}: {', '.join(extensions)}\n")

        # Custom directory organization
        custom_dir_frame = ttk.LabelFrame(
            frame, text="Custom Directory Organization", padding=10)
        custom_dir_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(custom_dir_frame, text="Select a directory to organize with custom rules:").pack(
            anchor=tk.W, pady=5)

        dir_select_frame = ttk.Frame(custom_dir_frame)
        dir_select_frame.pack(fill=tk.X, pady=5)

        self.custom_dir_var = tk.StringVar()
        ttk.Entry(dir_select_frame, textvariable=self.custom_dir_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_select_frame, text="Browse...",
                   command=self.browse_custom_directory).pack(side=tk.RIGHT, padx=5)

        ttk.Button(custom_dir_frame, text="Organize with Custom Rules",
                   command=self.organize_custom_dir).pack(pady=10)

    def _setup_logs_tab(self):
        frame = ttk.Frame(self.logs_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Logs display
        self.logs_text = tk.Text(frame, height=20, wrap=tk.WORD)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        self.logs_text.config(state=tk.DISABLED)

        # Scroll bar
        scrollbar = ttk.Scrollbar(self.logs_text, command=self.logs_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.logs_text.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Refresh Logs",
                   command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Logs",
                   command=self.clear_logs).pack(side=tk.LEFT, padx=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)

            # Preview what files will be organized
            self.update_preview(directory)

    def browse_custom_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.custom_dir_var.set(directory)

    def update_preview(self, directory):
        """Update the preview text with what files will be organized."""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        try:
            if not os.path.exists(directory):
                self.preview_text.insert(tk.END, "Directory does not exist.")
                return

            file_count = 0
            category_counts = {
                category: 0 for category in self.organizer.file_types}

            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)

                if os.path.isfile(item_path):
                    category = self.organizer.get_file_category(item_path)
                    category_counts[category] += 1
                    file_count += 1

            self.preview_text.insert(
                tk.END, f"Found {file_count} files to organize:\n\n")

            for category, count in category_counts.items():
                if count > 0:
                    self.preview_text.insert(
                        tk.END, f"{category}: {count} files\n")

        except Exception as e:
            self.preview_text.insert(tk.END, f"Error generating preview: {e}")

        self.preview_text.config(state=tk.DISABLED)

    def start_quick_clean(self):
        """Start the quick clean process in a separate thread."""
        self.status_var.set("Cleaning in progress...")
        self.progress_var.set(0)

        # Disable buttons during cleaning
        for widget in self.quick_clean_tab.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(state=tk.DISABLED)

        # Start cleaning in a separate thread
        threading.Thread(target=self._do_quick_clean, daemon=True).start()

    def _do_quick_clean(self):
        """Perform the actual cleaning process."""
        try:
            # Clear previous results
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.config(state=tk.DISABLED)

            self.progress_var.set(10)  # Start progress

            # Run cleanup with selected options
            results = self.organizer.run_cleanup(
                organize_desktop=self.organize_desktop_var.get(),
                organize_downloads=self.organize_downloads_var.get(),
                clean_temp=self.clean_temp_var.get(),
                clean_browser=self.clean_browser_var.get(),
                empty_recycle=self.empty_recycle_var.get(),
                check_running_apps=self.check_running_apps_var.get()
            )

            self.progress_var.set(90)  # Almost done

            # Update results text
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, "Cleanup completed!\n\n")

            # Show any running browsers
            if 'browsers_running' in results and results['browsers_running']:
                browsers_str = ", ".join(results['browsers_running'])
                self.results_text.insert(
                    tk.END, f"⚠️ Note: The following browsers were running during cleanup: {browsers_str}\n")
                self.results_text.insert(
                    tk.END, "Some browser cache files may have been skipped to avoid errors.\n\n")

            if self.clean_temp_var.get():
                self.results_text.insert(
                    tk.END, f"Temporary Files Cleaned: {results['temp_files_deleted']} items\n")
                # Add note about in-use files if applicable
                if hasattr(self.organizer, 'skipped_files') and self.organizer.skipped_files > 0:
                    self.results_text.insert(
                        tk.END, f"(Some files were in use and skipped)\n")

            if self.clean_browser_var.get():
                self.results_text.insert(
                    tk.END, f"Browser Cache Cleaned: {results['browser_cache_cleaned']} items\n")

            if self.organize_desktop_var.get():
                self.results_text.insert(
                    tk.END, f"Desktop Files Organized: {results['desktop_files_organized']} files\n")

            if self.organize_downloads_var.get():
                self.results_text.insert(
                    tk.END, f"Downloads Files Organized: {results['downloads_files_organized']} files\n")

            if self.empty_recycle_var.get():
                status = "Successfully emptied" if results['recycle_bin_emptied'] else "Failed to empty"
                self.results_text.insert(tk.END, f"Recycle Bin: {status}\n")

            # Add total count
            total_processed = (results["temp_files_deleted"] +
                               results["browser_cache_cleaned"] +
                               results["desktop_files_organized"] +
                               results["downloads_files_organized"])
            self.results_text.insert(
                tk.END, f"\nTotal items processed: {total_processed}\n")

            self.results_text.config(state=tk.DISABLED)

            self.progress_var.set(100)  # Complete
            self.status_var.set("Cleanup completed successfully!")

        except Exception as e:
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, f"Error during cleanup: {e}")
            self.results_text.config(state=tk.DISABLED)

            self.status_var.set(f"Error: {str(e)}")

        finally:
            # Re-enable buttons
            for widget in self.quick_clean_tab.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.config(state=tk.NORMAL)

    def organize_selected_dir(self):
        """Organize the selected directory."""
        directory = self.dir_var.get()

        if not directory:
            messagebox.showwarning(
                "No Directory Selected", "Please select a directory first.")
            return

        if not os.path.exists(directory):
            messagebox.showerror(
                "Error", "The selected directory does not exist.")
            return

        self.status_var.set(f"Organizing {directory}...")
        self.progress_var.set(10)

        # Start organizing in a separate thread
        threading.Thread(target=self._do_organize, args=(
            directory,), daemon=True).start()

    def _do_organize(self, directory):
        """Perform the actual organization."""
        try:
            # Organize directory
            files_organized = self.organizer.organize_directory(directory)

            self.progress_var.set(100)
            self.status_var.set(
                f"Organization completed. {files_organized} files organized.")

            # Update preview
            self.update_preview(directory)

            # Show message box
            self.root.after(0, lambda: messagebox.showinfo("Complete",
                                                           f"Organization completed successfully!\n\n{files_organized} files were organized."))

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"An error occurred during organization: {e}"))

    def organize_custom_dir(self):
        """Organize directory with custom rules."""
        directory = self.custom_dir_var.get()

        if not directory:
            messagebox.showwarning(
                "No Directory Selected", "Please select a directory first.")
            return

        if not os.path.exists(directory):
            messagebox.showerror(
                "Error", "The selected directory does not exist.")
            return

        self.status_var.set(f"Organizing {directory} with custom rules...")
        self.progress_var.set(10)

        # Start organizing with custom rules in a separate thread
        threading.Thread(target=self._do_organize, args=(
            directory,), daemon=True).start()

    def refresh_logs(self):
        """Refresh the logs display."""
        # In a real app, this would read from a log file
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.insert(tk.END, "Log refreshed at " +
                              time.strftime("%Y-%m-%d %H:%M:%S"))
        self.logs_text.config(state=tk.DISABLED)

    def clear_logs(self):
        """Clear the logs display."""
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    try:
        import ctypes
        # Make the application DPI aware on Windows
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    root = tk.Tk()
    app = FileOrganizerGUI(root)
    root.mainloop()

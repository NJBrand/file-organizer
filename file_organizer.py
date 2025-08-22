import os
import shutil
import datetime
import logging
import winreg
import subprocess
from pathlib import Path
import send2trash  # Need to install this package

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('FileOrganizer')


class FileOrganizer:
    def __init__(self):
        # Define file types and their corresponding folders
        self.file_types = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.webp'],
            'Documents': ['.doc', '.docx', '.pdf', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv'],
            'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma'],
            'Video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.3gp'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.ts'],
            'Executables': ['.exe', '.msi', '.bat', '.dll', '.app'],
            'Others': []  # For files that don't match any category
        }

        # Define paths of temporary files that can be safely deleted
        self.temp_locations = [
            os.path.join(os.environ['TEMP']),
            os.path.join(os.environ['LOCALAPPDATA'], 'Temp'),
            os.path.join(os.environ['WINDIR'], 'Temp')
        ]

        # Define paths of download and desktop folders for organizing
        self.download_folder = os.path.join(
            os.path.expanduser('~'), 'Downloads')
        self.desktop_folder = os.path.join(os.path.expanduser('~'), 'Desktop')

        # Define file patterns that should be skipped (system files or commonly locked files)
        self.skip_patterns = [
            'ntuser.dat',
            'usrclass.dat',
            'NTUSER.DAT',
            'desktop.ini',
            'thumbs.db',
            'IconCache',
            'iconcache',
            '.lock',
            '~',
            'log.txt',
            'Microsoft',
            'Windows',
            'Account Pictures'
        ]

        # Browsers processes to check for
        self.browsers = {
            'chrome': 'chrome.exe',
            'edge': 'msedge.exe',
            'firefox': 'firefox.exe',
        }

    def is_process_running(self, process_name):
        """Check if a process is running by name."""
        try:
            # Using tasklist command for Windows
            cmd = f'tasklist /FI "IMAGENAME eq {process_name}" /NH'
            output = subprocess.check_output(cmd, shell=True).decode('utf-8')
            # If the process is running, output contains the process name
            return process_name.lower() in output.lower()
        except:
            # If there's an error, assume process is not running
            return False

    def check_running_browsers(self):
        """Check which browsers are currently running."""
        running = {}
        for browser, process in self.browsers.items():
            running[browser] = self.is_process_running(process)
        return running

    def get_file_category(self, file_path):
        """Determine the category of a file based on its extension."""
        file_ext = os.path.splitext(file_path)[1].lower()

        for category, extensions in self.file_types.items():
            if file_ext in extensions:
                return category

        return 'Others'

    def clean_temp_files(self):
        """Clean temporary files from common locations."""
        total_deleted = 0
        skipped_files = 0

        # Files and folders to skip (commonly locked by system)
        skip_patterns = [
            'ntuser.dat',
            'usrclass.dat',
            'NTUSER.DAT',
            'desktop.ini',
            'thumbs.db',
            'IconCache',
            'iconcache',
            'chrome_',
            'edge_',
            '.lock',
            '~',  # temp files often start with ~
        ]

        logger.info("Cleaning temporary files...")

        for temp_location in self.temp_locations:
            if os.path.exists(temp_location) and os.path.isdir(temp_location):
                logger.info(f"Cleaning: {temp_location}")

                try:
                    items = os.listdir(temp_location)
                except Exception as e:
                    logger.warning(
                        f"Could not access directory {temp_location}: {e}")
                    continue

                for item in items:
                    # Skip files that match patterns known to be locked
                    if any(pattern in item.lower() for pattern in skip_patterns):
                        skipped_files += 1
                        continue

                    item_path = os.path.join(temp_location, item)

                    try:
                        # Skip items that don't exist (might have been deleted)
                        if not os.path.exists(item_path):
                            continue

                        if os.path.isfile(item_path):
                            # Try to delete the file safely using send2trash
                            send2trash.send2trash(item_path)
                            total_deleted += 1
                        elif os.path.isdir(item_path):
                            # For directories, only delete if older than 2 days
                            if (datetime.datetime.now() - datetime.datetime.fromtimestamp(
                                    os.path.getmtime(item_path))).days > 2:
                                send2trash.send2trash(item_path)
                                total_deleted += 1
                    except PermissionError:
                        # File is in use, skip without error message
                        skipped_files += 1
                    except OSError as e:
                        if "being used by another process" in str(e):
                            # File is in use by another process
                            skipped_files += 1
                        else:
                            # Log other OS errors
                            logger.debug(f"Could not delete {item_path}: {e}")
                            skipped_files += 1
                    except Exception as e:
                        logger.debug(f"Error deleting {item_path}: {e}")
                        skipped_files += 1

        logger.info(
            f"Temporary files cleanup completed. {total_deleted} items moved to recycle bin. {skipped_files} items skipped.")
        # Store skipped files count for GUI to use
        self.skipped_files = skipped_files
        return total_deleted

    def clean_browser_cache(self):
        """Clean browser cache files."""
        # Chrome cache locations
        chrome_cache_locations = [
            os.path.join(os.environ['LOCALAPPDATA'], 'Google',
                         'Chrome', 'User Data', 'Default', 'Cache'),
            os.path.join(os.environ['LOCALAPPDATA'], 'Google',
                         'Chrome', 'User Data', 'Default', 'Code Cache'),
            os.path.join(os.environ['LOCALAPPDATA'], 'Google',
                         'Chrome', 'User Data', 'Default', 'GPUCache')
        ]

        # Edge cache locations
        edge_cache_locations = [
            os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft',
                         'Edge', 'User Data', 'Default', 'Cache'),
            os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft',
                         'Edge', 'User Data', 'Default', 'Code Cache'),
            os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft',
                         'Edge', 'User Data', 'Default', 'GPUCache')
        ]

        # Firefox cache
        firefox_profile = os.path.join(
            os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
        firefox_caches = []

        if os.path.exists(firefox_profile):
            try:
                for profile in os.listdir(firefox_profile):
                    profile_path = os.path.join(firefox_profile, profile)
                    if os.path.isdir(profile_path):
                        # Firefox cache locations
                        cache_paths = [
                            os.path.join(profile_path, 'cache2'),
                            os.path.join(profile_path, 'startupCache'),
                            os.path.join(profile_path, 'thumbnails')
                        ]
                        for path in cache_paths:
                            if os.path.exists(path):
                                firefox_caches.append(path)
            except Exception as e:
                logger.warning(f"Error accessing Firefox profiles: {e}")

        # Combine all cache locations
        cache_locations = chrome_cache_locations + edge_cache_locations + firefox_caches

        total_cleaned = 0
        skipped_files = 0

        for location in cache_locations:
            if os.path.exists(location) and os.path.isdir(location):
                logger.info(f"Cleaning browser cache: {location}")
                try:
                    items = os.listdir(location)

                    # Skip if browser is running and has locked the directory
                    if not items and ("Chrome" in location or "Edge" in location):
                        logger.info(
                            f"Browser appears to be running, skipping {location}")
                        continue

                    for item in items:
                        item_path = os.path.join(location, item)
                        try:
                            if os.path.isfile(item_path):
                                send2trash.send2trash(item_path)
                                total_cleaned += 1
                            elif os.path.isdir(item_path):
                                # For nested cache directories
                                try:
                                    send2trash.send2trash(item_path)
                                    total_cleaned += 1
                                except:
                                    # Try to clean individual files inside if directory can't be deleted
                                    for subitem in os.listdir(item_path):
                                        try:
                                            sub_path = os.path.join(
                                                item_path, subitem)
                                            if os.path.isfile(sub_path):
                                                send2trash.send2trash(sub_path)
                                                total_cleaned += 1
                                        except:
                                            skipped_files += 1
                        except PermissionError:
                            # File is in use, skip silently
                            skipped_files += 1
                        except OSError as e:
                            if "being used by another process" in str(e):
                                skipped_files += 1
                            else:
                                logger.debug(
                                    f"Could not delete cache file {item_path}: {e}")
                                skipped_files += 1
                        except Exception as e:
                            logger.debug(
                                f"Error cleaning cache item {item_path}: {e}")
                            skipped_files += 1
                except PermissionError:
                    logger.info(
                        f"Browser is running, cannot access {location}")
                except Exception as e:
                    logger.debug(
                        f"Error accessing cache directory {location}: {e}")

        logger.info(
            f"Browser cache cleanup completed. {total_cleaned} items moved to recycle bin. {skipped_files} items skipped.")
        return total_cleaned

    def organize_directory(self, directory):
        """Organize files in a directory into categorized folders."""
        if not os.path.exists(directory):
            logger.error(f"Directory does not exist: {directory}")
            return 0

        logger.info(f"Organizing files in: {directory}")

        # Create category folders if they don't exist
        for category in self.file_types.keys():
            category_path = os.path.join(directory, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)

        # Move files to their respective category folders
        files_moved = 0

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)

            # Skip directories and the category folders we just created
            if os.path.isdir(item_path) and item in self.file_types.keys():
                continue

            # Only process files
            if os.path.isfile(item_path):
                category = self.get_file_category(item_path)
                destination = os.path.join(directory, category)

                # Create destination if it doesn't exist (shouldn't happen but just in case)
                if not os.path.exists(destination):
                    os.makedirs(destination)

                # Move the file
                try:
                    dest_file_path = os.path.join(destination, item)

                    # Handle file name conflicts
                    if os.path.exists(dest_file_path):
                        base_name, extension = os.path.splitext(item)
                        counter = 1
                        while os.path.exists(os.path.join(destination, f"{base_name}_{counter}{extension}")):
                            counter += 1
                        dest_file_path = os.path.join(
                            destination, f"{base_name}_{counter}{extension}")

                    shutil.move(item_path, dest_file_path)
                    files_moved += 1
                    logger.info(f"Moved: {item} to {category}")
                except Exception as e:
                    logger.error(f"Error moving {item_path}: {e}")

        logger.info(f"Organization completed. {files_moved} files moved.")
        return files_moved

    def clean_recycle_bin(self):
        """Empty the Recycle Bin."""
        try:
            # Open a handle to the recycle bin
            logger.info("Emptying Recycle Bin...")
            winreg.SHEmptyRecycleBin(None, None, 0)
            logger.info("Recycle Bin emptied successfully.")
            return True
        except Exception as e:
            logger.error(f"Error emptying Recycle Bin: {e}")
            return False

    def run_cleanup(self, organize_desktop=True, organize_downloads=True, clean_temp=True,
                    clean_browser=True, empty_recycle=False, check_running_apps=True):
        """Run the full cleanup and organization process.

        Args:
            organize_desktop: Whether to organize desktop files
            organize_downloads: Whether to organize downloads folder
            clean_temp: Whether to clean temporary files
            clean_browser: Whether to clean browser cache files
            empty_recycle: Whether to empty the recycle bin
            check_running_apps: If True, will check if browsers are running before cleaning
        """
        results = {
            "temp_files_deleted": 0,
            "browser_cache_cleaned": 0,
            "desktop_files_organized": 0,
            "downloads_files_organized": 0,
            "recycle_bin_emptied": False,
            "browsers_running": []
        }

        logger.info("Starting file cleanup and organization process...")

        # Check for running browsers if requested
        if check_running_apps and clean_browser:
            running_browsers = self.check_running_browsers()
            results["browsers_running"] = [browser for browser,
                                           running in running_browsers.items() if running]

            if results["browsers_running"]:
                browsers_str = ", ".join(results["browsers_running"])
                logger.warning(
                    f"Warning: The following browsers are running: {browsers_str}")
                logger.warning(
                    "Some browser cache files might be skipped to avoid errors")

        # Clean temporary files
        if clean_temp:
            try:
                results["temp_files_deleted"] = self.clean_temp_files()
            except Exception as e:
                logger.error(f"Error during temp file cleanup: {e}")
                results["temp_files_deleted"] = 0

        # Clean browser cache
        if clean_browser:
            try:
                results["browser_cache_cleaned"] = self.clean_browser_cache()
            except Exception as e:
                logger.error(f"Error during browser cache cleanup: {e}")
                results["browser_cache_cleaned"] = 0

        # Organize desktop
        if organize_desktop:
            try:
                results["desktop_files_organized"] = self.organize_directory(
                    self.desktop_folder)
            except Exception as e:
                logger.error(f"Error organizing desktop: {e}")
                results["desktop_files_organized"] = 0

        # Organize downloads
        if organize_downloads:
            try:
                results["downloads_files_organized"] = self.organize_directory(
                    self.download_folder)
            except Exception as e:
                logger.error(f"Error organizing downloads folder: {e}")
                results["downloads_files_organized"] = 0

        # Empty recycle bin
        if empty_recycle:
            try:
                results["recycle_bin_emptied"] = self.clean_recycle_bin()
            except Exception as e:
                logger.error(f"Error emptying recycle bin: {e}")
                results["recycle_bin_emptied"] = False

        logger.info("File cleanup and organization process completed!")

        # Summary message
        total_cleaned = (results["temp_files_deleted"] +
                         results["browser_cache_cleaned"] +
                         results["desktop_files_organized"] +
                         results["downloads_files_organized"])

        logger.info(f"Total items processed: {total_cleaned}")

        return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="File Organizer and Cleaner")

    parser.add_argument("--no-desktop", action="store_true",
                        help="Skip organizing desktop files")
    parser.add_argument("--no-downloads", action="store_true",
                        help="Skip organizing downloads folder")
    parser.add_argument("--no-temp", action="store_true",
                        help="Skip cleaning temporary files")
    parser.add_argument("--no-browser", action="store_true",
                        help="Skip cleaning browser caches")
    parser.add_argument("--empty-recycle", action="store_true",
                        help="Empty the Recycle Bin")
    parser.add_argument("--organize-dir", type=str,
                        help="Organize a specific directory")

    args = parser.parse_args()

    organizer = FileOrganizer()

    if args.organize_dir:
        if os.path.exists(args.organize_dir) and os.path.isdir(args.organize_dir):
            organizer.organize_directory(args.organize_dir)
        else:
            logger.error(
                f"The specified directory does not exist: {args.organize_dir}")
    else:
        organizer.run_cleanup(
            organize_desktop=not args.no_desktop,
            organize_downloads=not args.no_downloads,
            clean_temp=not args.no_temp,
            clean_browser=not args.no_browser,
            empty_recycle=args.empty_recycle
        )

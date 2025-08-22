# File Organizer and Cleaner

A Python application that helps you clean and organize files on your computer. Keep your desktop, downloads, and temporary files under control with this easy-to-use tool.

## Features

- **Clean Temporary Files**: Remove unnecessary temporary files from common system locations
- **Clean Browser Cache**: Clear browser cache files from Chrome, Edge, and Firefox
- **Organize Files**: Sort files into folders based on their types (Documents, Images, Videos, etc.)
- **Custom Organization**: Apply organization rules to any folder on your computer
- **User-Friendly GUI**: Easy-to-use graphical interface for all operations

## Requirements

- Python 3.6 or higher
- Windows OS (some features are Windows-specific)

## Installation

### Setup from GitHub

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/file-organizer-cleaner.git
   cd file-organizer-cleaner
   ```

2. Install required packages:
   ```
   pip install send2trash
   ```

### Direct Download

1. Download the zip file from the releases section
2. Extract to your desired location
3. Install required package:
   ```
   pip install send2trash
   ```

## Usage

### Command Line Interface

Run the file organizer from the command line with various options:

```powershell
python file_organizer.py [options]
```

Options:
- `--no-desktop`: Skip organizing desktop files
- `--no-downloads`: Skip organizing downloads folder
- `--no-temp`: Skip cleaning temporary files
- `--no-browser`: Skip cleaning browser caches
- `--empty-recycle`: Empty the Recycle Bin
- `--organize-dir DIR`: Organize a specific directory

### Graphical User Interface

For a more user-friendly experience, run the GUI version:

```powershell
python gui_organizer.py
```

The GUI provides several tabs:

1. **Quick Clean**: Run common cleaning operations with a single click
2. **Organize Files**: Select and organize specific directories
3. **Custom Cleanup**: Apply custom organization rules
4. **Logs**: View operation logs and history

## Safety Features

- Files are moved to the Recycle Bin instead of being permanently deleted
- The application skips files that are currently in use by other processes
- Organization preserves original file names (with numbering for duplicates)
- The program avoids modifying important system directories
- Smart detection of running browsers before cleaning cache

## File Type Categories

The application organizes files into the following categories:

- **Images**: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .ico, .svg, .webp
- **Documents**: .doc, .docx, .pdf, .txt, .rtf, .odt, .xls, .xlsx, .ppt, .pptx, .csv
- **Audio**: .mp3, .wav, .aac, .flac, .ogg, .m4a, .wma
- **Video**: .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm, .m4v, .mpeg, .3gp
- **Archives**: .zip, .rar, .7z, .tar, .gz, .bz2, .xz
- **Code**: .py, .js, .html, .css, .java, .cpp, .c, .h, .php, .rb, .go, .ts
- **Executables**: .exe, .msi, .bat, .dll, .app
- **Others**: Any file type not matching the above categories

## Recent Improvements

- Added better error handling for files that are locked by other processes
- Added skip patterns to avoid attempting to delete system files
- Added check for running browsers before cleaning cache files
- Added separate tracking of skipped files
- Added proper error handling for all cleanup operations
- Updated GUI to show information about running browsers and skipped files
- Added 'Advanced Options' section in the GUI

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

Use this application at your own risk. Always back up important files before using file organization and cleaning tools.

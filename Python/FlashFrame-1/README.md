# FlashFrame Photo Tournament Organizer

## Overview
FlashFrame is a desktop application designed for organizing and managing photo tournaments. It provides a user-friendly interface for comparing and selecting images in a tournament-style format.

## Features
- Tournament-style photo comparison (2 or 4 choices per match)
- Keyboard shortcuts for fast selection and undo
- Progress bar and round/match information
- View original images with zoom functionality
- Auto-save and manual save of tournament state
- Export/import settings and session history
- Display tournament tree/log

## Installation
1. Clone the repository or download the source code.
2. Navigate to the project directory.
3. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   python src/main.py
   ```
2. Select a folder containing your photo files when prompted.
3. Use the interface to navigate through the tournament and make selections.

## File Structure
```
FlashFrame/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── tournament.py
│   ├── ui.py
│   ├── settings.py
│   ├── utils.py
│   └── types/
│       └── __init__.py
├── requirements.txt
└── README.md
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
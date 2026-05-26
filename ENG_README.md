#ENG
# WordCounter

WordCounter is a simple desktop app for counting specific spoken phrases through a microphone.

The app listens to speech, recognizes text, and increases the counter when one of the configured phrases is detected. It can be useful for streams, games, local event tracking, or any situation where repeated voice commands need to be counted.

## Features

- Speech recognition through a microphone
- Custom phrase list
- Recognition language selection: Russian, Ukrainian, English
- Interface language selection: Ukrainian, Russian, English
- Microphone selection in settings
- Shows only active Windows input microphones
- Recognition log
- Manual counter reset
- Manual counter value input
- Custom counter label text
- Overlay mode
- Automatic settings saving
- Automatic first-run installation to `AppData`
- Desktop shortcut creation
- Single-file `.exe` build
- Custom app icon

## Changes From Version 1.2.4 to 1.4.2

### Added

- Added microphone selection in settings.
- Added saving of the selected microphone.
- Added microphone persistence by both device index and device name.
- Added manual counter value input.
- Added validation for counter values: only whole numbers `0` and higher are accepted.
- Added automatic installation to `AppData\Local\WordCounter`.
- Added desktop shortcut creation.
- Added `.exe` build.
- Added custom app icon.
- Added microphone filtering through the Windows Core Audio API.

### Fixed

- Fixed unstable behavior during long app sessions.
- Fixed UI updates from the background listening thread.
- Fixed multiple listening threads starting after pressing `START` several times.
- Fixed delayed reaction when pressing `STOP`.
- Fixed selected microphone resetting after changing the interface language.
- Fixed the overly large microphone list.
- Removed unnecessary devices such as `Microsoft Sound Mapper`, `Primary Sound Capture Driver`, `Stereo Mix`, `Line In`, and technical duplicates.
- Fixed `.exe` packaging issue where the app failed to start because Tcl/Tk data was missing.
- Fixed console windows appearing when launching the app.
- Fixed interface text encoding issues.

## Settings Location

Settings are stored in the user folder:

`AppData\Local\WordCounter\settings.json`

This keeps the program folder clean and makes updates easier.

## Launch

Download and run:

`WordCounter_1.4.2.exe`

On first launch, the app automatically creates its working folder in `AppData\Local\WordCounter` and creates a desktop shortcut.

## Version

Current version: `1.4.2`

# HEICON

## What does it do ?

HEICON allows at its core, to convert HEIC images to `.JPG` ones.

Currently it's possible to convert them to `.PNG` and `.JPG`

## Requirements

Python3.6+

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Common usage

Make sure that paths that include whitespaces in them are surrounded by " "
```bash
./heic_to_jpg.py --path <path_of_file_or_folder>
```

To see the list of available commands, do: 
```bash
./heic_to_jpg.py --help
```

To Debug or test the app, a sample image is provided in `debug_resources`

To run a debug, make sure the PATH(S) provided or if none is provided, the folder where the program is being executed contains the `debug_resources/sample1.heic` file


To Debug, simply enter
```bash
./heic_to_jpg.py --debug
```
### Linux

```bash
./heic_to_jpg # A privilege update of the file may be needed for its execution (e.g. chmod u+x heic_to_jpg)
```

### Windows

Simply open powershell and run the program
```bash
heic_to_jpg.exe
```

## To-do
- <input type="checkbox" checked> ~~Add multi-processing~~
- <input type="checkbox" checked> ~~Make an executable app on either Linux or Windows~~ (Might need to find a way to have a console open on windows and enter the parameters there since as of yet the user needs to execute it through a newly opened powershell/console window)
- <input type="checkbox"> Add a GUI


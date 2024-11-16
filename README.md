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

```bash
python heic_to_jpg.py
```

To see the list of available commands, do: 
```bash
python heic_to_jpg.py --help
```

To Debug or test the app, a sample image is provided in `debug_resources`

To run a debug, make sure the PATH provided or if none is provided, the folder where the program is being executed contains the `debug_resources/sample1.heic` file


To Debug, simply enter
```bash
python heic_to_jpg.py --debug
```

## To-do
- <input type="checkbox" checked> ~~Add multi-processing~~
- <input type="checkbox"> Make an executable app on either Linux or Windows
- <input type="checkbox"> Add a GUI


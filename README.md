# youtu-playlist
Search & Download mp3 by name from Youtube

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See Running the tests for notes on how to deploy the project on a live system.

### Prerequisites

```
Python 2.7
```

### Installing

```
pip install -r requirements.txt

run main.py with -c (fix fprobe or avprobe not found problem)
```

Check packages


Windows
```
pip list | Findstr /L "package"
```

Linux
```
pip list | grep "package"
```

## Running the tests

-c --check-up (fix fprobe or avprobe not found problem)
-s --source-file (file with list of songs)

Windows
```
python main.py -c -s song_names
```

Linux
```
./main.py -c -s song_names
```

## Authors

* **Tomer Eyzenberg** - *Initial work* - [eLoopWoo](https://github.com/eLoopWoo)

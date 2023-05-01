# Postcardcreator_automization
Automate the sending of free postcards over the postcardcreator app

# Table of contents
* [Installation](#installation)
* [Quick-Start](#quick-start)

# Installation
In order to install the postcard creator you need some dependencies for the emulator and to connect to it.
## Android studio
Install [Android studio](https://developer.android.com/studio) and launch an android emulator of you choice from there.
## Adb
ADB is also a requirement for this project. It is used to interect with the emulators on a low level to install and open applications or to send files.
## Appium
[Appium](http://appium.io/docs/en/2.0/quickstart/install/) is used to interact with the UI of the application and to perform the automation itself. You need to install [Appium](http://appium.io/docs/en/2.0/quickstart/install/) and the [UiAutomation2 Driver](http://appium.io/docs/en/2.0/quickstart/uiauto2-driver/) for the application to work.
## Installing the framework itself
To install the framework, first install all the dependencies.
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

# Quick start
## Checks if the emulator is visible and which device it is
```bash
adb devices
```
The output should look somewhat like this.
```bash
$ adb devices                                                     
List of devices attached
emulator-5554   device
```
## Start appium
Find out where your android sdk is stored and export it in ANDROID_HOME
```bash
export ANDROID_HOME=~/Android/Sdk && appium
```

# Which emulator to use
Tested on pixel 3a emulator on android studio, works headless and with gui
```bash
# Headless
./emulator -no-window -avd Pixel_3a_API_33_x86_64 -gpu on
# Windowed
./emulator -avd Pixel_3a_API_33_x86_64 -gpu on
```
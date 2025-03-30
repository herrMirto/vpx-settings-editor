# VPX Settings Editor

VPX Settings Editor is a little Python/PySide6 GUI that mimics most of the configuration dialogs from the regular VPX Windows version. The aim of this program is to have a similar way to manage the extensive VPinballX.ini file.

To speed up the development process the initial version was created using Qt-Creator.

Most of the options were added using the amazing [@deKay](https://github.com/dekay) Wiki [https://github.com/dekay/vpinball-wiki/wiki/VPinball-Ini](https://github.com/dekay/vpinball-wiki/wiki/VPinball-Ini) page to map the Windows option names with the .ini file.

Each menu option from the Windows version were separate in Tabs inside the GUI. Unfortunately, design is not my strongest skill so any enhancements on that part are very welcome. Also, this was a very first attempt to developing a qt-creator project

Some of the configuration tabs(VR/Editor/Global) are there just because it was easy to implement as most of their options won't be visible/working on VPX as of now.

## Installing

Download the latest build from the Releases page [https://github.com/herrMirto/vpx-settings-editor/releases/](https://github.com/herrMirto/vpx-settings-editor/releases/), extract it and copy to your $HOME/bin or any directory that's part of you $PATH variable.

### MacOS

After extracting the archive you will have to remove the quarantine flag through System Settings / Privacy & Security / Allow Anyway button or on the command line as shown below.

```
xattr -d com.apple.quarantine vpx-settings-editor
```

Create the configuration file $HOME/.config/vpx_settings_editor.cfg with the following content:

```
[Paths]
vpx_binary_path = /home/user/vpinball/build/VPinballX_BGFX
vpx_ini_path = /home/user/.vpinball/VPinballX.ini
```

* Make a backup of your VPinballX.ini file first.

## Python Development

The application uses Python3.12

Start creating a virtual environment and installing the dependencies:

## Clone the repo
```
git clone https://github.com/herrMirto/vpx-settings-editor.git
```

## Create the virtual environment
```
python -m venv ~/.vpx_settings_dev
source ~/.vpx_settings_dev/bin/activate
pip install -r requirements.txt
```

## Start the app
```
cd vpx-settings-editor/
python main.py
```

## Checking version

```
python main.py --version
```

- The app version is also shown inside the GUI

- The GUI is defined on the ui_form.py file

## QT Creator Development[WIP] - Version 16

### MacOS Installation

```
brew install qt-creator
```

### Ubuntu Linux Installation

Download the official release from [https://github.com/qt-creator/qt-creator/releases/download/v16.0.0/qtcreator-linux-x64-16.0.0.deb](https://github.com/qt-creator/qt-creator/releases/download/v16.0.0/qtcreator-linux-x64-16.0.0.deb)

```
## install 
sudo dpkg -i qtcreator-linux-x64-16.0.0.deb

## run
/opt/qt-creator/bin/qtcreator
```

Open the vpx-settings-editor.pyproject on QT Creator and follow the instructions to configure the Python environment.

## Sections

**[Audio]**

Controls the configuration for SSF(Surround Sound Feedback) and other related sound configurations, including altsound. The GUI already supports new naming schema to use the sound card device name instead of IDs. 

**[Video]**

The most complex and maybe less documented of the sections. Although 


**[Nudge and DOF]**

- Although DOF is still not supported on the VPX Standalone version the options are already present in the .ini file and available to be modified. 

**[Buttons]** 

- Map your Joystick buttons to VPX controls.

**[VR Options]**

- Controls VR Options (Not really usable on Linux or MacOS for now)

**[PUP Config]**

- Configurations related to PUP Pack(use with caution as the functionality is still under heavy development)


**[Global]**

- Sets Global(Optinal) configurations like Mass, Strenght and Elasticity.

**[Editor]**

- Some of the options are not applicable to VPX Standalone as there's no editor available for MacOS or Linux.

**[Screens/DMD]**

- Enables AltColor/ZeDMD/Pixelcade
- Setup many windows positioning

**[Logs]**

- Visualize vpinball.logs
- Visualize VPX Settings Editor logs

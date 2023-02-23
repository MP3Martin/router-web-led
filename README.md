# router-web-led

Control your router LEDs from a cool command line [TUI](https://en.wikipedia.org/wiki/Text-based_user_interface) (thanks to [Textual](https://github.com/Textualize/textual)).

<a href="#/"><img src="https://user-images.githubusercontent.com/60501493/220739554-e6051f5d-e634-419c-bc54-a0f19efb9aa8.png" width="800px" /></a>

# Why

I've created this project because I found an old router that used to be the main router in our house. I wanted to gain shell access to it (for fun). I searched the internet and found OpenWrt. It had so many great features + you could easily enable **SSH**. After I gained access to the router shell, I found that you could easily control the LEDs on the router by **echo**ing a string to a file. And then I got the idea to create this project.

# Warning
**Only tested on [TL-WR743ND v1](https://is.gd/3NgWP7), you might need to edit [router_led_web.sh](https://github.com/MP3Martin/router-web-led/blob/main/server/router_led_web.sh) to make the server work on your router. ALL OF THE INSTALL INSTRUCTIONS ARE TESTED ONLY ON THE ROUTER I HAVE MENTIONED BEFORE!**

# Installation

The hardest part of the installation is installing OpenWrt on your router.

## Server

1. Install [OpenWrt](https://openwrt.org/) on your router. Find your device on [this](https://openwrt.org/toh/start) list and click the correct link in the Device Page column. There should be install instructions. Use your favourite search engine to find more info / guides. **⚠ EVERYTHING IS AT YOUR OWN RISK, I am not responsible for anything you do wrong ⚠**
2. Connect to your router using [this](https://openwrt.org/docs/guide-quick-start/sshadministration) tutorial
3. Run `cd /www/cgi-bin/`
4. Run `vim router_led_web.sh`
5. Press `I` (very important!)
6. Open [this](https://github.com/MP3Martin/router-web-led/raw/main/server/router_led_web.sh) page in your computers's browser
7. Press `CTRL+A`
8. Press `CTRL+C`
9. Go back to your terminal and paste the copied text into it (try `CTRL+SHIFT+V` or right-click)
10. You can now edit the config at the top of the file (move up using *up arrow*)
11. Press `ESC` (escape)
12. Type `:wq` and press `ENTER`
13. Type `chmod +x router_led_web.sh`

Your server (router) is now set up!

## Client

1. Download latest stable release from [releases](https://github.com/MP3Martin/router-web-led/releases/latest)
2. Extract the compressed file and *cd* into it
3. Now *cd* into the **client** directory
4. Make sure you have **[Python 3.7+](https://www.python.org/downloads/#content)** installed
5. Run `python3 -m pip install -r requirements.txt`
6. To start the [TUI](https://en.wikipedia.org/wiki/Text-based_user_interface), run `python3 router_led_set.py`
7. Set the correct config information, hit the **Save Config** button and start the script using a switch on the bottom of the page.

You can use mouse or *TAB* / *arrow* key(s) to control the [TUI](https://en.wikipedia.org/wiki/Text-based_user_interface). Press buttons using mouse left button or *ENTER* key.

# Pull requests

Pull requests are welcome, you could maybe add more modes or optimise the code (remove useless / duplicate code if you find any).
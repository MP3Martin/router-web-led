#!/bin/sh

#
# LICENSE: MIT
# MADE_BY: https://github.com/MP3Martin
# 
# This is a web server to set router LEDs.
# Made for: TL-WR743ND v1 (https://is.gd/3NgWP7), but should work on
# more routers thanks to the configuration below this introduction.
#
# Tested with OpenWrt installed on the router.
# Put this script in /www/cgi-bin/ and don't forget to "chmod +x" it.
#
# Examples:
# http://ROUTER-IP/cgi-bin/cmd?led=4&pass=whentheimposterissus&state=1
# http://ROUTER-IP/cgi-bin/cmd?led=10101010&pass=whentheimposterissus&state=0&mode=1
#

# v v v !!! START OF CONFIGURATION, YOU SHOULD CHANGE THESE VARIABLES !!! v v v

# LED id to name
LED_0="tp-link\:green\:system"
LED_1="ath9k-phy0"
LED_2="tp-link\:green\:lan1"
LED_3="tp-link\:green\:lan2"
LED_4="tp-link\:green\:lan3"
LED_5="tp-link\:green\:lan4"
LED_6="tp-link\:green\:wan"
LED_7="tp-link\:green\:qss"

# Misc globals
LED_COUNT="8"
STUPID_PASSWORD="whentheimposterissus"

# ^ ^ ^ !!! END OF CONFIGURATION, YOU SHOULD CHANGE THESE VARIABLES !!! ^ ^ ^

set_led()
{
    # $1 is LED id
    # $2 is LED state
    
    # Get the led name by id
    LED_NAME="\$LED_"$1
    eval LED_NAME=$LED_NAME
    
    # Get the state
    #   0 is none
    #   1 is default-on
    LED_STATE=""
    
    if [ "$2" -eq 0 ]; then
        LED_STATE="none"
    fi
    
    if [ "$2" -eq 1 ]; then
        LED_STATE="default-on"
    fi
    
    # Turn on/off the led
    LED_TRIGGER_PATH="/sys/class/leds/$LED_NAME/trigger"
    COMMAND="echo $LED_STATE > $LED_TRIGGER_PATH"
    eval $COMMAND # I know, unsafe, but it doesn't work if i just run the command. Probably an
    #               error with the colons/backslashes in LED names. Pull request is welcome.
}

echo "Content-type: text/html"
echo ""

echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>LED Control</title>'
echo '</head>'
echo '<body>'


# Make sure we have been invoked properly.
if [ "$REQUEST_METHOD" != "GET" ]; then
    echo "<hr>Script Error:"\
    "<br>Usage error, cannot complete request, REQUEST_METHOD!=GET."\
    "<br>Check your FORM declaration and be sure to use METHOD=\"GET\".<hr>"
    exit 1
fi

# If no arguments, exit gracefully now.
if [ -z "$QUERY_STRING" ]; then
    echo "Error: Bro think he query 💀"
    exit 0
fi

# Extract the data you are looking for with sed:
WW=$(echo "$QUERY_STRING" | sed -n 's/^.*mode=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
XX=$(echo "$QUERY_STRING" | sed -n 's/^.*led=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
YY=$(echo "$QUERY_STRING" | sed -n 's/^.*state=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
ZZ=$(echo "$QUERY_STRING" | sed -n 's/^.*pass=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")

# Check stupid, unsecure and maybe funny password
if [ "$ZZ" != "$STUPID_PASSWORD" ]; then
    echo "Error: Bro think he password 💀"
    exit 0
fi

# Check if XX (led number) is a real number
if [ -n "$XX" ] && [ "$XX" -eq "$XX" ] 2>/dev/null; then
    :
else
    echo "Error: Bro think he number 💀"
    exit 0
fi

# Check if WW (mode) is a real number and auto assign default value if it is not a number
if [ -n "$WW" ] && [ "$WW" -eq "$WW" ] 2>/dev/null; then
    :
else
    WW=0
fi

# Check the mode
#   0 is a single LED (default)
#   1 is all LEDs at once
if ! [ "$WW" -eq 1 ]; then
    # Check if XX (led number) is in range "0" to "$LED_COUNT - 1"
    _temp=$(($LED_COUNT - 1))
    if [ "$XX" -ge 0 ] && [ "$XX" -le "$_temp" ]; then
        :
    else
        echo "Error: Bro think he LED 💀"
        exit 0
    fi
    
    # Check if YY (state) is a real number
    if [ -n "$YY" ] && [ "$YY" -eq "$YY" ] 2>/dev/null; then
        :
    else
        echo "Error: Bro think he number 💀"
        exit 0
    fi
    
    # Check if YY (state) is in range 0 - 1
    if [ "$YY" -ge 0 ] && [ "$YY" -le 1 ]; then
        :
    else
        echo "Error: Bro think he state 💀"
        exit 0
    fi
    
    # All good, set the LED
    set_led $XX $YY
else
    # This mode is way better than sending "$LED_COUNT" requests per frame.
    # The YY (state) variable will not be needed here.
    
    # Check if XX (led numberList) is "$LED_COUNT" characters big, error if not
    if ! [ "${#XX}" -eq "$LED_COUNT" ]; then
        echo "Error: Bro think he $LED_COUNT 💀"
        exit 0
    fi
    
    # Loop over the leds, set them one by one.
    #   0 = off
    #   1 = on
    while [ ${#XX} -gt 0 ]; do
        next=${XX#?}
        index=$(($LED_COUNT - ${#XX}))
        set_led $index ${XX%$next}
        XX=$next
    done
fi

echo "ඞ ok"
echo '</body>'
echo '</html>'

exit 0
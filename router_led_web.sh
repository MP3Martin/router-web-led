#!/bin/sh

echo "Content-type: text/html"
echo ""

echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>Form Example</title>'
echo '</head>'
echo '<body>'

# LED number to name
LED_0="tp-link:green:system"
LED_1="ath9k-phy0"
LED_2="tp-link:green:lan1"
LED_3="tp-link:green:lan2"
LED_4="tp-link:green:lan3"
LED_5="tp-link:green:lan4"
LED_6="tp-link:green:wan"
LED_7="tp-link:green:qss"

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
XX=`echo "$QUERY_STRING" | sed -n 's/^.*led=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"`
YY=`echo "$QUERY_STRING" | sed -n 's/^.*state=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"`
ZZ=`echo "$QUERY_STRING" | sed -n 's/^.*pass=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"`

# Check if XX (led number) is a real number
if [ -n "$XX" ] && [ "$XX" -eq "$XX" ] 2>/dev/null; then
    :
else
    echo "Error: Bro think he number 💀"
    exit 0
fi

# Check if XX (led number) is in range 0 - 7
if [ "$XX" -ge 0 ] && [ "$XX" -le 7 ]; then
    :
else
    echo "Error: Bro think he LED 💀"
    exit 0
fi

# All good, get led name by id
LED_NAME="$""LED_"$XX
eval LED_NAME=$LED_NAME

# Turn on/off the led
echo $LED_NAME > /root/led.txt

echo "ඞ ok"
echo '</body>'
echo '</html>'

exit 0
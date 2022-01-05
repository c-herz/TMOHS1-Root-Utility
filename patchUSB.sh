#!/bin/bash
echo "Running the patch script. . ."
mkdir -p /etc/backups/init.d/
echo 'Backing up original USB init script to /etc/backups/init.d/usb.backup'
if [ ! -f /etc/backups/init.d/usb.backup ]; then # only apply the patch if we haven't before
	cp /etc/init.d/usb /etc/backups/init.d/usb.backup

	patch -p0 /etc/init.d/usb << 'EOF'
	--- usb-unmodified	2022-01-04 16:18:40.368215949 -0500
	+++ usb	2022-01-05 02:27:35.885874954 -0500
	@@ -148,17 +148,15 @@
			sleep 1
		fi
	
	-	usbport=`cat /proc/cmdline | grep -o "androidboot.usbport=[0-9]*" | cut -d "=" -f2`
	-	case $usbport in
	-	0 )
	-		echo "usb pid 9059"
	-		custpid="9059"
	-		;;
	-	1 )
	-		echo "usb pid 9057"
	-		custpid="9057"
	-		;;
	-	esac
	+	###MODIFIED###
	+	# ADB ENABLE - changed to prevent auto-switching to 9057 on boot
	+	# Enables SELECTED_USB no matter what qualcomm's plans are :)
	+	# SELECT MODE BELOW:
	+	SELECTED_USB=9025
	+
	+	echo "User set usb pid" $SELECTED_USB
	+	custpid=$SELECTED_USB
	+
		usbpid=`ls -l /data/usb/boot_hsusb_composition |grep -o "compositions/[a-zA-Z0-9]*" |cut  -d "/" -f2 `
		echo "usbpid:" $usbpid
		if [ $usbpid != $custpid ]
	@@ -167,7 +165,7 @@
			rm /sbin/usb/boot_hsusb_composition
			ln -fs /sbin/usb/compositions/$custpid /data/usb/boot_hsusb_composition
		fi
	-
	+	
		# boot hsusb composition:
		if [ -d /sys/class/android_usb/android0 ]
		then
EOF
fi
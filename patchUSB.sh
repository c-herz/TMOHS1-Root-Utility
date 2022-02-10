#!/bin/bash
echo "Running the patch script. . ."
mkdir -p /etc/backups/init.d/
echo 'Backing up original USB init script to /etc/backups/init.d/usb.backup'
# only apply the patch if we haven't before (or our backup is the same as the existing file)
	cp /etc/init.d/usb /etc/backups/init.d/usb.backup
if [ ! -f /etc/backups/init.d/usb.backup ] || cmp -s '/etc/init.d/usb' '/etc/backups/init.d/usb.backup'; then 
	patch -p0 '/etc/init.d/usb' < '/cache/usb.patch'
fi
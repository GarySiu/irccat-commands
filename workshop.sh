#!/bin/bash
echo `date`: $* >> /usr/share/irccat/.notify.log
shift;shift;shift;shift;
/usr/share/irccat/setBoard.py wilson.lan.london.hackspace.org.uk "$*"

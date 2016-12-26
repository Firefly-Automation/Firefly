#! /bin/sh

PATH="/bin:/usr/bin:/sbin:/usr/sbin"
DAEMON="/opt/firefly_system/Firefly/system_scripts/firefly_service.sh"
PIDFILE="/var/run/scriptname.pid"
NAME="firefly"

test -x $DAEMON || exit 0

. /lib/lsb/init-functions

case "$1" in
  start)
     log_daemon_msg "Starting $NAME"
     start_daemon -p $PIDFILE $DAEMON
     log_end_msg $?
   ;;
  stop)
     log_daemon_msg "Stopping $NAME"
     killproc -p $PIDFILE $DAEMON
     PID=`ps x |grep feed | head -1 | awk '{print $1}'`
     kill -9 $PID       
     log_end_msg $?
   ;;
  force-reload|restart)
     $0 stop
     $0 start
   ;;
  status)
     status_of_proc -p $PIDFILE $DAEMON && exit 0 || exit $?
   ;;
 *)
   echo "Usage: /etc/init.d/$NAME {start|stop|restart|force-reload|status}"
   exit 1
  ;;
esac

exit 0
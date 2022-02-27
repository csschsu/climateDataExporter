#
# Install climateDataExporter
#
ROOTUID="0"

if [ "$(id -u)" -ne "$ROOTUID" ] ; then
    echo "This script must be executed with root privileges."
    exit 1
fi


echo "add user prometheus"
adduser prometheus --shell=/bin/false --no-create-home

echo "add prometheus group to current user -- require new login to activate"
usermod -g prometheus $USER

echo "create log directory and allow users in prometheus group to write"
LOGDIRECTORY="/var/log/climateDataExporter"
mkdir $LOGDIRECTORY
chown prometheus:prometheus $LOGDIRECTORY
chmod 775 $LOGDIRECTORY


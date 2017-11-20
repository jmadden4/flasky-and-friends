
gnome-terminal -e /home/joe/workspace/Nov5/startZookeeper.sh  --window-with-profile=Joe

sleep 10
echo 'started zookeeper instance'

gnome-terminal -e /home/joe/workspace/Nov5/startKafka.sh  --window-with-profile=Joe
sleep 5
echo 'started kafka instance'

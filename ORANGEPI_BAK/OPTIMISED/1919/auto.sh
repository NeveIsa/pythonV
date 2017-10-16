cd /root/OPTIMISED/1919/

rm log/*
screen -d -m python reduced1919_mask.py 0
screen -d -m python cam_decision2server.py

echo 0 | sudo tee /sys/devices/system/cpu/cpu1/online
echo 0 | sudo tee /sys/devices/system/cpu/cpu2/online
echo 0 | sudo tee /sys/devices/system/cpu/cpu3/online


echo 648000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq

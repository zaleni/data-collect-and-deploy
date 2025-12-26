bash
#!/bin/bash

VID="2bc5"

for dev in /sys/bus/usb/devices/*; do
  if [ -e "$dev/idVendor" ]; then
    vid=$(cat "$dev/idVendor")
    if [ "$vid" == "${VID}" ]; then
      port=$(basename $dev)
      product=$(cat "$dev/product" 2>/dev/null) # 产品名称
      serial=$(cat "$dev/serial" 2>/dev/null) # 序列号
      echo "发现Orbbec设备 $product，usb端口 $port，序列号 $serial"
    fi
  fi
done
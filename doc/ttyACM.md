The device requires a specific serial port setup:
# Configure serial port with no flow control
  stty -F /dev/ttyACM0 9600 cs8 -cstopb -parenb -crtscts -ixon -ixoff

And then use `screen` to connect: `screen /dev/ttyACM0 9600`


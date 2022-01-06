# Robot2
Designed to run on a Raspberry Pi 3 Model B+. Uses WiFi to connect to the network, serves up a web page with robot controls and the camera view. Clicking on links calls the appropriate API and move around. Calls to a Sabertooth 2x60 to control the motors.

To set up the Raspberry Pi, see history.out for some ideas.

To run the code:
* ssh to the Rasperry Pi on the robot
* cd Projects/Robot2
* source flaskenv/bin/activate
* sudo python3.10 sergei1.py

When finished...
either click on the "shutdown!" button in the web app, or use the following commands at the ssh prompt:
* deactivate
* sudo shutdown -P now

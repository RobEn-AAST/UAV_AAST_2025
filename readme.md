// todo put windspeed
// todo adjust plane speed from parameters
// todo 


## Backend

*Aiming for 3 separate main objects*

Missions: responsible for generating the waypoint sequence to solve any given mission
Uav: the main brain, responsible for uploading or interacting with the controller in any way

math_utils: responsible for any mathmatical related equation or other liek new_wp, bearing and such
nav_utils: responsible for navigation common tasks like avoiding obstacles
readers: utilities to read from files and such
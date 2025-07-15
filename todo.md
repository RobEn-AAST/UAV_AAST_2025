IMPORTANT STOP USING PLANE .JSON AS IT'S VWEERY BRITTLE AND SUBTLE TO MISTAKES, INSTEAD USE JSON
IMPORTANT STOP USING TUPLES FOR POINTS, INSTEAD USE A SPECIFIED CLASS
IMPORTANT TEST THE PATH FINDING FUNCTION SPECIALLY THE COST
IMPORTANT HANDLE THE WP 1, 2, 3, 4 BEING ORIGINAL MISSION, WP5 THE PAYLOAD, WP6, 7, 8, 9 THE SEAARCH ZONE
IMPORTANT MAKE AN API CALL TO GET WING SPEED AND BEARING
IMPORTANT THE CURRENT SURVEY CODE ASSUMES PERFECT CONDITIONS, DOESN'T CONCIDER HOW HARD THE UAV TURNS

make mission 1 like let us able to choose which to upload and which not to

## Bring back those but in the frontend
frontend Enter connection string with a drop down for available options
def uav_connect():
    print("choose the way of communication :")
    print("connection 1 is '127.0.0.1:14550' for local host")
    print("connection 2 is for network sharing")
    print("connection 3 for telemetry system")
    connection_type = input("Enter connection number:  ")


adjust initial bearing during takeoff to get it automatically maybe..

## important
!fix dubins path calculation calls
!obstacle avoidance, test obstacle avoidance module more and maybe find something better
!align the mission logic with what the competition actually wants
have a class point that includes (lat, long, alt, brng) instead of doing everythign hard codes as lists
?auto test?
stop using json we need to find a less error invoking thing, not sure about yaml either honestly
complete mission 2



some issues to point:
    spagetti code at entries.py
    repeated code logic for uav.py
    uav is responsible for missions, this breaks the idea of encapsulation
    uav is responsible for reading from files, again breaks core concept of encapsulation
    over optimization is not a good thing, why is there an entire class with two methods whose only purpose in life is to call json.load..
    - the fact that too many classes are used who does barely contain more than 2 lines of code is a readability killer as i have to trace 10 differnet short functions to know what a single block of code does
    - silent errors, for say reading a file when you call the function and it fails yes it prints that it failed but the caller doenst' know that instead he continues to run as if it worked fine, even worse it itself will cause an error as the returned type was an empty dictionary intead of dictionary with data, the errors must be handeled in teh caller too
    classes names should follow pascal case
    Convert and Reconvert, bad naming

    auto continue was set to false for some missions btw

    todoooooo:
    add mission 2 
    optimize survey if possible 
    add pdf reader
    add raduis acc

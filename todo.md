frontend Enter connection string with a drop down for available options
def uav_connect():
    print("choose the way of communication :")
    print("connection 1 is '127.0.0.1:14550' for local host")
    print("connection 2 is for network sharing")
    print("connection 3 for telemetry system")
    connection_type = input("Enter connection number:  ")


adjust initial bearing during takeoff to get it automatically
test obstacle avoidance module more and maybe find something better
have the payload path finder more separated
have a separated class for Coord



some issues to point:
    spagetti code at entries.py
    repeated code logic for uav.py
    uav is responsible for missions, this breaks the idea of encapsulation
    uav is responsible for reading from files, again breaks core concept of encapsulation
    over optimization is not a good thing, why is there an entire class with two methods whose only purpose in life is to call json.load..
    - the fact that too many classes are used who does barely contain more than 2 lines of code is a readability killer as i have to trace 10 differnet short functions to know what a single block of code does
    - silent errors, for say reading a file when you call the function and it fails yes it prints that it failed but the caller doenst' know that instead he continues to run as if it worked fine, even worse it itself will cause an error as the returned type was an empty dictionary intead of dictionary with data, the errors must be handeled in teh caller too
    classes names should follow pascal case
    Convert and Reconvert, what type of naming is this ;-;
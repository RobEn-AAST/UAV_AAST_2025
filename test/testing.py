import csv
with open('obstacles.csv', mode ='r')as file:
  obs_cords=[]
  csvFile = csv.reader(file)
  for lines in csvFile:
    obs_cords.append(lines)


  print(obs_cords)


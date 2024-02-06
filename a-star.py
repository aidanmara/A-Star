import math
from collections import deque
from re import split
import sys

######################################### GLOBAL VARIABLES ###############################################################
#Global txt files should remain static
coordinatesFile = 'coordinates.txt'
mapFile = 'map.txt'
#------------------------------------------------------------------------------------------------------

#Global dictionaries used in most functions, need to create it before others that are dependent upon it.
citiesCoords = dict()
citiesAdj = dict()
########################################## END OF GLOBAL VARIABLES ######################################################



############################################ FUNCTIONS ##################################################

#Build the dictionary with its coordinates to compute straight line distance later
def buildCoordList(coordinatesFile):
  
  #Read thru the file splitting into name and a list of coordinates for each city using format to our advantage
  for line in open(coordinatesFile, 'r'):
    
    #Split name and coordinates
    a = line.split(':')
    name = a[0]

    #Split coordinates into a list of latitude and longitude.
    coords = a[1].split(',')
    coords[0] = coords[0].strip('(')
    coords[1] = coords[1].strip('\n')
    coords[1] = coords[1].strip(')')

    #Update the global dictionary for coords
    citiesCoords.update({name: [float(coords[0]), float(coords[1])]})
    
#Build the dictionary with its neighbours to compute the shortest path later
def buildAdjList(mapFile):
  #Read thru the file creating a list of adjacencies for each city and their edge costs
  for line in open(mapFile, 'r'):
    
    #City to have adjacencies for
    a = line.split('-')
    name = a[0]
    temp = []

    #Split the adjacencies into a list of adjacencies
    adj = a[1].split(',')
    
    for item in adj:
      #**For some reason the split function wasn't working on the strings so I just read each character until I reached the char I was looking for...**

      #Give the adjacencies a name and a cost
      adjName = ''
      estVal = ''
      flag = 0
      
      for char in item:
        if flag == 0:
          if char != '(': adjName+=char
          else: 
            flag = 1
            continue
        if flag == 1:
          if char != ')': estVal+=char
          else: break
            
      #Add to temporary list to get past the split issue
      temp.append([adjName,float(estVal)])

    #Update the global dictionary for adjacencies
    #Essentially building a graph
    citiesAdj.update({name:temp})

#Call and build the dictionaries
buildCoordList(coordinatesFile)
buildAdjList(mapFile)

#Haversine Formula to compute the straight line distance between two cities
def haversine(la1,lon1,la2,lon2):
  radian = (math.pi/180) #Radian value

  radius = 3_958.8 #Radius of earth in miles

  #Convert coordinates to radians
  la1 = la1 * radian
  lon1 = lon1 * radian
  la2 = la2 * radian
  lon2 = lon2 * radian 

  #Apply Haversine's formula for given points
  innerFormula = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lon2 - lon1) / 2) ** 2
  return  2 * radius * math.asin(math.sqrt(innerFormula))
  
#Using the Haversine Formula compute the straight line distance for each city from our end city for estimation in A* algo
def buildStraightLineList(end: str, CityList: list):
  table = {}

  #Apply H Formula for each city in our scope
  for city in CityList:
    table.update({city:haversine(citiesCoords[city][0],citiesCoords[city][1],citiesCoords[end][0],citiesCoords[end][1])})
  
  return table

#AStar Algo to compute the shortest path from our end city to all other cities
def aStar(start: str, end: str): 
  #Build our straight line distance table using end city
  straightLineTable = buildStraightLineList(end, citiesCoords.keys())

  #Create a queue to store our cities to visit. Start with start and edge weigh of 0. //deque bc i like
  visitQue = deque()
  visitQue.append([start,0])

  #Create 2 dictionaries to store our visited cities previous city and the total cost of edge weight and straight line distance 
  prev = {}
  costTotal = {start:0}

  while visitQue:
      #Pop the first city in the queue and its current cost
      currCity, currCost = visitQue[0]

      #We reached the best path
      if currCity == end: break

      #For every adjacent node, use A* to check if it is the best path, if it is update its new total cost and the previous city
      for neighbor, edgeCost in citiesAdj[currCity]:
          new_cost = costTotal[currCity] + edgeCost + straightLineTable[neighbor]

          if neighbor not in costTotal or new_cost < costTotal[neighbor]:
              costTotal[neighbor] = new_cost
              prev[neighbor] = currCity
              visitQue.append([neighbor, new_cost])

      #Remove visited from queue, it can appear again
      visitQue.popleft()
      #Sort the queue by total cost so the current shortest path is in front
      visitQue = deque(sorted(visitQue, key=lambda x: costTotal[x[0]] + straightLineTable[x[0]]))

  #Create a list to store the path
  currCity = end
  path = []

  #Go thru the previous dictionary and build the path
  while currCity != start:
    path.append(currCity)
    currCity = prev[currCity]

  #Add the starting city as the last element of the path and reverse so it would be next city
  path.append(start)
  path.reverse()

  #Finally go thru the dictionary of adjacencies and costs to calculate the final routes cost
  
  finalCost = 0
  
  for i in range(len(path)-1):
    
    #In hindsight, this would be faster and less technical if I just used a dictionary to store the cost of each city, 
    #but I'm this far in and there arent that many cases to go thru knowing the dataset.
    for neighbor in citiesAdj[path[i]]:
      if neighbor[0] == path[i+1]:
        finalCost += neighbor[1]
    
    
  return path, finalCost
  
############################################ END OF FUNCTIONS #############################################################
def main():
  
  #Check if the user input is correct amount
  if len(sys.argv) != 3:
    print('\nInvalid Input Format. Please Input 2 Cities\n')
    return

  #If correct amount save values
  start,end = sys.argv[1],sys.argv[2]
  
  #And check if they are even in the dataset, it won't work otherwise
  if start not in citiesAdj.keys() or end not in citiesCoords.keys():
    print('Please Enter 2 Valid Cities From the Following List:\n')
    for name in citiesCoords.keys():
      print(name)
    print('\n')
    return
      

  #Perform A* on inputted start and end cities
  path,finalCost = aStar(start,end)

  #Print the path and cost in the specified format
  print('\nFrom city:', start)
  print('To city:', end)
  print('Best Route:', ' - '.join(path))
  print('Total distance:', finalCost,' mi\n')


if __name__ == "__main__":
  main()


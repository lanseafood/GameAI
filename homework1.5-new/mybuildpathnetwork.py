'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates the pathnetwork as a list of lines between all pathnodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world, agent = None):
    lines = []
    ### YOUR CODE GOES BELOW HERE ###
    
    #getting world dimensions
    x,y = world.getDimensions()
    # dimensions = (int(math.ceil(x/cellsize)), int(math.ceil(y/cellsize)))

    obstacles = world.getObstacles()

    # for each node in pathnodes
    #     for each subsequent node in pathnodes

    #         find the path between them. can it be traversed?
    #         if yes then 
    #         lines.add()
    #         else
    #         next 

    for node in range(len(pathnodes)): #getting indexes
        for nextNode in range(node +1, len(pathnodes)):
            start = pathnodes[node]
            end = pathnodes[nextNode]
            tryLine = (start, end)

            linesAllGood = True

            for o in obstacles:
                oPoints = o.getPoints()
                oLines = o.getLines()
                minD = 1000000000000000.0

                for line in oLines: #checking if the lines of obstacle collide with the line between these two points
                    if (calculateIntersectPoint(start, end, line[0], line[1]) != None): #there is collision
                        linesAllGood = False
                        break
                if linesAllGood == False:
                    break

                for point in oPoints:
                    cD = minimumDistance(tryLine, point)
                    if cD < minD:
                        minD = cD
                if minD < agent.maxradius:
                    linesAllGood = False
                    break

            if linesAllGood:
                lines.append(tryLine)
                            
    ### YOUR CODE GOES ABOVE HERE ###
    return lines

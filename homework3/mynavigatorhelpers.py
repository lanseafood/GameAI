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

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *




### This function optimizes the given path and returns a new path
### source: the current position of the agent
### dest: the desired destination of the agent
### path: the path previously computed by the Floyd-Warshall algorithm
### world: pointer to the world
def shortcutPath(source, dest, path, world, agent):
	### YOUR CODE GOES BELOW HERE ###
	# self.world.getLinesWithoutBorders(), self.world.getPoints()
	worldLines = world.getLinesWithoutBorders()
	worldPoints = world.getPoints()
	radius = agent.maxradius

	clear = True
	#does it collide with the world lines
	if canBridge(source, dest, worldLines, worldPoints, radius):
		return [source, dest]
	else:
		shortest_path = path
		path_size = getDistances(path)
		for i in xrange(len(path)):
			for j in xrange(i+1, len(path)):
				if canBridge(path[i], path[j], worldLines, worldPoints, radius):
					temp_path = path[0:i] + path[j:]
					temp_d = getDistances(temp_path)
					if temp_d < path_size:
						print 'old path'
						print shortest_path
						path_size = temp_d
						shortest_path = temp_path
						print 'new path'
						print shortest_path
	### YOUR CODE GOES BELOW HERE ###
		return shortest_path


def canBridge(source, dest, worldLines, worldPoints, radius):
	clear = True
	# print 'called canBridge'
	#does it collide with the world lines
	if rayTraceWorld(source,dest,worldLines) == None:
		line = (source,dest)
		minD = INFINITY
		for i in xrange(len(worldPoints)):
			test_p = worldPoints[i]
			min_d = minimumDistance(line, test_p)
			if min_d < minD:
				minD = min_d

		if minD < (radius):
			return False
		else:
		#         point = worldPoints[i]
		#         next_point = worldPoints[j]
		#         if rayTrace(point, next_point, line) != None:
		#             return False
			# print 'CAN BRDIGE RETURNS TRUE'
			return clear
	else:
		return False

def getDistances(path): #distance from source to dest from entire path
	dist = 0
	for i in xrange(len(path)):
		if i+1 != len(path):
			dist = dist + distance(path[i],path[i+1])
	return dist

### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
	### YOUR CODE GOES BELOW HERE ###
	path = nav.getPath()
	print 'THIS IS THE PATH FOR MY SMOOTH' + str(path)
	source = nav.getSource()
	dest = nav.getDestination()
	print 'trying to smooth'
	# print source
	# print dest
	# print nav.world
	if source != None and dest != None and canBridge(source, dest, nav.world.getLinesWithoutBorders(), nav.world.getPoints(), nav.agent.maxradius):
		nav.setPath([])
		nav.agent.moveToTarget(dest)
		print 'RETURNED TRUE'
		return True
	else:
	### YOUR CODE GOES ABOVE HERE ###
		return False




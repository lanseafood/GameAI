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
from mycreatepathnetwork import *
from mynavigatorhelpers import *


###############################
### AStarNavigator
###
### Creates a path node network and implements the FloydWarshall all-pairs shortest-path algorithm to create a path to the given destination.
			
class AStarNavigator(NavMeshNavigator):

	def __init__(self):
		NavMeshNavigator.__init__(self)
		

	### Create the pathnode network and pre-compute all shortest paths along the network.
	### self: the navigator object
	### world: the world object
	def createPathNetwork(self, world):
		self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
		return None
		
	### Finds the shortest path from the source to the destination using A*.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., it's current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		### Make sure the next and dist matricies exist
		if self.agent != None and self.world != None: 
			self.source = source
			self.destination = dest
			### Step 1: If the agent has a clear path from the source to dest, then go straight there.
			###   Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
			###   Tell the agent to move to dest
			### Step 2: If there is an obstacle, create the path that will move around the obstacles.
			###   Find the pathnodes closest to source and destination.
			###   Create the path by traversing the self.next matrix until the pathnode closes to the destination is reached
			###   Store the path by calling self.setPath()
			###   Tell the agent to move to the first node in the path (and pop the first node off the path)
			if clearShot(source, dest, self.world.getLines(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				start = findClosestUnobstructed(source, self.pathnodes, self.world.getLinesWithoutBorders())
				end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLinesWithoutBorders())
				if start != None and end != None:
					print len(self.pathnetwork)
					newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
					print len(newnetwork)
					closedlist = []
					path, closedlist = astar(start, end, newnetwork)
					if path is not None and len(path) > 0:
						path = shortcutPath(source, dest, path, self.world, self.agent)
						self.setPath(path)
						if self.path is not None and len(self.path) > 0:
							first = self.path.pop(0)
							self.agent.moveToTarget(first)
		return None
		
	### Called when the agent gets to a node in the path.
	### self: the navigator object
	def checkpoint(self):
		myCheckpoint(self)
		return None

	### This function gets called by the agent to figure out if some shortcutes can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

	def update(self, delta):
		myUpdate(self, delta)


def unobstructedNetwork(network, worldLines):
	newnetwork = []
	for l in network:
		hit = rayTraceWorld(l[0], l[1], worldLines)
		if hit == None:
			newnetwork.append(l)
	return newnetwork




def astar(init, goal, network):
	path = []
	open = []
	closed = [] #number of nodes it had to expand in the search
	### YOUR CODE GOES BELOW HERE ###
	open.append((0,init))
	# path.append(init)

	came_from = {}
	cost_so_far= {}
	came_from[init] = None
	cost_so_far[init] = 0

	while len(open) != 0:
		current = open.pop(0)[1]
		path.append(current)

		if current == goal:
			break

		for next in neighbors(network, current):
			new_cost = cost_so_far[current] + getDistance(current, next)
			if next not in cost_so_far or new_cost < cost_so_far[next]:
				cost_so_far[next] = new_cost
				open.append((new_cost, next))
				came_from[next] = current
				if next not in closed:
					closed.append(next)

		open = sorted(open, key=lambda, tup=tup[0])

	### YOUR CODE GOES ABOVE HERE ###
	return path, closed

def heuristic(a,b):
	(x1,y1) = a
	(x2,y2) = b
	return abs(x1-x2) + abs(y1-y2)

def neighbors(network, start)
	neighbors = []

	for element in network:
		if element[0] == start:
			neighbors.append[element[0]]
		elif element[1] == start:
			neighbors.append[element[1]]

	return neighbors	


def myUpdate(nav, delta):
	### YOUR CODE GOES BELOW HERE ###
	start = nav.getSource()
	dest = nav.getDestination()
	old_path = nav.getPath()

	#check for a new walkable path network
	newnetwork = unobstructedNetwork(self.pathnetwork, nav.world.getGates())				
	new_path, new_closed = astar(start, dest, newnetwork)
	if new_path != [] and old_path != new_path:
		nav.setPath(new_path)
	### YOUR CODE GOES ABOVE HERE ###
	# return None



def myCheckpoint(nav):
	### YOUR CODE GOES BELOW HERE ###
# check the next immediate node
	gates = nav.world.getGates()
	start = nav.getSource()
	dest = nav.getDestination()
	path = nav.getPath()

	for p in xrange(len(path)):
		if p < len(path):
			path_line = (path[p], path[p+1])
			if rayTraceWorld(path[p], path[p+1], gates) != None:
				newnetwork = unobstructedNetwork(self.pathnetwork, gates)				
				new_path, new_closed = astar(start, dest, newnetwork)
				if new_path == []:
					self.agent.stopMoving()
				else:
					nav.setPath(new_path)
	### YOUR CODE GOES ABOVE HERE ###
	# return None


### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
	### YOUR CODE GOES BELOW HERE ###
	#use old clear shot?
	# update to account for lines from the gates as well
	### YOUR CODE GOES ABOVE HERE ###
	clear = True
    line = (p1,p2)
    #does it collide with the world lines
    if rayTraceWorld(p1,p2,worldLines) != None: #doesn't collide with the obstacle lines
        return False
    minD = INFINITY
    for i in xrange(len(worldPoints)):
        test_p = worldPoints[i]
        min_d = minimumDistance(line, test_p)
        if min_d < minD:
            minD = min_d
    if minD < (agent.maxradius):
        # print minD
        return False
    else:
        return clear



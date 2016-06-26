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
                    # print len(self.pathnetwork)
                    newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
                    # print len(newnetwork)
                    closedlist = []
                    path, closedlist = astar(start, end, newnetwork)
                    # for i in path:
                    #     drawCross(self.world.debug, i)
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
    full_cost = {}
    for line in network:
        for x,y in line:
            # print x,y
            if x not in cost_so_far.keys():
                cost_so_far[x] = INFINITY
                full_cost[x] = INFINITY
            if y not in cost_so_far.keys():
                cost_so_far[y] = INFINITY
                full_cost[y] = INFINITY
    
    came_from[init] = None
    cost_so_far[init] = 0
    # print came_from
    while len(open) != 0:
        current = open[0][1]
        # print 'current node is ' + str(current)
        # print 'loaded current into the path ' + str(path)
        if current == goal:
            # print 'reached goal'
            # print reconstructPath(came_from, closed, goal)
            break
        open.pop(0)
        closed.append(current)

        for next_node in neighbors(network, current):
            # print type(cost_so_far[current])
            # print type(distance(current, next_node))
            # print 'in loop'
            if next_node in closed:
                continue #already evaluated
            score = cost_so_far[current] + distance(current, next_node) #+ distance(current, next_node)
            score_extra = score + distance(goal,next_node)

            if next_node not in open:
                open.append((score_extra,next_node))
            elif score >= cost_so_far[next_node]:
                continue
            came_from[next_node] = current
            cost_so_far[next_node] = score
            full_cost[next_node] = score_extra
            # closed.append(next_node)

        open = sorted(open, key=lambda dist:dist[0])
        print open

    obj = goal
    # print came_from
    path.append(goal)
    while obj in came_from.keys():
        obj = came_from[obj]
        if obj != None:
            path.append(obj)
    path.reverse()
    if obj != None:
        return [], closed

    # while obj != init:
    #     if obj in came_from.keys() and came_from[obj] != None:
    #         print 'the nodes path looking at is ' + str(obj) 
    #         print 'and i came from ' + str(came_from[obj])
            # path.append(came_from[obj])
    #         obj = came_from[obj]
    #     else:
    #         print 'no path'
    #         return [], closed
    # # path.append(init)
    # path.reverse()
    # print 'this was my init' + str(init)
    # print 'this is my goal ' + str(goal)
    # print 'this is the path found'+str(path)
    # print closed
    ### YOUR CODE GOES ABOVE HERE ###
    return path, closed

def reconstructPath(came_from, closed, goal):
    path = [goal]
    while goal in came_from.keys():
        goal = came_from[goal]
        if goal != None:
            path.append(goal)
    path.reverse()

    return path, closed


def heuristic(a,b):
    (x1,y1) = a
    (x2,y2) = b
    return abs(x1-x2) + abs(y1-y2)

def neighbors(network, start):
    neighbors = []
    # print start
    # print 'this is the network' + str(network)
    for line in network:
        # print line
        if line[0] == start:
            neighbors.append(line[1])
        elif line[1] == start:
            neighbors.append(line[0])
    # print 'these are the neighbors' + str(neighbors)
    return neighbors    


def myUpdate(nav, delta):
    ### YOUR CODE GOES BELOW HERE ###
    start = nav.getSource()
    dest = nav.getDestination()
    old_path = nav.getPath()
    world = nav.world
    worldLines = world.getLines()
    worldPoints = world.getPoints()
    agent = nav.agent 

    # print old_path
    #check for a new walkable path network
    # print start
    # print dest
    # print worldLines
    # print worldPoints

    if start != None and dest != None and clearShot(start, dest, worldLines, worldPoints, agent):
        nav.setPath(None)
        nav.agent.moveToTarget(dest)
        # print ' just going for it'
    # else:
    #     newnetwork = unobstructedNetwork(nav.pathnetwork, nav.world.getGates())                
    #     new_path, new_closed = astar(start, dest, newnetwork)
    #     if new_path != [] and old_path != new_path:
    #         nav.setPath(new_path)
        ### YOUR CODE GOES ABOVE HERE ###
    return None



def myCheckpoint(nav):
    ### YOUR CODE GOES BELOW HERE ###
# check the next immediate node
    gates = nav.world.getGates()
    start = nav.getSource()
    dest = nav.getDestination()
    path = nav.getPath()
    loc = nav.agent.getLocation()

    # print 'my real location is ' + str(loc)
    for p in xrange(len(path)):
        if p+1 < len(path):
            path_line = (path[p], path[p+1])
            if rayTraceWorld(path[p], path[p+1], gates) != None:
                # print 'tried mycheckpoint'
                newnetwork = unobstructedNetwork(nav.pathnetwork, gates)  
                # print 'CKPNT my start is this ' + str(loc)
                # print 'CKPNT my goal is this ' + str(dest)             
                new_path, new_closed = astar(loc, dest, newnetwork)
                if new_path == []:
                    nav.agent.stopMoving()
                    nav.setPath(None)
                else:
                    # print 'CKPNT this is the old path ' + str(path)
                    # print 'CKPNT this is the new path ' + str(new_path)
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
        # print 'theres a clear shot'
        return clear



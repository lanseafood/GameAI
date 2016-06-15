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
### APSPNavigator
###
### Creates a path node network and implements the FloydWarshall all-pairs shortest-path algorithm to create a path to the given destination.
            
class APSPNavigator(NavMeshNavigator):

    ### next: indicates which node to traverse to next to get to a given destination. A dictionary of dictionaries such that next[p1][p2] tells you where to go if you are at p1 and want to go to p2
    ### dist: the distance matrix. A dictionary of dictionaries such that dist[p1][p2] tells you how far from p1 to p2.

    def __init__(self):
        NavMeshNavigator.__init__(self)
        self.next = None
        self.dist = None
        

    ### Create the pathnode network and pre-compute all shortest paths along the network.
    ### self: the navigator object
    ### world: the world object
    def createPathNetwork(self, world):
        self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
        self.next, self.dist = APSP(self.pathnodes, self.pathnetwork)
        return None
        
    ### Finds the shortest path from the source to the destination.
    ### self: the navigator object
    ### source: the place the agent is starting from (i.e., it's current location)
    ### dest: the place the agent is told to go to
    def computePath(self, source, dest):
        ### Make sure the next and dist matricies exist
        if self.agent != None and self.world != None and self.next != None and self.dist != None: 
            self.source = source
            self.destination = dest
            if clearShot(source, dest, self.world.getLinesWithoutBorders(), self.world.getPoints(), self.agent):
                self.agent.moveToTarget(dest)
            else:
                start = findClosestUnobstructed(source, self.pathnodes, self.world.getLines())
                end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLines())
                if start != None and end != None and start in self.dist and end in self.dist[start] and self.dist[start][end] < INFINITY:
                    path = findPath(start, end, self.next)
                    path = shortcutPath(source, dest, path, self.world, self.agent)
                    self.setPath(path)
                    if len(self.path) > 0:
                        first = self.path.pop(0)
                        self.agent.moveToTarget(first)
        return None

    ### This function gets called by the agent to figure out if some shortcutes can be taken when traversing the path.
    ### This function should update the path and return True if the path was updated.
    def smooth(self):
        return mySmooth(self)










### Returns a path as a list of points in the form (x, y)
### start: the start node, one of the nodes in the path network
### end: the end node, one of the nodes in the path network
### next: the matrix of next nodes such that next[p1][p2] tells where to go next
def findPath(start, end, next):
    path = []
    ### YOUR CODE GOES BELOW HERE ###
    if next[start][end] == None:
        return path
    path.append(start)
    next_node = start
    while next[next_node][end] != end:
        if next[next_node][end] == None:
            return []
        else:
            next_node = next[next_node][end]
            path.append(next_node)
    print path
    ### YOUR CODE GOES ABOVE HERE ###
    return path




    
def APSP(nodes, edges):
    dist = {} # a dictionary of dictionaries. dist[p1][p2] will give you the distance.
    next = {} # a dictionary of dictionaries. next[p1][p2] will give you the next node to go to, or None
    for n in nodes:
        next[n] = {}
        dist[n] = {}
    ### YOUR CODE GOES BELOW HERE ###
    # print 'nothing in here right now'
    # print next
    # print dist

    #adding in distances for all the edges into dist matrix
    for e in edges:
        source = e[0]
        sink = e[1]
        dist[source][sink] = distance(source,sink)
        dist[sink][source] = distance(source,sink)
        next[source][sink] = sink
        next[sink][source] = source
    # print 'added in all the distances'
    # print next
    # print dist

    #checking if there is none, then it's a INF
    for f in nodes:
        for t in nodes:
            if f == t:
                dist[f][t] = INFINITY
                # next[f][t] = None
            else:
                if t not in dist[f].keys():
                    dist[f][t] = INFINITY
                    dist[t][f] = INFINITY
                if t not in next[f].keys():
                    next[f][t] = None
                    next[t][f] = None
    # print 'udpated for those that should be inf'
    # print dist

    #updating the matrix
    for k in range(len(nodes)):
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                intermediate = nodes[k]
                start = nodes[i]
                end = nodes[j]

                if dist[start][intermediate] + dist[intermediate][end] < dist[start][end]:
                    dist[start][end] = dist[start][intermediate] + dist[intermediate][end]
                    next[start][end] = next[start][intermediate]
    # print 'updated to the best path distances'
    # print dist
    # print next 
    #testing
    # print 'number of nodes reachable ' + str(len(nodes))
    # print 'total items in matrix ' + str(len(nodes)*len(nodes))
    # count = 0
    # for n in nodes:
    #     for p in nodes:
    #         if p not in next[n].keys():
    #             count = count + 1
    # print count 
    ### YOUR CODE GOES ABOVE HERE ###
    return next, dist


### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
    ### YOUR CODE GOES BELOW HERE ###
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
        # print minD
# line = (p1,p2)
# for i in xrange(len(worldPoints)): #doesn't collide with the obstacle corners
#     for j in xrange(i+1, len(worldPoints)):
#         point = worldPoints[i]
#         next_point = worldPoints[j]
#         if rayTrace(point, next_point, line) != None:
#             return False
        return clear


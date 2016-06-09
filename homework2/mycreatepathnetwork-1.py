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

def lineOnAnObstacle(p1, p2, obstacle_lines):
    if (p1,p2) not in obstacle_lines and (p2,p1) not in obstacle_lines:
        return True #true, not a line of an obstacle
    else:
        return False

def canMakeTriangle(p1,p2,p3,obstacle_lines):
    if (((rayTraceWorldNoEndPoints(p1, p3, obstacle_lines) != None) and ((p1, p3) not in obstacle_lines) or ((p3, p1) not in obstacle_lines)) or ((rayTraceWorldNoEndPoints(p2, p3, obstacle_lines) != None) or ((p2, p3) not in obstacle_lines) or ((p3, p2) not in obstacle_lines))):
        return True
    else:
        return False

def obstacleInTriangle(p, triangle_points):
    if pointInsidePolygonPoints(p, temp_triangle_points) and p not in temp_triangle_points:
        return True
    else:
        return False
def triangleInOb(m1, m2, m3,p1,p2,p3, ob, all_obstacle_lines):
    if (pointInsidePolygonPoints(m1, ob) and not lineOnAnObstacle(p1,p2,all_obstacle_lines)) or (pointInsidePolygonPoints(m2, ob) and not lineOnAnObstacle(p1,p3,all_obstacle_lines)) or (pointInsidePolygonPoints(m3, ob) and not lineOnAnObstacle(p2,p3,all_obstacle_lines)):
        return True
    else:
        return False

def findMidpoint(p1,p2):
    return ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)

def makeInitTriangles(world):
    world_points = world.getPoints()
    obstacles = world.getObstacles()
    all_obstacle_lines = world.getLinesWithoutBorders()

    all_obstacle_points = [] # all points of every obstacle, (x,y)
    for o in obstacles:
        all_obstacle_points.append(o.getPoints())

    triangles = []
    triangle_lines = []

    for p1_index in xrange(len(possible_points)):
        for p2_index in xrange(p1+1, len(possible_points)):

            # print 'checking point ' + str(p2)
            if p1_index != p2_index:
                p1 = possible_points[p1_index] #point 1
                p2 = possible_points[p2_index] #point 2
                # print 'p1 is ' + str(p1)
                # print 'p2 is' + str(p2)

                #CHECK THE LINE OF THE POINTS IS VALID
                # NOT AN OBSTACLE LINE ITSELF. 
                if (rayTraceWorldNoEndPoints(p1, p2, all_obstacle_lines) == None) or ((p1, p2) in all_obstacle_lines) or ((p2, p1) in all_obstacle_lines): 
                    break

                for p3_index in xrange(p1+2, len(possible_points)):
                    if p3_index != p1_index and p3_index != p2_index:
                        p3 = possible_points[p3_index] #point 3
                        #CHECK THE LINES OF THE POINTS IS VALID
                        #NOT AN OBSTACLE LINE ITSELF. 
                        if canMakeTriangle(p1,p2,p3,all_obstacle_lines):

                            triangle_valid = False

                            m1 = findMidpoint(p1,p2)
                            m2 = findMidpoint(p1,p3)
                            m3 = findMidpoint(p2,p3)

                            temp_triangle_points = [p1,p2,p3]

                            for ob in all_obstacle_points:
                                for ob_point in ob:
                                    if obstacleInTriangle(ob_point,temp_triangle_points):
                                        triangle_valid = True
                                        break

                                if triangleInOb(m1, m2, m3,p1,p2,p3, ob, all_obstacle_lines):
                                    triangle_valid = True
                                    break

                            triangle_center = ((p1[0]+p2[0]+p3[0])/3, (p1[1]+p2[1]+p3[0])/3)

                            for o in obstacles:
                                if o.pointInside(triangle_center):
                                    triangle_valid = True

                            if triangle_valid:
                                all_obstacle_lines.append((p1,p2))
                                all_obstacle_lines.append((p2,p3))
                                all_obstacle_lines.append((p1,p3))

                                triangles.append(temp_triangle_points)
                                triangle_lines.append((p1,p2))
                                triangle_lines.append((p2,p3))
                                triangle_lines.append((p1,p3))

                                all_obstacle_points.append(temp_triangle_points)

        return all_obstacle_lines, all_obstacle_points, triangles, triangleLines



# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
    nodes = [] #list of path nodes
    edges = [] #list of edges between path nodes
    polys = [] #list of hulls (list of list of nodes)

    # agent_size = agent.getMaxRadius()

    # #TRYING TO FIND THE TRIANGLES

    # obstacles = world.getObstacles()

    # all_obstacle_lines = world.getLinesWithoutBorders()
    # # o_points = world.getObstacles.getPoints()

    # # length,width = world.getDimensions()
    # # corners = [(0,0),(length,0),(length, width),(0,width)]
    # # possible_points = []
    # possible_points = world.getPoints() #all potential points for draw convex things to. 
    # all_obstacle_points = [] # all points of every obstacle, list of lists
    # for o in obstacles:
    #     all_obstacle_points.append(o.getPoints())

    # # all_obstacle_lines= [((0,0),(length,0)), ((length,0),(length, width)),((length, width),(0,width)), ((0,0), (0,width))] #including from corner to corner
    # # all_obstacle_lines= []
    # poly_dict = {} #key is poly, returns list of edges
    # all_reachable_points = {} #key is point, returns list of points reachable points

    # # print all_obstacle_lines
    # print possible_points
    # # print 'the length of possible points to cover is ' + str(len(possible_points))


       
    #find all triangles
    # for point in possible_points: #specific point
    #     list_of_points = all_reachable_points[point]
    #     for q in range(len(list_of_points)): #all connected poitns
    #         for w in range(q+1, len(list_of_points)): #in order

    #             p = list_of_points[q]
    #             r = list_of_points[w]
    #             print 'point is ' + str(point)
    #             print 'first option is ' + str(p)
    #             print 'second opetion is ' + str(r) 
    #             # r = random.choice(poss_points)
    #             print rayTraceWorldNoEndPoints(p,r, all_obstacle_lines)
    #             if p != r and isConvex([point, p, r]) and rayTraceWorldNoEndPoints(p,r, all_obstacle_lines) == None and rayTraceWorldNoEndPoints(point, p, all_obstacle_lines) == None and rayTraceWorldNoEndPoints(point, r, all_obstacle_lines) == None:
    #             # if p != r:
    #                 if (point,p) not in all_obstacle_lines or (p,point) not in all_obstacle_lines:
    #                     # print 'old' + str(all_obstacle_lines)
    #                     all_obstacle_lines.append((point,p)) 
    #                     all_obstacle_lines.append((p,point))  
    #                     # print 'new ' + str(all_obstacle_lines)           
    #                     print 'added 1st'
    #                 if (p,r) not in all_obstacle_lines or (r, p) not in all_obstacle_lines:
    #                     all_obstacle_lines.append((p,r))
    #                     all_obstacle_lines.append((r,p))
    #                     print 'added 2nd'
    #                 if (point,r) not in all_obstacle_lines or (r,point) not in all_obstacle_lines:
    #                     all_obstacle_lines.append((point,r))
    #                     all_obstacle_lines.append((r, point))
    #                     print 'added 3rd'

    #                 polys.append([point, p, r])
    #             # else:
    #             #     if p != r and isConvex([point, p, r]):
    #             #         try_ = [point, p, r]
    #             #         for pol in polys:
    #             #             if pol != try_ and polygonsAdjacent(pol,try_) != False:
    #             #                 polys.append([point, p, r])
    #             #                 break
    #             #     else:
    #             #         print 'NOPE'
    # print len(polys)
    #reduce number of triangles:
    # temp_p = polys
    # for p in polys:
    #     for p_ in polys:
    #         if p != p_ and polygonsAdjacent(p,p_) == False:
    #             if p in temp_p:
    #                 temp_p.remove(p)

    # polys = temp_p
    # print len(polys)

    # print polys
    #finding triangles for each obstacle point
    # for o in obstacles:
    #     points = o.getPoints()
    #     lines = o.getLines()
    #     for p in points:
    #         # temp_hull = [p]
    #         reacheable_points=[p]
    #         corner_points = []
    #         poly = []
    #         for c in corners:
    #             if rayTraceWorld(p, c, all_obstacle_lines) == None: #no collisions!
    #                 reacheable_points.append(c)
    #                 corner_points.append(c)
    #                 poly.append((p,c))
    #                 all_obstacle_lines.append((p,c))
    #         # getting lines between corners


    #         if isConvex(reacheable_points):
    #             polys.append(reacheable_points)


    # print points_grid
    #find all possible lines of all obstacles:
    # for node in range(len(points_grid)): #getting indexes
    #     lines = []
    #     for nextNode in range(node +1, len(points_grid)):
    #         p1 = possible_points[node]
    #         p2 = possible_points[nextNode]
    #         # print p1,p2
    #         # p_line = (p,potential)
    #         # for l in all_obstacle_lines:
    #         if rayTraceWorld(p1, p2, all_obstacle_lines) == None: #no collisions!
    #             lines.append((p1,p2))
    #             all_obstacle_lines.append((p1,p2))
    #             points_grid[node][nextNode] = 1
    #             hull_lines.append((p1,p2)) #all possible hull lines
    #     if len(lines) >= 3 and isConvex(lines):
    #         polys.append(lines)
    #     # else:
    #         divide into triangles

    #converge triangles to >3 edges




#PART 2,3 NEED TO FIX CENTROID
    #make pathnodes

    #for each triangle
    # for poly in polys: #poly is a list of points
    #     tot_x = 0
    #     tot_y = 0
    #     for point in poly: #point (x, y)
    #         #check for repeats
    #         if point not in nodes:         #add node into pathnode
    #             nodes.append(point + agent_size)
    #             tot_x += point[0] #FIX THIS CENTROID SHIT
    #             tot_y += point[1]

    #     # find center of each triangle
    #     centroid = (tot_x/len(poly), tot_y/len(poly))
    #     nodes.append(centroid)
    # #make edges
    #     #find midpoints of edges
    #     # midpoints = []
    #     for lines in poly_dict[poly]:
    #         for line in lines:
    #             midpoint = (int(math.ceil(line[0]/2)), int(math.ceil(line[1]/2)))
    #             # midpoints.append(midpoint)
    #             nodes.append(midpoint)
    #             edges.append((midpoint,centroid)) #add lines between each midpoint and center
    #             #add line between each endpoint and midpoint
    #             edges.append((line[0], midpoint))
    #             edges.append((midpoint, line[1]))

    #     for point in poly:        #add lines between each pathnode and the center
    #         edges.append((point,centroid))

    ### YOUR CODE GOES ABOVE HERE ###
    return nodes, edges, polys

    

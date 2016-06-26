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
from random import shuffle

def lineOnAnObstacle(p1, p2, obstacle_lines):
    if (p1,p2) not in obstacle_lines and (p2,p1) not in obstacle_lines:
        return False 
    else:
        return True

def cantMakeTriangle(p1,p2,p3,obstacle_lines):
    if (((rayTraceWorldNoEndPoints(p2, p3, obstacle_lines) != None) and ((p2, p3) not in obstacle_lines) and ((p3, p2) not in obstacle_lines)) or ((rayTraceWorldNoEndPoints(p3, p1, obstacle_lines) != None) and ((p3, p1) not in obstacle_lines) and ((p1, p3) not in obstacle_lines))):
        return True
    else:
        return False

def obstacleInTriangle(p, triangle_points):
    if pointInsidePolygonPoints(p, triangle_points) and p not in triangle_points:
        return True
    else:
        return False

def triangleInOb(m1, m2, m3,p1,p2,p3, ob, all_obstacle_lines):
    if (pointInsidePolygonPoints(m1, ob) and not lineOnAnObstacle(p1,p2,all_obstacle_lines)) or (pointInsidePolygonPoints(m2, ob) and not lineOnAnObstacle(p2,p3,all_obstacle_lines)) or (pointInsidePolygonPoints(m3, ob) and not lineOnAnObstacle(p3,p1,all_obstacle_lines)):
        return True
    else:
        return False

def findMidpoint(p1,p2):
    return ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)

def createTriangles(world): #lanssie
    possible_points = world.getPoints()
    obstacles = world.getObstacles()
    all_obstacle_lines = world.getLinesWithoutBorders()

    all_obstacle_points = [] # all points of every obstacle, (x,y)
    for o in obstacles:
        all_obstacle_points.append(o.getPoints())

    triangles = []

    for p1_index in xrange(len(possible_points)):
        for p2_index in xrange(p1_index+1, len(possible_points)):

            # print 'checking point ' + str(p2)
            if p1_index != p2_index:
                p1 = possible_points[p1_index] #point 1
                p2 = possible_points[p2_index] #point 2

                #CHECK THE LINE OF THE POINTS IS VALID
                if (rayTraceWorldNoEndPoints(p1, p2, all_obstacle_lines) != None) and ((p1, p2) not in all_obstacle_lines) and ((p2, p1) not in all_obstacle_lines): 
                    # print 'moving on from these'
                    continue

                for p3_index in xrange(p2_index+1, len(possible_points)):
                    if p3_index != p1_index and p3_index != p2_index:
                        p3 = possible_points[p3_index] #point 3
                        # print 'lookings at points ' + str(p1) + ' and ' + str(p2)+ ' and ' + str(p3) 
                        #CHECK THE LINES OF THE POINTS IS VALID
                        #NOT AN OBSTACLE LINE ITSELF. 
                        if cantMakeTriangle(p1,p2,p3,all_obstacle_lines):
                            # print 'moving on because cant make triangle'
                            continue

                        triangle_wrong = False

                        m1 = findMidpoint(p1,p2)
                        m2 = findMidpoint(p2,p3)
                        m3 = findMidpoint(p3,p1)
                        # print 'the midpoints are' + str(m1) + ' ' + str(m2) + ' ' + str(m3)
                        temp_triangle_points = [p1,p2,p3]
                        # print 'temp triangle is this ' + str(temp_triangle_points)

                        for ob in all_obstacle_points:
                            for ob_point in ob:
                                if obstacleInTriangle(ob_point,temp_triangle_points):
                                    triangle_wrong = True
                                    # print 'ob in triangle'
                                    break

                            if triangleInOb(m1, m2, m3,p1,p2,p3, ob, all_obstacle_lines):
                                # print 'triangle in ob'
                                triangle_wrong = True
                                break
                        
                        triangle_center = ((p1[0]+p2[0]+p3[0])/3, (p1[1]+p2[1]+p3[1])/3)
                        # print triangle_center

                        for o in obstacles:
                            if o.pointInside(triangle_center):
                                # print 'triangle point inside'
                                # print o.getPoints()
                                triangle_wrong = True
                                break

                        if triangle_wrong:
                            continue

                        # print 'APPENDED' + str(temp_triangle_points)
                        all_obstacle_lines.append((p1,p2))
                        all_obstacle_lines.append((p2,p3))
                        all_obstacle_lines.append((p3,p1))

                        triangles.append(temp_triangle_points)

                        # all_obstacle_points.append(temp_triangle_points)

    return triangles


#orders polygons points to be cloclwise
def orderPoints(polygon):
    x=0
    y=0
    for p in polygon:
        x += p[0]
        y += p[1]
    x /= len(polygon)
    y /= len(polygon)

    centroid=(x,y)

    a=[]
    for p in polygon:
        a1=math.atan2(p[1]-centroid[1],p[0]-centroid[0])
        a.append(a1)

    for i in range(len(polygon)-1):
        for j in range(len(polygon)-1-i):
            if a[j] > a[j+1]:
                t = a[j]
                a[j] = a[j+1]
                a[j+1] = t
                t = polygon[j]
                polygon[j] = polygon[j+1]
                polygon[j+1] = t

    return polygon

#merge polys
def merge(world, polygons):
    for p1 in xrange(len(polygons)):
        for p2 in xrange(p1+1, len(polygons)):
            points = polygonsAdjacent(polygons[p1], polygons[p2])
            if points != False : #if so, construct newPolygon
                newPolygon = polygons[p1]+polygons[p2]
                newPolygon = list(set(newPolygon))#remove duplicates
                newPolygon = orderPoints(newPolygon) #order points in CW 

                if isConvex(newPolygon):
                    polygons.pop(p2)
                    polygons.pop(p1)
                    polygons.append(newPolygon)
                    return True, polygons                   

    return False, polygons

#finds waypoints
def findWaypoints(polygons, world):
    midpoints = []
    all_points = []
    centroids = {} #key is the poly, result is centroid
    
    #adjoining edges:
    for p1 in xrange(len(polygons)):
        for p2 in xrange(p1+1, len(polygons)):
            share_points = polygonsAdjacent(polygons[p1], polygons[p2])
            if share_points != False:
                head = share_points[0]
                tail = share_points[1]
                mid = findMidpoint(head,tail)
                # print 'this is the mid of points'
                # print mid
                if mid not in midpoints:
                    midpoints.append(mid)
                    all_points.append(mid)
    
    #centroids
    for poly in polygons: #poly is a list of points
        # print pols
        tot_x = 0
        tot_y = 0
        for point in poly: #point (x, y)
            tot_x += point[0] 
            tot_y += point[1]
        # find center of each triangle
        centroid = (tot_x/len(poly), tot_y/len(poly))
        centroids[centroid] = poly
        all_points.append(centroid)
        # waypoints.append(centroid)

    return all_points, midpoints, centroids

#find pathnetwork
def findPaths(midpoints, polygons, centroids, world):
    lines = []
    obstaclePoints = world.getPoints()

    radius = world.getAgent().maxradius
    reachable = [] #all the reachable waypoints

    for key in centroids.keys():
        for node in midpoints:
            if key != node: #and node in obstaclePoints
                for poly in polygons:
                    if (pointOnPolygon(node,poly) and pointInsidePolygonPoints(key, poly)):
                        line = (key,node)
                        if line not in lines:
                            lines.append(line)
    
    for line in lines:
        smallest = 100000.0
        for op in obstaclePoints:
            if minimumDistance(line,op) < smallest:
                smallest = minimumDistance(line,op)
        if smallest > radius:
            reachable.append(line)

    return reachable

# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
    nodes = []
    edges = []
    polys = []
    ### YOUR CODE GOES BELOW HERE ###

    #get triangles
    polygons = createTriangles(world)

    #merge triangles:
    canMerge = True
    while(canMerge):
        canMerge, polys = merge(world, polygons)


    #get waypoints:
    nodes, midpoints, centroids = findWaypoints(polys, world)

    #get path edges:
    edges = findPaths(midpoints, polys, centroids, world)


    ### YOUR CODE GOES ABOVE HERE ###
    return nodes, edges, polys

    

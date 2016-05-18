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
from itertools import *

# Creates a grid as a 2D array of True/False values (True = 1 =  traversable). Also returns the dimensions of the grid as a (columns, rows) list.
def myCreateGrid(world, cellsize):
	grid = None
	dimensions = (0, 0)
	### YOUR CODE GOES BELOW HERE ###

	#getting world dimensions
	x,y = world.getDimensions()
	dimensions = (int(math.ceil(x/cellsize)), int(math.ceil(y/cellsize)))

	#building grid with all true so far
	grid = numpy.ones(dimensions, dtype=bool)
	# print grid

	#denotating where you can and can't traverse
	obstacles = world.getObstacles()
	# print obstacles

	#marking all the obstacle's points as false
	for o in obstacles:
		points = o.getPoints()
		for p in points:
			r = int(p[0]/cellsize)
			c = int(p[1]/cellsize)
			grid[r][c] = False

	# marking all points inside obstacle and lines as False
	for row in xrange(dimensions[0]):
		for col in xrange(dimensions[1]):
			x1 = int(row * cellsize)
			y1 = col * cellsize
			x2 = (row+1) * cellsize
			y2 = (col+1) * cellsize

			box = [(x1,y1), (x1,y2), (x2, y1), (x2, y2)] #the grid we are checking

			for o in obstacles:
				for corners in box:
					if o.pointInside(corners):
						grid[row][col] = False
						break
				#making sure the lines are taken care of
				lines = o.getLines()
				for v in xrange(0,3):
					if v < 3:
						if rayTraceWorld(box[v], box[v+1], lines) != None:
							grid[row][col] = False
							break
					else:
						if rayTraceWorld(box[v], box[0], lines) != None:
							grid[row][col] = False
							break
	### YOUR CODE GOES ABOVE HERE ###
	return grid, dimensions


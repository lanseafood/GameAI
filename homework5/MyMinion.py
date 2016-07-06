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
from moba import *

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###

		self.states.append(Move)
		self.states.append(Attack)
		# self.start()
		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)

	def findClosestObj(self,objects, current_location):
		closest = None
		minD = INFINITY
		for obj in objects:
			# print 'this is the object in the loop' + str(obj)
			if closest == None or distance(obj.getLocation(), current_location) < minD:
				minD = distance(obj.getLocation(), current_location)
				closest = obj
		# print 'this is the closest obj' + str(closest)
		return closest



############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		#check if there are towers
		world = self.agent.world
		team = self.agent.team
		own_location = self.agent.getLocation()
		target = None

		if len(world.getEnemyTowers(team)) > 0: #attack towers
			target = self.findClosestObj(world.getEnemyTowers(team), own_location)
		elif len(world.getEnemyBases(team)) > 0: #attack enemy base
			target = self.findClosestObj(world.getEnemyBases(team), own_location)
		elif len(world.getEnemyNPCs(team)) > 0: #attack enemy minions
			target = self.findClosestObj(world.getEnemyNPCs(team), own_location)
		else:
			print ' nothing exists lol'
			self.agent.stopMoving()
			return None
		# self.agent.changeState(Taunt, 'test this')
		# print 'this is the known target' + str(target)
		self.agent.changeState(Move, target)

		#what state are we in?
		### YOUR CODE GOES ABOVE HERE ###
		return None

	def findClosestObj(self,objects, current_location):
		closest = None
		minD = INFINITY
		for obj in objects:
			# print 'this is the object in the loop' + str(obj)
			if closest == None or distance(obj.getLocation(), current_location) < minD:
				minD = distance(obj.getLocation(), current_location)
				closest = obj
		# print 'this is the closest obj' + str(closest)
		return closest	
##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print "Hey " + str(self.victim) + ", I don't like you!"
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

class Move(State):

	def parseArgs(self, args):
		# print 'what dafuq r args' + str(args)
		# print args[0]
		self.target = args[0]
		self.target_location = self.target.getLocation()
		print self.target

	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving

		if self.target:
			if distance(self.agent.getLocation(), self.target_location) > BULLETRANGE:
				self.agent.navigateTo(self.target_location)
				print self.target_location
				print 'moving to my target!!'
			else:
				# self.agent.stopMoving()
				self.agent.turnToFace(self.target_location)
				self.agent.changeState(Attack, self.target)
				print 'im gonna fireeee'
	
	def exit(self):
		return None

	def execute(self, delta = 0):
		# State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		if self.target and self.target.getHitpoints() < 1:
			self.agent.changeState(Idle)
			print 'i moved back to idle from MOVE'
		# else:

		#shoot things on the way:
		#only if the target is farther away
		target_npc = self.findClosestNPC(self.agent.world.getEnemyNPCs(self.agent.team), self.agent.getLocation())
		dist_btwn_self_and_closest_enemy = distance(self.agent.getLocation(), target_npc.getLocation())

		dist_btwn_self_and_actual_target = distance(self.agent.getLocation(), self.target_location)

		if dist_btwn_self_and_closest_enemy <= BULLETRANGE and dist_btwn_self_and_actual_target > BULLETRANGE:
			self.agent.turnToFace(target_npc.getLocation())
			self.agent.shoot()
		if self.agent.navigator.path == None and dist_btwn_self_and_actual_target > BULLETRANGE:
			self.agent.navigateTo(self.target_location)
		if self.target and dist_btwn_self_and_actual_target <= BULLETRANGE:
			self.agent.stopMoving()
			self.agent.turnToFace(self.target_location)
			self.agent.shoot()

		print 'my path is ' + str(self.agent.navigator.path)

		### YOUR CODE GOES ABOVE HERE ###
		return None

	def findClosestNPC(self,objects, current_location):
		closest = None
		minD = INFINITY
		for obj in objects:
			# print 'this is the object in the loop' + str(obj)
			if closest == None or distance(obj.getLocation(), current_location) < minD:
				minD = distance(obj.getLocation(), current_location)
				closest = obj
		# print 'this is the closest obj' + str(closest)
		return closest	

class Attack(State):

	def parseArgs(self, args):
		self.target = args[0]
		self.target_location = self.target.getLocation()

	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		# self.agent.stopMoving()
		self.agent.shoot()

	def exit(self):
		return None
	
	def execute(self, delta = 0):
		# State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		if self.target.getHitpoints() < 1:
			self.agent.changeState(Idle)
			print 'im going back to idle from attack'
			return None
		self.agent.turnToFace(self.target_location)
		self.agent.shoot()


		### YOUR CODE GOES ABOVE HERE ###
		# return None



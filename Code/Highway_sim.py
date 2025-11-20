"""Simulating the bevahior of the cars in the Simulation"""

import random
from Highway_animation import Animation
from matplotlib.patches import Rectangle
import numpy as np


class Car:
	"""Keeps track of the variables and constants of an individual car"""

	def __init__(self, max_speed:float, car_length:float, color="red", 
			  car_width:float=0.6, time_rule:float=3, max_acceleration:float=3):
		#constant
		self.color = color
		self.max_speed = max_speed #[m/s]
		self.max_acc = max_acceleration #[m/s^2]
		self.time_rule = time_rule #[s]
		self.car_length = car_length
		self.car_width = car_width

		#variables
		self.car_infront = None
		self.car_behind = None
		self.cur_speed = None
		self.cur_pos = None
		self.lane = None
		self.time_since_lane_change = 0
		self.animation_object = None
	

	def change_speed(self, new_speed: float) -> None:
		self._speed = new_speed
	
	def change_pos(self, new_pos: float) -> None:
		self.cur_pos = new_pos
	
	def change_speed(self, new_speed: float) -> None:
		if new_speed >= 0:
			self.cur_speed = new_speed
		else:
			raise ValueError("Negative speed on one car.")
	
	def change_car_infront(self, new_car_infront: "Car") -> None:
		"""Changes which car is infront. """
		self.car_infront = new_car_infront
	
	def change_car_behind(self, new_car_behind: "Car") -> None:
		"""Changes which car is behind. """
		self.car_behind = new_car_behind

	def change_lane(self, new_lane_number:int) -> None:
		"""Changes the lane number of the car. """
		self.lane = new_lane_number

	def change_time_since_lane_change(self, new_time:float) -> None:
		"""Change how long ago a lane change was made. """
		self.time_since_lane_change = new_time

	def get_current_speed(self) -> float:
		return self.cur_speed
	
	def get_max_speed(self) -> float:
		"""Returns the max speed of the car. """
		return self.max_speed

	def get_max_acceleration(self) -> float:
		"""Returns the maximum acceleration of the car. """
		return self.max_acc

	def get_current_pos(self) -> float:
		"""Returns the current position of the car. """
		return self.cur_pos

	def get_current_lane(self) -> int:
		"""Returns the number of the current lane in which the car is in. """
		return self.lane

	def get_car_length(self) -> float:
		"""Returns the length of the car. """
		return self.car_length

	def get_car_infront(self) -> "Car":
		"""Returns the car infront of the car (or None if there is none). """
		return self.car_infront

	def get_car_behind(self) -> "Car":
		"""Returns the car behind of the car (or None if there is none). """
		return self.car_behind

	def get_time_rule(self) -> float:
		"""Returns the time rule [s] of the car. Time rule means how long it takes to reach the car infront \
			if it stood still. """
		return self.time_rule

	def get_car_color(self):
		"""Returns the color of the car. """
		return self.color

	def get_time_since_lane_change(self) -> float:
		"""Returns how long ago the car switched lane. """
		return self.time_since_lane_change

	def add_animation_object(self, animation_object) -> None:
		"""Add the animation object (Rectangle) to the Car object"""
		self.animation_object = animation_object
	
	def update_animation_object(self) -> None:
		"""Updates the animation object if there is one. TODO"""
		if self.animation_object != None:
			self.animation_object.xy = (self.lane + (1 - self.car_width)/2, self.cur_pos)


class Simulation:
	"""Keeps track of the whole simulation and does the calculations for the cars"""

	def __init__(self, road_length:float=100, number_of_lanes:int=1, speed_limit:float=30, 
			  standard_deviation_of_speed:float=1, number_of_cars:int=10, car_length:float=2, time_step:float=0.1):

		#constants
		self.road_length = road_length
		self.number_lanes = number_of_lanes
		self.speed_limit = speed_limit
		self.speed_sd = standard_deviation_of_speed
		self.number_cars = number_of_cars
		self.car_length = car_length
		self.t_step = time_step

		#Check that the cars fit on the road
		if self.road_length*self.number_lanes < self.number_cars*self.car_length:
			raise ValueError("The cars can't fit on the road due to road_length, number_of_lanes, number_of_cars and car_length")

		#variables
		self.list_of_lane_sets = [set() for _ in range(self.number_lanes)] #Creates list of empty sets
		self.t = 0
		self.t_list = []
		self.flowrate = None
		self.flowrate_list = []


	def simulate(self, time:float) -> None: #TODO not finished
		"""Run the simulation. """
		self.__insert_the_cars()
		while self.t < time:
			self.time_step()
		


	def simulate_animate(self) -> None:
		"""Runs the simulation and shows/makes the animation. """
		self.__insert_the_cars()
		self.__create_animation_objects()

		a = Animation(self)
		a.animate_highway()


	def time_step(self) -> None:
		"""Makes one step in time. """
		self.t_list.append(self.t)
		self.flowrate = self.__calc_flowrate()
		self.flowrate_list.append(self.flowrate)
		self.t += self.t_step
		
		car_set = set() #Make another set to do the lane changes (as to not get an error)
		for lane in self.list_of_lane_sets:
			for car in lane:
				car_set.add(car)
		
		for car in car_set: #Change lanes separetly to not get error
			#self.__health_check()
			#Maybe change lane
			if self.__switch_to_right_check(car=car) and car.get_time_since_lane_change() >= 5: #If the car has reached max speed and the right lane is clear
				#self.__health_check()
				self.__insert_car_in_lane(car, car.get_current_lane() + 1, car.get_current_lane())
				car.change_time_since_lane_change(0)
				#self.__health_check()
			elif self.__switch_to_left_check(car=car) and car.get_time_since_lane_change() >= 5: #If there is a cue and it is free to change to the left
				#self.__health_check()
				self.__insert_car_in_lane(car, car.get_current_lane() - 1, car.get_current_lane())
				car.change_time_since_lane_change(0)
				#self.__health_check()
			car.change_time_since_lane_change(car.get_time_since_lane_change() + self.t_step)
			
			#self.__health_check()

		#Do the speed and postition updates
		for lane in self.list_of_lane_sets:
			for car in lane:
				#self.__health_check()

				#Change speed
				self.__update_speed(car)

				#self.__health_check() #Car health check
		
		#Update positions
		for lane in self.list_of_lane_sets:
			for car in lane:
				car_pos = car.get_current_pos()
				
				#self.__health_check()

				#Change position
				car.change_pos((car_pos + car.get_current_speed()*self.t_step)%self.road_length)
				
				#Update animation object
				car.update_animation_object()

				#self.__health_check()


	def __calc_flowrate(self) -> float:
		"""Returns the current flow rate of the simulation. """
		v_tot = 0
		for lane in self.list_of_lane_sets:
			for car in lane:
				v_tot += car.get_current_speed()
		return v_tot / (self.road_length * self.number_lanes)


	def __make_new_car(self) -> Car:
		"""Returns an object from the class Car. """
		color = self.__return_random_color()
		max_speed = self.__make_max_speed()
		return Car(color=color, max_speed=max_speed, car_length=self.car_length, \
			 max_acceleration=4.3)


	def __return_random_color(self) -> str:
		"""Returns a random color. """
		color_list = ["black", "blue", "green", "red", "magenta"]
		rand_i = random.randint(0, len(color_list) -1)
		return color_list[rand_i]


	def __insert_car_in_lane(self, car:Car, lane_number:int, prev_lane:int) -> None: #Need big fixes
		"""Inserts car in correct position in a new lane. """
		#Change lane number
		car.change_lane(lane_number)

		#Store previous adjecent cars
		prev_car_infront = car.get_car_infront()
		prev_car_behind = car.get_car_behind()
		
		#Get new car infront and behind
		car_behind, car_infront = self.__get_car_infront_and_behind_for_any_lane(car=car, lane_number=lane_number)
		
		#Change to new car infront
		car.change_car_infront(car_infront)
		if car_infront != None: #If the car doesnt go to an empty lane
			car_infront.change_car_behind(car)

		#Change to new car behind
		car.change_car_behind(car_behind)
		if car_behind != None: #If the car doesnt go to an empty lane
			car_behind.change_car_infront(car)

		#Edit lane sets
		self.list_of_lane_sets[lane_number].add(car)
		self.list_of_lane_sets[prev_lane].remove(car)

		#Edit in the previous lane
		if prev_car_infront != None: #If it wasn't by itself in last lane
			if prev_car_infront == prev_car_behind: #If it's only car left
				prev_car_behind.change_car_infront(None)
				prev_car_infront.change_car_behind(None)
			else:
				prev_car_behind.change_car_infront(prev_car_infront)
				prev_car_infront.change_car_behind(prev_car_behind)
		
		#self.__health_check()


	def __get_car_infront_and_behind_for_any_lane(self, car:Car, lane_number:int) -> tuple[Car]:
		"""Returns car behind, car infront for a given car if it were in a certain lane. """
		car_pos = car.get_current_pos()
		car_infront = None
		car_behind = None
		for other_car in self.list_of_lane_sets[lane_number]:
			other_pos = other_car.get_current_pos()
			
			#Matching car infront
			if car_infront == None and car_behind == None:
				car_infront = other_car
				car_behind = other_car
			else:
				#Check if it's new car infront
				car_infront_pos = car_infront.get_current_pos()
				if (other_pos - car_pos) * (car_infront_pos - car_pos) > 0: #If new car is on same side of the car as the previous car infront
					if other_pos < car_infront_pos: # If new car is further back than previuos car infront
						car_infront = other_car #Change the car infront
				elif other_pos > car_pos: #If new car is infront and previous car infront is behind
					car_infront = other_car #Change the car infront
				
				#Check if new car behind
				car_behind_pos = car_behind.get_current_pos()
				if (other_pos - car_pos) * (car_behind_pos - car_pos) > 0: #If new car is on same side of the car as the previous car behind
					if other_pos > car_behind_pos: # If new car is further ahead than previuos car behind
						car_behind = other_car #Change the car behind
				elif other_pos < car_pos: #If new car is behind and previous car behind is infront
					car_behind = other_car #Change the car behind
		return car_behind, car_infront


	def __check_if_lane_is_clear(self, car:Car, lane_number:int) -> bool: #Need big fix
		"""Returns True or False whether a lane is clear to enter for a car. """
		if lane_number < 0 or lane_number >= self.number_lanes: #If not one of the lanes
			return False

		lane_set = self.list_of_lane_sets[lane_number]
		if len(lane_set) == 0: #If no car in lane
			return True
		else:
			for other_car in lane_set:
				distance = self.__get_distance_from_any_car_infront(car, other_car)
				other_speed = other_car.get_current_speed()
				extra_space = 1 * other_speed #Change for how much room the driver behind is given
				#If inside other car (see __get_distance_from_any_car_infront)
				if distance < 0 or distance > self.road_length - 2 * self.car_length - extra_space: #With padding for car behind
					return False
			return True #If none is inside


	def __insert_the_cars(self) -> None:
		"""Puts the cars in the starting positions"""
		cars_left = self.number_cars
		cur_lane = self.number_lanes-1
		while cars_left > 0:
			#Make and add car
			car = self.__make_new_car()
			self.list_of_lane_sets[cur_lane].add(car)
			
			#Change variables
			car.lane = cur_lane
			rel_pos = (self.number_cars - cars_left) // self.number_lanes
			car.change_pos(rel_pos * self.car_length)
			car.change_speed(0)
			self.__connect_first_car(cur_lane, car)
			
			#Change to next car
			cars_left -= 1
			cur_lane = (cur_lane - 1) % self.number_lanes
	

	def __make_max_speed(self) -> float:
		"""Returns the max speed of a single car. """
		speed = np.random.normal(self.speed_limit, self.speed_sd) #Normal distribution
		if speed > 0: #To make sure to be postive
			return speed
		else:
			return self.__make_max_speed()

	
	def __connect_first_car(self, lane:int, car:Car) -> None:
		"""Connects the car with the car_infront and car_behind in Car for the starting position. """
		lane_set = self.list_of_lane_sets[lane]
		if len(lane_set) > 1: #If not only car
			for other_car in lane_set: #Iterate over every car
				other_car_pos = other_car.get_current_pos()

				if other_car_pos == 0: #If the other car is the car in last place
					#Match as car infront
					car.car_infront = other_car
					other_car.car_behind = car
					if len(lane_set) == 2: #If it's the only other car
						#Match as car behind
						car.car_behind = other_car
						other_car.car_infront = car
				
				elif other_car_pos == car.cur_pos - self.car_length:
					#Match as car behind
					car.car_behind = other_car
					other_car.car_infront = car
	

	def __create_animation_objects(self) -> None:
		"""Gives each Car object an animation object in Car.animation_object"""
		
		lane_number = 0
		for lane in self.list_of_lane_sets:
			for car in lane:
				car.add_animation_object(Rectangle(xy=(lane_number + 0.2, car.get_current_pos()), width=0.6, \
									 height=self.car_length, color=car.get_car_color()))
			lane_number += 1
	

	def __switch_to_left_check(self, car:Car) -> bool:
		"""Checks if the car shouls switch to left lane. """
		bool1 = self.__check_if_cue(car)#If there is a cue
		left_lane = car.get_current_lane() - 1
		bool2 = self.__check_if_lane_is_clear(car, lane_number = left_lane) #If it is free to change to the left
		bool3 = self.__check_if_speed_is_bigger_in_other_lane(car=car, new_lane = left_lane) #Check if it is worth to switch
		return bool1 and bool2 and bool3


	def __switch_to_right_check(self, car:Car) -> bool:
		"""Checks if the car shouls switch to right lane. """
		right_lane = car.get_current_lane() + 1
		bool1 = self.__check_if_lane_is_clear(car, lane_number = right_lane) #If it is free to change to the right
		bool2 = self.__check_if_speed_is_not_smaller_in_other_lane(car=car, new_lane = right_lane) #Check if it is worth to switch
		return bool1 and bool2


	def __check_if_speed_is_bigger_in_other_lane(self, car:Car, new_lane:int) -> bool:
		"""Checks if the distance to the car infront would be bigger in a different lane. (Use if you prefer to not switch lane)"""
		if new_lane < 0 or new_lane + 1 > self.number_lanes:#If new lane not one of the lanes
			return False
		
		car_infront = car.get_car_infront()
		if car_infront == None: #If current lane is clear
			return False
		
		max_speed = car.get_max_speed()
		cur_dist = self.__get_distance_from_car_infront(car)
		time_rule = car.get_time_rule()
		cur_max_speed = min(max_speed, cur_dist/time_rule)
		if cur_max_speed == max_speed: #If speed could be max speed in current lane
			return False
		elif len(self.list_of_lane_sets[new_lane]) == 0: #Else if new lane is clear
			return True
		
		_, new_infront = self.__get_car_infront_and_behind_for_any_lane(car=car, lane_number=new_lane)
		#possible_dist = self.__get_distance_from_any_car_infront(car, new_infront)
		new_speed = new_infront.get_current_speed()
		cur_speed = car.get_current_speed()
		if new_speed > cur_speed * 1.2: #With padding to not get erratic behaviour
			return True


	def __check_if_speed_is_not_smaller_in_other_lane(self, car:Car, new_lane:int) -> bool:
		"""Checks if the distance to the car infront would be smaller in a different lane. (Use if you prefer to switch lane)"""
		if new_lane < 0 or new_lane + 1 > self.number_lanes:#If new lane not one of the lanes
			return False
		
		if len(self.list_of_lane_sets[new_lane]) == 0: #If new lane is clear
			return True

		car_infront = car.get_car_infront()
		_, new_infront = self.__get_car_infront_and_behind_for_any_lane(car=car, lane_number=new_lane)
		possible_dist = self.__get_distance_from_any_car_infront(car, new_infront)
		time_rule = car.get_time_rule()
		max_speed = car.get_max_speed()
		new_lane_speed = possible_dist/time_rule
		if new_lane_speed >= max_speed: #If new lane can achieve max speed
			return True
		
		if car_infront == None: #If current lane is clear
			return False
		
		#cur_dist = self.__get_distance_from_car_infront(car)
		#cur_max_speed = min(max_speed, cur_dist/time_rule)
		new_speed = new_infront.get_current_speed()
		cur_speed = car.get_current_speed()
		if cur_speed <= new_speed: #If the new lane is at least as fast
			return True


	def __check_if_cue(self, car:Car) -> bool:
		"""Checks if car is in a cue and should switch lane to the left. """
		if len(self.list_of_lane_sets[car.get_current_lane()]) == 1: #If only car in lane
			return False
		else:
			car_speed = car.get_current_speed()
			max_acc = car.get_max_acceleration()
			distance_infront = self.__get_distance_from_car_infront(car)
			time_rule_speed = distance_infront / car.get_time_rule() #If close to next car
			if car_speed + max_acc > time_rule_speed: #If needs to slow down due to other car
				return True
			else:
				return False


	def __update_speed(self, car: Car) -> None:
		"""Updates the speed for one time step and one car. """
		car_speed = car.get_current_speed()
		max_acc = car.get_max_acceleration()
		max_delta_v = max_acc * self.t_step
		max_speed = car.get_max_speed()
		if len(self.list_of_lane_sets[car.get_current_lane()]) == 1: #If only car in lane
			car.change_speed(np.min([car_speed + max_delta_v, max_speed]))
		else: #If other cars in lane
			distance_infront = self.__get_distance_from_car_infront(car)
			time_rule_speed = distance_infront / car.get_time_rule() #If close to next car
			car.change_speed(np.min([car_speed + max_delta_v, max_speed, time_rule_speed]))


	def __get_distance_from_car_infront(self, car:Car) -> float:
		"""Returns the distance from the car infront for a certain car. """
		distance = self.__get_distance_from_any_car_infront(car, car.get_car_infront())
		if distance < 0:
			raise ValueError("Negativt avstånd")
		return distance
	

	def __get_distance_from_any_car_infront(self, car:Car, other_car:Car) -> float:
		"""Returns the distance from any car infront for a certain car \
		(negative or bigger than road length - 2 * car length if car is inside other car). """
		car_pos = car.get_current_pos()
		car_infront_pos = other_car.get_current_pos()
		if car_pos < car_infront_pos:
			return car_infront_pos - car_pos - car.get_car_length()
		else:
			return self.road_length - car_pos + car_infront_pos - car.get_car_length()
			

	def __health_check(self) -> None:
		"""Checks that everything is correct with all the cars. """
		self.__flow_check()
		for lane in self.list_of_lane_sets:
			for car in lane:
				self.__car_check(car)
				self.__check_adjecent_cars(car)
				self.__check_lane(car)
				
			##Check that cars are properly connected			

	
	def __flow_check(self) -> None:
		"""Returns error if something is wrong with flow rate. """
		flowrate = self.flowrate
		if flowrate == None and self.t >= self.t_step * 2:
			raise ValueError("Flow rate is None. ")

		if self.flowrate < 0:
			raise ValueError("Flow rate is negative. ")
		
		if len(self.flowrate_list) != len(self.t_list):
			raise ValueError("Flow rate list not same length as time list. ")


	def __car_check(self, car:Car) -> None:
		"""Checks if the variables in car are correct. """
		speed = car.get_current_speed()
		if type(speed) != float and type(speed) != int and not isinstance(speed, np.float64):
			raise ValueError("Speed is not a number. ")
		if speed < 0: 
			raise ValueError("Speed is negative. ")
		pos = car.get_current_pos()
		if type(pos) != float and type(pos) != int and not isinstance(speed, np.float64):
			raise ValueError("Position is not a number. ")
		if pos < 0 or pos > self.road_length: 
			raise ValueError("Position is outside of road. ")


	def __check_adjecent_cars(self, car:Car) -> None:
		"""Checks the adjecent cars and returns error if something is wrong. """
		car_infront = car.get_car_infront()
		car_behind = car.get_car_behind()
		car_lane = car.get_current_lane()
		if type(car_infront) != type(car_behind):
			raise ValueError("Car infront or behind missing or accedentally there. ")
		if type(car_infront) != type(None):
			if car_lane != car_infront.get_current_lane() or car_lane != car_behind.get_current_lane():
				raise ValueError("Car, or adjecent cars have wrong lane number")
			#Checks that the cars infront are connected correctly
			new_car_infront = car_infront
			car_count = 1
			while new_car_infront != car:
				new_car_infront = new_car_infront.get_car_infront()
				car_count += 1
			if car_count != len(self.list_of_lane_sets[car_lane]):
				raise ValueError("The cars infront are connected wrong. ")
			#Checks that the cars behind are connected correctly
			new_car_behind = car_behind
			car_count = 1
			while new_car_behind != car:
				new_car_behind = new_car_behind.get_car_behind()
				car_count += 1
			if car_count != len(self.list_of_lane_sets[car_lane]):
				raise ValueError("The cars behind are connected wrong. ")
				

	def __check_lane(self, car:Car):
		"""Checks that the lane and the lane numbers are correct. """
		car_lane = car.get_current_lane()
		if car not in self.list_of_lane_sets[car_lane]:
			raise ValueError("Car not in correct lane set or lane number is wrong")
		for lane_number in range(len(self.list_of_lane_sets)):
			if car_lane != lane_number and car in self.list_of_lane_sets[lane_number]:
				raise ValueError("Car in wrong lane or lane number is incorrect")


def main():
	s = Simulation(road_length=100, number_of_cars=10, number_of_lanes=3, time_step=0.1, \
				speed_limit=30, standard_deviation_of_speed=2)
	""" s.simulate(time=300)
	a = Animation(s)
	a.plot_flowrate() """
	s.simulate_animate()

if __name__ == "__main__" :
	main()
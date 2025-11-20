"""The final project in sim-mod"""

from Highway_sim import Simulation
from Highway_animation import Animation
import numpy as np
import matplotlib.pyplot as plt


def characteristic_diagram(road_length=1000, number_of_lanes=3, time_step=0.1, \
				speed_limit=30, standard_deviation_of_speed=2, steps=10, time=300, car_length=2):
	flow_rate_list = []
	density_list = []
	RMSF_list = []
	cars_part1 = [3*i+1 for i in range(0, int((road_length*number_of_lanes/steps/car_length)//2)//3-1)]
	cars_part2 = [int((cars*road_length*number_of_lanes/steps/car_length)/6)*3+1 for cars in range(1, steps+1)]
	n_cars_list = cars_part1 + cars_part2
	for n_cars in n_cars_list:
		s = Simulation(road_length=road_length, number_of_cars=n_cars, number_of_lanes=number_of_lanes, time_step=time_step, \
					speed_limit=speed_limit, standard_deviation_of_speed=standard_deviation_of_speed, car_length=car_length)
		s.simulate(time=time)
		cutoff = int((time/time_step)//3)
		cur_flow_rate_list = s.flowrate_list[cutoff:]
		flow_rate_list.append(np.mean(cur_flow_rate_list))
		density_list.append(n_cars/road_length/number_of_lanes)

		variance = np.var(cur_flow_rate_list)
		RMSF_list.append(np.sqrt(variance))

		print(flow_rate_list[-1])
	plt.errorbar(density_list, flow_rate_list, RMSF_list)
	plt.xlabel("Density [#cars/m]")
	plt.ylabel("Flow rate [1/s]")
	plt.show()

		
def fundemental_diagram_sd(iterations=5, road_length=100, number_of_lanes=3, time_step=0.1, \
				speed_limit=30, standard_deviation_of_speed=2, steps=10, time=300, car_length=2):
	flow_rate_list = []
	density_list = []
	SE_list = []
	#n_cars_list = [1, 2, 3, 4, 5, 10, 15, 20, 25]
	#n_cars_list = [1, 3, 5, 7, 9, 11, 15, 29, 49]
	n_cars_list = [1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16, 29, 75]
	#cars_part1 = [2*i+1 for i in range(0, int((road_length*number_of_lanes/steps/car_length)//2)//2-1)]
	#cars_part2 = [int((cars*road_length*number_of_lanes/steps/car_length)/3)*2+1 for cars in range(1, steps+1)]
	#n_cars_list = cars_part1 + cars_part2
	for n_cars in n_cars_list:
		cur_flow_rate_list = []
		for _ in range(iterations):
			s = Simulation(road_length=road_length, number_of_cars=n_cars, number_of_lanes=number_of_lanes, time_step=time_step, \
						speed_limit=speed_limit, standard_deviation_of_speed=standard_deviation_of_speed, car_length=car_length)
			s.simulate(time=time)
			cutoff = int((time/time_step)//3)
			cur_flow_rate_list.append(np.mean(s.flowrate_list[cutoff:]))
			print(cur_flow_rate_list[-1])
			
		variance = np.var(cur_flow_rate_list)
		
		flow_rate_list.append(np.mean(cur_flow_rate_list))
		density_list.append(n_cars/road_length/number_of_lanes)
		SE_list.append(np.sqrt(variance/(len(cur_flow_rate_list)-1)))
		print(density_list[-1])

			
	plt.errorbar(density_list, flow_rate_list, SE_list)
	plt.xlabel("Density [#cars/m]")
	plt.ylabel("Flow rate [1/s]")
	plt.show()



def main():
	fundemental_diagram_sd(iterations=5, road_length=100, steps=4, number_of_lanes=3)
	#characteristic_diagram(road_length=100, steps=4, number_of_lanes=2)

if __name__ == "__main__" :
	main()
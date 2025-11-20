"""Animating the simulation"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class Animation:
	
	def __init__(self, simulation:"Simulation"):
		self.s = simulation


	def animate_highway(self):
		#Two figures, one for animation and one for plot
		fig, (ax, ax_graph) = plt.subplots(1, 2, figsize=(28, 7.5))
		
		#Animation
		ax.set_xlim(0, len(self.s.list_of_lane_sets)) #Amount of lanes
		ax.set_ylim(0, self.s.road_length) #Length of the road
		ax.set_ylabel("Length [m]")
		ax.set_xlabel("Length [m]")
		ax.set_aspect("equal") #Makes sure everything is proportional


		for lane in self.s.list_of_lane_sets:
			for car in lane:
				ax.add_patch(car.animation_object)

		timer = ax.text(0.5, 1.05, "Time: 0", transform=ax.transAxes, ha="center", va="bottom")


		#Graph
		ax_graph.set_xlim(self.s.t)
		if self.s.flowrate != None:
			ax_graph.set_ylim(self.s.flowrate * 1.2)
		else:
			ax_graph.set_ylim(1)
		ax_graph.set_ylabel("Flow rate [1/s]")
		ax_graph.set_xlabel("Time [s]")

		line, = ax_graph.plot([], [])

		def update(frame):
			self.s.time_step()
			timer.set_text(f"Time: {self.s.t:.2f} s")  # Update the timer text

			line.set_data(self.s.t_list, self.s.flowrate_list)
			ax_graph.set_xlim(0, self.s.t)
			if self.s.flowrate != None:
				ax_graph.set_ylim(0, max(self.s.flowrate_list) * 1.2)
			else:
				ax_graph.set_ylim(0, 1)

		
		anim = FuncAnimation(fig=fig, func=update, frames=200, interval=50)
		plt.show()

	
	def plot_flowrate(self):
		"""Plot the flow rate of one simulation. """
		plt.plot(self.s.t_list, self.s.flowrate_list)
		plt.ylabel("Flow rate [1/s]")
		plt.xlabel("Time [s]")
		plt.show()
		

	


def main():
	"""a = Animation(road_length=20, number_of_lanes=2)
	a.animate_highway()"""

if __name__ == "__main__" :
	main()
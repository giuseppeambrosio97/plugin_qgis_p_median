import numpy as np

import random
import math

from .util import euclidean_distance

class Solution_F:
	cost = 0

	def __init__(self, C, Z, k, OD_CZ):
		self.k = k
		if k >= len(Z):
			self.F = Z.copy()
		self.C = C.copy()
		self.Z = Z.copy()
		self.OD_CZ = OD_CZ
	
	def kmeans(self,Z,k):
		centroid_old = [Z[key].geometry for key in random.sample(Z.keys(), k)]
		label = [0 for _ in range(len(Z))]
		centroid_new = [[0,0] for _ in range(k)]
		centroid_len = [0 for _ in range(k)]

		#esegui finche non ci sono più cambiamenti
		while centroid_old != centroid_new:
			#per ogni zona
			for i,(key_zone,zone) in enumerate(Z.items()):
				best_value = math.inf
				#determina il centroide più vicino
				for id_centroid,centroid in enumerate(centroid_old):
					d = euclidean_distance(centroid,zone.geometry)
					if d < best_value:
						best_value = d
						label[i] = id_centroid
				centroid_new[label[i]][0] += zone.geometry[0]
				centroid_new[label[i]][1] += zone.geometry[1]
				centroid_len[label[i]]+=1

			#ricomputa centroidi
			for i in range(k):
				centroid_new[i][0] /= centroid_len[i]
				centroid_new[i][1] /= centroid_len[i]

			centroid_old = centroid_new

		return label

	def clustering_starting_point(self):
		def get_clusters(items,labels,k):
			clusters = [[] for _ in range(k)]

			for i,(key,_) in enumerate(items.items()):
				clusters[labels[i]].append(key)

			return clusters


		labels = self.kmeans(self.Z,self.k)
		clusters = get_clusters(self.Z,labels,self.k)

		starting_solution = []

		for i in range(self.k):
			starting_solution.append(random.choice(clusters[i]))

		self.F = {}
		self.ZmenoF = self.Z.copy()

		for key in starting_solution:
			self.add_to_F_from_ZmenoF(key)

		self.cost = self.evaluate(self.F)

	def random_starting_point(self):
		"""
			Inizializza la soluzione in maniera random
		"""
		self.F = {}
		self.ZmenoF = self.Z.copy()

		start_sol_keys = random.sample(self.ZmenoF.keys(), self.k)
		for key in start_sol_keys:
			self.add_to_F_from_ZmenoF(key)

		self.cost = self.evaluate(self.F)

	def add_to_F_from_ZmenoF(self, key):
		"""
			Prende la facility con chiave key in self.ZmenoF, l'aggiunge a self.F e dopodichè la elimina da self.ZmenoF

			Parameters
				key (string):
		"""
		self.F[key] = self.ZmenoF[key]
		del self.ZmenoF[key]


	def visite_next_k_random_neighbour(self, k):
		"""

			Parameters:
				k (int):
		"""
		best_local_F = {}
		best_local_ZmenoF = {}
		best_cost = math.inf
		for _ in range(k):
			F_to_test, ZmenoF_to_test = self.random_swap()
			flag, cost = self.update_best(best_cost, F_to_test)
			if not flag:
				best_cost = cost
				best_local_F = F_to_test
				best_local_ZmenoF = ZmenoF_to_test

		if self.cost > best_cost:
			self.cost = best_cost
			self.F = best_local_F
			self.ZmenoF = best_local_ZmenoF
			return False
		return True

	def visite_all_neighbour(self):
		best_local_F = {}
		best_local_ZmenoF = {}
		best_cost = math.inf
#        print("visite_all_neighbour+++++++++++++++++++++++++++++++++++++++")
		for to_out_key in self.F.keys():
			for to_in_key in self.ZmenoF.keys():
		#                print("to_out_key ", to_out_key)
		#                print("to_in_key ", to_in_key)
		#                print("+++++++++++++++++++++++++++++++++++++++++++")
				F_to_test, ZmenoF_to_test = self.swap(to_in_key, to_out_key)
#                print("F_to_test")
#                print(F_to_test)
#                print("ZmenoF_to_test")
#                print(ZmenoF_to_test)
				flag, cost = self.update_best(best_cost, F_to_test)

#                print("flag {} cost {}".format(flag,cost))
#                print("****************************************")
#                print("****************************************")

				if not flag:
					best_cost = cost
					best_local_F = F_to_test
					best_local_ZmenoF = ZmenoF_to_test

		if self.cost > best_cost:
			self.cost = best_cost
			self.F = best_local_F
			self.ZmenoF = best_local_ZmenoF
			return False
		return True

	def random_swap(self):
		to_out_key = random.choice(list(self.F.keys()))
		to_in_key = random.choice(list(self.ZmenoF.keys()))
		return self.swap(to_in_key, to_out_key)

	def swap(self, to_in_key, to_out_key):
		F_to_test = self.F.copy()
		ZmenoF_to_test = self.ZmenoF.copy()
		F_to_test[to_in_key], ZmenoF_to_test[to_out_key] = ZmenoF_to_test[to_in_key], F_to_test[to_out_key]
		del ZmenoF_to_test[to_in_key]
		del F_to_test[to_out_key]
		return F_to_test, ZmenoF_to_test

	def evaluate(self, F_to_Test):
		cost = 0
		for _, client in self.C.items():
			cost += self.d_cost_for_client(client, F_to_Test)*client.weight
		return cost

	def evaluate_solution(self):
		cost = 0
		for _, client in self.C.items():
			cost += self.d_cost_for_client(client, self.F)*client.weight
		return cost

	def d_cost_for_client(self, client, F_to_Test):
		cost_for_client = math.inf
		for key_facility, facility in F_to_Test.items():
			if self.OD_CZ[client.id, facility.id] < cost_for_client:
				cost_for_client = self.OD_CZ[client.id, facility.id]
				client.link_to_zone(key_facility)
		return cost_for_client

	def update_best(self, costo_local_best, F_to_test):
		cost_neighbour = self.evaluate(F_to_test)
		if costo_local_best <= cost_neighbour:
			return True, costo_local_best
		else:
			return False, cost_neighbour

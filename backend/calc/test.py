from typing import List

def generate_distributions(icebreakers: List[int], ships: List[int], max_ships_per_icebreaker):
    def distribute(remaining_ships, current_distribution):
        distributions.append([list(group) for group in current_distribution])
        if not remaining_ships:
            return
        for i in range(len(icebreakers)):
            if len(current_distribution[i]) < max_ships_per_icebreaker:
                new_distribution = [list(group) for group in current_distribution]
                new_distribution[i].append(remaining_ships[0])
                distribute(remaining_ships[1:], new_distribution)

    distributions = []
    distribute(ships, [[] for _ in icebreakers])
    return distributions


# Пример использования
icebreakers = [4,1,2,3]
ships = [1,2,3,4,5,6,7,8,9,10]
max_ships_per_icebreaker = 3

#distributions = generate_distributions(icebreakers, ships, max_ships_per_icebreaker)
#for distribution in distributions:
#    print(distribution)
#print(len(distributions))

from backend.crud.crud_types import VesselPathCRUD

vessel_paths = VesselPathCRUD().get_all()
ports = []

for vessel_path in vessel_paths:
    ports.append(vessel_path.source)
    ports.append(vessel_path.target)

print(list(set(ports)))
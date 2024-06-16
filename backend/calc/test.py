from itertools import combinations_with_replacement


def generate_distributions(icebreakers, ships, max_ships_per_icebreaker):
    num_icebreakers = len(icebreakers)

    # Генерируем все возможные распределения с количеством судов до max_ships_per_icebreaker на ледокол
    all_combinations = []
    for combination in combinations_with_replacement(range(num_icebreakers), len(ships)):
        distribution = [[] for _ in range(num_icebreakers)]
        for ship_index, icebreaker_index in enumerate(combination):
            if len(distribution[icebreaker_index]) < max_ships_per_icebreaker:
                distribution[icebreaker_index].append(ships[ship_index])
            else:
                break
        else:
            all_combinations.append(distribution)

    return all_combinations


# Пример использования
icebreakers = ['Icebreaker1', 'Icebreaker2']
ships = ['Ship1', 'Ship2', 'Ship3']
max_ships_per_icebreaker = 2

distributions = generate_distributions(icebreakers, ships, max_ships_per_icebreaker)
for distribution in distributions:
    print(distribution)


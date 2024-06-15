from intervaltree import Interval, IntervalTree


class Schedule:
    def __init__(self):
        self.busy_tree = IntervalTree()

    def reserve_interval(self, start, end):
        if self.busy_tree.overlap(start, end):
            raise ValueError("Новое окно пересекается с существующим")
        self.busy_tree.add(Interval(start, end))

    def get_reserved_intervals(self):
        return sorted(self.busy_tree)

    def find_closest_free_interval(self, target_date):
        sorted_intervals = sorted(self.busy_tree)
        for interval in sorted_intervals:
            if target_date < interval.begin:
                # Найден ближайший свободный интервал справа от target_date
                return Interval(target_date, interval.begin)
            elif target_date < interval.end:
                # Если target_date попадает в занятый интервал, ищем следующий свободный
                continue

        # Если target_date больше всех занятых интервалов
        if sorted_intervals and target_date >= sorted_intervals[-1].end:
            return Interval(target_date, None)

        return None


# Пример использования
schedule = Schedule()
schedule.reserve_interval(1, 5)
schedule.reserve_interval(10, 15)

# Получение списка зарезервированных интервалов
reserved_intervals = schedule.get_reserved_intervals()
print("Reserved Intervals:", reserved_intervals)

# Поиск ближайшего свободного интервала справа от заданной даты
closest_free_interval = schedule.find_closest_free_interval(6)
print("Closest Free Interval:", closest_free_interval)

closest_free_interval = schedule.find_closest_free_interval(16)
print("Closest Free Interval:", closest_free_interval)

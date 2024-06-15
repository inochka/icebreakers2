from backend.calc.vessel import Vessel,IceBreaker
from backend.data.vessels_data import vessels_data, icebreaker_data
from backend.data.template_data import templates_data
from backend.models import Template

class Grade:
    """Оценка стоимости проводки"""
    stuck_vessels:int = 0 #количество судов не достигших точки назначения
    total_time:int = 0 #общее время всех судов на маршруте в часах (на считая ледоколов) в часах

class Context:
    vessels = {}
    icebreakers = {}
    res_grade:Grade = None
    res_vessels = {} #результаты расчета
    res_icebreakers = {} #результаты расчета
    template_name: str = ""

    def __init__(self, tmp: Template | None = None):
        self.vessels.clear()
        self.icebreakers.clear()
        if tmp:
            self.template_name = tmp.name
            self.vessels = {v_id: Vessel(**vessels_data[v_id]) for v_id in tmp.vessels}
            self.icebreakers = {v_id: IceBreaker(**icebreaker_data[v_id]) for v_id in tmp.icebreakers}


    def get_templates_list(self) -> list:
        res = []
        for k,v in templates_data.items():
            res.append({'id':k, 'name':v['name']})
        return res


    def load_from_template(self, template_name):
        self.vessels.clear()
        self.icebreakers.clear()
        tmp = templates_data[template_name]
        self.template_name = template_name
        for v in tmp['vessels']:
            self.vessels[v] = Vessel(**vessels_data[v])
        for v in tmp['icebreakers']:
            self.icebreakers[v] =  IceBreaker(**icebreaker_data[v])


if __name__ == "__main__":
    context = Context()
    context.load_from_template('test_1')
    print('TEMPLATES: '+ str(context.get_templates_list()))
    print('VESSELS: '+ str(context.vessels))
    print('ICEBREAKERS: '+ str(context.icebreakers))

from vessel import Vessel,IceBreaker
from backend.data.vessels_data import vessels_data, icebreaker_data
from backend.data.template_data import templates_data
class Context:
    vessels = {}
    icebreakers = {}
    def get_templates_list(self) -> list:
        res = []
        for k,v in templates_data.items():
            res.append({'id':k, 'name':v['name']})
        return res
    def load_from_template(self,template_name):
        self.vessels.clear()
        self.icebreakers.clear()
        tmp = templates_data[template_name]
        print(tmp)
        for v in tmp['vessels']:
            self.vessels[v] = vessels_data[v]
        for v in tmp['icebreakers']:
            self.icebreakers[v] = icebreaker_data[v]

if __name__ == "__main__":
    context = Context()
    context.load_from_template('test_1')
    print('TEMPLATES: '+ str(context.get_templates_list()))
    print('VESSELS: '+ str(context.vessels))
    print('ICEBREAKERS: '+ str(context.icebreakers))

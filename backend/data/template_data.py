from itertools import islice
from backend.data.vessels_data import vessels_data, icebreaker_data

"""
templates_data = {'идентификатор шаблона': 
                    {
                    'name':'название шаблона' 
                    'vessels':[1,2,5,8],
                    'icebreakers':[1,2] 
                    }                
                }
"""

templates_data = {
    'main':{'name':"Датасеты из постановки задачи",
            'vessels':list(v for v in islice(vessels_data,0,len(vessels_data))),
            'icebreakers':list(v for v in islice(icebreaker_data,0,len(icebreaker_data)))
            },
    'test_1':{'name':"Заявки первой недели",
            'vessels':list(v for v in islice(vessels_data,0,4)),
            'icebreakers':list(v for v in islice(icebreaker_data,0,len(icebreaker_data)))
            }
}
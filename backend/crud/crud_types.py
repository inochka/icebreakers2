from backend.crud.crud import CRUD, T
from backend.models import Template, VesselPath, IcebreakerPath, Grade, Caravan, Algorythm
from uuid import uuid4
from typing import List, Dict, Any

class TemplatesCRUD(CRUD):
    filename = "templates.json"
    model = Template

    def _make_id_by_item(self, item: T):
        return item.name

class VesselPathCRUD(CRUD):
    filename = "vessel_paths.json"
    model = VesselPath

    def _make_id_by_item(self, item: T):
        return item.template_name + "_" + str(item.vessel_id)


class IcebreakerPathCRUD(CRUD):
    filename = "icebreaker_paths.json"
    model = IcebreakerPath

    def _make_id_by_item(self, item: T):
        return item.template_name + "_" + str(item.icebreaker_id)


class GradeCRUD(CRUD):
    filename = "grades.json"
    model = Grade

    def _make_id_by_item(self, item: T):
        return item.template_name

class CaravanCRUD(CRUD):
    filename = "caravans.json"
    model = Caravan

    def _make_id_by_item(self, item: T):
        return str(uuid4())

class AlgoCRUD(CRUD):
    filename = "algorythms.json"
    model = Algorythm

    def _make_id_by_item(self, item: T):
        return item.name
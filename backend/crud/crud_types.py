from backend.crud.crud import CRUD, T
from backend.models import Template, VesselPath, IcebreakerPath, Grade, Caravan
from uuid import uuid4

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
        return item.template_name + "_" + str(uuid4())
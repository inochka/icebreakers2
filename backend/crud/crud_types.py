from backend.crud.crud import CRUD, T
from backend.models import Template, VesselPath

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
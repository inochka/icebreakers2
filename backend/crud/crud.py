import json
from typing import Type, TypeVar, Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import uuid4
from backend.config import json_dir
from fastapi.encoders import jsonable_encoder

T = TypeVar('T', bound=BaseModel)

class CRUD:

    dir_path = json_dir
    filename: str
    model: Type[T]

    def __init__(self):
        #self.model = model
        self.filepath = self.dir_path / self.filename
        self.data: Dict[str, T] = self._load()

    def _load(self) -> Dict[str, T]:
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            return {k: self.model(**v) for k, v in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self) -> None:
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(jsonable_encoder(self.data), f, indent=4, ensure_ascii=False)

    def _make_id_by_item(self, item: T):
        # метод для получения идентификатора по модели
        return str(uuid4())

    def get(self, item_id: Any) -> Optional[T]:
        return self.data.get(item_id)

    def get_all(self) -> List[T]:
        return list(self.data.values())

    def get_by_filter_conds(self, filter_cond: dict[str, Any]):
        results = []
        if not self.data:
            return None

        if not set(filter_cond.keys()).issubset(set(vars(list(self.data.values())[0]).keys())):
            return None

        for idx, item in self.data.items():
            matched = True
            for cond, val in filter_cond.items():
                if getattr(item, cond) != val:
                    matched = False
                    break
            if matched:
                results.append(item)

        return results


    def post(self, item: T, item_id: Any | None = None) -> Optional[T]:
        if not item_id:
            item_id = self._make_id_by_item(item)
        self.data[item_id] = item
        self._save()
        return item

    def post_or_put_list(self, items: List[T]) -> Optional[List[T]]:
        for item in items:
            item_id = self._make_id_by_item(item)
            self.data[item_id] = item
        self._save()
        return items

    def put(self, item: T, item_id: Any | None = None) -> Optional[T]:
        if not item_id:
            item_id = self._make_id_by_item(item)
        if item_id in self.data:
            self.data[item_id] = item
            self._save()
            return item
        return None

    def delete(self, item_id: Any) -> Optional[T]:
        if item_id and item_id in self.data:
            item = self.data.pop(item_id)
            self._save()
            return item
        return None
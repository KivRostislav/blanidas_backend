from pydantic import BaseModel


class TemplateBaseInfo(BaseModel):
    id: int

class TemplateBaseNamedInfo(TemplateBaseInfo):
    name: str

class TemplateBaseFilter(BaseModel):
    pass

class TemplateBaseNamedFilter(TemplateBaseFilter):
    name_like: str | None = None

class TemplateBaseCreate(BaseModel):
    pass

class TemplateBaseNamedCreate(TemplateBaseCreate):
    name: str

class TemplateBaseUpdate(BaseModel):
    id: int

class TemplateBaseNamedUpdate(TemplateBaseUpdate):
    name: str

class TemplateBaseDelete(BaseModel):
    id: int

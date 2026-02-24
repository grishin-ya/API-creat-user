from pydantic import BaseModel


class DirectionBase(BaseModel):
    name: str


class DirectionCreate(DirectionBase):
    pass


class DirectionOut(DirectionBase):
    id: int

    class Config:
        from_attributes = True
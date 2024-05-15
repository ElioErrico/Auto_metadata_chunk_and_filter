from pydantic import BaseModel
from cat.mad_hatter.decorators import plugin


class MySettings(BaseModel):
    n_of_chunk_for_one_title: int = 5

@plugin
def settings_schema():
    return MySettings.schema()

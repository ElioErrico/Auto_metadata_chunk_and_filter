from pydantic import BaseModel
from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field, field_validator


class MySettings(BaseModel):
    n_of_chunk_for_one_title: int = 5
    create_tag_with_prompt: bool =True
    search_for_title_prompt: str = Field(
    title="Search for title prompt",
    default="""Take a deep breath and create a 2 words title for the following context. Use Keywords!\n""",
        extra={"type": "TextArea"},)
    upload_document_with_following_tag: bool =False
    tag_to_archive_in_metadata: str

@plugin
def settings_schema():
    return MySettings.schema()
    

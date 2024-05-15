from pydantic import BaseModel
from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field, field_validator


class MySettings(BaseModel):
    n_of_chunk_for_one_title: int = 5
    create_tag_with_prompt: bool =True
    search_for_title_prompt: str = Field(
    title="Search for title prompt",
    default="""Concentrati e individua un titolo conciso di 4 parole che descriva al meglio il seguente testo. Per individuare il titolo utilizza le seguenti regole:\n
1) Se nel testo è citato un errore, includi nel titolo il numero dell'errore (Non confondere il numero)\n
2) Se nel testo non è citato alcun errore non includere il numero dell'errore\n
3) Il titolo deve includere le parole chiave contenute nel testo
""",
        extra={"type": "TextArea"},
    )

@plugin
def settings_schema():
    return MySettings.schema()
    

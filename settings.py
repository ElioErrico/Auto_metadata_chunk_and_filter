from pydantic import BaseModel
from cat.mad_hatter.decorators import plugin


class MySettings(BaseModel):
    text_to_search_the_title: str = "Individua un titolo conciso di 4 parole che descriva al meglio il seguente testo. Per individuare il titolo utilizza le seguenti regole:"
    rule_1: str  = "1) Se nel testo è citato un errore, includi nel titolo il numero dell'errore"
    rule_2: str  = "2) Il titolo deve includere le parole chiave contenute nel testo"
    rule_3: str  = ""
    n_of_chunk_for_one_title: int = 5
    prompt_for_question_generation: str= "Genera 2 domande concise e mirate la cui risposta è contenuta nel seguente testo:"


@plugin
def settings_schema():
    return MySettings.schema()


from cat.mad_hatter.decorators import hook

@hook
def after_rabbithole_splitted_text(chunks, cat):

    concatenated_chunks_list = []

    settings = cat.mad_hatter.get_plugin().load_settings()
    n_of_chunk_for_one_title = settings["n_of_chunk_for_one_title"]
    text_to_search_the_title = settings["text_to_search_the_title"]
    rule_1=settings["rule_1"]
    rule_2=settings["rule_2"]
    rule_3=settings["rule_3"]
    complete_prompt_for_tile_search=text_to_search_the_title + "\n" + rule_1 + "\n" + rule_2 + "\n" + rule_3
    prompt_for_question_generation =settings["prompt_for_question_generation"]

    # Prima fase: Concatenazione dei chunks e creazione dei titoli
    for i in range(0, len(chunks), n_of_chunk_for_one_title):
        # Seleziona un gruppo di n chunk
        chunk_group = chunks[i:i + n_of_chunk_for_one_title]
        # Concatena il contenuto di ogni chunk nel gruppo
        concatenated_content = ''.join(chunk.page_content for chunk in chunk_group)
        concatenated_chunks_list.append(concatenated_content)

        # Genera un titolo per il contenuto concatenato
        title = cat.llm(f"{complete_prompt_for_tile_search}\n Testo: \n {concatenated_content}")
        
        # Aggiunge il titolo come metadato a ciascun chunk nel gruppo
        for chunk in chunk_group:
            chunk.metadata['titles'] = [title]
            chunk.page_content= title + ":\n" + chunk.page_content
            questions=cat.llm(f"{prompt_for_question_generation}\n {chunk.page_content}")
            chunk.page_content=chunk.page_content+ ":\n\n" + questions
    
    return chunks

    # La funzione ora modifica direttamente i metadati dei chunk in 'chunks'

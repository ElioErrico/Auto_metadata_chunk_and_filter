
from cat.mad_hatter.decorators import hook
from langchain.docstore.document import Document
from cat.looking_glass.cheshire_cat import CheshireCat

import os


def stampa(testo, nome_file, percorso="list_of_titles"):
    """
    Writes or appends text to a text file. If the file does not exist, creates it with the text as initial content.
    If the file exists, appends the text to the existing content.

    Args:
    testo (str): Text to be written or appended.
    nome_file (str): The name of the file.
    percorso (str): The directory path.
    """
    percorso_completo = os.path.join(percorso, nome_file)
    
    # Ensure the directory exists, otherwise create it
    if not os.path.exists(percorso):
        os.makedirs(percorso)
    
    # Determine the mode based on the existence of the file: append if it exists, write if not
    mode = 'a' if os.path.exists(percorso_completo) else 'w'
    
    # Write or append text to the file
    with open(percorso_completo, mode, encoding='utf-8') as file:
        file.write(testo + "\n")  # Append new text with a newline for readability

#Inizializzo il gatto per poter richiamare la memoria vettoriale
ccat = CheshireCat()

@hook
def after_cat_bootstrap(cat):
    #call global parameter so can be called through out the various hooks
    global list_of_titles
    list_of_titles=[]
        # Call the declarative memory --> object <class 'cat.memory.vector_memory_collection.VectorMemoryCollection'>
    declarative_memory = ccat.memory.vectors.declarative
    stampa(str(declarative_memory),"declarative_memory.txt")
    # Call the points of declarative memory --> tuple ([ ... ])
    points = declarative_memory.client.scroll(collection_name="declarative")
    stampa(str(points),"points.txt")
    """([

        Record(id='id_file', 
        payload={
        'page_content': "testo contenuto",
        'metadata': {'source': 'errore3_29_11_2023.txt', 'when': 1715505610.7838979}},
        vector=None,
        shard_key=None),

        Record(
        id='id_file', 
        payload={
        'page_content': "testo contenuto",
        'metadata': {'source': 'errore3_29_11_2023.txt',  'when': 1715505610.7838979}},
        vector=None,
        shard_key=None),

        Record(id='id_file', 
        payload={
        'page_content': "testo contenuto",
        'metadata': {'source': 'titolo_file.txt',  'when': 1715505610.7838979}},
        vector=None,
        shard_key=None)

        ])"""

    records = points[0]

    # Iterate on all the records of the declarative memory creating a list of titles
    for record in records:
        stampa(str(record.payload['metadata']['titles'][0]),f"{record.payload['metadata']['titles'][0]}.txt")
        list_of_titles.append(record.payload['metadata']['titles'][0])

    #clean the list from duplicates  
    list_of_titles=list(set(list_of_titles))
    stampa(str(list_of_titles),"list_of_titles.txt")

@hook  # default priority = 1
def before_agent_starts(agent_input, cat):
    
    #analize the conversation and select the list of title usefull for conversation
    prompt_to_edit_question=f"""
    Analizza con attenzione la conversazione:\n '{agent_input['chat_history']}'\n
    Analizza con attenzione l'ultima domanda dell'utente:\n '{agent_input['input']}'\n
    Estrai dalla lista la stringa che più c'entra con la conversazione e con la domanda dell'utente: \n {list_of_titles}
    Fornisci come output il contenuto della stringa senza alcun commento.
    """
    stampa(str(prompt_to_edit_question),"prompt_to_search_the_metadata.txt")

    #call a global var in order to filter the metadata
    # global filtered_metadata
    topic_of_the_question = cat.llm(prompt_to_edit_question)

    agent_input['input']=agent_input['input']+ " ("+topic_of_the_question+")" 

    stampa(str(agent_input['input']), "agent_input.txt")

    return agent_input

# @hook
# def before_cat_recalls_declarative_memories(declarative_recall_config, cat):
#     ccat.
#     #filter the metadata based on conversation
#     stampa(str(cat.working_memory("chat_history")),"filtered_metadata1.txt")
#     # declarative_recall_config["metadata"] = {"titles": list(filtered_metadata)}

#     return declarative_recall_config

@hook
def after_rabbithole_splitted_text(chunks, cat):

    #create list o concatenated chunks
    concatenated_chunks_list = []
    concatenated_chunk_titles=[]
    global list_of_titles

    #load settings
    settings = cat.mad_hatter.get_plugin().load_settings()
    n_of_chunk_for_one_title = settings["n_of_chunk_for_one_title"]
    text_to_search_the_title = settings["text_to_search_the_title"]
    rule_1=settings["rule_1"]
    rule_2=settings["rule_2"]
    rule_3=settings["rule_3"]
    complete_prompt_for_tile_search=text_to_search_the_title + "\n" + rule_1 + "\n" + rule_2 + "\n" + rule_3
    prompt_for_question_generation =settings["prompt_for_question_generation"]

    # let's find titles and questions
    for i in range(0, len(chunks), n_of_chunk_for_one_title):
        # Select each chunk group
        chunk_group = chunks[i:i + n_of_chunk_for_one_title]
        # Concatenates the chunks
        concatenated_content = ''.join(chunk.page_content for chunk in chunk_group)
        concatenated_chunks_list.append(concatenated_content)        
        
        # Generate a title based on concatenated chunk and settings
        title = cat.llm(f"{complete_prompt_for_tile_search}\n Testo: \n {concatenated_content}")
        
        concatenated_chunk_titles.append(str(title))
        stampa(str(concatenated_chunk_titles),"concatenated_chunk_titles.txt")
        
        # Generates metadata title for the new doc
        metadata_of_the_new_doc = {}
        metadata_of_the_new_doc['titles'] = [title]
        
        # update list of title
        list_of_titles.append(title)
        list_of_titles=list(set(list_of_titles))
        stampa(str(list_of_titles),"list_of_titles_after_upload.txt")
        
        # Create a new chunk longer than others with the concatenated chunks 
        concatenated_content=title + ":\n" +concatenated_content
        questions=cat.llm(f"{prompt_for_question_generation}\n {concatenated_content}")
        concatenated_content= concatenated_content + ":\n\n" + questions
        concatenated_new_document = Document(page_content=concatenated_content, metadata=metadata_of_the_new_doc )
        chunks.append(concatenated_new_document)

        # add metadata title to each chunk of the group
        for chunk in chunk_group:
            chunk.metadata['titles'] = [title]
            chunk.page_content= title + ":\n" + chunk.page_content
            questions=cat.llm(f"{prompt_for_question_generation}\n {chunk.page_content}")
            chunk.page_content=chunk.page_content+ ":\n\n" + questions
            concatenated_chunks_list.append(chunk.metadata)
    
    # update list of metadata with the uploaded document

    return chunks



from cat.mad_hatter.decorators import hook
from langchain.docstore.document import Document
import os
import json


def save_list_to_json(data_list, filename, path="list_of_titles"):
    # Assicurati che il percorso esista, altrimenti crealo
    if not os.path.exists(path):
        os.makedirs(path)
    
    # Crea il percorso completo del file
    full_path = os.path.join(path, filename)
    
    # Scrivi la lista nel file JSON
    with open(full_path, 'w') as file:
        json.dump(data_list, file)

def read_list_from_json(filename, path="list_of_titles"):
    # Crea il percorso completo del file
    full_path = os.path.join(path, filename)
    
    # Verifica se il file esiste e non è vuoto
    if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
        return []  # Ritorna una lista vuota se il file non esiste o è vuoto
    
    # Leggi il contenuto del file JSON e ritorna la lista
    with open(full_path, 'r') as file:
        try:
            data_list = json.load(file)
        except json.JSONDecodeError:
            # Gestisci il caso in cui il file non è un JSON valido
            return []

    return data_list 

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


@hook
def after_cat_bootstrap(cat):
    # call global parameter so can be called through out the various hooks
    global list_of_titles
    # read from json file the possible tags
    list_of_titles=read_list_from_json("list_of_tags.json")

@hook
def before_cat_recalls_declarative_memories(declarative_recall_config, cat):
    
    global list_of_titles

    # call chat history
    chat_history=cat.working_memory.history
    # let's classify the chat history based on json tags
    metadata_to_be_filtered= cat.classify(chat_history, labels=list_of_titles)
    # filter the documentation based on classified chat hisotry tag
    declarative_recall_config["metadata"] = {"titles": metadata_to_be_filtered}
    return declarative_recall_config

@hook
def after_rabbithole_splitted_text(chunks, cat):

    #create list o concatenated chunks
    concatenated_chunks_list = []
    global list_of_titles

    #load settings and set n° of chunk to aggregrate in order to find the correct tag of each chunk without forget the context
    settings = cat.mad_hatter.get_plugin().load_settings()
    n_of_chunk_for_one_title = settings["n_of_chunk_for_one_title"]

    for i in range(0, len(chunks), n_of_chunk_for_one_title):
        # Select each chunk group
        chunk_group = chunks[i:i + n_of_chunk_for_one_title]
        # Concatenates the chunks
        concatenated_content = ''.join(chunk.page_content for chunk in chunk_group)
        concatenated_chunks_list.append(concatenated_content)        
        
        # Generate a title based on concatenated chunk and settings
        title = cat.classify(concatenated_content, labels=list_of_titles)
        
        # Generates metadata title for the new doc
        metadata_of_the_new_doc = {}
        metadata_of_the_new_doc['titles'] = title
        # Add to the documents to be uploaded the whole concatenated document 
        concatenated_new_document = Document(page_content=concatenated_content, metadata=metadata_of_the_new_doc )
        chunks.append(concatenated_new_document)

        # add metadata title to each chunk of the group
        for chunk in chunk_group:
            chunk.metadata['titles'] = title
            concatenated_chunks_list.append(chunk.metadata)

    return chunks


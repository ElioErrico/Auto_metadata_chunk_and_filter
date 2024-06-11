from cat.mad_hatter.decorators import hook,plugin
from langchain.docstore.document import Document
import os
import json


def save_json(datas, filename, path):
    # Assicurati che il percorso esista, altrimenti crealo
    if not os.path.exists(path):
        os.makedirs(path)
    
    # Crea il percorso completo del file
    full_path = os.path.join(path, filename)
    
    # Scrivi la lista aggiornata nel file JSON
    with open(full_path, 'w') as file:
        json.dump(datas, file)

    

def read_json(filename, path):
    # Crea il percorso completo del file
    full_path = os.path.join(path, filename)
    
    # Verifica se il file esiste e non è vuoto
    if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
        return ["no classification"]  # Ritorna una lista vuota se il file non esiste o è vuoto
    
    # Leggi il contenuto del file JSON e ritorna la lista
    with open(full_path, 'r') as file:
        try:
            datas = json.load(file)
        except json.JSONDecodeError:
            # Gestisci il caso in cui il file non è un JSON valido
            return ["no classification"]

    return datas 

def stampa(testo, nome_file, path):
    """
    Writes or appends text to a text file. If the file does not exist, creates it with the text as initial content.
    If the file exists, appends the text to the existing content.

    Args:
    testo (str): Text to be written or appended.
    nome_file (str): The name of the file.
    percorso (str): The directory path.
    """
    percorso_completo = os.path.join(path, nome_file)
    
    # Ensure the directory exists, otherwise create it
    if not os.path.exists(path):
        os.makedirs(path)
    
    # Determine the mode based on the existence of the file: append if it exists, write if not
    mode = 'a' if os.path.exists(percorso_completo) else 'w'
    
    # Write or append text to the file
    with open(percorso_completo, mode, encoding='utf-8') as file:
        file.write(testo + "\n")  # Append new text with a newline for readability

def get_current_directory():
    """
    Restituisce il percorso della cartella in cui è eseguito il file Python in esecuzione.
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    return current_directory

@hook
def after_cat_bootstrap(cat):
    
    # read from json file the possible tags
    directory=get_current_directory()
    list_of_titles=read_json("list_of_tags.json",directory)
    

@hook
def before_cat_recalls_declarative_memories(declarative_recall_config, cat):
    directory=get_current_directory()
    list_of_titles=read_json("list_of_tags.json",directory)
    
    # call chat history and user message
    user_message=cat.working_memory.user_message_json["text"]

    stringify_chat_history=cat.stringify_chat_history(latest_n=2)

# NOT WORKING SO GOOD TO KEEP TRACK OF DISCUSSIONS
#    metadata_to_be_filtered=cat.classify(user_message, labels=list_of_titles)
#    if "no classification" in metadata_to_be_filtered:        
#        metadata_to_be_filtered= cat.classify(stringify_chat_history, labels=list_of_titles)        
#        if "no classification" in metadata_to_be_filtered:
#            return declarative_recall_config
    
    metadata_to_be_filtered= cat.classify(stringify_chat_history, labels=list_of_titles)        
    
    declarative_recall_config["metadata"] = {"titles": metadata_to_be_filtered}
    return declarative_recall_config


@plugin
def save_settings(settings):

    directory=get_current_directory()
    old_settings=read_json("settings.json", directory)
    
    if settings["upload_document_with_following_tag"] != old_settings["upload_document_with_following_tag"]:

        if settings["upload_document_with_following_tag"]==False and settings["create_tag_with_prompt"]==False:
            settings["upload_document_with_following_tag"]=False
            settings["create_tag_with_prompt"]=False
            save_json(settings, "settings.json", directory)
            return settings
        elif old_settings["upload_document_with_following_tag"]==False and old_settings["create_tag_with_prompt"]==False and settings["upload_document_with_following_tag"]==True and settings["create_tag_with_prompt"]==True:
            settings["upload_document_with_following_tag"]=False
            settings["create_tag_with_prompt"]=True
            save_json(settings, "settings.json", directory)             
        else:
            settings["create_tag_with_prompt"] = not settings["upload_document_with_following_tag"]

    elif settings["create_tag_with_prompt"] != old_settings["create_tag_with_prompt"]:

        if settings["upload_document_with_following_tag"]==False and settings["create_tag_with_prompt"]==False:
            settings["upload_document_with_following_tag"]=False
            settings["create_tag_with_prompt"]=False
            save_json(settings, "settings.json", directory)            
            return settings
        elif old_settings["upload_document_with_following_tag"]==False and old_settings["create_tag_with_prompt"]==False and settings["upload_document_with_following_tag"]==True and settings["create_tag_with_prompt"]==True:
            settings["upload_document_with_following_tag"]=False
            settings["create_tag_with_prompt"]=True
            save_json(settings, "settings.json", directory)  
        else:       
            settings["upload_document_with_following_tag"] = not settings["create_tag_with_prompt"]

    save_json(settings, "settings.json", directory)

    return settings


@hook
def after_rabbithole_splitted_text(chunks, cat):

    #create list o concatenated chunks
    concatenated_chunks_list = []
    directory=get_current_directory()
    list_of_titles=read_json("list_of_tags.json",directory)
    
    #load settings and set n° of chunk to aggregrate in order to find the correct tag of each chunk without forget the context
    settings = cat.mad_hatter.get_plugin().load_settings()

    n_of_chunk_for_one_title = settings["n_of_chunk_for_one_title"]
    create_tag_with_prompt=settings["create_tag_with_prompt"]
    search_for_title_prompt=settings["search_for_title_prompt"]

    upload_document_with_following_tag=settings["upload_document_with_following_tag"]
    tag_to_archive_in_metadata=settings["tag_to_archive_in_metadata"]

    for i in range(0, len(chunks), n_of_chunk_for_one_title):
        # Select each chunk group
        chunk_group = chunks[i:i + n_of_chunk_for_one_title]
        # Concatenates the chunks
        concatenated_content = ''.join(chunk.page_content for chunk in chunk_group)
        concatenated_chunks_list.append(concatenated_content)        
        
        # Generate a title based on concatenated chunk and settings
        if create_tag_with_prompt==False and upload_document_with_following_tag==False:
            title = cat.classify(concatenated_content, labels=list_of_titles)
        elif create_tag_with_prompt==True and upload_document_with_following_tag==False:
            title = cat.classify(concatenated_content, labels=list_of_titles)
            if "no classification" in title :
                title = cat.llm(search_for_title_prompt +"\n"+ concatenated_content)
                list_of_titles.append(title)
                list_of_titles=list(set(list_of_titles))
                save_json(list_of_titles,"list_of_tags.json",directory)
        elif create_tag_with_prompt==False and upload_document_with_following_tag==True:
                title = tag_to_archive_in_metadata
                list_of_titles.append(title)
                list_of_titles=list(set(list_of_titles))
                save_json(list_of_titles,"list_of_tags.json",directory)

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

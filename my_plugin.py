from cat.mad_hatter.decorators import hook
import os

def stampa(testo, nome_file, percorso="C:\\Users\\elio.errico\\Desktop\\python\\cheshire-cat-main\\core-main\\core"):
    
    percorso_completo = os.path.join(percorso, nome_file)
    
    # Assicurarsi che la cartella esista, altrimenti crearla
    if not os.path.exists(percorso):
        os.makedirs(percorso)
    
    # Scrivere il testo nel file
    with open(percorso_completo, 'w', encoding='utf-8') as file:
        file.write(testo)  

    return 



@hook  # default priority = 1
def before_rabbithole_splits_text(doc, cat):

    # nome_file="01_before_rabbithole_splits_text.txt"
    nome_file=str(doc[0].metadata['source'])
    content = str(doc[0].page_content)


    title=cat.llm(f"Trova un titolo conciso di 4 parole che descriva al meglio il seguente testo:\n {content}")
    doc[0].metadata["title"]=title
    metadata =str(doc[0].metadata)
    # titolo = "titolo= " + str(doc[0].metadata['title'])
    # testo=  content + "\n \n \n \n \n \n" + metadata + "\n \n \n \n \n \n" + titolo
    # stampa(testo,nome_file)

    return doc


@hook  # default priority = 1
def after_rabbithole_splitted_text(chunks, cat):

    for chunk in chunks:
        titolo_chunk =str(chunk.metadata['title'])
        testo_chunk=str(chunk.page_content)
        testo_chunk_con_titolo=titolo_chunk+":\n"+testo_chunk

        chunk.page_content=testo_chunk_con_titolo

    return chunks

# Auto metadata chunk and filter

This plugin:
1) classify your documents with metadata 
2) filter your documents filters by metadata.

## How it works???

1) Concatenates a parameterizable number of chunks (set the number in settings)
2) Reads the possible metadata in list_of_tags.json (You could edit the list depending on your documentation, Do not cancel "no classification" from the list)
3) Evaluates what is the correct metadata for each chunk analizing the concatenated content and classifies it using the list in list_of_tags.json
5) Upload each chunk that composes the concatenated content with the discoreved metadada
6) If the cat cannot find the correct metadata, generates a possible metadata of the chunk (set the prompt and/or disable this function from settings)
7) Before recalling declarative memory analyses and classifies the chat_history using same list_of_tags.json and filters the documentation
8) If you want you can add your metadata directly as an input avoiding the CAT to classify the DOC (to be setted in settings)

## How to use it:

1) edit the list_of_tags.json with the keywords of your document
2) the cat will classify your documentation with the list of the keywords (if you don't edit list_of_tags.json the cat will create the metadata)
3) If you want you can add your metadata directly as an input avoiding the CAT to classify the DOC
4) upload the document
5) chat with the cat

![image](https://github.com/ElioErrico/Auto_metadata_chunk_and_filter/assets/143315119/5e9c4d53-8682-4f06-a133-05f64edc1300)

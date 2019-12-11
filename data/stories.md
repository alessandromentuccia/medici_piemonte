## Happy path 1
* greet
  - utter_greet
* query_knowledge_list
  - action_query_list
* goodbye
  - utter_goodbye

## Happy path 2
* greet
  - utter_greet
* query_knowledge_list
  - action_query_list
* query_knowledge_attribute_of
  - action_query_attribute
* goodbye
  - utter_goodbye

## Hello
* greet
- utter_greet

## Bye
* goodbye
- utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot

## Query Knowledge Base
* query_knowledge_list
  - action_query_list

## Query Knowledge Base
* query_knowledge_attribute_of
  - action_query_attribute
  - slot{"object_type": "medico"}

## Query Knowledge Base
* query_knowledge_attribute_of
  - action_query_attribute
  - slot{"object_type": "ambulatorio"}

## Query Knowledge Base
* query_knowledge_attribute_of
  - action_query_attribute
  - slot{"object_type": "orario"}
## Query Knowledge Base
* query_knowledge_attribute_of{"attribute": "nome", "cognome": "Torino"}
    - slot{"attribute": "nome"}
    - slot{"cognome": "Torino"}
    - action_query_attribute
    - slot{"object_type": "medico"}
    - slot{"attribute": null}
    - slot{"mention": null}
    - slot{"knowledge_base_last_object": "TORINO"}
    - slot{"knowledge_base_last_object_type": "medico"}
    - slot{"cognome": null}
* query_knowledge_list{"object_type": "medico", "denom_comune": "Torino"}
    - slot{"denom_comune": "Torino"}
    - slot{"object_type": "medico"}
    - action_query_list
    - slot{"object_type": "medico"}
    - slot{"mention": null}
    - slot{"attribute": null}
    - slot{"knowledge_base_last_object": null}
    - slot{"knowledge_base_last_object_type": "medico"}
    - slot{"knowledge_base_listed_objects": ["D ADDONA", "D ADDONA", "D ADDONA", "D ADDONA", "D ADDONA", "POGLIANO", "POGLIANO", "POGLIANO", "POGLIANO", "POGLIANO", "BUSCA", "BUSCA", "BUSCA", "BUSCA", "BUSCA", "GRASSINO SANTORO", "GRASSINO SANTORO", "GRASSINO SANTORO", "GRASSINO SANTORO", "GRASSINO SANTORO", "MOSCA", "MOSCA", "MOSCA", "MOSCA", "MOSCA"]}
    - slot{"denom_comune": null}
* query_knowledge_list{"object_type": "ambulatorio", "denom_comune": "Torino"}
    - slot{"denom_comune": "Torino"}
    - slot{"object_type": "ambulatorio"}
    - action_query_list
    - slot{"object_type": "ambulatorio"}
    - slot{"mention": null}
    - slot{"attribute": null}
    - slot{"knowledge_base_last_object": null}
    - slot{"knowledge_base_last_object_type": "ambulatorio"}
    - slot{"knowledge_base_listed_objects": ["TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO", "TORINO"]}
    - slot{"denom_comune": null}
* query_knowledge_list{"object_type": "medico", "denom_comune": "Torino"}
    - slot{"denom_comune": "Torino"}
    - slot{"object_type": "medico"}
    - action_query_list
    - slot{"object_type": "medico"}
    - slot{"mention": null}
    - slot{"attribute": null}
    - slot{"knowledge_base_last_object": null}
    - slot{"knowledge_base_last_object_type": "medico"}
    - slot{"knowledge_base_listed_objects": ["D ADDONA", "D ADDONA", "D ADDONA", "D ADDONA", "D ADDONA", "POGLIANO", "POGLIANO", "POGLIANO", "POGLIANO", "POGLIANO", "BUSCA", "BUSCA", "BUSCA", "BUSCA", "BUSCA", "GRASSINO SANTORO", "GRASSINO SANTORO", "GRASSINO SANTORO", "GRASSINO SANTORO", "GRASSINO SANTORO", "MOSCA", "MOSCA", "MOSCA", "MOSCA", "MOSCA"]}
    - slot{"denom_comune": null}

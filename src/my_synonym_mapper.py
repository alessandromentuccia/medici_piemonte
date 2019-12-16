import os
import warnings
import json
from typing import Any, Optional, Text, Dict

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.tokenizers import Token, Tokenizer
from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.constants import (
    MESSAGE_RESPONSE_ATTRIBUTE,
    MESSAGE_INTENT_ATTRIBUTE,
    MESSAGE_TEXT_ATTRIBUTE,
    MESSAGE_TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
    MESSAGE_SPACY_FEATURES_NAMES,
    MESSAGE_VECTOR_FEATURE_NAMES,
)
import rasa.utils.io 

SYNONYM_TABLE_FILE = 'synonym_table.json'

class SynonymMapper(Component):
    """A custom sentiment analysis component"""
    name = "my_synonym_mapper"
    provides = ["tokens"]
    requires = ["tokens"]
    defaults = {}
    language_list = ["en", "it"]
    print(f'initialised the {name}')


    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        synonyms = self._load_synonyms()
        self.synonyms = synonyms if synonyms else {}
        super().__init__(component_config)
    
    def _load_synonyms(self) -> Dict:
        """Try to load synonyms from json.
            The file must be in the same dir of this file"""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, SYNONYM_TABLE_FILE)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as fp:
                synonyms = json.load(fp)
        else:
            synonyms = None
            warnings.warn(
                f"Failed to load synonyms file from '{file_path}' \n The '{SYNONYM_TABLE_FILE}' \
                must be in the same directory of my_synonym_mapper.py."
            )
        return synonyms


    def train(self, training_data: TrainingData, config: RasaNLUModelConfig, **kwargs: Any) -> None:
        """Not implemented"""
        #TODO: should we map the words in the examples in the same way ?
        
    def process(self, message: Message, **kwargs: Any) -> None:
        """Retrieve the tokens of the new message, maps words to synonyms 
            if they are presents in the synonym table."""

        tokens = message.get("tokens")
        self._replace_synonyms(tokens)

        message.set(MESSAGE_TOKENS_NAMES[MESSAGE_TEXT_ATTRIBUTE], tokens)

    def _replace_synonyms(self, tokens) -> None:
        """Mapp synonym if the word is present in the synonyms,
           leave the same word otherwise.
           The token is process in lowercase """
        for t in tokens:
            t.text = self.synonyms.get(t.text.lower(), t.text)

    def persist(self, file_name, model_dir):
        """Persist the synonym model into the passed directory."""
        
        # if self.synonyms:
        #     file_name = file_name + ".json"
        #     entity_synonyms_file = os.path.join(model_dir, file_name)
        #     write_json_to_file(
        #         entity_synonyms_file, self.synonyms, separators=(",", ": ")
        #     )
        #     return {"file": file_name}
        # else:
        #     return {"file": None}


    
    # @classmethod
    # def load(
    #     cls,
    #     meta: Dict[Text, Any],
    #     model_dir: Optional[Text] = None,
    #     model_metadata: Optional[Metadata] = None,
    #     cached_component: Optional["SynonymMapper"] = None,
    #     **kwargs: Any,
    # ) -> "SynonymMapper":

    #     synonyms_file = os.path.join(model_dir, SYNONYM_TABLE_FILE)
    #     if os.path.isfile(synonyms_file):
    #         synonyms = rasa.utils.io.read_json_file(synonyms_file)
    #     else:
    #         synonyms = None
    #         warnings.warn(
    #             f"Failed to load synonyms file from '{synonyms_file}'."
    #         )
    #     return cls(meta, synonyms)

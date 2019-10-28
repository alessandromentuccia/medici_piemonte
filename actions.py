from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase
from rasa_sdk.events import SlotSet
from neo4jstorage import Neo4jKnowledgeBase
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
import logging
from typing import Text, Callable, Dict, List, Any, Optional
from collections import defaultdict
from rasa_sdk.knowledge_base.utils import (
    SLOT_OBJECT_TYPE,
    SLOT_LAST_OBJECT_TYPE,
    SLOT_ATTRIBUTE,
    reset_attribute_slots,
    SLOT_MENTION,
    SLOT_LAST_OBJECT,
    SLOT_LISTED_OBJECTS,
    get_object_name,
    get_attribute_slots,
    resolve_mention
)

logger = logging.getLogger("rasa_sdk."+__name__)

# superclasse
class ActionPersona(ActionQueryKnowledgeBase):
    def safe_cast(self, val, to_type, default=''):
      try:
        return to_type(val)
      except (ValueError, TypeError):
        return default

    def __init__(self):
        # load knowledge base with data from the given file
        knowledge_base = Neo4jKnowledgeBase("bolt://sdnet-convplat1.sdp.csi.it:7687", "neo4j", "test")  #sdnet-convplat1.sdp.csi.it:7687  #localhost:7687

        # overwrite the representation function of the hotel object
        # by default the representation function is just the name of the object
        knowledge_base.set_representation_function_of_object(
            "doctor", lambda obj: obj["nome"] + " " + obj["cognome"] + " ( " + obj["comune"]  + " ) "
        )

        knowledge_base.set_entity_mapping(
            'doctor', lambda entity: 'Doctor' if (entity == 'doctor') else entity
        )

        knowledge_base.set_key_attribute_of_object('doctor','cognome')
        # definition of function to field and value for query

        knowledge_base.set_attribute_operator(
            lambda entity,attribute: 'contains' if (entity == 'doctor' and attribute in ('indirizzo, distretto, comune')) else '='
        )

       # knowledge_base.attribute_syn =[ {"telefono", "cellulare", "breve"}, {"direzione", "area_ufficio", "posizione_organizzativa"}];
        super().__init__(knowledge_base)

    
    def utter_attribute_value(
        self,
        dispatcher: CollectingDispatcher,
        object_name: Text,
        attribute_name: Text,
        attribute_value: Text,
    ) -> None:
        """
        Utters a response that informs the user about the attribute value of the
        attribute of interest.
        Args:
            dispatcher: the dispatcher
            object_name: the name of the object
            attribute_name: the name of the attribute
            attribute_value: the value of the attribute
        """
        if attribute_value:
            dispatcher.utter_message(
                "'{}' ha il valore '{}' per l'attributo '{}'.".format(
                    object_name, attribute_value, attribute_name
                )
            )
        else:
            dispatcher.utter_message(
                "Non ho trovato nessun valore valido per l'attributo '{}' di '{}'.".format(
                    attribute_name, object_name
                )
            )

    def utter_objects(
        self,
        dispatcher: CollectingDispatcher,
        object_type: Text,
        objects: List[Dict[Text, Any]],
        attributes: List[Dict[Text, Text]]
    ) -> None:
        """
        Utters a response to the user that lists all found objects.
        Args:
            dispatcher: the dispatcher
            object_type: the object type
            objects: the list of objects
        """
        if not attributes or len(attributes)==0:
            dispatcher.utter_message(
                "Non ho capito a chi fossi interessato, prova a spiegarmi diversamente cosa cerchi."
            )
            return
        else:
            dispatcher.utter_message("Ho cercato per le seguenti condizioni:")
            for attribute in attributes:
                synfound = False
                for attribute_syn_list in self.knowledge_base.attribute_syn:
                    if attribute["name"] in attribute_syn_list:  
                        synfound = True
                        synlist = []
                        for syn in attribute_syn_list:
                            synlist.append(syn)
                        dispatcher.utter_message(("{}: {}".format(",".join(synlist), attribute["value"])))
                if not synfound:
                    dispatcher.utter_message(("{}: {}".format(attribute["name"], attribute["value"])))

        if objects:
            if (len(objects)==25):
                dispatcher.utter_message(
                 "e ho trovato molti risultati, eccoti i primi 25:"
                )
            else:
                dispatcher.utter_message(
                 "ed ecco i risultati:"
                )

            repr_function = self.knowledge_base.get_representation_function_of_object(
                object_type
            )

            for i, obj in enumerate(objects, 1):
                dispatcher.utter_message("{}: {}".format(i, repr_function(obj)))
        else:
            dispatcher.utter_message(
                "Mi spiace, non ho trovato nessun risultato."
            )



## cerca anche per contenuti-> chi lavora nella direzione P.A. digitale
## quali sono i progettisti nella stanza 115?
## quale è il cellulare del primo? <- non va?
## quale è la sede di parodi claudio?
## chi lavora nell'area big data nell'ufficio T11?
## quali sono gli analista nell'ufficio t11?

## TODO
## aggiungere sinonimi sono->lavora->è nella sede
## chi risponde al breve 9455? <- prende unità organizzativa invece che numeor
## gestire la relazione chi è nello stesso ufficio/direzione/ di pippo?
## gestire il caso: dammi tutti i dettagli di .....
## mettere elenco direzioni come entities su graph
class ActionPersonaList(ActionPersona):
       
   

    def name(self):
        return "action_query_list"



    def run(self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """
        Executes this action. If the user ask a question about an attribute,
        the knowledge base is queried for that attribute. Otherwise, if no
        attribute was detected in the request or the user is talking about a new
        object type, multiple objects of the requested type are returned from the
        knowledge base.
        Args:
            dispatcher: the dispatcher
            tracker: the tracker
            domain: the domain
        Returns: list of slots
        """
        logger.info("action_query_list")
        object_type = tracker.get_slot(SLOT_OBJECT_TYPE)
        last_object_type = tracker.get_slot(SLOT_LAST_OBJECT_TYPE)
        attribute = tracker.get_slot(SLOT_ATTRIBUTE)

        new_request = object_type != last_object_type

        if not object_type:
            self.knowledge_base.default_object_type = 'doctor'

        logger.info('query objects attr:'+str(attribute) +' new_req:'+str(new_request))
        return self._query_objects_my(dispatcher, tracker)

        dispatcher.utter_template("utter_ask_rephrase", tracker)
        return []

    def _query_objects_my(
        self, dispatcher: CollectingDispatcher, tracker: Tracker
    ) -> List[Dict]:
        """
        Queries the knowledge base for objects of the requested object type and
        outputs those to the user. The objects are filtered by any attribute the
        user mentioned in the request.
        Args:
            dispatcher: the dispatcher
            tracker: the tracker
        Returns: list of slots
        """
        object_type = tracker.get_slot(SLOT_OBJECT_TYPE)
        object_attributes = self.knowledge_base.get_attributes_of_object(object_type)

        # get all set attribute slots of the object type to be able to filter the
        # list of objects
        attributes = get_attribute_slots(tracker, object_attributes)
        # query the knowledge base
        objects = self.knowledge_base.get_objects(object_type, attributes,object_identifier=None)

        self.utter_objects(dispatcher, object_type, objects, attributes)

        if not objects:
            return reset_attribute_slots(tracker, object_attributes)

        key_attribute = self.knowledge_base.get_key_attribute_of_object(object_type)

        last_object = None if len(objects) > 1 else objects[0][key_attribute]

        slots = [
            SlotSet(SLOT_OBJECT_TYPE, object_type),
            SlotSet(SLOT_MENTION, None),
            SlotSet(SLOT_ATTRIBUTE, None),
            SlotSet(SLOT_LAST_OBJECT, last_object),
            SlotSet(SLOT_LAST_OBJECT_TYPE, object_type),
            SlotSet(
                SLOT_LISTED_OBJECTS, list(map(lambda e: e[key_attribute], objects))
            ),
        ]

        return slots + reset_attribute_slots(tracker, object_attributes)


class ActionAttributoPersona(ActionPersona):
       
    
    def name(self):
        return "action_query_attribute"
    

    def run(self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """
        Executes this action. If the user ask a question about an attribute,
        the knowledge base is queried for that attribute. Otherwise, if no
        attribute was detected in the request or the user is talking about a new
        object type, multiple objects of the requested type are returned from the
        knowledge base.
        Args:
            dispatcher: the dispatcher
            tracker: the tracker
            domain: the domain
        Returns: list of slots
        """
        logger.info("action_query_attribute_of")
        object_type = tracker.get_slot(SLOT_OBJECT_TYPE)
        last_object_type = tracker.get_slot(SLOT_LAST_OBJECT_TYPE)
        attribute = tracker.get_slot(SLOT_ATTRIBUTE)

        new_request = object_type != last_object_type

        if not object_type:
            self.knowledge_base.default_object_type = 'doctor'

        logger.info('query attribute attr:'+str(attribute) +' new_req:'+str(new_request))
        return self._query_attribute(dispatcher, tracker)

        dispatcher.utter_template("utter_ask_rephrase", tracker)
        return []


    def _get_object_name(self,
            tracker: "Tracker",
            ordinal_mention_mapping: Dict[Text, Callable],
            use_last_object_mention: bool = True,
    ) -> Optional[Text]:
        """
        Get the name of the object the user referred to. Either the NER detected the
        object and stored its name in the corresponding slot (e.g. "PastaBar"
        is detected as "restaurant") or the user referred to the object by any kind of
        mention, such as "first one" or "it".
        Args:
            tracker: the tracker
            ordinal_mention_mapping: mapping that maps an ordinal mention to an object in a list
            use_last_object_mention: if true the last mentioned object is returned if
            no other mention could be detected
        Returns: the name of the actual object (value of key attribute in the
        knowledge base)
        """
        mention = tracker.get_slot(SLOT_MENTION)
        object_type = tracker.get_slot(SLOT_OBJECT_TYPE)

        # the user referred to the object by a mention, such as "first one"
        if mention:
            return resolve_mention(tracker, ordinal_mention_mapping)

        object_name = tracker.get_slot("cognome")
        if object_name:
            logger.info("using cognome"+object_name)
            return object_name

        # check whether the user referred to the objet by its name
        object_name = tracker.get_slot(object_type)
        if object_name:
            logger.info("using object type"+object_name)
            return object_name



        if use_last_object_mention:
            # if no explicit mention was found, we assume the user just refers to the last
            # object mentioned in the conversation
            return tracker.get_slot(SLOT_LAST_OBJECT)

        return None


    def _query_attribute(
        self, dispatcher: CollectingDispatcher, tracker: Tracker
    ) -> List[Dict]:
        """
        Queries the knowledge base for the value of the requested attribute of the
        mentioned object and outputs it to the user.

        Args:
            dispatcher: the dispatcher
            tracker: the tracker

        Returns: list of slots
        """
        object_type = tracker.get_slot(SLOT_OBJECT_TYPE)
        attribute = tracker.get_slot(SLOT_ATTRIBUTE)

        object_name = self._get_object_name(
            tracker,
            self.knowledge_base.ordinal_mention_mapping,
            self.use_last_object_mention,
        )



        logger.info("_query_attribute [object_type]:"+str(object_type) + " [attribute]:"+str(attribute)+" [object_name]:"+str(object_name))

        if not object_name or not attribute:
            logger.info("object_name or attribute not available")
            dispatcher.utter_template("utter_ask_rephrase", tracker)
            return [SlotSet(SLOT_MENTION, None)]

        object_attributes = self.knowledge_base.get_attributes_of_object(object_type)

        # get all set attribute slots of the object type to be able to filter the
        # list of objects
        attributes = get_attribute_slots(tracker, object_attributes)
        # query the knowledge base

        objects = self.knowledge_base.get_objects(object_type,attributes,object_name)
        key_attribute = self.knowledge_base.get_key_attribute_of_object(object_type)

        if not objects or attribute not in objects[0]:
            logger.info("object not found or attribute not in objects[0]")
            dispatcher.utter_template("utter_ask_rephrase", tracker)
            return [SlotSet(SLOT_MENTION, None)] + reset_attribute_slots(tracker, object_attributes)

        if len(objects) >1 :
            dispatcher.utter_message("Ho trovato più di un risultato:")
            
        for object_of_interest in objects:
            value = object_of_interest[attribute]
            repr_function = self.knowledge_base.get_representation_function_of_object(
                object_type
            )
            object_representation = repr_function(object_of_interest)
            key_attribute = self.knowledge_base.get_key_attribute_of_object(object_type)
            object_identifier = object_of_interest[key_attribute]

            self.utter_attribute_value(dispatcher, object_representation, attribute, value)

        slots = [
            SlotSet(SLOT_OBJECT_TYPE, object_type),
            SlotSet(SLOT_ATTRIBUTE, None),
            SlotSet(SLOT_MENTION, None),
            SlotSet(SLOT_LAST_OBJECT, object_identifier),
            SlotSet(SLOT_LAST_OBJECT_TYPE, object_type),
        ]

        return slots + reset_attribute_slots(tracker, object_attributes)
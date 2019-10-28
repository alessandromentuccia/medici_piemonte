from rasa_sdk.knowledge_base.storage import KnowledgeBase
import logging
from typing import Text, Callable, Dict, List, Any, Optional
from collections import defaultdict
from neo4j.v1 import GraphDatabase

logger = logging.getLogger("rasa_sdk."+__name__)

class Neo4jKnowledgeBase(KnowledgeBase):
    def __init__(self,  url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.entity_mapping_function = lambda object: str(object)
        self.attribute_field_function = lambda object_type, attribute: "TOUPPER"
        self.attribute_value_function = lambda object_type, attribute, value: "TOUPPER('"+value+"')"
        self.attribute_operator_function = lambda object_type, attribute: "="
        self.attribute_syn = [ {}]
        super(Neo4jKnowledgeBase, self).__init__()

    def set_entity_mapping(
        self, object_type: Text, entity_mapping_function: Callable
    ) -> None:
        self.entity_mapping_function = entity_mapping_function

    def set_attribute_field(
        self, attribute_field_function: Callable
    ) -> None:
        self.attribute_field_function = attribute_field_function

    def set_attribute_value(
        self, attribute_value_function: Callable
    ) -> None:
        self.attribute_value_function = attribute_value_function

    def set_attribute_operator(
        self, attribute_operator_function: Callable
    ) -> None:
        self.attribute_operator_function = attribute_operator_function

    def set_representation_function_of_object(
        self, object_type: Text, representation_function: Callable
    ) -> None:
        """
        Set the representation function of the given object type.

        Args:
            object_type: the object type
            representation_function: the representation function
        """
        self.representation_function[object_type] = representation_function

    def set_key_attribute_of_object(
        self, object_type: Text, key_attribute: Text
    ) -> None:
        """
        Set the key attribute of the given object type.

        Args:
            object_type: the object type
            key_attribute: the name of the key attribute
        """
        self.key_attribute[object_type] = key_attribute

    def get_attributes_of_object(self, object_type: Text) -> List[Text]:

        query = "MATCH(n:"+self.entity_mapping_function(object_type) +")"+ """
                    WITH LABELS(n) AS labels , KEYS(n) AS keys
                    UNWIND labels AS label
                    UNWIND keys AS key
                    RETURN DISTINCT label, COLLECT(DISTINCT key) AS props
                    ORDER BY label"""
        
        result = self.query_db(query)
        
        result_count = 0
        attribute = []
        for ris in result:
            result_count += 1
            attribute = ris["props"]

        logger.info('Result Attribute of '+object_type+' '+str(attribute))
        return attribute

    def get_objects(
        self, object_type: Text, attributes: List[Dict[Text, Text]],object_identifier: Text, limit: int = 5
    ) -> List[Dict[Text, Any]]:

        query = "MATCH(n:"+self.entity_mapping_function(object_type) +")" 

        ## todo portare fuori questa definizione
        

        logger.info("query objects:"+str(attributes))

        if object_identifier or attributes:
            query += ' WHERE '
            wherecond = []
        else:
            return None

        if object_identifier:
            wherecond.append(
                " TOUPPER(n." + self.get_key_attribute_of_object(object_type) +
                ") = TOUPPER('" + object_identifier +"') ")

        # filter objects by attributes
        if attributes:
            for attribute in attributes:
                synfound = False
                for attribute_syn_list in self.attribute_syn:
                    if attribute["name"] in attribute_syn_list:  
                        synfound = True
                        synwherecond = []
                        for syn in attribute_syn_list:
                            synwherecond.append(self.attribute_field_function(object_type,syn)+ 
                            "(n."+syn+") "+ self.attribute_operator_function(object_type,syn) +" "+
                            self.attribute_value_function(object_type,syn,attribute["value"].replace("'","\\'"))
                            +" " )
                        wherecond.append("("+  " OR ".join(synwherecond) +")")
                if not synfound:
                    wherecond.append(self.attribute_field_function(object_type,attribute["name"])+ 
                    "(n."+attribute["name"]+") "+ self.attribute_operator_function(object_type,attribute["name"]) +" "+
                    self.attribute_value_function(object_type,attribute["name"],attribute["value"].replace("'","\\'"))
                    +" " )
        
        query += " AND ".join(wherecond)


        query += ' RETURN n LIMIT 25'

        result = self.query_db(query)

        objects = []


        for record in result:
            entity =  {}
            for k, v in record['n'].items():
               entity[k] = str(v)
            objects.append(entity)

        print(objects)

        return objects

    def access_db(self):
        """Used to access the Neo4J DB"""
        try:
            driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        except Exception:
            raise ConnectionError
        return driver

    def query_db(self, query):
        """Receives a query to execute on the DB"""

        driver = self.access_db()
        logger.info('Obtained driver for querying Neo4J database')
        session = driver.session()
        logger.info('Created session through driver for querying')
        logger.info('Query: %s', query)
        
        with session.begin_transaction() as _tx:
            result = _tx.run(query)
        return result

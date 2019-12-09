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
        self.dict_attr = {} #dizionario contenente la mappatura degli attributi con i nomi sul db
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

    """funzione che crea un dictionary per il mapping tra attributi ed entity"""
    def set_entity_attribute_mapping(self, object_type: Text,  attributi: List[Dict[Text,Text]]): 
        logger.debug("inizio estrazione tabella dal db per attributi: %s", object_type)

        entity = [self.entity_mapping_function(object_type)]
        assobject = self.get_association_of_object(object_type)
        for ass in assobject:
            if type(ass) is list:
                for a in ass:
                    entity.append(a)
            else:
                entity.append(ass)
        logger.debug("log del contenuto di entity: %s", entity)
        query = ""
        plus_query = ""
        if attributi:
            for attributo in attributi: #per ogni attributo a cui associare la tabella
                for ent in entity: #per ogni tabella in relazione con l'entity  
                    query_initial = "OPTIONAL MATCH ("+ ent +":"+ ent +")" 
                    plus_query = " RETURN DISTINCT "+ ent +"."+ attributo['name'] +" As Result  Limit 1"
                    logger.debug("sviluppo mapping per attributo: " + str(attributo['name']) + " e entity " + ent)
                    
                    query += query_initial + plus_query
                    logger.debug("query parziale per l'attributo " + str(attributo['name']) +": " + query)
                    
                    result = self.query_db(query)    
                    for res in result:
                        if res['Result'] != None and ent +"."+ attributo['name'] not in self.dict_attr.keys():
                            self.dict_attr[attributo['name']] = ent + "." + attributo['name']
                            logger.debug("info attributo inserito in dict: " + str(attributo['name']))
                        else: 
                            logger.debug("attributo gia presente nel dict: " + str(attributo['name']))
                    query = "" 

    """Mi restituisce una lista con i nomi degli attributi di un entity"""
    """da generalizzare, in questo caso la query non è generalizzata"""
    def get_attributes_of_object(self, object_type: Text) -> List[Text]:

        #"+self.entity_mapping_function(object_type) +"
        query = "MATCH(n:Medici)-[rel1]-(m)-[rel2]-(o)"+ """ 
                    WITH LABELS(n) AS labels , KEYS(n)+KEYS(m)+KEYS(o) AS keys
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

    """restituisce la rete di relazioni di un entity"""
    def get_association_of_object(self, object_type: Text) -> List[List[Text]]:

        query = "MATCH (n:"+self.entity_mapping_function(object_type)+")-[first_rel]-(medium)" + """
                 OPTIONAL MATCH (medium)-[second_rel]-(last) WHERE NOT medium = last AND NOT type(first_rel) = type(second_rel)
                 RETURN DISTINCT type(first_rel) As first_rel, labels(medium) As medium, type(second_rel) As second_rel, labels(last) As last"""

        result = self.query_db(query)

        relation0 = []
        table0 = [] #lista delle tabelle trovate
        for res in result:
            print(res)
            if res['first_rel'] != None: 
                logger.debug('prima verifica')
                if res['second_rel'] != None and res['first_rel'] not in relation0: #elimino il caso per cui esistono relazioni parziali
                    logger.debug('seconda verifica')
                    relation0.append([res['first_rel'], res['second_rel']]) 
                    logger.debug('relazioni listate')         #sul db ci stanno 2 relazioni per l'entity dichiarata
                    r1 = str(res['medium'][0])
                    r3 = str(res['last'][0])
                    table0.append([r1, r3]) #accorgimento...sul db sono in una lista singola
                    logger.debug('table listate')
                    logger.debug(" sul db ci sono 2 relazioni in cascata per l'entity dichiarata: " + r1 + " ed " + r3)
                elif not any(res['first_rel'] in x for x in relation0):
                    logger.debug('else condition')
                    relation0.append(res['first_rel'])
                    r1= str(res['medium'][0])
                    table0.append(r1)
                    logger.debug(" sul db c'è 1 relazione per l'entity dichiarata: " + res['first_rel'] +", "+ r1)
                else:
                    logger.debug("non si hanno nuove relazioni")                
            else:
                logger.error('non ha trovato relazioni')

        logger.info("Result Associated object of "+object_type+": %s", str(table0))
        return table0

    def get_objects(
        self, object_type: Text, attributes: List[Dict[Text, Text]],object_identifier: Text, limit: int = 5
    ) -> List[Dict[Text, Any]]:
        
        #fase di associazione delle relazioni alla query
        plus_query = ""
        plus_query_moment = [] #lista in cui inserisco le query parziali create
        ass_object = self.get_association_of_object(object_type)
        if ass_object:
            for j in range(len(ass_object)): 
                if type(ass_object[j]) is list:
                    ass_object00 = ass_object[j]
                    for i in range(len(ass_object00)):
                        plus_query =  plus_query + "-[]-("+ass_object00[i]+")"
                    plus_query_moment.append(plus_query)
                else:
                    plus_query = "-[]-("+ass_object[j]+")" 
                    plus_query_moment.append(plus_query)
        
            logger.info("query objects:"+str(attributes))

            #fase di mapping degli attributi richiesti ed il nome dell'attributo sul db insieme alla tabella
            #self.dict_attr = {}
            self.set_entity_attribute_mapping(object_type, attributes)
            logger.debug("dict_attr: %s", self.dict_attr)

            #ricavare solo il nome delle tabelle dagli attributi
            table = ""
            for att in attributes:
                if self.dict_attr[att["name"]]:
                    logger.debug("split dell'attributo: " + att["name"])
                    element = self.dict_attr[att["name"]].split(".")
                    table = element[0] 
                else:
                    logger.debug("l'attributo " + att["name"] + " non è nella lista dict_attr")

            flag_query_true = False
            cont_query = 0
            while flag_query_true == False:
                #for pl in plus_query_moment:
                if table in plus_query_moment[cont_query]:
                    logger.debug("selezione della query: " + plus_query_moment[cont_query])
                    plus_query = plus_query_moment[cont_query]
                    flag_query_true = True
                cont_query += 1
            logger.debug("ENTITY: " + table)

        #preparazione della fase match della query
        query = "MATCH p = ("+self.entity_mapping_function(object_type) +":"+ self.entity_mapping_function(object_type) +")"+ plus_query

        #definire il where in caso ci fosse una condizione esplicitata
        if object_identifier or attributes:
            query += ' WHERE '
            wherecond = []
        else:
            return None

        if object_identifier:
            logger.debug("object_identifier definito: " + object_identifier)
            logger.debug("key_attribute_of_object definito: " + self.get_key_attribute_of_object(object_type)) 
            wherecond.append(
                " TOUPPER("+ self.entity_mapping_function(object_type) +"."+ self.get_key_attribute_of_object(object_type) +
                ") = TOUPPER('" + object_identifier +"') ")

        # fase di filtraggio degli oggetti in base agli attributi, preparazione query
        if attributes:
            for attribute in attributes:
                synfound = False
                for attribute_syn_list in self.attribute_syn:
                    if attribute["name"] in attribute_syn_list:  
                        synfound = True
                        synwherecond = []
                        for syn in attribute_syn_list:
                            synwherecond.append(self.attribute_field_function(object_type,syn)+ 
                            "("+table+"."+syn+") "+ self.attribute_operator_function(object_type,syn) +" "+
                            self.attribute_value_function(object_type,syn,attribute["value"].replace("'","\\'"))
                            +" " )
                        wherecond.append("("+  " OR ".join(synwherecond) +")")
                        logger.info("ATTRIBUTE1: %s", wherecond)
                if not synfound:
                    wherecond.append(self.attribute_field_function(object_type,attribute)+ 
                    "("+self.dict_attr[attribute["name"]]+") "+ self.attribute_operator_function(object_type,attribute) +" "+
                    self.attribute_value_function(object_type,attribute,attribute["value"].replace("'","\\'"))
                    +" " )
                    logger.info("ATTRIBUTE2: %s", wherecond)
        
        query += " AND ".join(wherecond)

        query += ' RETURN nodes(p) As Result LIMIT 25'

        #esecuzione della query
        result = self.query_db(query)

        objects = []

        for record in result:
            entity =  {}
            for rec in record['Result']:
                for k, v in rec.items():
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

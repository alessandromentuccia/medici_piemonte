from rasa_sdk.knowledge_base.storage import KnowledgeBase
import logging
from typing import Text, Callable, Dict, List, Any, Optional
from collections import defaultdict
from neo4j.v1 import GraphDatabase

logger = logging.getLogger("rasa_sdk."+__name__)

class Neo4jKnowledgeBase(KnowledgeBase):
    relation_name = []
    table_name = []

    def __init__(self,  url, username, password, init_object):
        self.url = url
        self.username = username
        self.password = password
        self.entity_mapping_function = lambda object: str(object)
        self.attribute_field_function = lambda object_type, attribute: "TOUPPER"
        self.attribute_value_function = lambda object_type, attribute, value: "TOUPPER('"+value+"')"
        self.attribute_operator_function = lambda object_type, attribute: "="
        self.attribute_syn = [ {}]
        self.key_attribute = lambda object: str(object)
        self.dict_attr = {} #dizionario contenente la mappatura degli attributi con i nomi sul db
        self.initial_object = init_object
        self.relation_object = self.relation_mapping_function(init_object) #mi creo le relazioni fin dal principio
        super(Neo4jKnowledgeBase, self).__init__()

    def insert_relation_name(self, rel_name : Text) -> None:
        self.relation_name.append(rel_name)

    def get_relation_name(self) -> List[Text]:
        return self.relation_name

    def insert_table_name(self, tab_name : Text) -> None:
        self.table_name.append(tab_name)

    def get_table_name(self,) -> List[Text]:
        return self.table_name

    """funzione che crea la mappa delle relazioni a partire da quella definita da principio"""
    def relation_mapping_function(self, init_object : Text) -> Text:
        s_entity = []
        s_relation = []
        s_result = []
        q_relation = ""
        logger.debug("initial object: " + init_object)
        query = "match (n:"+ init_object +")-[relation]-(medium) where relation is NOT null RETURN DISTINCT type(relation) As relation, labels(medium) As medium"
        result = self.query_db(query)
        try: #try se ci sono relazioni, se non ci sono fallisce e except
            for s in result:
                if s['relation'] != None and s['relation'] not in s_relation:
                    s_result.append([str(s['relation']),str(s['medium'][0])])
                    s_entity.append(s['medium'][0])
                    s_relation.append(s['relation'])
                    print(str(s['relation']))
            s_result = s_result.pop(0) #elimino una lista con
            
            logger.debug('fase 2')
            
            popentity = s_entity.pop(0)       
            relations = ""
            while popentity != "":
                if relations == "":
                    relations = "relation"
                logger.debug("popentity: " + str(popentity))
                subquery = "MATCH (n:"+ self.entity_mapping_function(popentity) +")-[relation]-(last) where relation is NOT null RETURN DISTINCT type(relation) As relation , labels(last) As last"     
                subresult = self.query_db(subquery)
                logger.debug('subquery')
                
                subsub = [] #lista degli elementi che dovranno popolare sResult 
                for sub in subresult:
                    if sub['relation'] != None and sub['last'][0] != None:
                        if sub['relation'] not in s_relation:
                            logger.debug('inizio del for: %s', str(sub['relation']) + ' -> ' + str(sub['last'][0]))
                            subsub.append(s_result) #mi creo una riga in subsub 
                            logger.debug('subsub: %s', subsub)
                            s_relation.append(sub['relation'])
                            s_entity.append(sub['last'][0])
                            for rr in subsub:   #per ogni vecchia relazione, viene ampliata la sua relazione se ne è provvista
                                logger.debug('rr: %s', rr)
                                if rr[1] == popentity:
                                    logger.debug('rr[1]: ' + str(rr[1])) 
                                    rr.append(sub['relation'])  
                                    rr.append(sub['last'][0])        
                                    logger.debug('rel: ' + str(sub['relation']) + ', ent: ' + str(sub['last'][0]))
                            logger.debug('subsub modificato: %s', subsub)
                        else:
                            logger.debug("la relazione e' gia stata inserita")
                    else:
                        logger.debug('La relazione o la tabella non sono state trovate')
                
                if s_entity != []: #se ci sono ancora tabelle nella lista delle tabelle da esplorare
                    logger.debug('s_entity: %s', s_entity) 
                    popentity = s_entity.pop(0) #estrarre nome entity e poi di seguito ricomincio ciclo while
                    s_result = subsub #reinserisco il risultato aggiornato in s_result 
                else: 
                    logger.debug('sono finite le tabelle in relazione')
                    popentity = ""
            logger.debug('risultato query relazioni: %s', s_result)

            #ciclo di costruzione della query
            #q_relation += "("+ self.initial_object +")"
            for s_res in s_result:
                if s_res != None:
                    rel = []
                    tab = []
                    for sr in range(len(s_res)):
                        if sr%2 == 0:
                            rel.append(s_res[sr])
                            logger.debug("1: "+str(sr) + ", " + s_res[sr])
                            q_relation += "-["+s_res[sr]+"]"
                        elif sr%2 == 1:
                            tab.append(s_res[sr])
                            logger.debug("2: "+str(sr) + ", " + s_res[sr])
                            q_relation += "-("+s_res[sr]+")"
                logger.debug("q_relation: " + q_relation)
            self.relation_name = rel
            self.table_name = tab
        except:
            logger.debug("nessuna relazione trovata")
        return q_relation

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
        if attributi:
            for attributo in attributi: #per ogni attributo a cui associare la tabella
                logger.debug("mappato attributo1: %s", attributo['name'])
                self.dict_attr[attributo['name']] = self.get_object_type_by_attribute(attributo['name']) +"."+ attributo['name'] 
                logger.debug("mappato attributo1: %s", self.dict_attr[attributo['name']])

    def set_entity_ob_id_mapping(self, attributo: Text): 
        logger.debug("inizio estrazione tabella dal db per attributi")
        if attributo:
            #for attributo in attributi: #per ogni attributo a cui associare la tabella
            logger.debug("mappato attributo2: %s", attributo)
            self.dict_attr[attributo] = self.get_object_type_by_attribute(attributo) +"."+ attributo
            logger.debug("mappato attributo2: %s", self.dict_attr[attributo])

    """funzione che restituisce il nome della tabella dell'attributo"""
    def get_object_type_by_attribute(self, attribute) -> Text:
        query = "MATCH (n) WHERE EXISTS(n."+ attribute +") RETURN DISTINCT LABELS(n) AS Entity"
        oggetto = ""
        result = self.query_db(query) 
        if result:  
            for res in result:
                if res['Entity'][0] != None and (res['Entity'][0] in self.relation_object or res['Entity'][0] in self.initial_object):
                    oggetto = res['Entity'][0]
        return oggetto

    """Mi restituisce una lista con i nomi degli attributi di un entity"""
    """da generalizzare, in questo caso la query non è generalizzata"""
    def get_attributes_of_object(self, object_type: Text) -> List[Text]:

        query = "MATCH ("+ self.initial_object +":"+ self.initial_object +")"+ self.relation_object +" WITH LABELS("+ self.initial_object +") AS labels , KEYS("+ self.initial_object +")"
        _tab = self.get_table_name()
        for rel in _tab:
            query = query + "+KEYS(" + rel + ")"
        query += " AS keys UNWIND labels AS label UNWIND keys AS key RETURN DISTINCT label, COLLECT(DISTINCT key) AS props ORDER BY label"
        
        result = self.query_db(query)
        
        result_count = 0
        attribute = []
        for ris in result:
            result_count += 1
            attribute = ris["props"]

        logger.info('Result Attribute of '+ str(self.entity_mapping_function(object_type)) +': '+str(attribute))
        return attribute

    def get_objects(
        self, object_type: Text, attributes: List[Dict[Text, Text]],object_identifier: Text, last_object: Text, limit: int = 5
    ) -> List[Dict[Text, Any]]:
        
        #fase di associazione delle relazioni alla query
        self.set_entity_attribute_mapping(object_type, attributes)
        logger.debug("dict_attr: %s", self.dict_attr)

        logger.debug("object_type: %s ", object_type)
        #preparazione della fase match della query
        query = "MATCH p = ("+ self.initial_object +")" + self.relation_object 

        #definire il where in caso ci fosse una condizione esplicitata
        if object_identifier or attributes:
            logger.debug("attributes: %s ", attributes)
            query += ' WHERE EXISTS('+ self.entity_mapping_function(object_type) +'.'+ self.get_key_attribute_of_object(object_type) +') AND '
            wherecond = []
            logger.debug("query parziale 1: " + query)
        else:
            return None
        
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
                            "("+self.entity_mapping_function(object_type)+"."+syn+") "+ self.attribute_operator_function(object_type,syn) +" "+
                            self.attribute_value_function(object_type,syn,attribute["value"].replace("'","\\'"))
                            +" " )
                        wherecond.append("("+  " OR ".join(synwherecond) +")")
                        logger.info("ATTRIBUTE1: %s", wherecond)
                if not synfound:
                    logger.debug("list_dict: " + self.dict_attr[attribute["name"]])
                    wherecond.append(self.attribute_field_function(object_type,attribute)+ 
                    "("+self.dict_attr[attribute["name"]]+") "+ self.attribute_operator_function(object_type,attribute["name"]) +" "+
                    self.attribute_value_function(object_type,attribute["name"],attribute["value"].replace("'","\\'"))
                    +" " )
                    logger.info("ATTRIBUTE2: %s", wherecond)
        else: #caso in cui si ha delle mention
            if object_identifier:
                self.set_entity_ob_id_mapping(last_object)
                if last_object:
                    tabella = self.dict_attr[last_object]
                    logger.debug("tabella definito: " + tabella) 
                else:
                    tabella = self.entity_mapping_function(object_type) +"."+ self.get_key_attribute_of_object(object_type)
                logger.debug("object_identifier definito: " + object_identifier)
                logger.debug("key_attribute_of_object definito: " + self.get_key_attribute_of_object(object_type)) 
                wherecond.append(
                    "TOUPPER("+ tabella +
                    ") = TOUPPER('" + object_identifier +"') ")
                logger.debug("query parziale 1,1: " + query) 
        
        query += " AND ".join(wherecond)
        logger.debug("query parziale 2: " + query)

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

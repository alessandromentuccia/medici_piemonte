"""This class should after being defined should return entity/attribute values based on the Json
parameters it receives."""
import logging
from neo4j.v1 import GraphDatabase


class Neo4jDB:
    """This class allows for the main to access the neo4j database and make basic queries"""
    url = ""
    username = ""
    password = ""

    # Defines the Neo4J db I'm going to access
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def access_db(self):
        """Used to access the Neo4J DB"""
        try:
            driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        except Exception:
            raise ConnectionError
        return driver

    def query(self, entity, list_param):
        """Receives a list of attributes and the entity and returns a dictionary of values
        from making a query to the DB"""

        # if type(entity) is not str or type(listParam) is not list:
        # EnvironmentError

        param_str = ', '.join([' n.' + param for param in list_param])

        driver = self.access_db()
        logging.debug('Obtained driver for querying Neo4J database')
        session = driver.session()
        logging.debug('Created session through driver for querying')
        query = "MATCH(n:{}) RETURN {}".format(entity, param_str)

        with session.begin_transaction() as _tx:
            result = _tx.run(query)
            print("QUERY SUCCESS")
            # se ho almeno 1 risultato:
            # queryDict = dict.fromkeys(sandroArray, [])
            query_dict = {key: [] for key in set(list_param)}
            result_count = 0
            for ris in result:
                result_count += 1
                for _x in list_param:
                    key = 'n.' + _x
                    if ris[key] is None:
                        logging.error('The key [%s] was not found in the Neo4J query', key)
                    else:
                        if ris[key] not in query_dict[_x]:
                            query_dict[_x].append(ris[key])
            #  altrimenti
            if result_count == 0:
                logging.error('The query failed to find values for the entity %s', entity)
                logging.warning('Please check that the node label exists in the Neo4J DB')
                return None
        return query_dict

    def match_lookup_by_node_name(self, node_name, attribute_name):
        """Database query for lookup entities"""
        lookup_query = "MATCH(n:{}) RETURN n.{}".format(node_name, attribute_name)
        key = "n." + attribute_name
        driver = self.access_db()
        session = driver.session()

        with session.begin_transaction() as _tx:
            result = _tx.run(lookup_query)
        lookup_list = []

        for ris in result:
            if ris[key] is None:
                logging.error('The key [%s] was not found in the Neo4J query', key)
                break
            lookup_list.append(ris[key])

        if not lookup_list:
            logging.error('The query failed to find values for the entity %s', node_name)
            logging.warning('Please check that the node label exists in the Neo4J DB')
            return None
        return lookup_list

    def cerca_ospedale_citta(self, citta):
        "Searches the db for hospitals within the Neo4J system"
        driver = self.access_db()
        session = driver.session()
        query_search_hospital = 'MATCH(n:Ospedale{{citta:TOUPPER("{}")}}) RETURN n.name'.format(citta)
        with session.begin_transaction() as _tx:
            result = _tx.run(query_search_hospital)

        key = 'n.name'
        search_list = []
        for ris in result:
            search_list.append(ris[key])

        return search_list

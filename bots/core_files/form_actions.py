"Contains an example of a FormAction"
from rasa_core_sdk.forms import FormAction
# from rasa_core_sdk.events import SlotSet

# from cp_config import ConvPlatformConfig

# cfg = ConvPlatformConfig()

# logger = logging.getLogger(__name__)

# Neo4J DB details
"""
URL = 'bolt://' + cfg.neo4j_server + ':' + cfg.neo4j_port_bolt
DB_NAME = cfg.neo4j_user
PASSWORD = cfg.neo4j_password
"""


class ActionCercaOspedaleCitta(FormAction):
    """FormAction version of action search hospital"""
    def name(self):
        return 'action_cerca_ospedale_citta'

    @staticmethod
    def required_slots(tracker):
        return [
            'citta'
        ]

    def submit(self, dispatcher, tracker, domain):

        citta = tracker.get_slot('citta')
        """
        _n = Neo4jDB(URL, DB_NAME, PASSWORD)
        _query_result = _n.cerca_ospedale_citta(citta)

        if not _query_result:
            dispatcher.utter_message("Non ho trovota un ospedale a {}".format(citta))
            return []
        dispatcher.utter_message("I seguenti ospedali sono a {}".format(citta))
        hospitals = ",\n".join(_query_result)
        """
        dispatcher.utter_message('... placeholder per ricerca con citta=' + citta)
        return []

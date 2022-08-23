from emora_stdm import KnowledgeBase
from _globals import PATHDIR

central_knowledge = KnowledgeBase()
central_knowledge.load_json_file(PATHDIR.replace('__***__','_common.json'))
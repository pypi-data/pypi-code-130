from vid2info.state.scene_state import SceneState
from vid2info.state.element_state import ElementState
from vid2info.state.state_buffer import StateBuffer
from vid2info.state.config import BUFFER_SIZE

class FiniteStateMachine:
    def __init__(self, state_buffer_size : int = BUFFER_SIZE, running_online : bool = False,
                 scene_state_class : type = SceneState, element_state_class : type = ElementState):
        self.state_buffer = StateBuffer(buffer_size=state_buffer_size, running_online=running_online,
                                        element_state_class=element_state_class, scene_state_class=scene_state_class)
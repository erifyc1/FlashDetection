import numpy as np
from sortedcontainers import SortedDict

class ChromaticityTree:
  def __init__(self):
    self.ct = SortedDict()
  
  def push(self, element):
    self.ct[element] = self.ct.get(element, 0) + 1

  def pop(self, element):
    num_occurrences = self.ct.get(element, 0)
    if num_occurrences == 0:
      print("Element is not in chromaticity tree")
    elif num_occurrences == 1:
      del self.ct[element]
    else:
      self.ct[element] = num_occurrences - 1
  
  def min(self):
    if self.ct:
      return next(iter(self.ct))
    else:
      print("Chromaticity tree has no elements")
  
  def max(self):
    if self.ct:
      return next(reversed(self.ct))
    else:
      print("Chromaticity tree has no elements")

class Region:
    def __init__(self, chromaticity, red_percentage):
        self.chromaticity = chromaticity
        self.red_percentage = red_percentage
        Region.MAX_CHROMATICITY_DIFF = 0.2
        Region.MAX_RED_PERCENTAGE = 0.8

        self.states = set()
        Region.add_start_state(chromaticity, red_percentage, self.states)

    @staticmethod
    def should_transition(state, chromaticity, red_percentage, should_check_red_percentage):
        if should_check_red_percentage and red_percentage < Region.MAX_RED_PERCENTAGE:
            return False

        if abs(chromaticity - state.max_chromaticity) >= Region.MAX_CHROMATICITY_DIFF:
            return True

        if abs(chromaticity - state.min_chromaticity) >= Region.MAX_CHROMATICITY_DIFF:
            return True
        
        return False

    @staticmethod
    def update_or_add_state(state, state_set):
        for s in state_set:
            if s == state:
                s.chromaticity_tree.push(state.chromaticity)
                return
        state_set.add(state)

    @staticmethod
    def add_start_state(chromaticity, red_percentage, state_set):
        state_A = State('A', chromaticity)
        state_set.add(state_A)

        if red_percentage >= Region.MAX_RED_PERCENTAGE:
            state_B = State('B', chromaticity)
            state_set.add(state_B)
    
    def state_machine(self, other_region):
        changed_state_set = set()

        for state in self.states:
            # We always stay in the current state
            Region.update_or_add_state(state, changed_state_set)

            # This could be our new start state
            Region.add_start_state(other_region.chromaticity, other_region.red_percentage, changed_state_set)

            if state.name == 'A':
                if Region.should_transition(state, other_region, True):
                    # We can move to state C if the chromaticity increased/decreased by MAX_CHROMATICITY_DIFF and there is a saturated red
                    state_c = State('C', other_region.chromaticity)
                    Region.update_or_add_state(state_c, changed_state_set)
            elif state.name == 'B':
                if Region.should_transition(state, other_region, False):
                    # We can move to state D if the chromaticity increased/decreased by MAX_CHROMATICITY_DIFF
                    state_d = State('D', other_region.chromaticity)
                    Region.update_or_add_state(state_d, changed_state_set)
            elif state.name == 'C':
                if Region.should_transition(state, other_region, False):
                    # We can move to state E if the chromaticity increased/decreased by MAX_CHROMATICITY_DIFF
                    state_e = State('E', other_region.chromaticity)
                    Region.update_or_add_state(state_e, changed_state_set)
            elif state.name == 'D':
                if Region.should_transition(state, other_region, True):
                    # We can move to state E if the chromaticity increased/decreased by MAX_CHROMATICITY_DIFF and there is a saturated red
                    state_e = State('E', other_region.chromaticity)
                    Region.update_or_add_state(state_e, changed_state_set)
        
        self.states = changed_state_set
    
    def is_flash(self):
        state_e = State('E', State.INVALID_CHROMATICITY)
        if state_e in self.states:
            return True
        return False

class State:
    def __init__(self, name, chromaticity, start_idx):
        if name not in ['A', 'B', 'C', 'D', 'E']:
            raise ValueError("Invalid state name")
        self.start_idx = start_idx
        self.name = name
        self.chromaticity_tree = ChromaticityTree()
        self.chromaticity_tree.push(chromaticity)
    
    def __hash__(self):
        return hash(self.name, self.start)

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.name == other.name

class Buffer:
    def __init__(self, num_frames, n):
        self.index = 0
        self.regions = np.empty((n, n), dtype = object)
        self.num_frames = num_frames
        self.n = n

    def initialize_buffer(self):
        for i in range(self.n):
            for j in range(self.n):
                # TODO: Change this to use the actual values corresponding to the first frame
                self.regions[i][j] = Region(np.random.rand(), np.random.rand())

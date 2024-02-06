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

class SRChecker:
  def __init__(self):
    self.ct = ChromaticityTree()
    self.rp = {}
    self.MAX_RED_PERCENTAGE = 0.8
    self.MAX_CHROMATICITY_DIFF = 0.2
  
  def ct_push(self, element):
    return self.ct.push(element)
  
  def ct_pop(self, element):
    return self.ct.pop(element)
  
  def ct_min(self):
    return self.ct.min()
  
  def ct_max(self):
    return self.ct.max()
  
  def add_rp(self, element):
    if element >= self.MAX_RED_PERCENTAGE:
      # We only need to add the element if its red percentage is above the maximum
      self.rp[element] = self.rp.get(element, 0) + 1
  
  def remove_rp(self, element):
    if element >= self.MAX_RED_PERCENTAGE:
      if element in self.rp:
        del self.rp[element]
      else:
        self.rp[element] -= 1
  
  def is_sat_red_transition(self):
    return self.rp and (self.ct_max() - self.ct_min()) >= self.MAX_CHROMATICITY_DIFF

class BufferSRChecker:
  def __init__(self, n):
    self.sr_checkers = np.empty((n, n), dtype = object)
    self.n = n

    for i in range(n):
      for j in range(n):
        self.sr_checkers[i, j] = SRChecker()
  
  def is_problematic_region(self):
    for i in range(self.n):
      for j in range(self.n):
        if self.sr_checkers[i, j].is_sat_red_transition():
          print("There is a problematic region at (" + str(i) + "," + str(j) + ")")

def saturated_red_detector(dangerous, frame_rate, num_frames, n):
  """
  Detects a pair of opposing transitions involving a saturated red.
  That is, the transition involves a state having R/(R + G + B) >= 0.8 and a chromaticity difference of 0.2

  Each region in a given frame will have a corresponding chromaticity tree, in addition to a red percentage multiset.
  We then determine if any region meets these criteria.

  n: Determines the number of regions (e.g., n = 4 indicates 16 regions/frame)
  """
  checker = BufferSRChecker()
  """
  TODO
  Populate the frame buffer with the initial frames.

  As each frame is added, call sr_checkers[i, j].ct_push(el) to push the
  chromaticity value el to the SRChecker of the appropriate region.

  As each frame is added, also call sr_checkers[i, j].add_rp(el) to push the
  red percentage el to the SRChecker of the appropriate region.
  """

  """
  TODO
  Populate the buffer with new frames.

  Determine whether there is a saturated red opposing transition for curr buffer.
  for i in range(n):
    for j in range(n):
      if sr_checkers[i, j].is_sat_red_transition():
        print("Identified problematic region")

  Call ct_pop() and remove_rp() for each region in the frame leaving buffer.
  Call ct_push() and add_rp() for each region in the frame entering buffer.
  """
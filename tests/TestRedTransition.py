from red_transition_fsm import ChromaticityTree
from red_transition_fsm import Region
from red_transition_fsm import State
from red_transition_fsm import Buffer

test_ctree = ChromaticityTree()
test_ctree.push(3)
test_ctree.push(5)
# Tests that we correctly find the minimum and maximum element
assert test_ctree.min() == 3
assert test_ctree.max() == 5
# Tests that we correctly update the minimum when element is removed
test_ctree.pop(3)
assert test_ctree.min() == 5
# Tests that we correctly update the minimum when element is added
test_ctree.push(3)
assert test_ctree.min() == 3
# Tests that we can correctly handle duplicate elements
test_ctree.push(3)
test_ctree.pop(3)
assert test_ctree.min() == 3
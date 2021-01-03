# some code and pseudo code have been picked up from lecture notes and solutions for quizzes and exercises in udacities classroom.
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

# TODO: Update the unit list to add the new diagonal units
diag_units_1 = [ tp[0] + tp[1] for tp in list(zip('ABC', '123')) + list(zip('DEF', '456')) + list(zip('GHI', '789')) ]
diag_units_2 = [ tp[0] + tp[1] for tp in list(zip('ABC', '987')) + list(zip('DEF', '654')) + list(zip('GHI', '321')) ]
diag_units = [diag_units_1, diag_units_2]
unitlist = unitlist + diag_units


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).

    See Also
    --------
    Pseudocode for this algorithm on github:
    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """
    # TODO: Implement this function!
    values_copy = values.copy()

    for boxA in values.keys():
        for boxB in peers[boxA]:
            ASolnCount = len(values[boxA])
            BSolnCount = len(values[boxB])

            if(ASolnCount == 2 and BSolnCount == 2 and values[boxA] == values[boxB]):
                common_peers = set(peers[boxA]).intersection(set(peers[boxB])) 
                for peer in common_peers:
                    if(len(values[peer]) == 1):
                        continue
                    for digit in values[boxA]:
                        values_copy[peer] = values_copy[peer].replace(digit, '')
                        
    return values_copy

def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    
    solved_boxes = [box for box in values.keys() if len(values[box]) == 1]
    
    for box in solved_boxes:
        for peer_bx in peers[box]:
            values[peer_bx] = values[peer_bx].replace(values[box], '')

    return values

def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """

    # pick some digit from the set "123456789".
    # Next answer the question how many boxes can this digit be assigned to ?
    # if the answer is 1 then assign that digit to that box.
    for unit in unitlist:
        for digit in '123456789':
            possible_boxes = [box for box in unit if digit in values[box]]
            if len(possible_boxes) == 1:
                values[possible_boxes[0]] = digit
    return values

def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    
    # use elminate and only_choice strategy one after the other and then check for stalling.
    stalled = False

    while(not stalled):
        before_state = len([box for box in values.keys() if len(values[box]) == 1])
        eliminate(values)
        only_choice(values)
        after_state = len([box for box in values.keys() if len(values[box]) == 1])
        if(not state_changed(before_state, after_state)):
            stalled = True        
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def state_changed(before_state, after_state):
    return before_state != after_state

def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    
    # apply naked_twin strategy first and then reduce_puzzle. 
    # this will be the complete the reduction phase.
    values = naked_twins(values)
    values = reduce_puzzle(values)

    # check if not able to solve... then backtrack and use dfs for a new option.
    if(not values):
        return False

    # check if solved.
    is_solved = all([len(values[box]) == 1 for box in boxes])
    if(is_solved):
        return values

    # if its not solved apply dfs from by selecting an unsolved box with minimum number of options.
    unsolved_bxs = [bx for bx in values.keys() if len(values[bx]) > 1]
    selected_bx = min(unsolved_bxs, key = lambda bx: len(values[bx]))
    
    for option in values[selected_bx]:
        new_sudoku = values.copy()
        new_sudoku[selected_bx] = option
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    
    solved_diag_sudoku = {'G7': '8', 'G6': '9', 'G5': '7', 'G4': '3', 'G3': '2', 'G2': '4', 'G1': '6', 'G9': '5',
                          'G8': '1', 'C9': '6', 'C8': '7', 'C3': '1', 'C2': '9', 'C1': '4', 'C7': '5', 'C6': '3',
                          'C5': '2', 'C4': '8', 'E5': '9', 'E4': '1', 'F1': '1', 'F2': '2', 'F3': '9', 'F4': '6',
                          'F5': '5', 'F6': '7', 'F7': '4', 'F8': '3', 'F9': '8', 'B4': '7', 'B5': '1', 'B6': '6',
                          'B7': '2', 'B1': '8', 'B2': '5', 'B3': '3', 'B8': '4', 'B9': '9', 'I9': '3', 'I8': '2',
                          'I1': '7', 'I3': '8', 'I2': '1', 'I5': '6', 'I4': '5', 'I7': '9', 'I6': '4', 'A1': '2',
                          'A3': '7', 'A2': '6', 'E9': '7', 'A4': '9', 'A7': '3', 'A6': '5', 'A9': '1', 'A8': '8',
                          'E7': '6', 'E6': '2', 'E1': '3', 'E3': '4', 'E2': '8', 'E8': '5', 'A5': '4', 'H8': '6',
                          'H9': '4', 'H2': '3', 'H3': '5', 'H1': '9', 'H6': '1', 'H7': '7', 'H4': '2', 'H5': '8',
                          'D8': '9', 'D9': '2', 'D6': '8', 'D7': '1', 'D4': '4', 'D5': '3', 'D2': '7', 'D3': '6',
                          'D1': '5'}
    print("original soln:\n")
    display(solved_diag_sudoku)
    print("my soln:\n")
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

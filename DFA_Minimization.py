from graphviz import Digraph
from texttable import Texttable
import json
import graphviz
import pydot
import re
import os

def inputToMinimizedDFA ():

    dfa_source = dict()
    dfa_source = {
        'alphabet': set(),
        'states': set(),
        'initial_state': '0',
        'accepting_states': set(),
        'transitions': dict()
    }
    
    #Creating a class for a diagram
    dot = Digraph()

    tableSourceDFA = []
    tableTargetDFA = []
    
    print('Please enter the alphabet symbols in your alphabet separated by white spaces.')
    alphabetInput = input()
    alphabetInput = alphabetInput.split()

    #Creating an array of alphabet symbols
    alphabetArray = []

    numOfAlphSymb = len(alphabetInput)
    for i in range(numOfAlphSymb):
        alphabetArray.append(alphabetInput[i])
        dfa_source['alphabet'].add(alphabetInput[i])
    
    #Creating the first row of the table consisting of one white space and all the alphabet symbols.
    firstRow = []
    firstRow.append(' ')
    for i in range (numOfAlphSymb):
        firstRow.append(alphabetInput[i])

    tableSourceDFA.append(firstRow)
    tableTargetDFA.append(firstRow)
    
    #Prompting the user to enter all the states
    print('Please enter the states separated by white spaces. They are your table row names.')
    statesInput = input()
    statesInput = statesInput.split()
    numOfInputStates = len(statesInput)

    #Prompting the user to enter the start state
    print('Please enter the start state out of the list you entered.')
    startState = input()
    dfa_source['initial_state'] = startState

    #Prompting the user to enter the accepting state / states
    print('Please enter the accepting state or states out of the list you entered.')
    print('If there are several accepting states, separate them by white spaces.')
    acceptingStates = input()

    #For each state, creating a node in the diagram and a row in the table
    updatedStatesInput = []
    for i in range(numOfInputStates):
        if ((startState == statesInput[i]) and (startState in acceptingStates)):
            updatedStatesInput.append('->*' + statesInput[i])
            dfa_source['accepting_states'].add(statesInput[i])
        elif (startState == statesInput[i]):
            updatedStatesInput.append('->' + statesInput[i])
        elif (statesInput[i] in acceptingStates):
            updatedStatesInput.append('*' + statesInput[i])
            dfa_source['accepting_states'].add(statesInput[i])
        else:
            updatedStatesInput.append(statesInput[i])

        dfa_source['states'].add(statesInput[i])
    
    #Prompting the user to fill out the table.
    #The user is asked to fill out one cell at a time.
    # In parallel, the edges of the graph and their labels are created on the diagram. 
    transitions = dict()
    
    for i in range (numOfInputStates):
        key1 = str(statesInput[i])
        print('Entering input for row '+ key1 + '.')
        localList = []
        localList.append(updatedStatesInput[i])
        for j in range(numOfAlphSymb):
            key2 = str(alphabetArray[j])
            print('Please enter an input for alphabetical symbol '+ key2 + '.')
            localInput = input()
            transitions[key1, key2] = localInput
            localList.append(localInput)
        
        tableSourceDFA.append(localList)
    dfa_source['transitions'] = transitions
    
    #Showing the entered information to the user in a tabular form. 
    #The user is prompted to answer "Yes" if the table is correct.
    t = Texttable()
    t.add_rows(tableSourceDFA)
    print(t.draw())
    
    print('Here is the table constructed based on your input. Is it correct? Type Yes or No.')
    answer = input()

    if (answer != 'Yes'):
        print('Table incorrect. Exiting program.')
        exit()
    
    #Greatest-fixpoint algorithm

    currentSetOfPartitions = set()
    nextSetOfPartitions = set()

    #Checking that the accepting and non-accepting states are
    #in different partitions
    for state_s in dfa_source['states']:
        for state_t in dfa_source['states']:
            if (
                            state_s in dfa_source['accepting_states']
                    and state_t in dfa_source['accepting_states']
            ) or (
                            state_s not in dfa_source['accepting_states']
                    and state_t not in dfa_source['accepting_states']
            ):
                nextSetOfPartitions.add((state_s, state_t))
    
    #Checking that each pair of state belongs to the same
    #state relation, meaning any alphabet symbol applied
    #to each of the pair members should lead to the pair of states that are
    #non-distinguishable
                
    while currentSetOfPartitions != nextSetOfPartitions:
        currentSetOfPartitions = nextSetOfPartitions
        nextSetOfPartitions = currentSetOfPartitions.copy()
        for (state_1, state_2) in currentSetOfPartitions:
            for a in dfa_source['alphabet']:
                if (state_1, a) in dfa_source['transitions'] \
                        and (state_2, a) in dfa_source['transitions']:
                    
                    if (
                            dfa_source['transitions'][state_1, a],
                            dfa_source['transitions'][state_2, a]
                    ) not in currentSetOfPartitions:
                        nextSetOfPartitions.remove((state_1, state_2))
                        break
                else:
                    nextSetOfPartitions.remove((state_1, state_2))
                    break
                
    #Creating equivalences of states
    equivalence = dict()
    for (state_1, state_2) in currentSetOfPartitions:
        equivalence.setdefault(state_1, set()).add(state_2)
    
    #Creating a final dfa_min dictionary
    dfa_min = {
        'alphabet': dfa_source['alphabet'].copy(),
        'states': set(),
        'initial_state': dfa_source['initial_state'],
        'accepting_states': set(),
        'transitions': dfa_source['transitions'].copy()
    }

    for equivalence_set in equivalence.values():
        if dfa_min['states'].isdisjoint(equivalence_set):
            e = equivalence_set.pop()
            dfa_min['states'].add(e)
            equivalence_set.add(e)

    dfa_min['accepting_states'] = \
        dfa_min['states'].intersection(dfa_source['accepting_states'])

    for t in dfa_source['transitions']:
        if t[0] not in dfa_min['states']:
            dfa_min['transitions'].pop(t)
        elif dfa_source['transitions'][t] not in dfa_min['states']:
            dfa_min['transitions'][t] = \
                equivalence[dfa_source['transitions'][t]]. \
                    intersection(dfa_min['states']).pop()

    #Sorting the set of states alphabetically

    dfa_min['states'] = sorted(dfa_min['states'])

    #Constructing the minimized DFA table
    #First row
    for i in dfa_min['states']:
        localList = []
        if (i == dfa_min['initial_state']):
            if i in dfa_min['accepting_states']:
                dot.node('Fake', 'q', style = 'invisible')
                dot.edge('Fake', i, style = 'bold')
                dot.node(i, i, root = 'true', shape = 'doublecircle')
                j = '->*' + i
            else:
                j = '->' + i
                dot.node('Fake', 'q', style = 'invisible')
                dot.edge('Fake', i, style = 'bold')
                dot.node(i, i, root = 'true')
        elif (i in dfa_min['accepting_states']):
            j = '*' + i
            dot.node(i, i, shape = 'doublecircle')
        else:
            j = i
            dot.node(i, i)
        localList.append(j)
        for a in dfa_min['alphabet']:
            localList.append(dfa_min['transitions'][i, a])
            dot.edge(i,str(dfa_min['transitions'][i, a]), label = a)
        tableTargetDFA.append(localList)

    #Showing the entered information to the user in a tabular form. 
    print('Here is the table of the minimized DFA.')
    t = Texttable()
    t.add_rows(tableTargetDFA)
    print(t.draw())

    print("The diagram has been output as a PDF file.")
    #Outputting the FA diagram using the render() method
    return dot.render('FA_diagram.gv', view=True)  # doctest: +SKIP

 #main
var = inputToMinimizedDFA() 

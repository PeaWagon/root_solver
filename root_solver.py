#!/usr/bin/env python

import random
import sys
#from copy import deepcopy
from operator import itemgetter


#TODO: should make the number of decimal places
# different than the error


class RootSolver(object):
    """ using an evolutionary algorithm to find
        roots of an equation
        
        for now, the equation will be continuous
        and have a single dependent variable
        i.e. y = f(x)
    """
    def __init__(self, equation, POP_SIZE=10, LEFT_BOUND=-1000, RIGHT_BOUND=1000, ERROR=10e-6, T_SIZE=7, MNM=3, FLIP_CHANCE=0.5, VERBOSE=True, SIGNIFICANCE=1):
        # note the equation can be a lambda equation:
        # example: lambda x: x**2 - 5
        # right now, input equation as a string
        # i.e. use:
        # "x**2 - 5"
        # left and right bounds should be integers
        self.VERBOSE = VERBOSE
        self.equation = equation
        self.POP_SIZE = POP_SIZE
        self.LEFT_BOUND = LEFT_BOUND
        self.RIGHT_BOUND = RIGHT_BOUND
        self.ERROR = ERROR
        self.error_length = self.get_error_length()
        self.value_length = self.get_value_length()
        self.roots = []
        self.MNM = MNM
        self.population = self.generate_population()
        self.MAX_ROOTS = self.parse_equation()
        self.T_SIZE = T_SIZE
        self.FLIP_CHANCE = FLIP_CHANCE
        # significance for determinining roots
        self.SIG = SIGNIFICANCE

    def v_print(self, things):
        """ verbose print if self.VERBOSE is set to True
            things should be a tuple
        """
        if self.VERBOSE:
            for thing in things:
                print(thing)
    
    def get_value_length(self):
        """ checks the bounds (make sure they are integers)
            also determines how big the numbers should be
            prior to the decimal point
        """
        try:
            self.LEFT_BOUND = int(self.LEFT_BOUND)
            self.RIGHT_BOUND = int(self.RIGHT_BOUND)
        except ValueError:
            sys.exit("ERROR: The left and right bounds must be intergers.")
        else:
            # plus 1 for space for +/-
            s = max(len(str(abs(self.LEFT_BOUND))), 
                    len(str(abs(self.RIGHT_BOUND))))+1
            return s

    def parse_equation(self):
        """ turns equation string into a useable function
        
            returns the maximum power value
        
            the equation should have simple exponents
            i.e. no bracketed exponents
            
            the equation should have a single variable
            (for now, anyway - this should be easy to fix
            later)
            
            add feature to change all variables to x (only
            if there is a single variable)
        """
        variables = []
        powers = []
        p = ''
        for c in self.equation:
            if p == '**':
                powers.append(int(c))
                p = ''
            elif c == '*':
                p+='*'
            elif c.isalpha():
                variables.append(c)  
        all_same = True
        if variables:
            first = ord(variables[0])
            for v in variables:
                if ord(v) != first:
                    all_same = False
        else:
            first = 120
        # if they are all the same letter and not equal to 'x'
        if all_same and first != 120:
            self.equation = self.equation.replace(variables[0], 'x')
        return max(powers)

    def generate_population(self):
        """ generates a population of possible roots
            maximum fitness is granted if the
            population member is a root (or within error)
            i.e. max fitness when:
                f(pmem) = [-error, error]
            makes a population of random numbers
            that are in the domain:
            [LEFT_BOUND, RIGHT_BOUND]
            the size of each number (i.e. how many decimal places)
            is determined by the error (default 10e-6)
        """
        self.population = []
        for _ in range(self.POP_SIZE):
            pmem = random.randint(self.LEFT_BOUND, self.RIGHT_BOUND)
            # don't want to exceed bounds
            if pmem == self.LEFT_BOUND or pmem == self.RIGHT_BOUND:
                pmem = str(pmem)+'.'+'0'*self.error_length
            else:
                pmem = str(pmem)+'.'
                for i in range(self.error_length):
                    pmem+=str(random.randint(0,9))
            # add '-' placeholder
            if pmem[0] != '-':
                pmem = '+'+pmem
            # add '0' placeholders
            while len(pmem[:pmem.index('.')]) != self.value_length:
                if pmem[0] == '-':
                    pmem = '-0'+pmem[1:]
                else:
                    pmem = '+0'+pmem[1:]
            

            self.population.append(pmem)
        self.v_print(('population:', self.population))
        return self.population

    def get_error_length(self):
        """ finds out the size of the error (as a string)
        """
        if self.ERROR >= 1 or self.ERROR <= 0:
            raise ValueError("The error value should be in the range (0,1).")
        str_er = str(self.ERROR)
        try:
            meow = str_er.index('e')
        except ValueError:
            decimal = str_er.index('.')
            meow = len(str_er[decimal+1:])
            return meow
        else:
            decimal_places = int(str_er[meow+2:])
            return decimal_places

    def tournament(self):
        """ tournament selection to determine
            which pmems to evaluate
        """
        if self.T_SIZE > self.POP_SIZE:
            raise ValueError("The tournament size cannot be larger than the population size.")
        tourney = []
        for _ in range(self.T_SIZE):
            while True:
                r = random.randint(0, self.POP_SIZE-1)
                if r not in tourney:
                    tourney.append(r)
                    break
        return tourney

    def eval_fitness(self, ty):
        """ for each member of the population
            in the tournament (ty), evaluate fitness
            
            fitness will be the absolute value
            of the function at the pmem
            want smallest fitness (closest to zero)
        """
        results = []
        for pmem in ty:
            x = float(self.population[pmem])
            y = eval(self.equation)
            results.append([pmem, x, y, abs(y)])
        
        results = sorted(results, key=itemgetter(3))

        return results

    def new_eval_fitness(self, ty):
        """ new fitness evaluation to try and solve issues whereby
            all of the pmems have the exact same fitness
            
            add a penalty to fitness equal to how many other
            pmems have a similar result in the tournament
            selection
        """
        results = []
        for pmem in ty:
            x = float(self.population[pmem])
            y = eval(self.equation)
            results.append([pmem, x, y, abs(y)])
        
        extra = []
        # loop over x values
        for i, t in enumerate(results):
            count = 0
            for r in results:
                if float(r[1])-0.25 <= t[1] <= float(r[1])+0.25:
                    count += 1
            results[i][3] += count*10
            
        results = sorted(results, key=itemgetter(3))
        
        
            
        
        return results
    
    def mutate(self, pmem):
        """ the mutate function works on a population member
            (i.e. pmem). the pmem variable is equal to an index
            from the self.population list
            the return value is a new pmem value
            the number of point mutations applied to the parent
            population member is equal to a random number
            between 1 and the self.MNM value (MNM = maximum number
            of mutations)
            
            if a value of a parent is -10.001 and a mutation
            location of 0 is chosen, then there is a chance
            to change the value of the child to +10.001
            this chance is set to 1 in 4 (25%)
            
            note: the change of sign is not a symmetrical
            operator (i.e. cannot change positive value to
            negative). not sure if this will favour positive
            values so much as to break the code, but we shall see
            might just be easier to not mutate the sign (in that
            case just change flip chance to 0)
            
            RESULT: using a non-zero flip value (0.25) actually
            prevented the algorithm from finding a root (because
            the chance of getting a negative was lower than a
            positive - the population was skewed to be positive)
            aka bad for symmetric functions
            only useful to use the non-zero flip value if you
            are specifically looking for a positive root
            
            I could later imbue a small chance that a mutation
            causes a decimal point change, although
            that would be more complicated to implement (so add
            as a maybe for later)
            
            BUG POSSIBLE: if the MNM value is higher than
            the length of the "gene" aka value then this function
            could get stuck in an infinite loop. make sure to fix
            that here before submitting final version
            
            PROBLEM: algorithm gets easily stuck in positive root
            need to add a mutation to switch from positive to negative
            that isn't asymmetric. well actually it can find the
            negative root it just gets stuck really easily
        """
        # get the parent value at the given pmem location
        parent_value = self.population[pmem]
        # make a child copy of the parent
        child_value = parent_value[:]
        
        # how many mutations to do
        # make sure that the number of mutations cannot exceed
        # the length of the "gene" (avoids infinite loop below)
        # it is called as parent_value - 1 to account for the decimal
        # point (which at present cannot be mutated)
        if len(parent_value)-1 < self.MNM:
            num_mutations = random.randint(1, len(parent_value)-1)
        else:
            num_mutations = random.randint(1, self.MNM)
        # for debugging purposes
        #num_mutations = 5
        # mutation locations list
        m_loc = []
        for _ in range(num_mutations):
            while True:
                # choose a location to mutate
                loc = random.randint(0, len(parent_value)-1)
                # make sure it's not the decimal point
                # make sure the location hasn't already been chosen
                if parent_value[loc] != '.' and loc not in m_loc:
                    m_loc.append(loc)
                    break
        
        while True:
            for l in m_loc:
                if not l:
                    chance = random.randint(1,100)
                    if chance <= self.FLIP_CHANCE*100:
                        if parent_value[0] == '-':
                            new_value = '+'
                        else:
                            new_value = '-'
                    elif parent_value[l] == '-':
                        new_value = '-'
                    else:
                        new_value = '+'
                else:
                    new_value = str(random.randint(0,9))
                child_value = child_value[:l]+new_value+child_value[l+1:]
            # make sure child is within boundaries before returning it
            if self.LEFT_BOUND <= float(child_value) <= self.RIGHT_BOUND:
                return child_value

    def replace(self, t_data):
        """ the input is the tournament data (list of lists)
            there is no explicit output. only the population
            is changed to remove the worst members of the tournament
            and replace these members with the offspring of the
            best members of the tournament
        """
        child1 = self.mutate(t_data[0][0])
        child2 = self.mutate(t_data[1][0])

        self.population[t_data[-1][0]] = child1
        self.population[t_data[-2][0]] = child2
        # check to see if any of the children/parents are roots
        for i in (0,1,-1,-2):
            x = float(self.population[t_data[i][0]])
            result = eval(self.equation)
            if -self.ERROR <= result <= self.ERROR:
                self.check_root(t_data[i][0])
        self.v_print(('\nnew population:', self.population))
        
    def check_root(self, pmem):
        """ see if the given population member is within
            ERROR of being a root. if yes, add to self.roots
            
            note: should also check to see if it is an improvement
            to the current roots (if there are any)
            
            first should make it check if max roots is satisfied
            
            working here
        """
        x = float(self.population[pmem])
        result = eval(self.equation)
        
        # if no roots have been found yet
        if not self.roots:
            self.roots.append(x)
            return

        # if self.roots is non-empty
        # check if root is better
        # and also that root is not significantly different
        # from other roots (i.e. don't want multiple of the
        # same root)
        for i, rt in enumerate(self.roots):
            x = rt
            old_result = eval(self.equation)
            if rt-self.SIG <= float(self.population[pmem]) <= rt+self.SIG:
                if result < old_result:
                    self.roots[i] = float(self.population[pmem])
                    return
            elif len(self.roots) < self.MAX_ROOTS:
                if float(self.population[pmem]) != rt:
                # add root
                    self.roots.append(float(self.population[pmem]))
                    return

if __name__ == '__main__':
    # mevs=mating events, aka how long the program will run
    MEVS = 10000
    # or you can call the function until some bound has been reached
    # initialise RootSolver object
    test2 = RootSolver("y**2+7*y-10", VERBOSE=False, POP_SIZE=15, MNM=5, ERROR=0.0001, T_SIZE=7)
    # run over mevs
    for _ in range(MEVS):
        t = test2.tournament()      # choose tourney members
        r = test2.eval_fitness(t)   # eval fitnesses for tourney members
        test2.replace(r)         # swap worst tourney for best parents' children
        #print(test2.roots)
    print('\n', test2.roots, sep='')







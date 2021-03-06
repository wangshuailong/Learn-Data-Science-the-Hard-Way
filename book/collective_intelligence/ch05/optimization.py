#! /usr/bin/env python

import time
import random
import math

people= [('Setmor', 'BOS'),
        ('Franny', 'DAL'),
        ('Zooey', 'CAK'),
        ('Walt', 'ORD'),
        ('Buddy', 'ORD'),
        ('Les', 'OMA')]

# LaGuardia airport in New York
destination = 'LGA'

flights = {}

for line in file('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])

    # add details to the list of possiable flights
    flights[(origin, dest)].append((depart, arrive, int(price)))

def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3]*60 + x[4]

def printschedule(r):
    for d in range(len(r)/2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[d]]
        ret = flights[(destination, origin)][r[d + 1]]
        print '%10s%10s %5s%5s $%3s %5s-%5s $%3s' % (name, origin,
                out[0], out[1], out[2], ret[0], ret[1], ret[2])

def schedulecost(sol):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24 * 60

    for d in range(len(sol)/2):
        # Get the inbound and outbound flights
        origin = people[d][1]
        print flights[(origin, destination)]
        print int(sol[d])
        print 'd', d
        print 'sol: ', sol
        print flights[(origin, destination)][int(sol[d])]
        outbound = flights[(origin, destination)][int(sol[d])]
        # print outbound
        print flights[(destination, origin)]
        print 'returnf: ', [int(sol[d])]
        returnf = flights[(destination, origin)][int(sol[d])]

        # Total price is the price of all outbound and return flights
        totalprice += outbound[2]
        totalprice += returnf[2]

        # Track the latest arrival and earliest departure
        if latestarrival < getminutes(outbound[1]):
            latestarrival = getminutes(outbound[1])
        if earliestdep > getminutes(outbound[0]):
            earliestdep = getminutes(returnf[0])

    # Every Person must wait at the airport until the latest person arrives
    # They also must arrive at the same time and wait for their flights
    totalwait = 0
    for d in range(len(sol)/2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        returnf = flights[(destination, origin)][int(sol[d])]
        totalwait += latestarrival - getminutes(outbound[1])
        totalwait += earliestdep - getminutes(returnf[0]) # - earliestdep

    # Does this solution require an extra day of car rental?
    # That will be 50 $
    if latestarrival > earliestdep:
        totalprice += 50
        
    return totalprice + totalwait

def randomoptimize(domain, costf):
    best = 999999999
    bestr = None
    for i in range(10000):
        # create a random solution
        r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

        # get the cost
        cost = costf(r)

        # compare with the best one so far
        if cost < best:
            best = cost
            bestr = r
    return r

def hillclimb(domain, costf):
    # create a random solution
    sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
    print 'sol: ', sol

    # Main loop
    while 1:
        # create list of neighboring solution
        neighbors = []
        for j in range(len(domain)):

            # One way in each direction
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0: j] + [sol[j] + 1] + sol[j + 1: ])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0: j] + [sol[j] - 1] + sol[j + 1: ])

        # see what the best solution among the neighbors is
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            print neighbors[j]
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]

        # If there's no improvement, then we have reached the top
        if best == current:
            break

    return sol

def annealingoptimize(domain, costf, T = 10000.0, cool = 0.95, step = 1):
    # Initialize the values randomly
    vec = [float(random.randint(domain[i][0], domain[i][1])) for i in range(len(domain))]

    while T > 0.1:
        # Choose one of the indices
        i = random.randint(0, len(domain) - 1)

        # choose a direction to change it
        dir = random.randint(-step, step)

        # create a new list with one of the values changed
        vecb = vec[:]
        vecb[i] += dir
        if vecb[i] < domain[i][0]:
            vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]:
            vecb[i] = domain[i][1]

        # calculate the current cost and the new cost
        ea = costf(vec)
        eb = costf(vecb)
        p = pow(math.e, (-eb-ea)/T)

        # Is this better or does it make the probability cutoff
        if (eb < ea or random.random() < p):
            vec = vecb

        # decrease the temperature
        T = T*cool
    return vec

def geneticoptimize(domain, costf, popsize = 50, step = 1, 
        mutprod = 0.2, elite = 0.2, maxiter = 100):
    # Mutation operation
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        print 'i value: ', i
        print 'vec[i]: ', vec[i]
        print 'domain[i][0]: ', domain[i][0]
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            print 'test mutate 1'
            return vec[0: i] + [vec[i] - step] + vec[i + 1: ]
        else: # if vec[i] < domain[i][1]:
            print 'test mutate 2'
            return vec[0: i] + [vec[i] + step] + vec[i + 1: ]

    # Crossover operation
    def crossover(r1, r2):
        i = random.randint(1, len(domain) - 2)
        return r1[0: i] + r2[i: ]

    # Build the Initial population
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
        pop.append(vec)

    # for p in pop:
        # print p
        # pscore = [costf(p), p]
        # print pscore
        # l = range(len(p)/2)
        # print l

    # How many winners for each generation
    topelite = int(elite * popsize)

    # Main loop
    for i in range(maxiter):
        # print i, '\n'
        # print '\n'
        # print pop
        # for p in pop:
        #     s = costf(p)
        #     print p, s
        #    print '\n'
        # print 'test'
        scores = [(costf(v), v) for v in pop]
        # print 'get score %d', i , scores 
        scores.sort()
        # print 'scores sort: ', scores
        ranked = [v for (s, v) in scores]

        # start with the pure winner
        pop = ranked[0: topelite]
        print 'pop: ', pop

        # Add mutate and bred forms of the winner
        while len(pop) < popsize:
            if random.random() < mutprod:
                # Mutation
                c = random.randint(0, topelite)
                print 't1c:', c
                print 'ranked c: ', ranked[c]
                print mutate(ranked[c])
                pop.append(mutate(ranked[c]))
                print 'pop append 1: ', pop
            else:
                #Crossover
                c1 = random.randint(0, topelite)
                c2 = random.randint(0, topelite)
                print 't2c1: ', c1
                print 'ranked[c1]', ranked[c1]
                print 'ranked[c2]', ranked[c2]
                print crossover(ranked[c1], ranked[c2])
                pop.append(crossover(ranked[c1], ranked[c2]))
                print 'pop append 2: ', pop
        print 'ttttttttttt'
        print pop
        # print current best score
        print scores[0][0]

    return scores[0][1]


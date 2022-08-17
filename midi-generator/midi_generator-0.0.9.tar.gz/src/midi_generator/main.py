import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

from .config import Configuration
from .genetic import generator, fitness, mutation, check_remaining_ticks, individual_to_melody
from deap import base, creator, tools, algorithms

from output import write_file


def ea_simple_with_elitism(population, toolbox, cxpb, mutpb, ngen, stats=None,
                           hall_of_fame=None, verbose=False):
    """This algorithm is similar to DEAP eaSimple() algorithm, with the modification that
    halloffame is used to implement an elitism mechanism. The individuals contained in the
    halloffame are directly injected into the next generation and are not subject to the
    genetic operators of selection, crossover and mutation.
    """
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if hall_of_fame is None:
        raise ValueError("halloffame parameter must not be empty!")

    hall_of_fame.update(population)
    hof_size = len(hall_of_fame.items) if hall_of_fame.items else 0

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen + 1):

        # Select the next generation individuals
        offspring = toolbox.select(population, len(population) - hof_size)

        # Vary the pool of individuals
        offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # add the best back to population:
        offspring.extend(hall_of_fame.items)

        # Update the hall of fame with the generated individuals
        hall_of_fame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    return population, logbook


if __name__ == '__main__':
    toolbox = base.Toolbox()
    configuration = Configuration()
    gene_generator = generator(Configuration())
    toolbox.register("Note", gene_generator)
    creator.create("FitnessComposed", base.Fitness, weights=(-1.0, -1.0))
    creator.create("Individual", list, fitness=creator.FitnessComposed)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.Note, n=32)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", fitness)
    toolbox.register("select", tools.selStochasticUniversalSampling)
    toolbox.register("mutate", mutation, configuration)
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("select", tools.selTournament, tournsize=3)
    decorator = check_remaining_ticks()
    toolbox.decorate("mate", decorator)
    toolbox.decorate("mutate", decorator)
    population = toolbox.population(30)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min)
    stats.register("avg", np.mean)
    stats.register("min_axis", np.min, axis=0)
    stats.register("avg_axis", np.mean, axis=0)

    hof = tools.HallOfFame(10)
    population, logbook = ea_simple_with_elitism(population, toolbox, cxpb=0.4, mutpb=0.2,
                                                 ngen=100, stats=stats, hall_of_fame=hof)

    hof.update(population)
    best = hof.items[0]
    print("-- Best Ever Individual = ", best)
    print("-- Best Ever Fitness = ", best.fitness.values)

    # plot statistics:
    minFitnessValues, meanFitnessValues = logbook.select("min", "avg")
    plt.figure(1)
    sns.set_style("whitegrid")
    plt.xlabel('Generation')
    plt.ylabel('Min / Average Fitness')
    plt.title('Min and Average fitness over Generations')
    plt.plot(minFitnessValues, color="red")
    plt.plot(meanFitnessValues, color='green')

    minFitnessValues, meanFitnessValues = logbook.select("min_axis", "avg_axis")
    minSyncopationValues = list(map(lambda x: x[0], minFitnessValues))
    meanSyncopationValues = list(map(lambda x: x[0], meanFitnessValues))
    minNotesNo = list(map(lambda x: x[1], minFitnessValues))
    meanNotesNo = list(map(lambda x: x[1], minFitnessValues))

    plt.figure(2)
    plt.title('Syncopation min and avg')
    plt.xlabel('Generation')
    plt.ylabel('Min / Average syncopation')
    plt.plot(minSyncopationValues, color="red")
    plt.plot(meanSyncopationValues, color="green")
    plt.figure(3)
    plt.title('Notes min and avg')
    plt.xlabel('Generation')
    plt.ylabel('Min / Average notes')
    plt.plot(minNotesNo, color="red")
    plt.plot(meanNotesNo, color="green")
    plt.show()

    write_file(individual_to_melody(best), "best")
    write_file(individual_to_melody(best), 'best')

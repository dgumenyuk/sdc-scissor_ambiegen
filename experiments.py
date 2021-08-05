import click
import os

@click.group()
def cli():
    pass


@cli.command()
@click.option('--generator', default='frenetic', help='Test case generator')
@click.option('--risk-factor', default=0.7, help='Risk factor of the driving AI')
@click.option('--time-budget', default=10, help='Time budget for generating tests')
@click.option('--oob-tolerance', default=0.95, help='Proportion of the car allowd to go off the lane')
@click.option('--speed-limit', default=70, help='Speed limit in km/h')
@click.option('--map-size', default=200, help='Size of the road map')
def run_simulations(generator, risk_factor, time_budget, oob_tolerance, speed_limit, map_size):

    command = r"python .\competition.py "
    command += r"--visualize-tests "
    command += r"--time-budget " + str(time_budget) + r" "
    command += r"--oob-tolerance " + str(oob_tolerance) + r" "
    command += r"--risk-factor " + str(risk_factor) + r" "
    command += r"--speed-limit " + str(speed_limit) + r" "
    command += r"--executor beamng "
    command += r"--beamng-home C:\Users\birc\Documents\BeamNG.research.v1.7.0.1 "
    command += r"--beamng-user C:\Users\birc\Documents\BeamNG.research "
    command += r"--map-size " + str(map_size) + r" "
    command += r"--module-name frenetic.src.generators.random_frenet_generator "
    command += r"--class-name CustomFrenetGenerator"

    if generator == 'frenetic':
        os.system(command)
    else:
        print('Unknown test generator: {}'.format(generator))
    

if __name__ == '__main__':
    cli()

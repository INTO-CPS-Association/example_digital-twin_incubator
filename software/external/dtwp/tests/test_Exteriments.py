import unittest

import Experiments


class ExperimentTest(unittest.TestCase):

    def testSequence(self):
        sequence_list = []

        class MyExperiment(Experiments.Experiment):
            def describe(self):
                pass

            def do_experiment(self):
                sequence_list.append(1)

        experiment = MyExperiment()
        experiment.run()
        self.assertSequenceEqual(sequence_list, [1])

    def testServiceSequence(self):
        sequence_list = []
        sequence_persistent_list = []
        tester = self

        class ServiceX:

            def __init__(self, name):
                self.name = name

            def __enter__(self):
                sequence_list.append(self.name)
                sequence_persistent_list.append(self.name)

            def __exit__(self, type, value, traceback):
                index = len(sequence_list) - 1 - sequence_list[::-1].index(self.name)
                del sequence_list[index]

        class MyExperimentService(Experiments.ExperimentWithServices):
            def get_services(self):
                return [ServiceX('A'), ServiceX('B')]

            def describe(self):
                pass

            def do_experiment(self):
                tester.assertSequenceEqual(sequence_list, ['A', 'B'])
                sequence_list.append(1)

        experiment = MyExperimentService()
        experiment.run()
        self.assertSequenceEqual(sequence_list, [1])
        self.assertSequenceEqual(sequence_persistent_list, ['A', 'B'])

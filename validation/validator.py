import abc
import logging

import numpy as np

from matplotlib import pyplot as plt
from scipy.stats import chisquare


class Validator(abc.ABC):
    def __init__(
        self,
        num_candidates,
        all_outcomes=None,
        sampler_func=None,
        sampler_parameters=None,
    ):
        self.num_candidates = num_candidates
        if all_outcomes:
            self.all_outcomes = all_outcomes
        else:
            self.all_outcomes = []
            self.set_all_outcomes()
        self.sampler_func = sampler_func
        if sampler_parameters is None:
            sampler_parameters = {}
        self.sampler_parameters = sampler_parameters
        self.theoretical_distribution = None
        self.observed_distribution = None
        self.chi_square_result = None

    def sampler(self, num_samples):
        """
        The sampler, returns observations
        """
        return [
            self.sample_cast(s)
            for s in self.sampler_func(
                num_samples, self.num_candidates, **self.sampler_parameters
            )
        ]

    @abc.abstractmethod
    def sample_cast(self, sample):
        """
        Cast the samples returned by the sampler to the correct type (tuple for ordinal samplers).
        """

    @abc.abstractmethod
    def set_all_outcomes(self):
        """
        Populates the `self.all_outcomes` member of the class.
        """
        pass

    @abc.abstractmethod
    def set_theoretical_distribution(self):
        """
        Populates the `self.theoretical_distribution` member of the class.
        """
        pass

    def set_observed_distribution(self, num_samples):
        """
        Populates the `self.observed_distribution` member of the class.
        """
        samples = np.zeros(len(self.all_outcomes))
        for obs in self.sampler(num_samples):
            samples[self.all_outcomes.index(obs)] += 1
        self.observed_distribution = samples / num_samples

    def run(
        self,
        num_samples,
        model_name="",
        graph_title="",
        graph_xlabel="",
        graph_ylabel="",
        graph_x_tick_labels=None,
        graph_file_path=None,
    ):
        self.set_theoretical_distribution()
        self.set_observed_distribution(num_samples)
        self.run_chi_square_test()

        if not graph_title:
            if not model_name:
                model_name = self.__name__.replace("Validator", "")
            graph_title = f"Observed versus theoretical frequencies for {model_name}"
            graph_title += f"\n(#num_candidates = {self.num_candidates}"
            if self.sampler_parameters:
                graph_title += ', '
                for key, value in self.sampler_parameters.items():
                    graph_title += f"{key} = {value}, "
                graph_title = graph_title[:-2]

            graph_title += (
                f")\n#samples = {num_samples}, chi² p-value = {self.chi_square_result.pvalue}"
            )

        self.plot_frequencies(
            graph_title=graph_title,
            xlabel=graph_xlabel,
            ylabel=graph_ylabel,
            x_tick_labels=graph_x_tick_labels,
            file_path=graph_file_path,
        )

    def run_chi_square_test(self):
        if self.theoretical_distribution is None or self.observed_distribution is None:
            raise ValueError(
                "Before running the chi_sqaure test you need to populate the "
                "`theoretical_distribution` and the `observed_distribution` "
                "members of the validator"
            )
        test_result = chisquare(
            f_obs=self.observed_distribution, f_exp=self.theoretical_distribution
        )
        if test_result.pvalue < 0.1:
            logging.error(f"\tChi-Square test failed, p-value is {test_result.pvalue}.")
            logging.error(
                f"\tThe observed frequencies likely do not follow the theoretical "
                "distribution."
            )
        else:
            logging.info(f"\tChi-Square test passed, p-value is {test_result.pvalue}.")
            logging.info(
                "\tWe cannot conclude that the observations do not come from the theoretical "
                "distribution."
            )
        self.chi_square_result = test_result

    def plot_frequencies(
        self,
        graph_title="",
        xlabel="",
        ylabel="",
        x_tick_labels=None,
        file_path=None,
    ):
        if self.theoretical_distribution is None or self.observed_distribution is None:
            raise ValueError(
                "Before ploting the frequency graph you need to populate the "
                "`theoretical_distribution` and the `observed_distribution` "
                "members of the validator"
            )
        plt.close("all")

        sort_permutation = np.flip(self.theoretical_distribution.argsort())
        frequencies = self.observed_distribution[sort_permutation]
        distribution = self.theoretical_distribution[sort_permutation]
        if x_tick_labels:
            new_x_tick_labels = [x_tick_labels[k] for k in sort_permutation]
            x_tick_labels = new_x_tick_labels

        fig, ax = plt.subplots()
        ax.bar(np.arange(len(frequencies)) - 0.2, frequencies, width=0.4)
        ax.bar(np.arange(len(distribution)) + 0.2, distribution, width=0.4)
        if not graph_title:
            graph_title = "Observed versus theoretical frequencies"
        ax.set_title(graph_title)
        ax.legend(["Observations", "Theoretical"])
        if not xlabel:
            xlabel = "Rank identifier (ordered by theoretical frequency)"
        ax.set_xlabel(xlabel)
        if not ylabel:
            ylabel = "Frequency"
        ax.set_ylabel(ylabel)
        if x_tick_labels:
            ax.set_xticks(range(len(x_tick_labels)))
            ax.set_xticklabels(x_tick_labels, rotation=90)

        if file_path:
            plt.savefig(file_path, bbox_inches="tight", dpi=300)
        else:
            plt.show()

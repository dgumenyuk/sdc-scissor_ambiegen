import logging

import pandas as pd
import numpy as np
import sklearn.metrics

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import KFold, cross_validate, train_test_split, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.preprocessing import LabelEncoder
from sklearn import preprocessing
from sklearn.metrics import classification_report


def _cost_effectiveness_scorer(estimator, X, y):
    estimator.fit(X, y)
    y_pred = estimator.predict(X)
    nr_safe_predicted = np.sum(y_pred)
    nr_unsafe_predicted = len(y_pred) - nr_safe_predicted

    rand_sim_times = []
    random_unsafe_predicted = np.random.permutation(
        np.append(np.ones(nr_unsafe_predicted, dtype="int32"), np.zeros(nr_safe_predicted), dtype="int32")
    )
    rand_sim_times.append(np.sum(X[random_unsafe_predicted]))

    random_tot_sim_time = np.mean(rand_sim_times)

    sdc_scissor_tot_sim_time = np.sum(X[y_pred])
    pass


class CostEffectivenessEvaluator:
    def __init__(self, classifier, data_frame: pd.DataFrame, label: str, time_attribute: str):
        """

        :param classifier:
        :param data_frame:
        :param label:
        :param time_attribute:
        """
        self.classifier = classifier
        self.data_frame = data_frame
        self.label = label
        self.time_attribute = time_attribute
        self.X_model_attributes = [
            "direct_distance",
            "full_road_diversity",
            "mean_road_diversity",
            "max_angle",
            "max_pivot_off",
            "mean_angle",
            "mean_pivot_off",
            "median_angle",
            "median_pivot_off",
            "min_angle",
            "min_pivot_off",
            "num_l_turns",
            "num_r_turns",
            "num_straights",
            "road_distance",
            "std_angle",
            "std_pivot_off",
            "total_angle",
        ]

    def evaluate_with_random_baseline(self, train_split=0.8, top_k=5):
        """
        Evaluate the cost-effectiveness of SDC-Scissor.
        """
        dd = self.data_frame
        dd = dd.dropna()
        dd = dd.sample(frac=1, ignore_index=True, random_state=12)

        le = LabelEncoder()
        dd[self.label] = le.fit_transform(dd[self.label])

        n = dd.shape[0]
        logging.debug("N={}".format(n))
        n_train = int(n * train_split)
        n_test = n - n_train
        dd_train: pd.DataFrame = dd.iloc[:n_train, :]
        dd_test: pd.DataFrame = dd.iloc[n_train:, :]

        dd_train_passes = dd_train.iloc[le.inverse_transform(dd_train[self.label]) == "PASS", :]
        dd_train_fails = dd_train.iloc[le.inverse_transform(dd_train[self.label]) == "FAIL", :]

        n_train_passes = dd_train_passes.shape[0]
        n_train_fails = dd_train_fails.shape[0]
        logging.debug("n_train_passes={}, n_train_fails={}".format(n_train_passes, n_train_fails))
        diff = np.abs(n_train_passes - n_train_fails)

        # sampling for balancing
        if n_train_passes > n_train_fails:
            dd_diff = dd_train_fails.sample(diff)
            logging.debug("dd_diff: {}".format(dd_diff))
            dd_train_balanced = pd.concat([dd_train, dd_diff])
        elif n_train_passes < n_train_fails:
            dd_diff = dd_train_passes.sample(diff)
            logging.debug("dd_diff: {}".format(dd_diff))
            dd_train_balanced = pd.concat([dd_train, dd_diff])
        else:
            dd_train_balanced = dd_train

        self.classifier.fit(dd_train_balanced[self.X_model_attributes], dd_train_balanced[self.label])
        y_pred_encoded = self.classifier.predict(dd_test[self.X_model_attributes])

        y_pred_probs = self.classifier.predict_proba(dd_test[self.X_model_attributes])
        logging.debug("class probabilities: {}".format(y_pred_probs))

        y_pred = le.inverse_transform(y_pred_encoded)
        dd_test[self.label] = le.inverse_transform(dd_test[self.label])
        y_true = dd_test[self.label]
        logging.debug(classification_report(y_true, y_pred))
        logging.debug("classes: {}".format(self.classifier.classes_))

        fail_encoded = le.transform(["FAIL"])[0]
        pass_encoded = 1 - fail_encoded
        logging.debug("fail_encoded={}".format(fail_encoded))

        is_predicted_unsafe = y_pred == "FAIL"

        pd.set_option("mode.chained_assignment", None)
        dd_y_pred_probs = pd.DataFrame({"PASS": y_pred_probs[:, pass_encoded], "FAIL": y_pred_probs[:, fail_encoded]})
        dd_test["PASS_prob"] = dd_y_pred_probs["PASS"].to_numpy().copy()
        dd_test["FAIL_prob"] = dd_y_pred_probs["FAIL"].to_numpy().copy()

        dd_test_unsafe_predicted: pd.DataFrame = dd_test.loc[is_predicted_unsafe, :]
        dd_test_unsafe_predicted_sorted = dd_test_unsafe_predicted.sort_values(by=["FAIL_prob"], ascending=False)
        dd_top_k = dd_test_unsafe_predicted_sorted.iloc[:top_k, :]

        nr_true_positives = np.sum(dd_top_k[self.label] == 'FAIL')
        nr_negatives = np.sum(dd_top_k[self.label] == 'PASS')
        ce = nr_true_positives / nr_negatives

        tot_sim_time_by_sdc_scissor = np.sum(dd_top_k[self.time_attribute])
        tot_sim_time_by_sdc_scissor_true_positives = np.sum(dd_top_k.loc[dd_top_k[self.label] == 'FAIL', self.time_attribute])

        beta = tot_sim_time_by_sdc_scissor_true_positives / tot_sim_time_by_sdc_scissor
        logging.debug("beta={}".format(beta))

        gamma_lst = []
        ce_baseline_lst = []
        for i in range(30):
            dd_rand_sample = dd_test.sample(top_k, ignore_index=True)
            nr_true_positives_baseline = np.sum(dd_rand_sample[self.label] == 'FAIL')
            nr_negatives_baseline = np.sum(dd_rand_sample[self.label] == 'PASS')
            ce_baseline_lst.append(nr_true_positives_baseline / nr_negatives_baseline)
            tot_random_baseline_time = np.sum(dd_rand_sample[self.time_attribute])
            tot_random_baseline_time_true_positives = np.sum(dd_rand_sample.loc[dd_rand_sample[self.label] == 'FAIL', self.time_attribute])
            gamma_tmp = tot_random_baseline_time_true_positives / tot_random_baseline_time
            gamma_lst.append(gamma_tmp)

        gamma = np.mean(gamma_lst)
        logging.debug('gamma={}'.format(gamma))
        ce_baseline = np.mean(ce_baseline_lst)
        return ce, beta, ce_baseline, gamma

    def evaluate_with_longest_roads(self, train_split=0.8, top_k=5):
        dd = self.data_frame
        dd = dd.dropna()
        dd = dd.sample(frac=1, ignore_index=True, random_state=12)

        le = LabelEncoder()
        dd[self.label] = le.fit_transform(dd[self.label])

        n = dd.shape[0]
        logging.debug("N={}".format(n))
        n_train = int(n * train_split)
        n_test = n - n_train
        dd_train: pd.DataFrame = dd.iloc[:n_train, :]
        dd_test: pd.DataFrame = dd.iloc[n_train:, :]

        dd_train_passes = dd_train.iloc[le.inverse_transform(dd_train[self.label]) == "PASS", :]
        dd_train_fails = dd_train.iloc[le.inverse_transform(dd_train[self.label]) == "FAIL", :]

        n_train_passes = dd_train_passes.shape[0]
        n_train_fails = dd_train_fails.shape[0]
        logging.debug("n_train_passes={}, n_train_fails={}".format(n_train_passes, n_train_fails))
        diff = np.abs(n_train_passes - n_train_fails)

        # sampling for balancing
        if n_train_passes > n_train_fails:
            dd_diff = dd_train_fails.sample(diff)
            logging.debug("dd_diff: {}".format(dd_diff))
            dd_train_balanced = pd.concat([dd_train, dd_diff])
        elif n_train_passes < n_train_fails:
            dd_diff = dd_train_passes.sample(diff)
            logging.debug("dd_diff: {}".format(dd_diff))
            dd_train_balanced = pd.concat([dd_train, dd_diff])
        else:
            dd_train_balanced = dd_train

        self.classifier.fit(dd_train_balanced[self.X_model_attributes], dd_train_balanced[self.label])
        y_pred_encoded = self.classifier.predict(dd_test[self.X_model_attributes])
        y_pred_probs = self.classifier.predict_proba(dd_test[self.X_model_attributes])
        dd_test[self.label] = le.inverse_transform(dd_test[self.label])
        y_pred = le.inverse_transform(y_pred_encoded)
        y_true = dd_test[self.label]
        logging.debug(classification_report(y_true, y_pred))

        fail_encoded = le.transform(["FAIL"])[0]
        pass_encoded = 1 - fail_encoded
        logging.debug("fail_encoded={}".format(fail_encoded))

        is_predicted_unsafe = y_pred == "FAIL"

        pd.set_option("mode.chained_assignment", None)
        dd_y_pred_probs = pd.DataFrame({"PASS": y_pred_probs[:, pass_encoded], "FAIL": y_pred_probs[:, fail_encoded]})
        dd_test["PASS_prob"] = dd_y_pred_probs["PASS"].to_numpy().copy()
        dd_test["FAIL_prob"] = dd_y_pred_probs["FAIL"].to_numpy().copy()

        dd_test_unsafe_predicted: pd.DataFrame = dd_test.loc[is_predicted_unsafe, :]
        dd_test_unsafe_predicted_sorted = dd_test_unsafe_predicted.sort_values(by=["FAIL_prob"], ascending=False)
        dd_top_k = dd_test_unsafe_predicted_sorted.iloc[:top_k, :]

        nr_true_positives = np.sum(dd_top_k[self.label] == 'FAIL')
        nr_negatives = np.sum(dd_top_k[self.label] == 'PASS')
        ce_sdc_scissor = nr_true_positives / nr_negatives

        is_predicted_unsafe = y_pred == "FAIL"
        nr_unsafe_predicted = np.sum(is_predicted_unsafe)
        logging.debug("{} tests as unsafe predicted.".format(nr_unsafe_predicted))

        tot_sim_time_by_sdc_scissor = np.sum(dd_top_k[self.time_attribute])
        tot_sim_time_by_sdc_scissor_true_positives = np.sum(dd_top_k.loc[dd_top_k[self.label] == 'FAIL', self.time_attribute])
        logging.debug("total simulation time by SDC-Scissor: {} seconds".format(tot_sim_time_by_sdc_scissor))
        beta = tot_sim_time_by_sdc_scissor_true_positives / tot_sim_time_by_sdc_scissor

        dd_test_sorted_by_length = dd_test.sort_values(by=["road_distance"], ascending=False)
        logging.debug("sorted by road_distance: {}".format(dd_test_sorted_by_length["road_distance"]))

        dd_road_length_baseline_selection = dd_test_sorted_by_length.loc[np.arange(n_test) < top_k, :]
        nr_true_positives_rl_baseline = np.sum(dd_road_length_baseline_selection[self.label] == 'FAIL')
        nr_negatives_rl_baseline = np.sum(dd_road_length_baseline_selection[self.label] == 'PASS')
        ce_rl_baseline = nr_true_positives_rl_baseline / nr_negatives_rl_baseline

        tot_road_length_baseline_time = np.sum(dd_road_length_baseline_selection[self.time_attribute])
        tot_road_length_baseline_time_true_positives = np.sum(
            dd_road_length_baseline_selection.loc[dd_road_length_baseline_selection[self.label] == 'FAIL', self.time_attribute]
        )

        ce_random_baseline_lst = []
        for i in range(30):
            dd_rand_sample = dd_test.sample(top_k, ignore_index=True)
            nr_true_positives_baseline = np.sum(dd_rand_sample[self.label] == 'FAIL')
            nr_negatives_baseline = np.sum(dd_rand_sample[self.label] == 'PASS')
            ce_random_baseline_lst.append(nr_true_positives_baseline / nr_negatives_baseline)

        ce_random_baseline = np.mean(ce_random_baseline_lst)

        gamma = tot_road_length_baseline_time_true_positives / tot_road_length_baseline_time
        return ce_sdc_scissor, ce_random_baseline, ce_rl_baseline


if __name__ == "__main__":
    logging.info("cost_effectiveness_evaluator.py")

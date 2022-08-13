import pygrank as pg
import pytest


def test_optimizer_errors():
    from pygrank.algorithms import optimize
    with pytest.raises(Exception):
        optimize(loss=lambda p: (p[0] - 2) ** 2 + (p[1] - 1) ** 4, max_vals=[5, 5], parameter_tol=1.E-8, divide_range=1)
    with pytest.raises(Exception):
        optimize(loss=lambda p: (p[0] - 2) ** 2 + (p[1] - 1) ** 4, max_vals=[5, 5], min_vals=[5, 6])
    with pytest.raises(Exception):
        optimize(loss=lambda p: (p[0] - 2) ** 2 + (p[1] - 1) ** 4, max_vals=[5, 5], shrink_strategy="unknown")
    with pytest.raises(Exception):
        optimize(loss=lambda p: (p[0] - 2) ** 2 + (p[1] - 1) ** 4, max_vals=[5, 5], partition_strategy="unknown")


def test_optimizer_verbose():
    import sys, io
    prev_stdout = sys.stdout
    sys.stdout = io.StringIO("")
    pg.optimize(loss=lambda p: (p[0]-2)**2+(p[1]-1)**4, max_vals=[5, 5], parameter_tol=1.E-8, verbose=True)
    output = sys.stdout.getvalue()
    sys.stdout = prev_stdout
    assert len(output) > 0


def test_optimizer():
    # https://en.wikipedia.org/wiki/Test_functions_for_optimization

    for optimizer in [pg.optimize, pg.nelder_mead]:
        # a simple function
        p = pg.optimize(loss=lambda p: (p[0]-2)**2+(p[1]-1)**4, max_vals=[5, 5], parameter_tol=1.E-8, verbose=False)
        assert abs(p[0]-2) < 1.E-6
        assert abs(p[1]-1) < 1.E-6

        # a simple function
        p = pg.optimize(loss=lambda p: (p[0]-2)**2+(p[1]-1)**4, max_vals=[5, 5], parameter_tol=1.E-8, verbose=False,
                        partition_strategy="step", partitions=0.01)
        assert abs(p[0]-2) < 1.E-6
        assert abs(p[1]-1) < 1.E-6

        # a simple function
        p = pg.optimize(loss=lambda p: (p[0]-2)**2+(p[1]-1)**4, max_vals=[5, 5], parameter_tol=1.E-8, verbose=False,
                        partition_strategy="step", partitions=0.01, randomize=True)
        assert abs(p[0]-2) < 1.E-6
        assert abs(p[1]-1) < 1.E-6

        # a simple function with redundant inputs and tol instead of parameter tolerance
        p = pg.optimize(loss=lambda p: (p[0]-2)**2+(p[1]-1)**4,
                        max_vals=[5, 5, 5], min_vals=[0, 0, 5], deviation_tol=1.E-6, shrink_strategy="shrinking", verbose=False)
        assert abs(p[0]-2) < 1.E-1
        assert abs(p[1]-1) < 1.E-1
        # TODO: check why shrinking is not as good

        # Beale function
        beale = lambda p: (1.5-p[0]+p[0]*p[1])**2+(2.25-p[0]+p[0]*p[1]**2)**2+(2.625-p[0]+p[0]*p[1]**3)**2
        p = pg.optimize(loss=beale,
                        max_vals=[4.5, 4.5], min_vals=[-4.5, -4.5], parameter_tol=1.E-8, verbose=False)
        assert abs(p[0]-3) < 1.E-6
        assert abs(p[1]-0.5) < 1.E-6

        # noisy Beale function
        from random import random, seed
        seed(0)
        noisy_beale = lambda p: (1.5 - p[0] + p[0] * p[1]) ** 2 + (2.25 - p[0] + p[0] * p[1] ** 2) ** 2 + (
                    2.625 - p[0] + p[0] * p[1] ** 3) ** 2 + random()
        p = pg.optimize(loss=noisy_beale,
                        validation_loss=beale,
                        max_vals=[4.5, 4.5], min_vals=[-4.5, -4.5], parameter_tol=1.E-8, verbose=False)
        assert abs(p[0] - 3) < .1
        assert abs(p[1] - 0.5) < .1

        # Beale function with nelder mead
        p = pg.nelder_mead(loss=beale,
                        max_vals=[4.5, 4.5], min_vals=[-4.5, -4.5], parameter_tol=1.E-8, verbose=False)
        assert abs(p[0] - 3) < 1.E-6
        assert abs(p[1] - 0.5) < 1.E-6

        # Beale function with lbfgsb
        p = pg.lbfgsb(loss=beale,
                        max_vals=[4.5, 4.5], min_vals=[-4.5, -4.5], parameter_tol=1.E-8, verbose=False)
        assert abs(p[0] - 3) < 1.E-6
        assert abs(p[1] - 0.5) < 1.E-6

        # Beale function
        p = pg.optimize(loss=beale,
                        max_vals=[4.5, 4.5], min_vals=[-4.5, -4.5], parameter_tol=1.E-8, verbose=False)

        # Booth function
        p = pg.optimize(loss=lambda p: (p[0]+2*p[1]-7)**2+(2*p[0]+p[1]-5)**2,
                        max_vals=[10, 10], min_vals=[-10, -10], parameter_tol=1.E-6, verbose=False)
        assert abs(p[0] - 1) < 1.E-6
        assert abs(p[1] - 3) < 1.E-6

        # Beale function with depth instead of small divide range
        p = pg.optimize(loss=lambda p: (1.5-p[0]+p[0]*p[1])**2+(2.25-p[0]+p[0]*p[1]**2)**2+(2.625-p[0]+p[0]*p[1]**3)**2,
                        max_vals=[4.5, 4.5], min_vals=[-4.5, -4.5], parameter_tol=1.E-8, divide_range=2, depth=100, verbose=False)
        assert abs(p[0] - 3) < 1.E-6
        assert abs(p[1] - 0.5) < 1.E-6


def test_autotune():
    _, G, groups = next(pg.load_datasets_multiple_communities(["bigraph"]))
    group = groups[0]
    training, evaluation = pg.split(pg.to_signal(G, {v: 1 for v in group}), training_samples=0.5)
    auc1 = pg.AUC(evaluation, exclude=training)(pg.PageRank().rank(training))
    auc2 = pg.AUC(evaluation, exclude=training)(pg.HeatKernel().rank(training))
    auc3 = pg.AUC(evaluation, exclude=training)(pg.ParameterTuner(optimization_dict=dict()).rank(training))
    assert min(auc1, auc2) <= auc3 and max(auc1, auc2)*0.9 <= auc3


def test_autotune_manual():
    _, G, groups = next(pg.load_datasets_multiple_communities(["bigraph"]))
    group = groups[0]
    training, evaluation = pg.split(pg.to_signal(G, {v: 1 for v in group}), training_samples=0.5)
    auc1 = pg.AUC(evaluation, exclude=training)(pg.PageRank().rank(training))
    alg2 = pg.ParameterTuner(lambda params: pg.PageRank(params[0]), max_vals=[0.99], min_vals=[0.5]).tune(training)
    auc2 = pg.AUC(evaluation, exclude=training)(alg2.rank(training))
    assert auc1 <= auc2


def test_autotune_methods():
    import numpy as np
    _, G, groups = next(pg.load_datasets_multiple_communities(["bigraph"]))
    group = groups[0]
    training, evaluation = pg.split(pg.to_signal(G, {v: 1 for v in group}))
    aucs = [pg.AUC(evaluation, exclude=training)(ranker.rank(training)) for ranker in pg.create_demo_filters().values()]
    auc2 = pg.AUC(evaluation, exclude=training)(pg.AlgorithmSelection().rank(training))
    assert max(aucs)-np.std(aucs) <= auc2


def test_hoptuner_arnoldi():
    _, G, groups = next(pg.load_datasets_multiple_communities(["bigraph"]))
    group = groups[0]
    training, evaluation = pg.split(pg.to_signal(G, {v: 1 for v in group}), training_samples=0.5)
    auc1 = pg.AUC(evaluation, exclude=training)(pg.HopTuner(measure=pg.AUC).rank(training))
    auc2 = pg.AUC(evaluation, exclude=training)(pg.HopTuner(basis="arnoldi", measure=pg.AUC, krylov_dims=20).rank(training))
    #assert abs(auc1-auc2) < 0.005 # TODO investigate why arnoldi tuning does not work that well for hop tuner


def test_hoptuner_explicit_algorithm():
    _, G, groups = next(pg.load_datasets_multiple_communities(["bigraph"]))
    group = groups[0]
    training, evaluation = pg.split(pg.to_signal(G, {v: 1 for v in group}), training_samples=0.5)
    auc1 = pg.AUC(evaluation, exclude=training)(pg.HopTuner(lambda params: pg.GenericGraphFilter(params, krylov_dims=10), basis="arnoldi", measure=pg.AUC).rank(training))
    auc2 = pg.AUC(evaluation, exclude=training)(pg.HopTuner(basis="arnoldi", krylov_dims=10, measure=pg.AUC).rank(training))
    assert abs(auc1-auc2) < 0.005


def test_hoptuner_autorgression():
    _, G, groups = next(pg.load_datasets_multiple_communities(["bigraph"]))
    group = groups[0]
    training, evaluation = pg.split(pg.to_signal(G, {v: 1 for v in group}), training_samples=0.01)
    auc1 = pg.AUC(evaluation, exclude=training)(pg.HopTuner(measure=pg.AUC).rank(training))
    auc3 = pg.AUC(evaluation, exclude=training)(pg.HopTuner(measure=pg.AUC, autoregression=5).rank(training))
    assert auc3 > auc1*0.9
    # TODO: add a stricter test once a publication of HopTuner finds best method


def test_impulse_tuning():
    _, G, groups = next(pg.load_datasets_multiple_communities(["bigraph"]))
    group = groups[0]
    training, evaluation = pg.split(pg.to_signal(G, {v: 1 for v in group}), training_samples=0.1)
    auc1 = pg.AUC(evaluation, exclude=training)(pg.ParameterTuner(lambda params: pg.GenericGraphFilter(params)).rank(training))
    auc2 = pg.AUC(evaluation, exclude=training)(pg.ParameterTuner(lambda params: pg.ImpulseGraphFilter(params)).rank(training))
    assert auc2 > auc1*0.9


def test_hoptuner_arnoldi_backends():
    _, G, groups = next(pg.load_datasets_multiple_communities(["bigraph"]))
    group = groups[0]
    training, evaluation = pg.split(pg.to_signal(G, {v: 1 for v in group}), training_samples=0.5)
    auc1 = pg.AUC(evaluation, exclude=training)(pg.HopTuner(basis="arnoldi", measure=pg.AUC).rank(training))
    auc2 = pg.AUC(evaluation, exclude=training)(pg.HopTuner(basis="arnoldi", measure=pg.AUC, tuning_backend="pytorch").rank(training))
    auc3 = pg.AUC(evaluation, exclude=training)(pg.HopTuner(basis="arnoldi", measure=pg.AUC, tuning_backend="tensorflow").rank(training))
    assert auc1 == auc2
    assert auc1 == auc3


def test_autotune_backends():
    _, G, groups = next(pg.load_datasets_multiple_communities(["bigraph"]))
    group = groups[0]
    training, evaluation = pg.split(pg.to_signal(G, {v: 1 for v in group}), training_samples=0.5)
    for tuner in [pg.HopTuner, pg.AlgorithmSelection, pg.ParameterTuner]:
        auc3 = pg.AUC(evaluation, exclude=training)(tuner(measure=pg.KLDivergence, tuning_backend="pytorch").rank(training))
        auc2 = pg.AUC(evaluation, exclude=training)(tuner(measure=pg.KLDivergence, tuning_backend="tensorflow").rank(training))
        auc1 = pg.AUC(evaluation, exclude=training)(tuner(measure=pg.KLDivergence).rank(training))
        # TODO: maybe fix KLDivergence implementation to not be affected by backend.epsilon()
        assert abs(auc1-auc2) < 0.005  # different results due to different backend.epsilon()
        assert abs(auc1-auc3) < 0.005

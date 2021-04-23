# Standard library imports
import itertools
from typing import Dict

# Third party imports
import pandas as pd
from statsmodels.genmod.families.family import Binomial
from statsmodels.genmod.generalized_linear_model import GLM

# Geo:N:G imports
from geong_common import config


def filter_data(data, filters: Dict[str, str]):
    """Filter data in a DataFrame based on the given filters"""
    for column, value in filters.items():
        data = data.loc[data.loc[:, column] == value]
    return data


def _train(elements, model_cfg):
    """Construct one model per building block type"""
    models = {}
    target = model_cfg.target
    for model in model_cfg.sections:
        # Construct model formula from configuration
        terms = " + ".join(["1"] + [f"C({f})" for f in model.factors])

        # Train model
        models[model.label] = GLM.from_formula(
            f"{target} ~ {terms}",
            family=Binomial(),
            data=filter_data(elements, {model_cfg.label_column: model.label}),
        ).fit(scale="X2")
    return models


def _get_combinations(model_cfg):
    """Construct all combinations of factors for all models"""
    factors = sorted(set.union(*[set(s.factors) for s in model_cfg.sections]))

    # Find all combinations of model factors
    combinations = []
    for model in model_cfg.sections:
        combinations.extend(
            itertools.product(
                [model.label],
                *[model.get(f, {}).get("values", [""]) for f in factors],
            )
        )

    return pd.DataFrame(combinations, columns=[model_cfg.label_column] + factors)


def calculate(elements, dataset):
    """Calculate the Geo:N:G models, read config based on dataset"""
    return calculate_from_config(elements, config.geong.models[dataset])


def calculate_from_config(elements, model_cfg):
    """Calculate the Geo:N:G models"""
    models = _train(elements, model_cfg)
    combinations = _get_combinations(model_cfg)

    # Predict for all models and combinations
    return combinations.assign(
        net_gross=combinations.apply(
            lambda row: models[row.loc[model_cfg.label_column]].predict(row).item(),
            axis="columns",
        )
    )

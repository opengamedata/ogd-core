
## import standard libraries
import logging
import math
import re
import typing
## import local libraries
from models.FeatureModel import FeatureModel

## @class LogisticModel
class LinearModel(FeatureModel):
    def __init__(self, coefficient_map: typing.Dict[str, float], levels: typing.List[int] = []):
        super().__init__(levels)
        self._coeff_map = coefficient_map

    ## Function to evaluate a logistic regression model, creating a prediction.
    #  This is based around the equation for probability of Y=1, denoted as p:
    #  p = 1 / (1 + e^-logit(X)),
    #  where X is the input data used to predict Y, and
    #  logit(X) = b0 + b1*x1 + b2*x2 + ... + bn*xn,
    #  where bi are the coefficients.
    #  Based on information at https://www.medcalc.org/manual/logistic_regression.php
    def _eval(self, row: typing.Dict):
        ret_val = 0
        for coeff_name in self._coeff_map.keys():
            # case where coefficient is a normal feature
            if coeff_name in row.keys():
                try:
                    ret_val += self._coeff_map[coeff_name] * row[coeff_name]
                except Exception as err:
                    print(f"Got {type(err)} error when trying to add {coeff_name} term. Value is {row[coeff_name]}. Type is {type(row[coeff_name])}")
                    raise err
            # enum case, where we have coefficient = feature_name.enum_val
            # e.g. maybe we've got a feature that returns a classification as either Foo or Bar, and we want Foo's to count as 0.5 towards the model.
            # then we'll have coefficient 0.5 = classification.Foo.
            # in the code here, we get logit += 0.5 * 1.0 for Foo, and 0.5 * 0.0 for Bar.
            # I'm mildly confused as to why I put this case in here, must have found some case where it could occur?
            elif re.search("\w+\.\w+", coeff_name):
                pieces = coeff_name.split(".")
                if pieces[0] in row.keys():
                    ret_val += self._coeff_map[coeff_name] * (1.0 if row[pieces[0]] == pieces[1] else 0.0)
                else:
                    print(f"Found an element of model that is not a feature: {coeff_name}")
            # specific cases, where we just hardcode a thing that must be consistent across all models.
            elif coeff_name == "Intercept":
                ret_val += self._coeff_map[coeff_name]
            elif coeff_name == "display_name":
                pass
            # default case, print a line.
            else:
                print(f"Found an element of model that is not a feature: {coeff_name}")
        return ret_val
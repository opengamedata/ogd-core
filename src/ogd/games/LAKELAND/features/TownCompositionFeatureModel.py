from models.FeatureModel import FeatureModel
import typing

# This is a model that returns a dictionary with the number of homes, farms, and dairy
# farms a user bought in level 0 of their session

class TownCompositionFeatureModel(FeatureModel):
  def _eval(self, row: typing.Dict) -> dict:
      homes = row["lvl0_count_buy_home"]
      farms = row["lvl0_count_buy_farm"]
      dairy = row["lvl0_count_buy_livestock"]

      amounts = {'homes': homes, 'farms': farms, 'dairy': dairy}

      return amounts
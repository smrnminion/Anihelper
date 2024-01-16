import pytest
from actions.predict import Predict, Algoritms


@pytest.fixture(scope="class")
def predict() -> Predict:
    return Predict()


class TestPredict:
    def test_find_name_ok(self, predict: Predict):
        assert "Death Note" == predict.find_name("Death Note")

    def test_find_names_ok(self, predict: Predict):
        print(predict.find_names("Naruto", count=4))

        assert {
            "Naruto x UT",
            "Haruwo",
            "Naruto",
            "Nayuta",

        } == set(predict.find_names("Naruto", count=4))

    def test_recomend_cos_ok(self, predict: Predict):
        predict.algoritm = Algoritms.COS_SIM
        predict.recommend("Fullmetal Alchemist: Brotherhood", count=5)
        predict.recommend("Angel Beats!", count=5)

    def test_recomend_knn_ok(self, predict: Predict):
        predict.algoritm = Algoritms.KNN
        predict.recommend("Fullmetal Alchemist: Brotherhood", count=5)
        predict.recommend("Angel Beats!", count=5)

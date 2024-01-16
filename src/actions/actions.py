from typing import Any, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.predict import Predict
from loguru import logger

predict = Predict()


class ActionClosestTo(Action):
    def name(self) -> Text:
        return "action_get_closest_to"

    def run(self, dispatcher, tracker, domain):
        target_name = str(tracker.get_slot("target_name"))
        # count = tracker.get_slot("count")
        count = 5

        try:
            count = int(count)
        except ValueError:
            dispatcher.utter_message("Неправильный формат:(")

        found_name = "Naruto"
        try:
            found_name = predict.find_name(target_name)
            logger.debug(found_name)

        except Exception:
            dispatcher.utter_message("Такое аниме я не знаю:(")
            return []

        predictions = list(predict.recommend(found_name, count=count))[1:]

        message = f"Я знаю аниме {found_name}, вам понравятся такие аниме как:\n\n"
        for prediction in predictions:
            message += f"{prediction.v}\n"
        dispatcher.utter_message(message)

        return []

class ActionBestFromGenre(Action):
    def name(self) -> Text:
        return "action_get_best_from_genre"

    def run(self, dispatcher, tracker, domain):
        target_name = str(tracker.get_slot("target_name"))
        field_name = "genre"
        # count = tracker.get_slot("count")
        count = 5

        predictions = "\n".join(predict.best_from(count=count, field=field_name, name=target_name))
        dispatcher.utter_message(f"Самые лучшее аниме по жанру {target_name}: \n\n{predictions}")

        return []
    
class ActionRecommendBestAnime(Action):
    def name(self) -> Text:
        return "action_recommend_best_anime"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Any):
        
        watched_anime_list = tracker.get_slot("target_name")

        if not watched_anime_list:
            dispatcher.utter_message("Пожалуйста, укажите список аниме, которые вы уже посмотрели.")
            return []

        if isinstance(watched_anime_list, str):
            watched_anime_list = watched_anime_list.split(", ")

        recommendation_count = 5

        try:
            recommendations = predict.recommend_best_anime(watched_anime_list, recommendation_count)
            message = "Основываясь на вашем списке, рекомендую вам следующие аниме:\n\n"
            message += "\n".join(recommendations)
        except Exception as e:
            logger.error(f"Error while recommending anime: {e}")
            message = "Произошла ошибка при попытке найти рекомендации."

        dispatcher.utter_message(message)
        return []
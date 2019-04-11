from anthill.platform.remote_models import remote_model_factory


__all__ = ['Bot', 'BotAction', 'BotResultFormatter']

Bot = remote_model_factory('bot.Bot')
BotAction = remote_model_factory('bot.Action')
BotResultFormatter = remote_model_factory('bot.ResultFormatter')

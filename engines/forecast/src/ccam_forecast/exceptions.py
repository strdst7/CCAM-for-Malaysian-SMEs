class ForecastError(Exception):
    pass


class ModelNotTrainedError(ForecastError):
    pass


class TrainingError(ForecastError):
    pass


class DataError(ForecastError):
    pass


class EnsembleError(ForecastError):
    pass

from borneo.analysis import Analysis


class {{ study_name }}Analysis(Analysis):

    def __init__(self, model, **kwargs):
        """{{ study_name }}Analysis constructor"""
        super(Analysis, self).__init__(model, **kwargs)

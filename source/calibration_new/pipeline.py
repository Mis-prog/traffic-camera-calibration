class CalibrationPipeline:
    def __init__(self, init_stage, refine_stage=None):
        self.init_stage = init_stage
        self.refine_stage = refine_stage

    def run(self, camera, **kwargs):
        camera = self.init_stage.run(camera, **kwargs)
        if self.refine_stage:
            camera = self.refine_stage.run(camera, **kwargs)
        return camera

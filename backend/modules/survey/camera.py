class Camera:
    def __init__(
        self,
        spacingAt100Alt: float,
        focalLength: float,
        imgWidth: float,
        imgHeight: float,
        sensorWidth: float,
        sensorHeight: float,
    ):
        self.spacing = spacingAt100Alt
        self.focalLength = focalLength
        self.imgWidth = imgWidth
        self.imgHeight = imgHeight
        self.sensorWidth = sensorWidth
        self.sensorHeight = sensorHeight

    def adjutSpacingToAlt(self, alt: float):
        self.spacing *= alt / 100


camera_modules = {
    "sonya6000": Camera(
        spacingAt100Alt=47,
        focalLength=20,
        imgWidth=6000,
        imgHeight=4000,
        sensorWidth=23.5,
        sensorHeight=15.6,
    ),
    "goProHero4Black": Camera(
        spacingAt100Alt=100.33,
        focalLength=2.94,
        imgWidth=40000,
        imgHeight=3000,
        sensorWidth=6.17,
        sensorHeight=4.56,
    ),
    "goproHero13":Camera(
        spacingAt100Alt=54.91,
        focalLength=34,
        imgWidth=5568,
        imgHeight=4872,
        sensorWidth=71.8,
        sensorHeight=50.8,
        
    )

}

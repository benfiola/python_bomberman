import time


class Animation(object):
    @staticmethod
    def slide(sprite):
        ad = sprite.animation_data
        curr_time = time.time() * 1000
        curr_duration = curr_time - ad.start_time
        time_since_last_update = curr_time - ad.last_update
        if curr_duration >= ad.duration:
            sprite.rect.topleft = ad.target
            sprite.animation_data = None
        else:
            ad.curr = (ad.curr[0]+(ad.speed[0]*time_since_last_update), ad.curr[1]+(ad.speed[1]*time_since_last_update))
            sprite.rect.topleft = (round(ad.curr[0]), round(ad.curr[1]))
            ad.last_update = curr_time


class AnimationData(object):
    def __init__(self, function, duration):
        self.function = function
        self.duration = duration
        self.start_time = time.time()*1000
        self.last_update = self.start_time


class SlideAnimationData(AnimationData):
    def __init__(self, duration, source, target):
        super(SlideAnimationData, self).__init__(Animation.slide, duration)
        self.curr = source
        self.source = source
        self.target = target
        self.speed = ((target[0]-source[0])/duration, (target[1]-source[1])/duration)




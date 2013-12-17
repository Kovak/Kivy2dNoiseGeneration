from __future__ import division
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (ObjectProperty, ListProperty, 
    NumericProperty)
from kivy.clock import Clock
from noise import snoise2
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.core.image import ImageData
from kivy.vector import Vector
import cProfile
from math import floor

def lerp(a, p, q): 
    return tuple((_p + ((_q - _p) * a)) for _p, _q in zip(p, q))


class NoiseGenerator(object):

    def step_between_colors(self, color1, color2, number_of_steps):
        colors = []
        distance_between_steps = 1/(number_of_steps-1)
        for x in range(number_of_steps):
            new_color = lerp(distance_between_steps*x, color1, color2)
            colors.append(new_color)
        color_print = [[color/255 for color in z] for z in colors]
        return colors

    def generate_noise_circle(self, octaves, freq, color_value_list, 
        threshold, offset, radius, size, do_alpha):
        data = ''
        freq = freq * octaves
        for x in range(size[0]):
            for y in range(size[1]):
                noise_val = snoise2((x+offset[0]) / freq, (y+offset[1]) / freq, octaves)
                if noise_val < 0:
                    noise_val = 0
                alpha = self.test_threshold(noise_val, threshold, do_alpha)
                color = None
                if not self.test_in_circle(x, y, size, radius):
                    color = [0, 0, 0]
                    alpha = 0
                else:
                    for color_range_tuple in color_value_list:
                        color_range = color_range_tuple[1]
                        if color_range[0] <= noise_val <= color_range[1]:
                            color = [z*255 for z in color_range_tuple[0]]
                            break
                color.append(alpha)
                for each in color:
                    data = data + chr(int(each))
        return self.generate_texture(data, size, 'rgba')


    def test_threshold(self, noise_val, threshold, do_alpha):
        if noise_val < threshold:
            return 0
        elif do_alpha:
            return noise_val*255
        else:
            return 255

    def test_in_circle(self, x, y, size, radius):
        if Vector(x, y).distance((size[0]/2., size[1]/2.)) > radius:
            return False
        else:
            return True

    def generate_texture(self, data, size, mode, mipmap=False):
        idata = ImageData(size[0], size[1], mode, data)
        return Texture.create_from_data(idata, mipmap)


class RootWidget(Widget):
    gen_texture = ObjectProperty(None)
    noise_size = ListProperty((128, 128))
    noise_radius = NumericProperty(64)
    noise_objects = ListProperty([])
    noise_added = NumericProperty(0)

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.n_gen = NoiseGenerator()
        Clock.schedule_once(self.setup)

    def setup(self, dt):
        color_value_list = [((1., 0.521568627, .231372549), (0., .25)),
        ((0., 1., .2), (.25, 1.))]
        self.add_noise(4, 16., color_value_list, self.noise_radius, 
            self.noise_size)

    def add_noise(self, octaves, freq, color_value_list, radius, size, 
        do_alpha=False, threshold=0., offset = (0, 0)):
        self.noise_objects.append({
            'oct': octaves, 'freq': freq, 
            'color_value_list': color_value_list,
            'threshold': threshold,
            'offset': offset,
            'texture': self.n_gen.generate_noise_circle(octaves, freq, 
                color_value_list, threshold, offset, radius, size, do_alpha)})
        self.noise_added += 1

    def on_size(self, instance, value):
        self.draw_all_noise()

    def on_pos(self, instance, value):
        self.draw_all_noise()

    def on_noise_objects(self, instance, value):
        self.draw_all_noise()

    def draw_all_noise(self):
        self.canvas.clear()
        noise_objects = self.noise_objects
        with self.canvas:
            for noise in noise_objects:
                Rectangle(pos=(self.size[0]/2. - self.noise_size[0]/2., 
                    self.size[1]/2. - self.noise_size[1]/2.),
                    size= self.noise_size, texture=noise['texture'])

class TestApp(App):

    def build(self):
        pass

if __name__ == '__main__':
    #TestApp().run()
    cProfile.run('TestApp().run()', 'prof')

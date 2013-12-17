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

class RootWidget(Widget):
    gen_texture = ObjectProperty(None)
    noise_size = ListProperty((128, 128))
    noise_radius = NumericProperty(64)
    noise_objects = ListProperty([])
    noise_added = NumericProperty(0)

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        Clock.schedule_once(self.setup)

    def setup(self, dt):
        
        self.add_noise(8, 5., 12, (1., 0.521568627, .231372549), (0., 1., .2), 
            allow_negatives=False)
        #self.add_noise(6, 5., 4, (1., 0.521568627, .231372549), (0., 1., .2), 
        #    allow_negatives=False, threshold=.6)
        #self.add_noise(2, .5, 16, (0., 0., .5), (0., 0., 1.), threshold=.5, 
        #    offset=(50, 50), func = Ridged(2))
        #self.add_noise(8, 16., 2, (.7, .7, .7), (1., 1., 1.), threshold=.6)
        #self.add_noise(4, 16., 2, (0., .2, .9), (0., .5, .2))

    def add_noise(self, octaves, freq, number_of_steps, color1, color2, 
        threshold=0., offset = (0, 0), allow_negatives=True, func=None):
        self.noise_objects.append({
            'oct': octaves, 'freq': freq, 'number_of_steps': number_of_steps, 
            'color1': color1, 'color2': color2, 'threshold': threshold,
            'offset': offset,
            'texture': self.generate_texture(octaves, freq, number_of_steps, 
                color1, color2, threshold, offset, allow_negatives, func=func)})
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

    def convert_noise_to_texture_with_color(self, octaves, 
        freq, number_of_steps, color1, color2, threshold, offset):
        noise_size = self.noise_size
        data = ''
        radius = self.noise_radius
        freq = freq * octaves
        colors_to_use = self.step_between_colors(
            color1, color2, number_of_steps)
        gradient_step = 1/number_of_steps
        for x in range(noise_size[0]):
            for y in range(noise_size[1]):
                noise_val = snoise2((x+offset[0]) / freq, (y+offset[1]) / freq, octaves)
                alpha = 255
                if Vector(x, y).distance(
                    (noise_size[0]/2., noise_size[1]/2.)) > radius:
                    alpha = 0
                if noise_val < threshold:
                    alpha = 0
                color_index = floor((noise_val)/gradient_step)
                if color_index == number_of_steps:
                    color_index = number_of_steps - 1
                noise_tuple = [z for z in colors_to_use[int(color_index)]]
                for each in noise_tuple:
                    data = data + chr(int(each))
                data = data + chr(alpha)
        idata = ImageData(self.noise_size[0], self.noise_size[1],
            'rgba', data)
        return Texture.create_from_data(idata, mipmap=False)
                
    def step_between_colors(self, color1, color2, number_of_steps):
        colors = []
        distance_between_steps = 1/(number_of_steps-1)
        for x in range(number_of_steps):
            new_color = lerp(distance_between_steps*x, color1, color2)
            colors.append(new_color)
        color_print = [[color/255 for color in z] for z in colors]
        return colors

    def generate_texture(self, octaves, freq, number_of_steps, color1, color2,
        threshold, offset, allow_negatives, func = None):
        color1 = [int(x*255) for x in color1]
        color2 = [int(x*255) for x in color2]
        return self.convert_noise_to_texture_with_color(octaves, freq,
            number_of_steps, color1, color2, threshold, offset)

class TestApp(App):

    def build(self):
        pass

if __name__ == '__main__':
    #TestApp().run()
    cProfile.run('TestApp().run()', 'prof')

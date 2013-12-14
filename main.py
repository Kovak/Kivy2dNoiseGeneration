from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (ObjectProperty, ListProperty, 
    NumericProperty)
from pygame import image as pyg_image
from noise import snoise2
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color
from kivy.core.image import ImageData
from kivy.vector import Vector

class RootWidget(Widget):
    gen_texture = ObjectProperty(None)
    noise_size = ListProperty((256, 256))
    noise_radius = NumericProperty(128)
    planet_base_color = ListProperty((0., 0., 1.,))
    noise_objects = ListProperty([])
    noise_added = NumericProperty(0)

    
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        Clock.schedule_once(self.setup)

    def setup(self, dt):
        #self.add_noise(8, 16., (0., .2, .8), (0., .3, .7))
        #self.add_noise(1, 16., (.5, .5, 0.), (.3, 1., .6))
        self.add_noise(16, 16., (.3, .7, 0.), (0., 0., 0.))
        self.add_noise(8, 16., (.3, .5, 0.), (.3, .3, 0.))
        self.add_noise(12, 4., (.9, .9, .9), (1., 1., 1.))


    def add_noise(self, octaves, freq, color1, color2):
        self.noise_objects.append({
            'oct': octaves, 'freq': freq, 'color1': color1, 'color2': color2,
            'texture': self.generate_texture(octaves, freq, color1, color2)})
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
                

    def generate_texture(self, octaves, freq, color1, color2):
        octaves = octaves
        freq = freq * octaves
        data = ''
        radius = self.noise_radius
        color1 = [int(x*255) for x in color1]
        color2 = [int(x*255) for x in color2]
        noise_size = self.noise_size
        for x in range(noise_size[0]):
            for y in range(noise_size[1]):
                noise_val = int(snoise2(x / freq, y / freq, octaves)*255)
                if noise_val < 0:
                    noise_val = 0
                if Vector(x, y).distance((noise_size[0]/2., noise_size[1]/2.)) > radius:
                    noise_val = 0
                alpha = 0
                if noise_val > 0:
                    alpha = 255
                if noise_val <= 128:
                    color = color1
                else:
                    color = color2
                noise_tuple = (color[0], color[1], color[2], alpha)
                for each in noise_tuple:
                    data = data + chr(each)
        idata = ImageData(self.noise_size[0], self.noise_size[1],
            'rgba', data)
        return Texture.create_from_data(idata, mipmap=False)

class TestApp(App):

    def build(self):
        pass

if __name__ == '__main__':
    TestApp().run()

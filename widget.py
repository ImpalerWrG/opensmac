import pygame, render
import txt 
import math

def add((x1, y1), (x2, y2)):
  return x1 + x2, y1 + y2
def sub((x1, y1), (x2, y2)):
  return x1 - x2, y1 - y2

#widget size is internal for drawing, should be set by parent

class Widget(object):
  expand = 0, 0
  shrink = 0, 0
  #size = 0, 0

  def __init__(self, **kwargs):
    self.init()
    for key, val in kwargs.iteritems():
      setattr(self, key, val)
    if 'child' in dir(self):
      self.child.parent = self
    if 'children' in dir(self):
      for child in self.children:
        child.parent = self
    if 'renderer' in dir(self):
      self.set_all(renderer = self.renderer)

  def init(self):
    self.setsize = None
    self.size = 0, 0
    self.shrink = 0, 0
    self.pos = 0, 0
    return
    self.expand = 0, 0
  def set_all(self, **kwargs):
    for key, val in kwargs.iteritems():
      setattr(self, key, val)
    if 'child' in dir(self):
      self.child.set_all(**kwargs)
    if 'children' in dir(self):
      for child in self.children:
        child.set_all(**kwargs)

  def on_mousebutton(self, event):
    pass
  def on_mousemove(self, event):
    pass
  def on_mouseout(self, event):
    pass
  def inside(self, (mx, my)):
    w, h = self.size
    x, y = self.pos
    return mx > x and mx < x + w - 1 and my > y and my < y + h - 1

  def events(self, events):
    for event in events:
      if event.type == pygame.MOUSEMOTION:
        #mx, my = event.pos
        if self.inside(event.pos):
          self.on_mousemove(event) 
        else:
          self.on_mouseout(event)
      if event.type == pygame.MOUSEBUTTONDOWN:
        if self.inside(event.pos):
          self.on_mousebutton(event)


  def get_size(self):
    if self.setsize:
      return self.setsize, self.expand, self.shrink
    else:
      return (0, 0), self.expand, self.shrink

  def set_size(self, pos, size):
    self.pos = pos
    self.size = size
 
  def do(self, events): pass
  def draw(self): pass

class Label(Widget):
  def init(self):
    self.high = False
    self.pos = 0, 0
    self.size = 0, 0
    self.bold = False
  def on_mousebutton(self, event):
    pass#self.high = not self.high
  def on_mousemove(self, event):
    self.high = True
  def on_mouseout(self, event):
    self.high = False

  def do(self, events):
    self.events(events)

  def get_size(self):
    return self.renderer.font_size(self.text, self.bold), (0, 0), (0, 0)

  def draw(self):
    if self.high:
      self.renderer.font_render(self.text, (0, 0, 0), self.pos, self.size, self.color, bold = self.bold)
    else:
      self.renderer.font_render(self.text, self.color, self.pos, self.size, bold = self.bold)

class Image(Widget):
  def init(self):
    self.expand = 0, 0
  def get_size(self):
    return self.image.get_size(), (0, 0), (0, 0)
  def draw(self):
    self.renderer.surface.blit(self.image, self.pos)

class Glue(Widget):
  def init(self):
    self.setsize = 0, 0
    self.expand = 1, 1

class Bar(Glue):
  def draw(self):
    print self.pos, self.size
    (x, y), (w, h) = self.pos, self.size
    self.renderer.frect(x, y, x + w - 1, y + h - 1, self.color)


class Parent(Widget):
  def do(self, events):
    return self.child.do(events)
  def draw(self):
    self.child.draw() 

class Expand(Parent):
  def init(self):
    self.set_expand = 0, 0
  def get_size(self):
    sex, sey = self.set_expand
    size, (cex, cey), shrink = self.child.get_size()
    return size, (sex, sey), shrink
  def set_size(self, pos, size):
    self.child.set_size(pos, size)

class Frame(Parent):
  def get_size(self):
    childsize, childexpand, childshrink = self.child.get_size()
    return add(childsize, (self.fwidth*2, self.fwidth*2)), childexpand, childshrink

  def set_size(self, pos, size):
    self.pos = pos
    self.size = size
    self.child.set_size(add(pos, (self.fwidth, self.fwidth)), sub(size, (self.fwidth*2, self.fwidth*2)))
 
  def drawframe(self): pass 
  def draw(self):
    self.drawframe()
    self.child.draw() 

class OPFrame(Frame):
  def drawframe(self):
    w, h = self.size
    x, y = self.pos
    self.renderer.rect(x, y, x + w - 1, y + h - 1, self.color)

class OPRFrame(Frame):
  def drawframe(self):
    w, h = self.size
    x, y = self.pos
    l, t, r, b = x, y, x + w - 1, y + h - 1
    self.renderer.naline(l + 1, t, r - 1, t, self.color)
    self.renderer.naline(l + 1, b, r - 1, b, self.color)
    self.renderer.naline(l, t + 1, l, b - 1, self.color)
    self.renderer.naline(r, t + 1, r, b - 1, self.color)

class MultiParent(Widget):
  children = []
  def do(self, events):
    for child in self.children:
      child.do(events)
    return []

  def draw(self):
    #print self, self.pos, self.size
    clip = self.renderer.get_clip()
    w, h = self.size
    x, y = self.pos
    self.renderer.set_clip(pygame.Rect(self.pos, self.size))
    for child in self.children:
      child.draw()
    self.renderer.set_clip(clip)
    #self.renderer.rect(x, y, x+w-1, y+h-1, red)

class VBox(MultiParent):
  def get_size(self):
    self.childgeo = [child.get_size() for child in self.children]
    childsizes = [size for size, expand, shrink in self.childgeo]
    childexps = [expand for size, expand, shrink in self.childgeo]
    childshrinks = [shrink for size, expand, shrink in self.childgeo]
    self.size = max([w for w, h in childsizes]+[0]), sum([h for w, h in childsizes])
    self.childexp = max([w for w, h in childexps]+[0]), sum([h for w, h in childexps])
    self.childshrink = max([w for w, h in childshrinks]+[0]), sum([h for w, h in childshrinks])
    return self.size, self.childexp, self.childshrink
    #return (0, 0), (1, 1)

  def set_size(self, pos, size):
    self.pos = pos
    x, y = pos
    w, h = size
    ew, eh = sub(size, self.size) #extra width and height
    self.size = size
    cex, cey = self.childexp
    csx, csy = self.childshrink
    euy, suy = 0, 0
    if cey: euy = float(eh)/cey # vert expand unit
    if csy: suy = float(eh)/csy # vert shrink unit
    '''
    print 'obj', self
    #print 'ch', self.children
    #print 'chgeo', self.childgeo
    print self.childexp
    for c in zip(self.children, self.childgeo):
      print c
    #eux = ew #hor expand
    print 'size, self.size', size, self.size
    print 'euy', euy
    '''
    if eh < 0 and csy == 0: #badness
      #print 'badness', self, eh, len(self.children)
      clip = float(eh) / (len(self.children)) #badness clip 
    oy = 0
    draw = []
    assert(euy >= 0)
    #print ' childsets', self
    for child, ((cw, ch), (ex, ey), (sx, sy)) in zip(self.children, self.childgeo):
      if ex: cw = w              # hor expand
      elif cw > w: cw = w        # hor cut
      if ey : ch = ch + int(ey * euy)    # vert expand
      #print ey
      if sy and eh < 0: ch = ch + int(sy * suy)    # vert shrink
      if eh < 0 and csy == 0: ch = int(ch + clip)  #vert badness clip
      #print '  child.set_size', x, y+oy ,'/', ch, cw
      child.set_size((x, y + oy), (cw, ch))
      oy += ch
    #print ' endchildsets', self

class HBox(MultiParent):
  def get_size(self):
    self.childgeo = [child.get_size() for child in self.children]
    childsizes = [size for size, expand, shrink in self.childgeo]
    childexps = [expand for size, expand, shrink in self.childgeo]
    childshrinks = [shrink for size, expand, shrink in self.childgeo]
    self.size = sum([w for w, h in childsizes]+[0]), max([h for w, h in childsizes]+[0])
    self.childexp = sum([w for w, h in childexps]+[0]), max([h for w, h in childexps]+[0])
    self.childshrink = sum([w for w, h in childshrinks]+[0]), max([h for w, h in childshrinks]+[0])
    #print 'hbox', self.size, self.childexp, self.childshrink
    #print childexps
    return self.size, self.childexp, self.childshrink

  def set_size(self, pos, size):
    self.pos = pos
    x, y = pos
    w, h = size
    ew, eh = sub(size, self.size)
    self.size = size
    cex, cey = self.childexp
    csx, csy = self.childshrink
    eux, sux = 0, 0
    if cex: eux = float(ew)/cex 
    if csx: sux = float(ew)/csx 

    #euy = eh
    if ew < 0 and csx == 0:
      clip = float(ew) / (len(self.children))

    ox = 0
    for child, ((cw, ch), (ex, ey), (sx, sy)) in zip(self.children, self.childgeo):
      if ey: ch = h
      elif ch > h: ch = h
      if ex: cw = cw + int(ex * eux)
      if sx and eh < 0: cw = cw + int(sx * sux)
      if ew < 0 and csx == 0: cw = int(cw + clip)  #vert badness clip
      child.set_size((x + ox, y), (cw, ch))
      ox += cw

class Box(MultiParent):
  def init(self):
    self.expand = 1, 1
  def get_size(self):
    self.childgeo = [child.get_size() for child in self.children]
    return self.size, self.expand, self.shrink
    
  def set_size(self, pos, size):
    pass 

class StrLstBox(VBox):
  lines = []
  def set_lines(self, lines):
    self.lines = lines
    self.children = [Label(text = line, color = blue1) for line in self.lines]
    self.set_all(renderer = self.renderer)
  #def init(self):
  #  self.set_lines(self.lines)

class ObjView(VBox):
  def do(self, events):
    if self.ref:
      obj = getattr(self.ref, self.attr)
      if obj:
        self.children = [Label(text = repr(obj), color = self.color2)] + \
          [Label(text = k+' : '+repr(v), color = self.color) for k, v in vars(obj).iteritems()]
      else:
        self.children = [Label(text = 'None', color = self.color)]
      self.set_all(renderer = self.renderer)
      return
    if self.obj:
      self.children = [Label(text = k+' : '+repr(v), color = blue1) for k, v in vars(self.obj).iteritems()]
      self.set_all(renderer = self.renderer)

class ListView(VBox):
  def do(self, events):
    if self.ref:
      lst = getattr(self.ref, self.attr)
      if lst:
        self.children = [Label(text = repr(e), color = self.color) for e in lst]
      else:
        self.children = [Label(text = 'None', color = self.color)]
      self.set_all(renderer = self.renderer)
      return
    #if self.obj:
    #  self.children = [Label(text = k+' : '+repr(v), color = blue1) for k, v in vars(self.obj).iteritems()]
    #  self.set_all(renderer = self.renderer)



class RootWidget(Widget):
  def do(self, events):
    self.child.do(events) 
    self.child.get_size()
    self.child.set_size((0, 0), self.renderer.get_size())
    self.renderer.clear()
    self.child.draw()
    render.flip()
    return True 

black = (0, 0, 0)
red = (255, 0, 0)
white = (255, 255, 255)
blue1 = 92, 124, 188
bluegreen1 = (24, 184, 228)
green1 = (112, 156, 56)
green2 = (48, 76, 40)
green3 = (32, 56, 32)
backstripe1 = (8, 20, 32)
landgrid = (16, 40, 24)
baseheader = (48, 60, 112)

def lab(txt): return Label(text = txt, color = blue1)
def HB(lst): return HBox(children = lst)
def VB(lst): return VBox(children = lst)
def bframe(widget): return OPFrame(child = widget, fwidth = 2, color = blue1)


akeys = [k for k, v in txt.data.alphax.rawdata]
#sect = txt.data.alphax.citizens
lstbox = StrLstBox()

class ActLabel(Label):
  def on_mousebutton(self, event):
    lstbox.set_lines(getattr(txt.data.alphax, self.text.lower()))
#Label(on_mousebutton = (lambda self, e: lstbox.set_lines(getattr(txt.data.alphax, self.text.lower()))))
#def ALabel(text

#VBox(children = [lab(line) for line in sect])
wid = HBox(children = [VBox(children = [ActLabel(text = line, color = blue1) for line in akeys]), Bar(color = blue1), bframe(lstbox)])
wid = HBox(children = [VBox(children = [ActLabel(text = line, color = blue1) for line in akeys]), bframe(lstbox)])
#for i in range(1):
#  wid = bframe(wid)

widfr = bframe(wid)
#wid = OPFrame(child = wid, fwidth = 2, color = blue1)

#menu = HB([lab('fail'), Glue(setsize = (10, 0), expand = (0, 0)), lab('klunk'), Glue(expand = (1, 0)), lab('quit')])
#m = Expand(child = menu, set_expand = (1, 0))
#widgets = VB([widfr, lab('miso')])
#widgets = widfr


#main(widgets)

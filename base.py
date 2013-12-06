base_coverage = [
   (-3, -1), (-2, -2), (-1, -3),
   (-3, 1), (-2, 0), (-1, -1), (0, -2), (1, -3),
   (-2, 2), (-1, 1), (1, -1), (2, -2),
   (-1, 3), (0, 2), (1, 1), (2, 0), (3, -1),
   (1, 3), (2, 2), (3, 1)]

class Base():
  def __init__(self, map, faction, pos, name):
    self.map = map
    self.faction = faction
    self.name = name
    self.pos = pos
    self.pop = 1#random.randint(1, 12)
    self.nuts = 0
    self.mins = 0
    self.facs = []
    self.worked_squares = []
    self.calc_citizens()

  @property
  def growth(self):
    gr = self.faction.growth.copy()
    #creche, golden age; vats?
    return gr

  def die(self):
    pass 

  def calc_citizens(self):
    self.talents = 0
    self.drones = 0
    self.specs = self.pop - self.drones - len(self.worked_squares)

  def turn(self):
    squares = [self.map.tsquare(pos) for pos in (self.worked_squares + [self.pos])]
    nuts = sum([sq.nutrient(self).val for sq in squares])
    self.nuts += nuts - 2*self.pop
    if self.nuts < 0:
      self.nuts = 0
      self.pop -= 1
      if self.pop == 0:
        self.die()

    growth = self.faction.society('growth')
    grow_thres = (self.pop + 1) * (10 - growth.val)
    if self.nuts >= grow_thres:
      self.nuts -= grow_thres
      self.pop += 1 
      self.calc_citizens()
    #drones?
    #autoplace new workers

    mins = sum([sq.mineral(self).val for sq in squares])
    eng = sum([sq.energy(self).val for sq in squares])
    psych = (eng * self.faction.psych)/100
    econ = (eng * self.faction.econ)/100
    labs = (eng * self.faction.labs)/100
  
  def toggle_worker(self, pos):
    if pos in self.map.mcoor_lst(self.pos, base_coverage) and pos != self.pos:
      square = self.map.tsquare(pos)
      if pos not in self.worked_squares:
        if not square.base and not square.worked:
          if self.specs > 0:
            self.worked_squares.append(pos)
            square.worked = True
            self.specs -= 1
      else:
        self.worked_squares.remove(pos)
        square.worked = False
        self.specs += 1
 
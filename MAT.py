#!/usr/bin/env python

import datetime
import random
import sys

class Stats:
  def __init__(self):
    self._curEq = None
    self._results = []

  def startEq(self, eq):
    self._curEq = eq
    self._start = datetime.datetime.now()

  def endCurrent(self, correct):
    if self._curEq == None:
      return
    self._results.append((self._curEq, datetime.datetime.now() - self._start, correct))
    self._curEq = None

  def cancleCurrent(self):
    self._curEq = None

  def getStats(self):
    stats = {}
    stats['total'] = len(self._results)
    stats['correct'] = len(list(filter(lambda x: x[2], self._results)))
    stats['percent'] = stats['correct'] * 100.0 / stats['total']
    stats['rt'] = (sum(map(lambda x: x[1], self._results), datetime.timedelta()) / stats['total']).total_seconds() * 1000
    return stats


class Trainer:
  def __init__(self, mode):
    if mode == '':
      mode = 'mult'
    self._mode = mode
    self._stats = Stats()
    self._eqs = []
    self._generateEquations()
    self._ops = {
      '*': lambda x, y: x*y,
      '^': lambda x, y: x**y,
      '√': lambda x, y: round(y**(1.0/x))
    }

  def askEquation(self):
    if len(self._eqs) == 0:
      self._showStats()
      print('Done. One next round...')
      self._generateEquations()
    eq = self._eqs.pop()
    self._stats.startEq(eq)
    result, paused = self._readNumber('%d %s %d = ' % eq)
    if paused:
      self._stats.cancleCurrent()
    if result != self._ops[eq[1]](eq[0], eq[2]):
      self._stats.endCurrent(False)
      print('Wrong: %d %s %d = %d' % (eq[0], eq[1], eq[2], self._ops[eq[1]](eq[0], eq[2])))
      self._eqs.append(eq)
      random.shuffle(self._eqs)
    else:
      self._stats.endCurrent(True)
      print('Correct!')

  def run(self):
    try:
      while True:
        self.askEquation()
    except KeyboardInterrupt:
      self._showStats()

  def _showStats(self):
    stats = self._stats.getStats()
    print('\nStatistic:\n  Correct: %d of %d (%.2f %%)\n  Average time per response: %d msec' % (stats['correct'], stats['total'], stats['percent'], stats['rt']))

  def _generateEquations(self):
    if 'multbig' in self._mode:
      self._eqs += [(x, '*', y) for x in range(1, 21) for y in range(1, 21)]
    elif 'mult' in self._mode:
      self._eqs += [(x, '*', y) for x in range(1, 10) for y in range(1, 10)]
    if 'pow' in self._mode:
      self._eqs += [(x, '^', y) for x in range(1, 10) for y in range(2, 4)]
      self._eqs += [(x, '^', 2) for x in range(10, 31)]
    if 'root' in self._mode:
      self._eqs += [(y, '√', x**y) for x in range(1, 10) for y in range(2, 4)]
      self._eqs += [(2, '√', x**2) for x in range(10, 31)]
    if len(self._eqs) == 0:
      raise ValueError('%s is not supported.\nKnown parameters are: mult, multbig, pow, root.' % self._mode)
    random.shuffle(self._eqs)

  @staticmethod
  def _readNumber(prompt):
    paused = False
    while True:
      try:
        number = int(input(prompt))
      except ValueError:
        print('Not a Number. Retry...')
        continue
      except KeyboardInterrupt:
        paused = True
        try:
          input('\nPaused. Press ctrl+C again to exit. Enter to continue...')
        except KeyboardInterrupt as i:
          raise i
        continue
      break
    return (number, paused)

if __name__ == '__main__':
  try:
    trainer = Trainer(''.join(sys.argv[1:]))
    trainer.run()
  except ValueError as v:
    print(v)

#!/usr/bin/env python2.7
'''
A simple test for :class:`PseudoPositioner`
'''
from __future__ import print_function

import time

import config
from ophyd.controls import (EpicsMotor, PseudoPositioner)


def test():
    def callback(sub_type=None, timestamp=None, value=None, **kwargs):
        logger.info('[callback] [%s] (type=%s) value=%s' % (timestamp, sub_type, value))

    def done_moving(**kwargs):
        logger.info('Done moving %s' % (kwargs, ))

    loggers = ()
               # 'ophyd.controls.positioner',
               # 'ophyd.session',

    config.setup_loggers(loggers)
    logger = config.logger

    def calc_fwd(pseudo0=0.0, pseudo1=0.0, pseudo2=0.0):
        return [-pseudo0, -pseudo1, -pseudo2]

    def calc_rev(real0=0.0, real1=0.0, real2=0.0):
        return [-real0, -real1, -real2]

    def done(**kwargs):
        print('** Finished moving (%s)' % (kwargs, ))

    real0 = EpicsMotor(config.motor_recs[0], name='real0')
    real1 = EpicsMotor(config.motor_recs[1], name='real1')
    real2 = EpicsMotor(config.motor_recs[2], name='real2')

    logger.info('------- Sequential pseudo positioner')
    pos = PseudoPositioner([real0, real1, real2],
                           forward=calc_fwd, reverse=calc_rev,
                           pseudo=['pseudo0', 'pseudo1', 'pseudo2'],
                           simultaneous=False,
                           name='pseudopos')

    logger.info('Move to (.2, .2, .2), which is (-.2, -.2, -.2) for real motors')
    pos.move((.2, .2, .2), wait=True)
    logger.info('Position is: %s (moving=%s)' % (pos.position, pos.moving))

    if 0:
        logger.info('Move to (-.2, -.2, -.2), which is (.2, .2, .2) for real motors')
        pos.move((-.2, -.2, -.2), wait=True, moved_cb=done)

        logger.info('Position is: %s (moving=%s)' % (pos.position, pos.moving))

        # No such thing as a non-blocking move for a sequential (i.e.,
        # non-simultaneous) pseudo positioner

        # Create another one and give that a try

    pos = PseudoPositioner([real0, real1, real2],
                           forward=calc_fwd, reverse=calc_rev,
                           pseudo=['pseudo0', 'pseudo1', 'pseudo2'],
                           simultaneous=True,
                           name='pseudopos')

    logger.info('------- Simultaneous pseudo positioner')
    logger.info('Move to (2, 2, 2), which is (-2, -2, -2) for real motors')
    ret = pos.move((2, 2, 2), wait=False, moved_cb=done)
    while not ret.done:
        logger.info('Pos=%s %s (err=%s)' % (pos.position, ret, ret.error))
        time.sleep(0.1)

    print('Done')

if __name__ == '__main__':
    test()
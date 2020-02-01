#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/19 10:38
# @Version : 1.0
# @File    : show_eeg.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved

from __future__ import division
from __future__ import print_function
import numpy as np
import scipy.signal as scipy_signal
import matplotlib.pyplot as plt
from copy import copy
from keymonitor import KEYMONITOR
import random

class PlotEEG():
    def __init__(self,channels=8,yamp = 100,timerange=5,srate = 250, notchfilter=True,bandpass = [1,90]):
        self.channels = channels
        self.yamp = yamp
        self.timerange = timerange
        self.srate = srate
        self.notchfilter = notchfilter
        self.bandpass = [1,90]
        fs = self.srate/2
        if self.bandpass is not None:
            self._bp = True
            # bandpass filter
            Wp = np.array([bandpass[0] / fs, bandpass[1] / fs])
            Ws = np.array([(bandpass[0]*0.5) / fs, (bandpass[1]+10) / fs])
            N, Wn = scipy_signal.cheb1ord(Wp, Ws, 3, 40)
            self.bpB, self.bpA = scipy_signal.cheby1(N, 0.5, Wn, 'bandpass')
        else:
            self._bp = False

        # notch filter
        Fo = 50
        Q = 15
        w0 = Fo / (fs)
        self.notchB, self.notchA = scipy_signal.iirnotch(w0=w0, Q=Q)


        self._plength = self.srate * timerange
        self._flength = self.srate * (1+timerange)

        self._t = np.arange(0,timerange,1/self.srate)
        self.signal = [np.ones([self.channels,self._t.size])]

        self.update_yscale()
        self.ticks = []
        for i in range(self.channels):
            self.ticks.append('ch'+str(i+1))
        plt.ion()

    def update_yscale(self):
        self._yscale = np.arange(self.yamp,self.yamp + self.channels*self.yamp*2,self.yamp*2)

    def update(self,data):  #data: 行向量
        self.signal.append(data)
        eeg = np.hstack(self.signal)
        self.signal = [eeg[:, -self._flength:]]
        sig = copy(eeg)
        if eeg.shape[-1] > self._flength:
            if self.notchfilter:
                sig = scipy_signal.filtfilt(self.notchB, self.notchA, sig)
            if self._bp:
                sig = scipy_signal.filtfilt(self.bpB, self.bpA, sig)
            psig = sig[:,-self._plength:]

            plt.clf()
            for i in range(self.channels):
                plt.plot(self._t,psig[i,:] + self._yscale[i])
            plt.ylim([0,self._yscale[-1]+self.yamp])
            plt.yticks(self._yscale,self.ticks)
            plt.grid()
            plt.pause(0.01)

class PlotEEG2():
    def __init__(self, channels=8, yamp=100, timerange=5, srate=250, notchfilter=True, bandpass=[1, 90]):
        self.peeg = PlotEEG(channels, yamp, timerange, srate, notchfilter, bandpass)
        self.key = KEYMONITOR()
        self.on = True

    def update(self,data):
        k = self.key.get_key()
        if k is not None:
            if k == '=':
                self.peeg.yamp *= 1.25
                self.peeg.update_yscale()
            elif k == '-':
                self.peeg.yamp *= 0.8
                self.peeg.update_yscale()
            elif k == 'esc':
                self.on = False
            else:
                pass
        self.peeg.update(data)

def main():
    import time
    p = PlotEEG2(channels=1)
    while p.on:
        s = []
        for i in range(50):
            s.append(random.randint(1,50))
        data = np.array([s])
        p.update(data)
        time.sleep(0.2)

if __name__ == '__main__':
    main()


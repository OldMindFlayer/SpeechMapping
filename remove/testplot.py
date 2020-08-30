# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 15:45:29 2020

@author: AlexVosk
"""

from matplotlib import pyplot as plt
import numpy as np
import numpy.ma as ma

scores = [np.arange(24).reshape(12,2), np.arange(1,25).reshape(12,2)]


plt.close('all')
nrows = len(scores)
ncols = scores[0].shape[1]
fig, ax = plt.subplots(nrows = nrows,
                       ncols = ncols,
                       figsize=(12,8))
row_titles = ['R^2 actions', 'R^2 objects', '50Hz']
col_titles = ['rest', 'action', 'object']

viridis_cm = plt.cm.get_cmap('viridis', 256)
viridis_cm.set_bad('black', 1)

def array_into_grid(self, array):
    return (array.reshape([self.GRID_X,self.GRID_Y]).T)[::-1,:]


for i in range(nrows):
    for b in range(ncols):
        plt.subplot(3, ncols, i*ncols + (b+1))  
        im = array_into_grid(self.pair_r2[i][:,b])
        
        
        
        im_masked = ma.masked_array(im, self.PAIR_BAD_CH[i])
        plt.imshow(im_masked, cmap = viridis_cm)
        plt.colorbar();
        for m in range(self.GRID_Y):
            for n in range(self.GRID_X):
                plt.text(n, m, str(self.ecog_channel_grid[m,n]), color='white', ha='center', va='center' )
        plt.plot([0.5, 0.5], [-0.5, 1.5], color='silver', lw=2)
        plt.plot([2.5, 2.5], [-0.5, 1.5], color='silver', lw=2)
        plt.title(str(self.fbandmins[b])+'-'+str(self.fbandmaxs[b])+ ' Hz');
        if b == 0:
            plt.text(-10, 5, row_titles[i], size = 24)
        plt.axis("off")

for b in range(3):
    plt.subplot(3,self.pair_r2[0].shape[1], self.pair_r2[0].shape[1]*2 + (b+1))
    im = self.GRID50Hz[b]
    plt.imshow(im)
    plt.colorbar();
    for m in range(self.GRID_Y):
        for n in range(self.GRID_X):
            plt.text(n, m, str(self.ecog_channel_grid[m,n]), color='white', ha='center', va='center' )
    plt.plot([0.5, 0.5], [-0.5, 1.5], color='silver', lw=2)
    plt.plot([2.5, 2.5], [-0.5, 1.5], color='silver', lw=2)
    plt.title(col_titles[b]);
    if b == 0:
        plt.text(-8, 5, row_titles[2], size = 24)
    plt.axis("off")

fig.tight_layout()
plt.savefig(self.path_to_results_file)
from matplotlib import pyplot as plt
from matplotlib import colors
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import h5py
from scipy.signal import butter, lfilter
#import PNinterpolate
from scipy import stats
from scipy.io import savemat
import numpy.ma as ma
import os
import pylab
import errno
import sys
import config

config.init()
#arg = sys.argv
#path_to_experiment_data = arg[1] + '/experiment_data/experiment_data.h5'
#path_to_results = arg[1] + '/results_full/R2.png'
path_big = 'C:/Workspace/SpeechMapping/data/SeleznevaFull2/11_03_20/experiment_data/'
path_to_experiment_data = path_big + 'experiment_data_part2.h5'
path_to_results = path_big + 'R2_new2.png'

print(path_to_experiment_data)


GRID_X  = config.config['processing'].getint('grid_size_x')
GRID_Y  = config.config['processing'].getint('grid_size_y')
NUM_CHANNELS = GRID_X*GRID_Y;
GRID_CHANNAL_MIN = config.config['processing'].getint('grid_channel_min')
GRID_CHANNAL_MAX = config.config['processing'].getint('grid_channel_max')
DEC     = 3;
TH50HZ  = 20;
FMAX    = 120;
FMIN    = 60;
FSTEP   = 20;
ecog_grid_numbers = np.arange(GRID_CHANNAL_MIN, GRID_CHANNAL_MAX+1).reshape(GRID_X, GRID_Y).T[::-1,:]
print(ecog_grid_numbers)

assert NUM_CHANNELS == (GRID_CHANNAL_MAX - GRID_CHANNAL_MIN + 1)


def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_lowpass(cutoff, fs, order=3):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_bandstop_filter(data, lowcut, highcut, fs, order):

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    i, u = butter(order, [low, high], btype='bandstop')
    y = lfilter(i, u, data)
    return y

def filterEMG(MyoChunk,fmin,fmax, fs):
    
    blow, alow = butter_lowpass(cutoff = 2, fs = fs, order=5)

    if(fmin > 0):
        bband,aband = butter_bandpass(lowcut=fmin, highcut=fmax, fs = fs, order=3)
    else:
        bband,aband = butter_lowpass(cutoff = fmax, fs = fs, order=3)
        
    MyoChunk = lfilter(bband,aband, MyoChunk.T).T

    np.abs(MyoChunk, out=MyoChunk)
    
    for j in range(MyoChunk.shape[1]):
        MyoChunk[:,j] = lfilter(blow,alow, MyoChunk[:,j])

    return MyoChunk

#srate   = 2048
#first 
ch_idxs_ecog = range(GRID_CHANNAL_MIN - 1, GRID_CHANNAL_MAX)
#print(list(ch_idxs_ecog))
#print(GRID_CHANNAL_MIN - 1, NUM_CHANNELS + GRID_CHANNAL_MAX)
plt.close('all');


data_groups = [];
data_groups.append('data_rest');
data_groups.append('data_actions');
data_groups.append('data_objects');

VALS  = [0,1,1]; 


PAIRS = [(0,1),(0,2)];

ECOG = []; GRID50Hz = []; BAD_CH = [];
FEAT = [];SRATE = [];
fbandmins = np.arange(FMIN,FMAX,FSTEP)
fbandmaxs = fbandmins + FSTEP

for data_group in data_groups:
    print('Processing ' + data_group);
    with h5py.File(path_to_experiment_data,'r+') as f1:
        raw_data    = np.array(f1[data_group]['raw_data'])
        srate       = f1['fs'][()]
        SRATE.append(srate);
    
    ecog_data      = np.copy(raw_data[:,ch_idxs_ecog])
    ecog_50hz_av   = np.mean(filterEMG(ecog_data,48,52, srate), axis = 0)
    grid_50hz_av   = (ecog_50hz_av.reshape([GRID_X,GRID_Y]).T)[::-1,:];
    GRID50Hz.append(grid_50hz_av);
    bad_ch = ecog_50hz_av > TH50HZ;
    BAD_CH.append(bad_ch);
    
    ecog_data[:,bad_ch] = 0;
    
    # notch-filter power-line
    for i in range(ecog_data.shape[1]):
        for freq in np.arange(50,200,50):
            ecog_data[:,i] = butter_bandstop_filter(ecog_data[:,i], freq-2, 
                             freq+2, srate, 4)
    ECOG.append(ecog_data);

assert np.unique(SRATE).shape[0]==1, 'Sampling rates should be the same'
    
PAIR_R2 = [];
PAIR_P  = [];        
for pair in PAIRS:
    i = pair[0];
    j = pair[1];
    print('Calculating prediction score for pair', pair)
    # create dependent variable
    y = np.vstack((np.ones((ECOG[i].shape[0],1))*VALS[i],
                   np.ones((ECOG[j].shape[0],1))*VALS[j]))[::DEC];
                   
    res_r2 = np.zeros( (ECOG[i].shape[1],len(fbandmins)));           
    res_p = np.ones((ECOG[i].shape[1],len(fbandmins)));           
    
    for ch in range(ECOG[i].shape[1]):
        
        if( BAD_CH[i][ch] | BAD_CH[j][ch] ):
            res_r2[ch,:] = 0;
            res_p[ch,:]  = 1;
        else:
            ecog_i = np.zeros((ECOG[i].shape[0],1));
            ecog_i[:,0] = np.copy(ECOG[i][:,ch]);
            ecog_j = np.zeros((ECOG[j].shape[0],1));
            ecog_j[:,0] = np.copy(ECOG[j][:,ch]);
            ecog_concat = np.vstack((ecog_i,ecog_j));
            for f in range(len(fbandmins)):
                fbandmin = fbandmins[f]
                fbandmax = fbandmaxs[f]
                x = filterEMG(ecog_concat,fbandmin,fbandmax,srate)[::DEC]
                scaler = MinMaxScaler([-1, 1])
                scaler.fit(x)
                x = scaler.transform(x)    
                slope, intercept, r_value_1, p_value, std_err = stats.linregress(x[:,0], y[:,0]);
                res_r2[ch,f] = r_value_1**2 if r_value_1 >0 else 0;
                res_p[ch,f]  = p_value;

    PAIR_P.append(res_p);
    PAIR_R2.append(res_r2);

    
    
    
    
plt.close('all');
k=1;


BAD_CH_mod = []
for bad_ch in BAD_CH:
    BAD_CH_mod.append((bad_ch.reshape([GRID_X,GRID_Y]).T)[::-1,:])
#BAD_CH_mod[0][4,5] = True
PAIR_BAD_CH = [np.logical_or(BAD_CH_mod[0], BAD_CH_mod[1]), np.logical_or(BAD_CH_mod[0], BAD_CH_mod[2])]
#print(PAIR_BAD_CH[0])



fig, ax = plt.subplots(nrows = len(PAIR_R2),
                       ncols = PAIR_R2[0].shape[1],
                       figsize=(12,8))
row_titles = ['R^2 actions', 'R^2 objects', '50Hz']
col_titles = ['rest', 'action', 'object']

viridis_cm = plt.cm.get_cmap('viridis', 256)
viridis_cm.set_bad('black', 1)

number_locations = np.arange(GRID_CHANNAL_MAX-GRID_CHANNAL_MIN+1).reshape(GRID_X, GRID_Y).T[::-1,:]

for i in range(2):
    for b in range(PAIR_R2[i].shape[1]):
        plt.subplot(3,PAIR_R2[i].shape[1],(i)*PAIR_R2[i].shape[1] + (b+1))  
        im  = (PAIR_R2[i][:,b].reshape([GRID_X,GRID_Y]).T)[::-1,:];
        plt.imshow(im, cmap = viridis_cm)
        #im_masked = ma.masked_array(im, PAIR_BAD_CH[i])
        #plt.imshow(im_masked, cmap = viridis_cm)
        plt.colorbar();
        for m in range(number_locations.shape[0]):
            for n in range(number_locations.shape[1]):
                plt.text(n, m, str(ecog_grid_numbers[m,n]), color='white', ha='center', va='center' )
        plt.plot([0.5, 0.5], [-0.5, 1.5], color='silver', lw=2)
        plt.plot([2.5, 2.5], [-0.5, 1.5], color='silver', lw=2)
        plt.title(str(fbandmins[b])+'-'+str(fbandmaxs[b])+ ' Hz');
        if b == 0:
            plt.ylabel(row_titles[i], size = 24)

for b in range(3):
    plt.subplot(3,PAIR_R2[0].shape[1], PAIR_R2[0].shape[1]*2 + (b+1))
    im = GRID50Hz[b]
    plt.imshow(im)
    plt.colorbar();
    plt.title(col_titles[b]);
    if b == 0:
        plt.ylabel(row_titles[2], size = 24)

fig.tight_layout()
plt.savefig(path_to_results)
plt.show()

#fig2, ax2 = plt.hist()
            
#from matplotlib import cm
##Q = np.mean(res_re[:,5:5,0],axis=1);
#Q = res_re[:,6,0];
#Qmin = np.min(Q);
#Qmax = np.max(Q);
#QQ = (Q-Qmin)/(Qmax-Qmin);
#for i in range(QQ.shape[0]):
#    row = i%8;
#    col = int(i/8);
#    x = X0+col*dX;
#    y = Y0-row*dY;
#    ind = int(QQ[i]*255);
#    ax  = plt.plot(x,y, color=(0.3, 0.3, 0.3, 1),  marker='o',
#             markerfacecolor=cm.viridis(ind), markersize=22, alpha = 0.75)              
#
#plt.colorbar();
#            
#       
    
                

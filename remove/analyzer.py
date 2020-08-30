from matplotlib import pyplot as plt
import numpy as np
from os import makedirs
import h5py
import numpy.ma as ma
from pathlib import Path
import time
from filterEMG import filterEMG, butter_bandstop_filter

class Decoder():
    def __init__(self):
        pass
        
    def get_parameters(self, config):
        self.config = config
    
        self.INTERVAL_START = config['decoder'].getfloat('interval_start')
        self.INTERVAL_STOP  = config['decoder'].getfloat('interval_stop')
        self.single_picture_time = self.config['display'].getfloat('single_picture_time')
    
        # create direcoties based on path
        self.results_path = Path(config['paths']['results_path'])
        makedirs(self.results_path, exist_ok=True)
        self.path_to_results_file = self.results_path/'score_1.png'
        file_name_number = 1
        while self.path_to_results_file.is_file():
            file_name_number += 1
            self.path_to_results_file = Path(config['paths']['results_path'])/('score_{}.png'.format(file_name_number))
            

        self.GRID_X  = config['decoder'].getint('grid_size_x')
        self.GRID_Y  = config['decoder'].getint('grid_size_y')
        self.DEC     = config['decoder'].getint('dec')
        self.TH50HZ  = config['decoder'].getint('th50hz')
        self.FMAX    = config['decoder'].getint('fmax')
        self.FMIN    = config['decoder'].getint('fmin')
        self.FSTEP   = config['decoder'].getint('fstep')
        self.num_channels = self.GRID_X*self.GRID_Y
        self.GRID_CHANNEL_FROM = config['decoder'].getint('grid_channel_from')
        self.DATA_GROUPS = self.config['recorder']['group_names'].split(' ')
        
        
        
        
        self.VALS  = [0,1,1]; 
        self.PAIRS = [(0,1),(0,2)];
        self.ECOG, self.STIM, self.GRID50Hz, self.BAD_CH = [], [], [], []
        self.FEAT, self.SRATE = [], []
        self.fbandmins = np.arange(self.FMIN, self.FMAX, self.FSTEP)
        self.fbandmaxs = self.fbandmins + self.FSTEP
        self.MEASURE = config['decoder']['linregress']
        self.pair_r2 = []
        
        
        # create channel grid with numbers equal to numbers from lsl stream
        if config['decoder'].getboolean('plot_grid_base'):
            self.ecog_channel_grid = np.arange(1, self.GRID_CHANNEL_TO - self.GRID_CHANNEL_FROM + 2).reshape(self.GRID_X, self.GRID_Y).T[::-1,:]
        else:
            self.ecog_channel_grid = np.arange(self.GRID_CHANNEL_FROM, self.GRID_CHANNEL_TO+1).reshape(self.GRID_X, self.GRID_Y).T[::-1,:]
        print(self.ecog_channel_grid)




    def process_file_last(self):
        self.process_file(Path(self.config['paths']['experiment_data_path']))

    def process_file(self, path, groups):
        processed_data = {}
        for group in groups:
            self._printm('Processing ' + group);
            with h5py.File(path,'r+') as file:
                raw_data = np.array(file[group]['raw_data'])
                picture_indices = np.array(file[group]['picture_indices'])
                srate = file['fs'][()]
            processed_data[group] = self._process_data(raw_data, picture_indices, srate)
        return processed_data
        
        
        #prediction_values = []
        #for i, j in self.PAIRS:
        #    res_r2, res_p = self._prediction_score(processed_data[i], processed_data[j])
        #    self.pair_r2.append(res_r2)
        
    def _preprocess_data(self, raw_data, picture_indices, srate):
        # range of channels with eeg data, e.g. for grid 1 to 20 => range(0, 20) ~ [0, 1, ..., 19]
        ch_idxs_ecog = np.arange(self.GRID_CHANNEL_FROM, self.GRID_CHANNEL_FROM + self.num_channels) - 1
        # channel with time of picture onset
        
        # copy ecog and stim data
        data_ecog = np.copy(raw_data[:,ch_idxs_ecog])
        #data_stim = np.copy(raw_data[:,ch_idxs_stim])
        
        # get 50hz averege of data
        ecog_50hz_av = np.mean(filterEMG(data_ecog, 48, 52, srate), axis = 0)
        
        
        # bad channels - array where 50hz average is > threshold        
        bad_ch = ecog_50hz_av > self.TH50HZ
    
        # broadcast 0 on all bad channels
        #data_ecog[:, bad_ch] = 0
        
        # notch-filter power-line (remove 50hz from good channels)
        for channel in range(data_ecog.shape[1]):
            if channel not in bad_ch:
                for freq in np.arange(50,200,50):
                    data_ecog[:,channel] = butter_bandstop_filter(data_ecog[:,channel], freq-2, freq+2, srate, 4)
        
        return ProcessedData(data_ecog=data_ecog, 
                             picture_indices=picture_indices, 
                             ecog_50hz_av=ecog_50hz_av,
                             bad_ch=bad_ch, 
                             srate=srate)


    def prediction_score(self, data_i, data_j, model, model_params):
        # matricies to store values of r2 and p
        values = np.zeros((self.num_channels, len(self.fbandmins)))
        #res_p = np.ones((self.num_channels, len(self.fbandmins)))

        def indices(data):
            ind = np.zeros(0)
            for start, stop in data.picture_indices:
                length = stop - start
                interval_start = int(start + length * self.INTERVAL_START/self.single_picture_time)
                interval_stop = int(start + length * self.INTERVAL_STOP/self.single_picture_time)
                print(length, interval_start, interval_stop)
                if interval_start < interval_stop:
                    ind = np.append(ind, np.arange(interval_start, interval_stop))
                print(ind.shape)
            ind  = ind.astype(int)
            return ind
        
        indj = indices(data_j)
        indi = np.arange(min(indj.shape[0], data_j.data_ecog.shape[0]))
        
        for channel in range(self.num_channels):
            if data_i.bad_ch[channel] | data_j.bad_ch[channel]:
                values[channel,:] = 0
            else:
                for freq_index in range(len(self.fbandmins)):
                    fbandmin = self.fbandmins[freq_index]
                    fbandmax = self.fbandmaxs[freq_index]
                    
                    xi = filterEMG(data_i.data_ecog,fbandmin,fbandmax, data_i.srate)[indi]
                    xj = filterEMG(data_j.data_ecog,fbandmin,fbandmax, data_j.srate)[indj]
                    
                    values[channel, freq_index] = model(xi, xj, model_params)
        return Score(values = values,
                     data_i = data_i,
                     data_j = data_j)












    def plot_results(self, scores):
        plt.close('all');
        nrows = len(scores)
        ncols = scores[0].values.shape[1]
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
                im = array_into_grid(scores[i][:,b])
                
                bad_channels = np.logical_or(scores[i].data_i.bad_ch, scores[i].data_j.bad_ch)
                
                im_masked = ma.masked_array(im, array_into_grid(bad_channels))
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
        
        
        #for b in range(3):
        #    plt.subplot(3,self.pair_r2[0].shape[1], self.pair_r2[0].shape[1]*2 + (b+1))
        #    grid50hz
        #    im = self.GRID50Hz[b]
        #    plt.imshow(im)
        #    plt.colorbar();
        #    for m in range(self.GRID_Y):
        #        for n in range(self.GRID_X):
        #            plt.text(n, m, str(self.ecog_channel_grid[m,n]), color='white', ha='center', va='center' )
        #    plt.plot([0.5, 0.5], [-0.5, 1.5], color='silver', lw=2)
        #    plt.plot([2.5, 2.5], [-0.5, 1.5], color='silver', lw=2)
        #    plt.title(col_titles[b]);
        #    if b == 0:
        #        plt.text(-8, 5, row_titles[2], size = 24)
        #    plt.axis("off")
        
        fig.tight_layout()
        plt.savefig(self.path_to_results_file)
        plt.show()

    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)



class ProcessedData:
    def __init__(self, data_ecog, picture_indices, ecog_50hz_av, bad_ch, srate):
        self.data_ecog = data_ecog
        self.picture_indices = picture_indices
        self.ecog_50hz_av = ecog_50hz_av
        self.bad_ch = bad_ch
        self.srate = srate

class Score:
    def __init__(self, values, data_i, data_j):
        self.values = values
        self.data_i = data_i
        self.data_j = data_j




if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read(Path('decoder.py').resolve().parents[1]/'util/custom_config_processing.ini')


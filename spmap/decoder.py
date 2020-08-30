from matplotlib import pyplot as plt
import numpy as np
from os import makedirs
import h5py
import numpy.ma as ma
from pathlib import Path
import time
from filterEMG import filterEMG, butter_bandstop_filter
import models


class Decoder():
    def __init__(self, config):        
        self.GRID_X  = config['decoder'].getint('grid_size_x')
        self.GRID_Y  = config['decoder'].getint('grid_size_y')
        self.TH50HZ  = config['decoder'].getint('th50hz')
        self.FMAX    = config['decoder'].getint('fmax')
        self.FMIN    = config['decoder'].getint('fmin')
        self.FSTEP   = config['decoder'].getint('fstep')
        self.num_channels = self.GRID_X*self.GRID_Y
        self.GRID_CHANNEL_FROM = config['decoder'].getint('grid_channel_from')
        self.DATA_GROUPS = config['recorder']['group_names'].split(' ')
        self.fbandmins = np.arange(self.FMIN, self.FMAX, self.FSTEP)
        self.fbandmaxs = self.fbandmins + self.FSTEP
        self.use_interval = config['decoder'].getboolean('use_interval')
        self.INTERVAL_START = config['decoder'].getfloat('interval_start')
        self.INTERVAL_STOP  = config['decoder'].getfloat('interval_stop')
        self.single_picture_time = config['display'].getfloat('single_picture_time')
        self.measure = config['decoder']['measure']
        
        # create direcoties based on path
        self.experiment_data_path = config['paths']['experiment_data_path']
        self.results_path = Path(config['paths']['results_path'])
        makedirs(self.results_path, exist_ok=True)
        self.path_to_results_file = self.results_path/'score_1.h5'
        self.path_to_results_picture = self.results_path/'score_1.png'
        file_name_number = 1
        while self.path_to_results_file.is_file() or self.path_to_results_picture.is_file():
            file_name_number += 1
            self.path_to_results_file = Path(config['paths']['results_path'])/('score_{}.h5'.format(file_name_number))
            self.path_to_results_picture = Path(config['paths']['results_path'])/('score_{}.png'.format(file_name_number))





    def process_current_file(self):
        processed_data = self.process_file(self.experiment_data_path)
        score_obj = self.prediction_score(processed_data[self.DATA_GROUPS[0]],
                                       processed_data[self.DATA_GROUPS[1]],
                                       models.get_model(self.measure))
        score_act = self.prediction_score(processed_data[self.DATA_GROUPS[0]],
                                       processed_data[self.DATA_GROUPS[2]],
                                       models.get_model(self.measure))
        self.save_score(self.DATA_GROUPS[1], score_obj.values)
        self.save_score(self.DATA_GROUPS[2], score_act.values)
        self.plot_results([score_obj, score_act], processed_data)
        
        
        
        


    def process_file(self, path):
        processed_data = {}
        for group in self.DATA_GROUPS:
            self._printm('Processing ' + group);
            with h5py.File(path,'r+') as file:
                raw_data = np.array(file[group]['raw_data'])
                picture_indices = np.array(file[group]['picture_indices'])
                srate = file['fs'][()]
            processed_data[group] = self._process_data(group, raw_data, picture_indices, srate)
        print()
        return processed_data
        
    # process raw data,         
    def _process_data(self, name, raw_data, picture_indices, srate):
        # range of channels with eeg data, e.g. for grid 1 to 20 => range(0, 20) ~ [0, 1, ..., 19]
        ch_idxs_ecog = np.arange(self.GRID_CHANNEL_FROM, self.GRID_CHANNEL_FROM + self.num_channels) - 1
        
        # copy ecog and stim data
        data_ecog = np.copy(raw_data[:,ch_idxs_ecog])
        
        # get 50hz averege of data
        ecog_50hz_av = np.mean(filterEMG(data_ecog, 48, 52, srate), axis = 0)
                
        # bad channels - array where 50hz average is > threshold        
        bad_ch = ecog_50hz_av > self.TH50HZ
            
        # notch-filter power-line (remove 50hz from good channels)
        for channel in range(data_ecog.shape[1]):
            if channel not in bad_ch:
                for freq in np.arange(50,200,50):
                    data_ecog[:,channel] = butter_bandstop_filter(data_ecog[:,channel], freq-2, freq+2, srate, 4)
        
        return ProcessedData(name = name,
                             data_ecog=data_ecog, 
                             picture_indices=picture_indices, 
                             ecog_50hz_av=ecog_50hz_av,
                             bad_ch=bad_ch, 
                             srate=srate)


    def prediction_score(self, data_i, data_j, model, *args, **kwargs):
        # matricies to store score
        score = np.zeros((self.num_channels, len(self.fbandmins)))

        def indices(data):
            ind = np.zeros(0)
            for start, stop in data.picture_indices:
                length = stop - start
                interval_start = int(start + length * self.INTERVAL_START/self.single_picture_time)
                interval_stop = int(start + length * self.INTERVAL_STOP/self.single_picture_time)
                if interval_start < interval_stop:
                    ind = np.append(ind, np.arange(interval_start, interval_stop))
            ind = ind.astype(int)
            return ind
        
        if self.use_interval:
            indj = indices(data_j)
        else:
            indj = np.arange(data_j.data_ecog.shape[0])
        indi = np.arange(min(data_i.data_ecog.shape[0], indj.shape[0]))
        
        # if there is no pictures
        if indi.shape[0] == 0:
            return Score(values = score,
                         data_i = data_i,
                         data_j = data_j)
        
        bad_channels = np.logical_or(data_i.bad_ch, data_j.bad_ch)
        for freq_index in range(len(self.fbandmins)):
            fbandmin = self.fbandmins[freq_index]
            fbandmax = self.fbandmaxs[freq_index]
            
            xi = filterEMG(data_i.data_ecog, fbandmin, fbandmax, data_i.srate)[indi]
            xj = filterEMG(data_j.data_ecog, fbandmin, fbandmax, data_j.srate)[indj]
            for channel in range(self.num_channels): 
                if not bad_channels[channel]:
                    score[channel, freq_index] = model(xi[:,[channel]], xj[:,[channel]], args, kwargs)
        score[bad_channels, :] = 0            
        
        return Score(values = score,
                     data_i = data_i,
                     data_j = data_j)

    def save_score(self, name, data):
        with h5py.File(self.path_to_results_file, 'a') as file:
            file[name] = data











    def plot_results(self, scores, data):
        plt.close('all')
        plot_shape = (len(scores) + 1, scores[0].values.shape[1])
        fig, ax = plt.subplots(nrows = plot_shape[0],
                               ncols = plot_shape[1],
                               figsize=(12,8))
        
        def get_minmax_score(scores):
            min_score, max_score = 0, 0.3
            for score in scores:
                min_score = np.amin(score.values) if np.amin(score.values) < min_score else min_score
                max_score = np.amax(score.values) if np.amax(score.values) > max_score else max_score
            return min_score, max_score
        min_score, max_score = get_minmax_score(scores)
        
        row_titles = ['R^2 objects', 'R^2 actions', '50Hz']
        col_titles = self.DATA_GROUPS
        
        viridis_cm = plt.cm.get_cmap('viridis', 256)
        viridis_cm.set_bad('black', 1)

        def array_into_grid(array):
            return (array.reshape([self.GRID_X,self.GRID_Y]).T)[::-1,:]
        
        ecog_channel_grid = array_into_grid(np.arange(self.GRID_CHANNEL_FROM, self.GRID_CHANNEL_FROM + self.num_channels))
        print(ecog_channel_grid)
        for i in range(plot_shape[0] - 1):
            for j in range(plot_shape[1]):
                plt.subplot(plot_shape[0], plot_shape[1], (i*plot_shape[1] + j + 1))  
                
                im = array_into_grid(scores[i].values[:,j])                
                bad_channels = np.logical_or(scores[i].data_i.bad_ch, scores[i].data_j.bad_ch)                
                im_masked = ma.masked_array(im, array_into_grid(bad_channels))

                plt.imshow(im_masked, cmap = viridis_cm, vmin=min_score, vmax=max_score)
                plt.colorbar()
                
                for m in range(self.GRID_Y):
                    for n in range(self.GRID_X):
                        plt.text(n, m, str(ecog_channel_grid[m,n]), color='white', ha='center', va='center' )
                plt.plot([0.5, 0.5], [-0.5, 1.5], color='silver', lw=2)
                plt.plot([2.5, 2.5], [-0.5, 1.5], color='silver', lw=2)
                plt.title(str(self.fbandmins[j])+'-'+str(self.fbandmaxs[j])+ ' Hz');
                if j == 0:
                    plt.text(-10, 5, row_titles[i], size = 24)
                plt.axis("off")
        
        
        
        for j in range(plot_shape[1]):
            plt.subplot(3, plot_shape[1], plot_shape[1]*2 + (j+1))
            im = array_into_grid(data[self.DATA_GROUPS[j]].ecog_50hz_av)
            plt.imshow(im)
            plt.colorbar();
            for m in range(self.GRID_Y):
                for n in range(self.GRID_X):
                    plt.text(n, m, str(ecog_channel_grid[m,n]), color='white', ha='center', va='center' )
            plt.plot([0.5, 0.5], [-0.5, 1.5], color='silver', lw=2)
            plt.plot([2.5, 2.5], [-0.5, 1.5], color='silver', lw=2)
            plt.title(col_titles[j]);
            if j == 0:
                plt.text(-8, 5, row_titles[2], size = 24)
            plt.axis("off")
        
        fig.tight_layout()
        plt.savefig(self.path_to_results_picture)
        plt.show()

    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)



class ProcessedData:
    def __init__(self, name, data_ecog, picture_indices, ecog_50hz_av, bad_ch, srate):
        self.name = name
        self.data_ecog = data_ecog
        self.picture_indices = picture_indices
        self.ecog_50hz_av = ecog_50hz_av
        self.bad_ch = bad_ch
        self.srate = srate

    def __repr__(self):
        result = ''
        result += self.name + '\n'
        result += 'data_ecog shape: ' + str(self.data_ecog.shape) + '\n'
        result += 'picture_indices shape: ' + str(self.picture_indices.shape) + '\n'
        result += 'number of bad_ch: ' + str(np.sum(self.bad_ch)) + '\n'
        result += 'srate: ' + str(self.srate) + '\n'
        return result
    


class Score:
    def __init__(self, values, data_i, data_j):
        self.values = values
        self.data_i = data_i
        self.data_j = data_j




if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read(Path('decoder.py').resolve().parents[1]/'util/custom_config_processing.ini')


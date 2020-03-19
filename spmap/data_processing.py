from matplotlib import pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import h5py
from scipy.signal import butter, lfilter
#import PNinterpolate
from scipy import stats
import numpy.ma as ma
from pathlib import Path

class DataProcessing():
    def __init__(self, config):
        self.config = config
        self.use_interval = config['processing'].getboolean('use_interval')
        
        # paths to files
        self.path_to_experiment_data_file = Path(config['paths']['experiment_data_path'])
        file_name_base = 'R2.png'
        if self.use_interval:
            file_name_base = 'R2_interval.png'
        self.path_to_results_file = Path(config['paths']['results_path'])/file_name_base
        file_name_number = 1
        while self.path_to_results_file.is_file():
            if self.use_interval:
                self.path_to_results_file = Path(config['paths']['results_path'])/('R2_interval_{}.png'.format(file_name_number))
            else:
                self.path_to_results_file = Path(config['paths']['results_path'])/('R2_{}.png'.format(file_name_number))
            file_name_number += 1


        self.GRID_X  = config['processing'].getint('grid_size_x')
        self.GRID_Y  = config['processing'].getint('grid_size_y')
        self.NUM_CHANNELS = self.GRID_X*self.GRID_Y;
        self.grid_channel_from = config['processing'].getint('grid_channel_from')
        self.grid_channel_to = config['processing'].getint('grid_channel_to')
        self.DEC     = 3;
        self.TH50HZ  = 20;
        self.FMAX    = 120;
        self.FMIN    = 60;
        self.FSTEP   = 20;
        self.INTERVAL_START = config['processing'].getfloat('interval_start')
        self.INTERVAL_STOP  = config['processing'].getfloat('interval_stop')
        self.data_groups = self.config['data_saving']['group_names'].split(' ')
        
        self.VALS  = [0,1,1]; 
        self.PAIRS = [(0,1),(0,2)];
        self.ECOG, self.STIM, self.GRID50Hz, self.BAD_CH = [], [], [], []
        self.FEAT, self.SRATE = [], []
        self.PAIR_BAD_CH = []
        self.fbandmins = np.arange(self.FMIN, self.FMAX, self.FSTEP)
        self.fbandmaxs = self.fbandmins + self.FSTEP

        self.PAIR_R2, self.PAIR_P = [], []        

        # create channel grid with numbers equal to numbers from lsl stream
        assert self.NUM_CHANNELS == (self.grid_channel_to - self.grid_channel_from + 1)
        if config['processing'].getboolean('plot_grid_base'):
            self.ecog_channel_grid = np.arange(1, self.grid_channel_to - self.grid_channel_from + 2).reshape(self.GRID_X, self.GRID_Y).T[::-1,:]
        else:
            self.ecog_channel_grid = np.arange(self.grid_channel_from, self.grid_channel_to+1).reshape(self.GRID_X, self.GRID_Y).T[::-1,:]
        print(self.ecog_channel_grid)




    def _butter_bandpass(self, lowcut, highcut, fs, order=3):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a
    
    def _butter_lowpass(self, cutoff, fs, order=3):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a
    
    def _butter_bandstop_filter(self, data, lowcut, highcut, fs, order):
    
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
    
        i, u = butter(order, [low, high], btype='bandstop')
        y = lfilter(i, u, data)
        return y
    
    # main_filter
    def _filterEMG(self, MyoChunk, fmin, fmax, fs):
        blow, alow = self._butter_lowpass(cutoff = 2, fs = fs, order=5)
        if(fmin > 0):
            bband,aband = self._butter_bandpass(lowcut=fmin, highcut=fmax, fs = fs, order=3)
        else:
            bband,aband = self._butter_lowpass(cutoff = fmax, fs = fs, order=3)
        MyoChunk = lfilter(bband,aband, MyoChunk.T).T
        np.abs(MyoChunk, out=MyoChunk)
        for j in range(MyoChunk.shape[1]):
            MyoChunk[:,j] = lfilter(blow,alow, MyoChunk[:,j])
        return MyoChunk


    def _data_process(self):
        ch_idxs_ecog = range(self.grid_channel_from - 1, self.grid_channel_to)
        ch_idxs_stim = -1

        for data_group in self.data_groups:
            print('Processing ' + data_group);
            with h5py.File(self.path_to_experiment_data_file,'r+') as file:
                raw_data = np.array(file[data_group]['raw_data'])
                srate = file['fs'][()]
                self.SRATE.append(srate);
            
            ecog_data = np.copy(raw_data[:,ch_idxs_ecog])
            stim_data = np.copy(raw_data[:,ch_idxs_stim]) 
            ecog_50hz_av = np.mean(self._filterEMG(ecog_data,48,52, srate), axis = 0)
            grid_50hz_av = (ecog_50hz_av.reshape([self.GRID_X,self.GRID_Y]).T)[::-1,:];
            self.GRID50Hz.append(grid_50hz_av);
            bad_ch = ecog_50hz_av > self.TH50HZ;
            self.BAD_CH.append(bad_ch);
            
            # broadcast 0 on all bad channels
            ecog_data[:,bad_ch] = 0;
            
            # notch-filter power-line
            for i in range(ecog_data.shape[1]):
                for freq in np.arange(50,200,50):
                    ecog_data[:,i] = self._butter_bandstop_filter(ecog_data[:,i], freq-2, freq+2, srate, 4)
            self.ECOG.append(ecog_data);
            self.STIM.append(stim_data);

        assert np.unique(self.SRATE).shape[0]==1, 'Sampling rates should be the same'
        
        # make pair of bad channel grids
        BAD_CH_mod = []
        for bad_ch in self.BAD_CH:
            BAD_CH_mod.append((bad_ch.reshape([self.GRID_X, self.GRID_Y]).T)[::-1,:])
        self.PAIR_BAD_CH = [np.logical_or(BAD_CH_mod[0], BAD_CH_mod[1]), np.logical_or(BAD_CH_mod[0], BAD_CH_mod[2])]

    
    
    def _prediction_score_calculation(self):
        for pair in self.PAIRS:
            i = pair[0]
            j = pair[1]
            print('Calculating prediction score for pair', pair)
            # create dependent variable
            y = np.vstack((np.ones((self.ECOG[i].shape[0],1))*self.VALS[i],
                           np.ones((self.ECOG[j].shape[0],1))*self.VALS[j]))[::self.DEC]
                           
            res_r2 = np.zeros((self.ECOG[i].shape[1],len(self.fbandmins)))
            res_p = np.ones((self.ECOG[i].shape[1],len(self.fbandmins)))
            

            if not self.use_interval:
                for ch in range(self.ECOG[i].shape[1]):
                    if (self.BAD_CH[i][ch] | self.BAD_CH[j][ch]):
                        res_r2[ch,:] = 0
                        res_p[ch,:]  = 1
                    else:
                        ecog_i = np.zeros((self.ECOG[i].shape[0],1));
                        ecog_i[:,0] = np.copy(self.ECOG[i][:,ch]);
                        ecog_j = np.zeros((self.ECOG[j].shape[0],1));
                        ecog_j[:,0] = np.copy(self.ECOG[j][:,ch]);
                        ecog_concat = np.vstack((ecog_i,ecog_j));
                        for f in range(len(self.fbandmins)):
                            fbandmin = self.fbandmins[f]
                            fbandmax = self.fbandmaxs[f]
                            x = self._filterEMG(ecog_concat, fbandmin, fbandmax, self.SRATE[0])[::self.DEC]
                            scaler = MinMaxScaler([-1, 1])
                            scaler.fit(x)
                            x = scaler.transform(x)    
                            slope, intercept, r_value_1, p_value, std_err = stats.linregress(x[:,0], y[:,0]);
                            res_r2[ch,f] = r_value_1**2 if r_value_1 >0 else 0;
                            res_p[ch,f]  = p_value;
            
            #----#
            else:
                for ch in range(self.ECOG[i].shape[1]):
                    if( self.BAD_CH[i][ch] | self.BAD_CH[j][ch] ):
                        res_r2[ch,:] = 0;
                        res_p[ch,:]  = 1;
                    else:
                        ecog_i = np.zeros((self.ECOG[i].shape[0],1));
                        ecog_i[:,0] = np.copy(self.ECOG[i][:,ch]);
                        ecog_j = np.zeros((self.ECOG[j].shape[0],1));
                        ecog_j[:,0] = np.copy(self.ECOG[j][:,ch]);
                        stim_i = np.zeros((self.STIM[i].shape[0],1));
                        stim_j = np.zeros((self.STIM[j].shape[0],1));
                        stim_i[:,0]      = np.copy(self.STIM[i]); 
                        stim_j[:,0]      = np.copy(self.STIM[j]); 
                        
                        ecog_concat = np.vstack((ecog_i,ecog_j));
                        #stim_concat = np.vstack((stim_i,stim_j));
                        
                        ind_stim_i = np.argwhere(stim_i[:,0]==1)[:,0];
                        ind_stim_j = np.argwhere(stim_j[:,0]==1)[:,0];
                        
                        # find indices around stimulus onset
                        if( (ind_stim_i.shape[0]==0) & (ind_stim_j.shape[0]==0)):
                            ind = range(0,ecog_concat.shape[0]);
                        elif((ind_stim_i.shape[0]==0) & (ind_stim_j.shape[0]!=0)):
                            indj = np.zeros(0);
                            for k  in ind_stim_j:
                                indj = np.append(indj, np.array(range( k+int(self.INTERVAL_START*self.SRATE[0]),k+int(self.INTERVAL_STOP*self.SRATE[0]))));
                            indi = np.array(range(0,min(ecog_i.shape[0],indj.shape[0])));
                        elif((ind_stim_i.shape[0]!=0) & (ind_stim_j.shape[0]==0)):      
                            indi = np.zeros(0);
                            for k  in ind_stim_i:
                                indi = np.append(indi, np.array(range( k+int(self.INTERVAL_START*self.SRATE[0]),k+int(self.INTERVAL_STOP*self.SRATE[0] ))));
                            indj = np.array(range(0,min(ecog_j.shape[0],indi.shape[0])));
                        else:
                            indj = np.zeros(0);
                            for k  in ind_stim_j:
                                indj = np.append(indj, np.array(range( k+int(self.INTERVAL_START*self.SRATE[0]),k+int(self.INTERVAL_STOP*self.SRATE[0]))));
                            indi = np.zeros(0);
                            for k  in ind_stim_i:
                                indi = np.append(indi, np.array(range( k+int(self.INTERVAL_START*self.SRATE[0]),k+int(self.INTERVAL_STOP*self.SRATE[0]))));
                           
                            indj = np.array(range(0,min(ecog_j.shape[0],indi.shape[0])));
                
                        # cast as it
                        indi  = indi.astype(int);
                        indj = indj.astype(int);
                   
        
                        for f in range(len(self.fbandmins)):
                            fbandmin = self.fbandmins[f]
                            fbandmax = self.fbandmaxs[f]
                            
                            xi = self._filterEMG(ecog_i,fbandmin,fbandmax,self.SRATE[0])[indi]
                            xj = self._filterEMG(ecog_j,fbandmin,fbandmax,self.SRATE[0])[indj]
                            x = np.vstack((xi,xj));
                           
                            y = np.vstack((np.ones((xi.shape[0],1))*self.VALS[i],
                               np.ones((xj.shape[0],1))*self.VALS[j]));
                
                            
                            scaler = MinMaxScaler([-1, 1])
                            scaler.fit(x)
                            x = scaler.transform(x)    
                            slope, intercept, r_value_1, p_value, std_err = stats.linregress(x[:,0], y[:,0]);
                            res_r2[ch,f] = r_value_1**2 if r_value_1 >0 else 0;
                            res_p[ch,f]  = p_value;
            #---#


            self.PAIR_P.append(res_p);
            self.PAIR_R2.append(res_r2);


    def calculate(self):
        self._data_process()
        self._prediction_score_calculation()

    def plot_results(self):
        plt.close('all');        
        fig, ax = plt.subplots(nrows = len(self.PAIR_R2),
                               ncols = self.PAIR_R2[0].shape[1],
                               figsize=(12,8))
        row_titles = ['R^2 actions', 'R^2 objects', '50Hz']
        col_titles = ['rest', 'action', 'object']
        
        viridis_cm = plt.cm.get_cmap('viridis', 256)
        viridis_cm.set_bad('black', 1)
        
        for i in range(2):
            for b in range(self.PAIR_R2[i].shape[1]):
                plt.subplot(3,self.PAIR_R2[i].shape[1],(i)*self.PAIR_R2[i].shape[1] + (b+1))  
                im  = (self.PAIR_R2[i][:,b].reshape([self.GRID_X, self.GRID_Y]).T)[::-1,:];
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
            plt.subplot(3,self.PAIR_R2[0].shape[1], self.PAIR_R2[0].shape[1]*2 + (b+1))
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
        plt.show()


if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read(Path('display.py').resolve().parents[1]/'util/custom_config_processing.ini')
    dp = DataProcessing(config)
    dp.calculate()
    dp.plot_results()

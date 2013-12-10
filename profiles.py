# Script to generate depth vs. [data] profiles for data
# from the Occoquan Reservoir lab. 

import os
import matplotlib.pyplot as plt
import traceback

def load_data(textfile, station_field='STA', date_field='DATE2', sep='\t', nodata = 'NULL'):
    
    # Load data from profiles.txt.
    # Hierarchy:
    # {data_dict}
    #   - 'RE02':{} (STA)
    #       - '1/28/2010':{} (DATE2)
    #           - 'DEPTH':      [1, 2, 4, ...]
    #           - 'DO':         [12.1, 12.1, 12, ...]
    #           - 'ORP':        [506, 504, 503, ...]
    #           - 'FIELDPH':    [7.1, 7.1, 7.1, ...]
    #           - 'COND25':     [326, 325, 325, ...]
    #           - 'FIELDNO3':   [1.04, 1.04, 1.04, ...]


    file_open = open(textfile)
    lineno = 1
    header_dict = {}
    data_dict = {}
    
    for line in file_open:
        
        # Process header row
        if lineno == 1:
            header = line.strip().split(sep)
            
            for index in range(0, len(header)):
                column_name = header[index]
                header_dict[column_name] = index
        
        # Process all other rows
        else:
            data = line.strip().split(sep)
            
            # Reformat data - set 'None' values and convert to floats.
            for index in range(0, len(data)):
                value = data[index]
                
                if value == nodata:
                    data[index] = None
                
                else:
                    try:
                        data[index] = float(value)
                    except:
                        None
            
            station = data[header_dict[station_field]]
            date = data[header_dict[date_field]]
            
            if data_dict.has_key(station) == False:
                data_dict[station] = {}
                
            if data_dict[station].has_key(date) == False:
                data_dict[station][date] = {}
            
            for column in header_dict.keys():
                if column!=station_field and column!=date_field:
                    if data_dict[station][date].has_key(column) == False:
                        data_dict[station][date][column] = [data[header_dict[column]]]
                    else:
                        data_dict[station][date][column].append(data[header_dict[column]])
        
        lineno += 1
                
    file_open.close()
    return data_dict, header_dict

    
def create_output_dir(data, fields, directory):
    os.mkdir(directory)
    
    # Create station folders
    for station in data.keys():
        os.mkdir(os.path.join(directory, station))
        
        # Create subfolders for each field (TEMP, DO, etc.)
        for field in fields:
            os.mkdir(os.path.join(directory, station, field))        

            
def __reformat_date__(date):
    split_date = date.strip().split('/')
    
    year = split_date[2]
    month =  split_date[0]
    day = split_date[1]
    
    if len(month) == 1:
        month = '0' + month
    
    if len(day) == 1:
        day = '0' + day
        
    reformatted = year + month + day
    return reformatted
    

def plot_data(data, depth_field, format_dict, output_dir):
    
    stations = os.listdir(output_dir)
    for station in stations:
        print station
        
        for date in data[station].keys():
            date_reformatted = __reformat_date__(date)
            
            fields = os.listdir(os.path.join(output_dir, station))
            for field in fields:
                
                try:
                    # Plot greyed-out profiles for other stations
                    for station2 in stations:
                        if station2 != station:
                            x_data = data[station2][date][field]
                            y_data = data[station2][date][depth_field]
                            plt.plot(x_data, y_data, color='0.8')                    
                    
                    # Plot profile for this station
                    x_data = data[station][date][field]
                    y_data = data[station][date][depth_field]
                    plt.plot(x_data, y_data, color='0.0')
                    
                    # Y-axis formatting
                    plt.gca().invert_yaxis()
                    plt.ylabel('Depth (ft)')
                    plt.gca().set_ylim(60, 0)
                    
                    # X-axis formatting
                    plt.xlabel(format_dict[field]['label'])                    
                    x_min = format_dict[field]['min']
                    x_max = format_dict[field]['max']
                    plt.gca().set_xlim(x_min, x_max)
                    
                    plt.title(station + ' ' + field + ' ' + date)
                    
                    # Save; clear figure
                    filename = station + "_" + field + "_" + date_reformatted + '.png'
                    plt.savefig(os.path.join(output_dir, station, field, filename))
                    plt.clf()
                
                except:
                    print 'error: ', station, date, field
                    traceback.print_exc()
                    print '\n'

                    
def plot_data_allstations(data, depth_field, format_dict, output_dir):
    
    stations = data.keys()
    stations.sort()

    dates = data[stations[0]].keys()
    
    fields = format_dict.keys()
    for field in fields:
        print field
        os.mkdir(os.path.join(output_dir, field))
        
        for date in dates:
            date_reformatted = __reformat_date__(date)
            
            for station in stations:
                
                # Plot profile for each station
                x_data = data[station][date][field]
                y_data = data[station][date][depth_field]
                plt.plot(x_data, y_data)
                
            # Y-axis formatting
            plt.gca().invert_yaxis()
            plt.ylabel('Depth (ft)')
            plt.gca().set_ylim(60, 0)
            
            # X-axis formatting
            plt.xlabel(format_dict[field]['label'])                    
            x_min = format_dict[field]['min']
            x_max = format_dict[field]['max']
            plt.gca().set_xlim(x_min, x_max)
            
            # Legend
            plt.legend(stations, loc=4)
            
            plt.title(field + ' ' + date)
            
            # Save; clear figure
            filename = field + "_" + date_reformatted + '.png'
            plt.savefig(os.path.join(output_dir, field, filename))
            plt.clf()
        
                
if __name__ == '__main__':

    textfile = 'C:/dev/python/cee5134termproj/profiles.txt'
    data, header = load_data(textfile)
    
    output_dir = r'C:\temp\cee5134\profile_plots'
    output_fields = ['DO', 'ORP', 'FIELDPH', 'TEMP', 'COND25', 'FIELDNO3', 'DOSAT']
    formatting = {'DO':{'min':0, 'max':25, 'label':'Dissolved Oxygen (mg/L)'},
                  'ORP':{'min':0, 'max':1000, 'label':'Oxidation-Reduction Potential (mV)'},
                  'FIELDPH':{'min':6, 'max':10, 'label':'pH'},
                  'TEMP':{'min':0, 'max':35, 'label':'Temperature (deg. C)'},
                  'COND25':{'min':100, 'max':900, 'label':r'Conductivity ($\mu$S/cm)'},
                  'FIELDNO3':{'min':0, 'max':12, 'label':'Nitrate Concentration (mg/l)'},
                  'DOSAT':{'min':0, 'max':200, 'label':'Dissolved Oxygen Saturation (%)'}}
    # create_output_dir(data, output_fields, output_dir)
    # plot_data(data, 'DEPTH', formatting, output_dir)
    plot_data_allstations(data, 'DEPTH', formatting, output_dir)
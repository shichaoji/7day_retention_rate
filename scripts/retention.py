
# coding: utf-8


import pandas as pd
from time import time
from pandas.tseries.offsets import Day
day7=Day(7)



def load_data(path):
    global data, data_all

    start=time()

    # Choose to not parse the index col
    data=pd.read_csv(path,index_col='event_time',parse_dates=True,usecols=[1,2,3,4,5])
    data=data.sort_index()
    # Can not be sure 'SHOT_RECORDED' is informative, if I treat it like "OPEN", cannot guarantee the user actually played, 
    # so thoses records are removed 
    data=data[data['event_name']!='SHOT_RECORDED']

    # Can not be sure 'APP_CLOSED' is informative in this specific task.
    # Cannot treat them as "OPEN" status and assumes the app was just opened minutes ago but not recoreded.
    # Since an 'APP_CLOSED' status may imply the app was opened more than 7 days ago, 
    # I myself sometime have apps backgrounded for weeks. 
    data=data[data['event_name']!='APP_CLOSED']

    # Since now 'event_name' feature has only one category 'APP_OPEN', it can be dropped
    data=data.drop('event_name',axis=1)        

    # keep date only, since the specific time is not matter in this particular task
    data.index=pd.to_datetime(data.index.date)
    
    print 'used: {:.2f}s'.format(time()-start)
    print 'from ',data.index[0].strftime('%Y-%m-%d'), 'to ',data.index[-1].strftime('%Y-%m-%d')
    print len(data), 'records'

    data_all=data.copy()


def get_filltered_data():
    return data

def get_all_data():
    return data_all


class Date_info():
    
    """from date (integer): month,day(,2016): """
    def __init__(self, date):

        self.all_data=data_all
        
        self.data=data
         
        self.date=self.process_date(date)
        
        
        self.day1=self.date.strftime('%Y-%m-%d')
        self.day7=(self.date+day7).strftime('%Y-%m-%d')
        
        self.history_dic=self.history()
        self.day1_data=self.newusers_day1()
        self.day7_data=self.match_day7()
        self.match=self.matched()
        
        self.stat=self.calculate()
        
    def process_date(self, date):
        
        if type(date)==str:
            try:
                date=date.replace('-','/')
            except:
                pass

            if date.count('/')==1: 
                date+='/2016'

            month, day, year = date.strip().split('/')
            month=int(month.strip());day=int(day.strip()); year=int(year.strip())

            return pd.datetime(year,month,day)
        
        return date
        
    def history(self):
        """get unique userIDs before the specific date"""
        df=self.all_data[:self.day1].drop(self.all_data[self.day1:self.day1].index)
        df_dic=df['user_id'].value_counts().to_dict()
        return df_dic
    
    def judge(self,user_id):
        
        """helper function for deciding if a user_id appears in the dictionary contains historical data"""

        try:
            self.history_dic[user_id]
            return False
        except:
            return True
    
    def newusers_day1(self):
        data=self.data[self.day1:self.day1].drop_duplicates()
        data.ix[:,'date']=data.index
        data.index=data['user_id']
        data=data.drop('user_id',axis=1)
        
        data=data[data.index.map(self.judge)]
        return data
                
    def match_day7(self):
        data=self.data[self.day7:self.day7].drop_duplicates()
        data.ix[:,'date']=data.index
        data.index=data['user_id']
        data=data.drop('user_id',axis=1)
        
        return data
    
    def matched(self):
        match=pd.merge(self.day1_data,self.day7_data,left_index=True,right_index=True)
        return match
        
    def calculate(self):
        stat={'day1_no':len(self.day1_data),
                 'day7_no':len(self.day7_data),
             'matched':len(self.match)}
        return stat
    


    
    def __str__(self):
        """day1 new users, day7 unique users, day7 matched users """
        return "day1 new     user No.: {}\nday7 unique  user No.: {} \nday7 matched user No.: {}".format(len(self.day1_data)
                                            ,len(self.day7_data),len(self.match))



def analyze():
    global statistics
    
    


    
    start=time()
    
    period=data_all.index.unique()
    statistics=pd.DataFrame(period,columns=['date'])

    
    statistics['instance']=statistics['date'].apply(Date_info)

    print 'used: {:.2f}s'.format(time()-start)

    statistics['day1']=statistics['instance'].apply(lambda x:x.stat['day1_no'])
    statistics['day7']=statistics['instance'].apply(lambda x:x.stat['day7_no'])
    statistics['matched']=statistics['instance'].apply(lambda x:x.stat['matched'])
    statistics.index=statistics['date']
    statistics=statistics.drop(['instance','date'],axis=1)
    statistics['single_day_retention']=statistics['matched']/statistics['day1']

    try:
        retention=float(statistics['matched'].sum())/statistics['day1'].sum()
    except:
        retention=0
        print 'retention rate is 0'


    print 'during {} days period between {} and {}'.format((period[-1]-period[0]).days+1,
                                                    period[0].strftime('%Y-%m-%d'),period[-1].strftime('%Y-%m-%d'))
    print 'The overall 7 days retention rate is {:.2f}%'.format(retention*100)
    print 'call get_stat_df() to get details, which will return a DataFrame'
    print 'call interval_rate("start_date","end_date") for 7-day retention rate of specific time period'




date=()
def filter_data(*X):
    """filter data by 'os' (and 'version'), pass nothing will reset dataset to origial"""
    global data
    data=data_all.copy()
    if len(X)==2:
        data=data[data['os_name']==X[0]]
        data=data[data['app_version']==X[1]]
        print 'filtered by %s, %s'%X
        print str(data.shape[0]) + ' records'
    elif len(X)==1:  
        data=data[data['os_name']==X[0]]
        print 'filtered by %s'%X
        print str(data.shape[0]) + ' records'
    elif len(X)==0:
        print 'reset dataset'
    else:
        print 'input format "os","version",or filter_data() to reset'
        


def get_stat_df():
    return statistics



def interval_rate(*date):
    global plot_df
    if len(date)==0:      
        if statistics['day1'].sum()==0:
            plot_df=statistics.copy()
            return 0
        else:
            plot_df=statistics.copy()
            return statistics['matched'].sum()/float(statistics['day1'].sum())
    elif len(date)==2:
        
        stat=statistics.loc[date[0]:date[1],:]
        if stat['day1'].sum()==0:
           plot_df=stat.copy() 
           return 0
        else:
            plot_df=stat.copy()
            return stat['matched'].sum()/float(stat['day1'].sum())
    else:
        print 'input format "mm-dd-yy","mm-dd-yy" (start, end),or do not pass anything for the entire time interval'
    
            
    




def plotting(*name):
    
    
    try:
        df=plot_df.copy()
    except:
        print 'run interval_rate() first'
        return 
    
    from bokeh.io import output_file, output_notebook, show
    from bokeh.charts import Line
    from bokeh.layouts import row, column


    
    


    p=Line(df[['day1','day7','matched']],plot_width=950,plot_height=400,legend='top_right')
#    q=Line(df[['matched']],plot_width=950,plot_height=400,color='blue')
    r=Line(df[['single_day_retention']],plot_width=950,plot_height=400,color='purple')
    layout=column(p,r)
    
    if len(name)>0:
        output_file(name[0]+'.html')
        show(layout)
    else:
        output_notebook()
        show(layout)
        
    







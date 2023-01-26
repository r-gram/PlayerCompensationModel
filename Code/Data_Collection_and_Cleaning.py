import pandas as pd
import numpy as np
import time

#Read in data
def draft_2017():
    draft2017DF = pd.read_csv("../Data/NFL_2017_Draft.csv")
    return draft2017DF
def salaries_2017():
    salaries2017DF = pd.read_csv("../Data/NFL_2017_Player_Salaries.csv")
    return salaries2017DF

#Get only player, team, and their salary
def clean_sal():
	temp = salaries_2017()
	salaries2017 = temp[['Player', 'Tm', 'Cap Hit']]
	return salaries2017

def rename_draft():
    temp = draft_2017()
    #Rename Columns
    #Rnd=Draft Round, Pick=Overall Pick, Tm=Team, Player, Pos=Position, 
    #Age, To=Stats up to, AP1=First team all-pro, PB=Pro Bowl, St=Number of years as starter, 
    #G=games played, Cmp=passes completed, Att=passes attempted, Yds=passing yards, TD=passing tds, 
    #Int=ints thrown, Att.1=rushing attempts, Yds.1=rushing yrds, TD.1=rushing tds, Rec=receptions,
    #Yds.2=rec yards, TD.2=rec tds, Solo=solo tackles, Int.1=defensive int, Sk=sacks, -9999=unique id
    draft2017 = temp.rename(columns={'Rnd': 'Rnd', 'Pick': 'Pick', 'Tm': 'Tm', 'Player': 'Player', 'Pos': 'Pos', 'Age': 'Age', 'To': 'To', 'AP1': 'AP1', 'PB': 'PB', 'St': 'St', 'G': 'G', 'Cmp': 'Cmp', 'Att': 'PassAtt', 'Yds': 'PassYds', 'TD': 'PassTD', 'Int': 'PassInt', 'Att.1': 'RushAtt', 'Yds.1': 'RushYds', 'TD.1': 'RushTD', 'Rec': 'Rec', 'Yds.2': 'RecYds', 'TD.2': 'RecTD', 'Solo': 'DefSolo', 'Int.1': 'DefInt', 'Sk': 'DefSk', '-9999': 'id'})
    return draft2017
def rename_salary():
    temp = clean_sal()
    salaries2017 = temp.rename(columns={'Cap Hit': 'BaseSal'})
    return salaries2017

def joinDraftAndSalaries():
    draft2017 = rename_draft()
    salaries2017 = rename_salary()
    #Get 2017 Draft class salaries
    joinLeft = pd.merge(left=draft2017, right=salaries2017, how='left', left_on=['Player', 'Tm'], right_on=['Player', 'Tm'])
    return joinLeft

def saveDaS():
    return joinDraftAndSalaries().to_csv('Draft&Salaries2017.csv', index=False)
    #Some Salaries were not complete so the missing values were manually added

#Get the id of drafted players
def getPlayerID(pos):
    df = rename_draft()
    players = df.loc[df['Pos'] == pos]
    player_ids = list(players['id'])
    return player_ids

#Scrape PFR for QB regular season stats
def scrapePFR_QBs_Reg():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    QBs = getPlayerID('QB')
    #Make the DataFrame with QB stats
    QB_DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', 'P_Cmp', 'P_Att', 'P_Cmp%', 'P_Yds', 'P_TD', 'P_Int', 'P_Rate', 'P_Sk', 'P_SkYd', 'P_Y/A', 'P_AY/A',
                                         'R_Att', 'R_Yds', 'R_Y/A', 'R_TD',
                                         'F_Fmb', 'F_Fl', 'F_FF', 'F_FR', 'F_Yds', 'F_TD',
                                         'Snap%'])
    #Do the web scraping
    for yr in years:
        for qb in QBs:
            try:
                time.sleep(2)
                full_url = url_head + qb + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if 'Passing' in df.columns:
                    passing_stats = df[[('Passing', 'Cmp'), ('Passing', 'Att'), ('Passing', 'Cmp%'), ('Passing', 'Yds'), ('Passing', 'TD'), ('Passing', 'Int'), ('Passing', 'Rate'), ('Passing', 'Sk'), ('Passing', 'Yds.1'), ('Passing', 'Y/A'), ('Passing', 'AY/A')]]
                    passing_stats.insert(0, 'Pos', 'QB')
                    passing_stats.insert(0, 'Year', yr)
                    passing_stats.insert(0, 'Player', qb)
                    passing_stats = list(passing_stats.iloc[-1])
                else:
                    passing_stats = [qb, yr, 'QB', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Rushing' in df.columns:
                    rushing_stats = df[[('Rushing', 'Att'), ('Rushing', 'Yds'), ('Rushing', 'Y/A'), ('Rushing', 'TD')]]
                    rushing_stats = list(rushing_stats.iloc[-1])
                else:
                    rushing_stats = [np.nan, np.nan, np.nan, np.nan]
                if 'Fumbles' in df.columns:
                    fumble_stats = df[[('Fumbles', 'Fmb'), ('Fumbles', 'FL'), ('Fumbles', 'FF'), ('Fumbles', 'FR'), ('Fumbles', 'Yds'), ('Fumbles', 'TD')]]
                    fumble_stats = list(fumble_stats.iloc[-1])
                else:
                    fumble_stats = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Off. Snaps' in df.columns:
                    if 'Did Not Play' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    snapPct_stats = df[[('Off. Snaps', 'Pct')]]
                    snapPct_stats = pd.DataFrame(snapPct_stats[('Off. Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    snapPct = [snapPct_stats[('Off. Snaps', 'Pct')].mean()]
                else:
                    snapPct = [np.nan]
                stats = passing_stats + rushing_stats + fumble_stats + snapPct
                QB_DataFrame.loc[len(QB_DataFrame.index)] = stats
            except ImportError:
                time.sleep(2)
                stats = [qb, yr, 'QB', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                QB_DataFrame.loc[len(QB_DataFrame.index)] = stats
    #Save DF as .csv
    return QB_DataFrame.to_csv('QB_DataFrame.csv', index=False)

'''
def scrapePFR_RBs_Reg():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)
'''

def scrapePFR_WRs_Reg():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    WRs = getPlayerID('WR')
    #Make the DataFrame with WR stats
    WR_DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', 'Rec_Tgt', 'Rec_Rec', 'Rec_Yds', 'Rec_Y/R', 'Rec_TD', 'Rec_Ctch%', 'Rec_Y/Tgt',
                                         'Rus_Att', 'Rus_Yds', 'Rus_Y/A', 'Rus_TD',
                                         'F_Fmb', 'F_Fl', 'F_FF', 'F_FR', 'F_Yds', 'F_TD',
                                         'Snap%'])
    #Do the web scraping
    for yr in years:
        for wr in WRs:
            try:
                time.sleep(2)
                full_url = url_head + wr + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if 'Receiving' in df.columns:
                    receiving_stats = df[[('Receiving', 'Tgt'), ('Receiving', 'Rec'), ('Receiving', 'Yds'), ('Receiving', 'Y/R'), ('Receiving', 'TD'), ('Receiving', 'Ctch%'), ('Receiving', 'Y/Tgt')]]
                    receiving_stats.insert(0, 'Pos', 'WR')
                    receiving_stats.insert(0, 'Year', yr)
                    receiving_stats.insert(0, 'Player', wr)
                    receiving_stats = list(receiving_stats.iloc[-1])
                else:
                    receiving_stats = [wr, yr, 'WR', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Rushing' in df.columns:
                    rushing_stats = df[[('Rushing', 'Att'), ('Rushing', 'Yds'), ('Rushing', 'Y/A'), ('Rushing', 'TD')]]
                    rushing_stats = list(rushing_stats.iloc[-1])
                else:
                    rushing_stats = [np.nan, np.nan, np.nan, np.nan]
                if 'Fumbles' in df.columns:
                    fumble_stats = df[[('Fumbles', 'Fmb'), ('Fumbles', 'FL'), ('Fumbles', 'FF'), ('Fumbles', 'FR'), ('Fumbles', 'Yds'), ('Fumbles', 'TD')]]
                    fumble_stats = list(fumble_stats.iloc[-1])
                else:
                    fumble_stats = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Off. Snaps' in df.columns:
                    if 'Did Not Play' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    snapPct_stats = df[[('Off. Snaps', 'Pct')]]
                    snapPct_stats = pd.DataFrame(snapPct_stats[('Off. Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    snapPct = [snapPct_stats[('Off. Snaps', 'Pct')].mean()]
                else:
                    snapPct = [np.nan]
                stats = receiving_stats + rushing_stats + fumble_stats + snapPct
                WR_DataFrame.loc[len(WR_DataFrame.index)] = stats
            except ImportError:
                time.sleep(2)
                stats = [wr, yr, 'WR', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                WR_DataFrame.loc[len(WR_DataFrame.index)] = stats
    #Save DF as .csv
    return WR_DataFrame.to_csv('WR_DataFrame.csv', index=False)

'''
def scrapePFR_TEs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_Gs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_Cs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_OLs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_FBs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_Ks():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_DEs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_Ss():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)
'''
'''
def scrapePFR_CBs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[('Defense', 'Int'), ('Defense', 'Targets'), ('Defense', 'Completions'), ('Defense', 'Comp %'), ('Defense', 'Rec. Yds'), ('Defence', 'Yds/Comp')
                                ('Defense', 'TD'), ('Defence', 'Passer Rating'), ('Defense', 'Blitzes'), ('Defense', 'QB Hurries'), ('Defense', 'QB Knockdowns'), ('Defense', 'Batted Passes')
                                ('Defense', 'Pressures'), ('Defense', 'Missed Tackles'), ('Defense', 'Missed Tackle %')]]
                    stats.insert(0, 'Pos', 'CB')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', CB)
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)
'''
'''
def scrapePFR_LBs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_Ts():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_OLBs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_DTs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_DBs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_ILBs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_DLs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_LSs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    s = getPlayerID('')
    #Make the DataFrame with  stats
    _DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', ])
    #Do the web scraping
    for yr in years:
        for  in s:
            try:
                full_url = url_head +  + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', '')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', )
                    list_stats = list(stats.iloc[-1])
                    _DataFrame.loc[len(_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return _DataFrame.to_csv('_DataFrame.csv', index=False)

def scrapePFR_NTs():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    NTs = getPlayerID('NT')
    #Make the DataFrame with  stats
    NT_DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos'])
    #Do the web scraping
    for yr in years:
        for nt in NTs:
            try:
                full_url = url_head + nt + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[[]]
                    stats.insert(0, 'Pos', 'NT')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', nt)
                    list_stats = list(stats.iloc[-1])
                    NT_DataFrame.loc[len(NT_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return NT_DataFrame.to_csv('NT_DataFrame.csv', index=False)
'''

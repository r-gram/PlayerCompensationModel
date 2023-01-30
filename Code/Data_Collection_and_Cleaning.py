import pandas as pd
import numpy as np
import time

#Read in data
'''
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
'''

def getDraftClass():
    #Creat variables
    url_head = 'https://www.pro-football-reference.com/years/'
    years = [str(yr) for yr in range(2000, 2019)]
    Draft_DataFrame = pd.DataFrame(columns=['Rnd', 'Pick', 'Tm', 'Player', 'Pos', 'Year'])

    for yr in years:
        try:
            time.sleep(2)
            full_url = url_head + yr + '/draft.htm'
            df = pd.read_html(full_url)[0]
            df.columns = df.columns.get_level_values(0)
            df = df[['Unnamed: 0_level_0', 'Unnamed: 1_level_0', 'Unnamed: 2_level_0', 'Unnamed: 3_level_0', 'Unnamed: 4_level_0']]
            df = df.rename(columns={"Unnamed: 0_level_0": "Rnd", "Unnamed: 1_level_0": "Pick", "Unnamed: 2_level_0": "Tm", "Unnamed: 3_level_0": "Player", "Unnamed: 4_level_0": "Pos"})
            df = df[df.Rnd != 'Rnd']
            df['Player'] = df['Player'].map(lambda x: x.rstrip(' HOF'))
            df['Year'] = yr
            Draft_DataFrame = pd.concat([Draft_DataFrame, df], ignore_index=True)
        except ImportError:
            time.sleep(2)
    return Draft_DataFrame.to_csv('Draft_DataFrame.csv', index=False)


def listDraftedPlayers(pos, year):
    draftedPlayers = pd.read_csv("../Data/Draft_DataFrame.csv")
    draftedPlayers = draftedPlayers.loc[(draftedPlayers['Pos'] == pos) & (draftedPlayers['Year'] == year)]
    players = draftedPlayers['Player'].tolist()
    return players


def scrapeQB_Stats():
    url_head = 'https://www.pro-football-reference.com/years/'
    years = [str(yr) for yr in range(2000, 2019)]
    QB_DataFrame = pd.DataFrame(columns=['Rk', 'Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'QBrec', 'Cmp', 'Att',
                                         'Cmp%', 'Yds', 'TD', 'TD%', 'Int', 'Int%', '1D', 'Lng', 'Y/A', 'AY/A',
                                         'Y/C', 'Y/G', 'Rate', 'Sk', 'Yds.1', 'Sk%', 'NY/A', 'ANY/A', '4QC', 'GWD', 'Year'])
    for yr in years:
        players = listDraftedPlayers('QB', int(yr))
        for year in range(int(yr), int(yr)+4):
            try:
                time.sleep(2)
                full_url = url_head + str(year) + '/passing.htm'
                df = pd.read_html(full_url)[0]
                df['Player'] = df['Player'].map(lambda x: x.rstrip('*+'))
                df = df.loc[df['Player'].isin(players)]
                df['Year'] = str(year)
                if 'QBR' in df.columns:
                    df = df.drop('QBR', axis=1)
                QB_DataFrame = pd.concat([QB_DataFrame, df])
            except ImportError:
                time.sleep(2)
    QB_DataFrame['QBrec'] = QB_DataFrame['QBrec'].fillna('0-0-0')
    QB_DataFrame['Win'] = QB_DataFrame['QBrec'].str.split('-').str[0]
    QB_DataFrame['Loss'] = QB_DataFrame['QBrec'].str.split('-').str[1]
    QB_DataFrame['Tie'] = QB_DataFrame['QBrec'].str.split('-').str[2]
    QB_DataFrame = QB_DataFrame.drop('QBrec', axis=1)
    QB_DataFrame = QB_DataFrame.fillna('0')
    QB_DataFrame = QB_DataFrame.astype({'Rk': 'int', 'Player': 'object', 'Tm': 'object', 'Age': 'int', 'Pos': 'object', 'G': 'int', 'GS': 'int', 'Win': 'int', 'Loss': 'int', 'Tie': 'int',
                                        'Cmp': 'int', 'Att': 'int', 'Cmp%': 'float', 'Yds': 'int', 'TD': 'int', 'TD%': 'float', 'Int': 'int', 'Int%': 'float', '1D': 'int', 'Lng': 'int', 'Y/A': 'float', 'AY/A': 'float',
                                        'Y/C': 'float', 'Y/G': 'float', 'Rate': 'float', 'Sk': 'int', 'Yds.1': 'int', 'Sk%': 'float', 'NY/A': 'float', 'ANY/A': 'float', '4QC': 'int', 'GWD': 'int', 'Year': 'object'})
    agg_functions = {'Rk': 'mean', 'Tm': 'last', 'Age': 'last', 'Pos': 'last', 'G': 'sum', 'GS': 'sum', 'Win': 'sum', 'Loss': 'sum', 'Tie': 'sum',
                     'Cmp': 'sum', 'Att': 'sum', 'Cmp%': 'mean', 'Yds': 'sum', 'TD': 'sum', 'TD%': 'mean', 'Int': 'sum', 'Int%': 'mean', '1D': 'sum', 'Lng': 'mean', 'Y/A': 'mean', 'AY/A': 'mean',
                     'Y/C': 'mean', 'Y/G': 'mean', 'Rate': 'mean', 'Sk': 'sum', 'Yds.1': 'sum', 'Sk%': 'mean', 'NY/A': 'mean', 'ANY/A': 'mean', '4QC': 'sum', 'GWD': 'sum', 'Year': 'last'}
    QB_DataFrame = QB_DataFrame.groupby(QB_DataFrame['Player']).aggregate(agg_functions)
    return QB_DataFrame.to_csv('QB_DataFrame.csv', index=True)

'''
def scrapeRB_Stats():
    url_head = 'https://www.pro-football-reference.com/years/'
    years = [str(yr) for yr in range(2000, 2019)]
    RB_DataFrame = pd.DataFrame(columns=[#'Rk', 'Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'QBrec', 'Cmp', 'Att',
                                         #'Cmp%', 'Yds', 'TD', 'TD%', 'Int', 'Int%', '1D', 'Lng', 'Y/A', 'AY/A',
                                         ])#'Y/C', 'Y/G', 'Rate', 'Sk', 'Yds.1', 'Sk%', 'NY/A', 'ANY/A', '4QC', 'GWD', 'Year'])
    for yr in years:
        players = listDraftedPlayers('RB', int(yr))
        for year in range(int(yr), int(yr)+4):
            try:
                time.sleep(2)
                full_url = url_head + str(year) + '/rushing.htm'
                df = pd.read_html(full_url)[0]
                df['Player'] = df['Player'].map(lambda x: x.rstrip('*+'))
                df = df.loc[df['Player'].isin(players)]
                df['Year'] = str(year)
                #if 'QBR' in df.columns:
                #    df = df.drop('QBR', axis=1)
                RB_DataFrame = pd.concat([RB_DataFrame, df])
            except ImportError:
                time.sleep(2)
    QB_DataFrame['QBrec'] = QB_DataFrame['QBrec'].fillna('0-0-0')
    QB_DataFrame['Win'] = QB_DataFrame['QBrec'].str.split('-').str[0]
    QB_DataFrame['Loss'] = QB_DataFrame['QBrec'].str.split('-').str[1]
    QB_DataFrame['Tie'] = QB_DataFrame['QBrec'].str.split('-').str[2]
    QB_DataFrame = QB_DataFrame.drop('QBrec', axis=1)
    QB_DataFrame = QB_DataFrame.fillna('0')
    QB_DataFrame = QB_DataFrame.astype({'Rk': 'int', 'Player': 'object', 'Tm': 'object', 'Age': 'int', 'Pos': 'object', 'G': 'int', 'GS': 'int', 'Win': 'int', 'Loss': 'int', 'Tie': 'int',
                                        'Cmp': 'int', 'Att': 'int', 'Cmp%': 'float', 'Yds': 'int', 'TD': 'int', 'TD%': 'float', 'Int': 'int', 'Int%': 'float', '1D': 'int', 'Lng': 'int', 'Y/A': 'float', 'AY/A': 'float',
                                        'Y/C': 'float', 'Y/G': 'float', 'Rate': 'float', 'Sk': 'int', 'Yds.1': 'int', 'Sk%': 'float', 'NY/A': 'float', 'ANY/A': 'float', '4QC': 'int', 'GWD': 'int', 'Year': 'object'})
    agg_functions = {'Rk': 'mean', 'Tm': 'last', 'Age': 'last', 'Pos': 'last', 'G': 'sum', 'GS': 'sum', 'Win': 'sum', 'Loss': 'sum', 'Tie': 'sum',
                     'Cmp': 'sum', 'Att': 'sum', 'Cmp%': 'mean', 'Yds': 'sum', 'TD': 'sum', 'TD%': 'mean', 'Int': 'sum', 'Int%': 'mean', '1D': 'sum', 'Lng': 'mean', 'Y/A': 'mean', 'AY/A': 'mean',
                     'Y/C': 'mean', 'Y/G': 'mean', 'Rate': 'mean', 'Sk': 'sum', 'Yds.1': 'sum', 'Sk%': 'mean', 'NY/A': 'mean', 'ANY/A': 'mean', '4QC': 'sum', 'GWD': 'sum', 'Year': 'last'}
    QB_DataFrame = QB_DataFrame.groupby(QB_DataFrame['Player']).aggregate(agg_functions)
    return QB_DataFrame.to_csv('QB_DataFrame.csv', index=True)
'''
'''
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
                    if 'Physically Unable to Perform' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
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


def scrapePFR_RBs_Reg():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    RBs = getPlayerID('RB')
    #Make the DataFrame with WR stats
    RB_DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', 'Rus_Att', 'Rus_Yds', 'Rus_Y/A', 'Rus_TD',
                                         'Rec_Tgt', 'Rec_Rec', 'Rec_Yds', 'Rec_Y/R', 'Rec_TD', 'Rec_Ctch%', 'Rec_Y/Tgt',
                                         'F_Fmb', 'F_Fl', 'F_FF', 'F_FR', 'F_Yds', 'F_TD',
                                         'OffSnap%',
                                         'STSnap%'])
    #Do the web scraping
    for yr in years:
        for rb in RBs:
            try:
                time.sleep(2)
                full_url = url_head + rb + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if 'Rushing' in df.columns:
                    rushing_stats = df[[('Rushing', 'Att'), ('Rushing', 'Yds'), ('Rushing', 'Y/A'), ('Rushing', 'TD')]]
                    rushing_stats.insert(0, 'Pos', 'RB')
                    rushing_stats.insert(0, 'Year', yr)
                    rushing_stats.insert(0, 'Player', rb)
                    rushing_stats = list(rushing_stats.iloc[-1])
                else:
                    rushing_stats = [rb, yr, 'RB', np.nan, np.nan, np.nan, np.nan]
                if 'Receiving' in df.columns:
                    receiving_stats = df[[('Receiving', 'Tgt'), ('Receiving', 'Rec'), ('Receiving', 'Yds'), ('Receiving', 'Y/R'), ('Receiving', 'TD'), ('Receiving', 'Ctch%'), ('Receiving', 'Y/Tgt')]]
                    receiving_stats = list(receiving_stats.iloc[-1])
                else:
                    receiving_stats = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
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
                    if 'Physically Unable to Perform' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    snapPct_stats = df[[('Off. Snaps', 'Pct')]]
                    snapPct_stats = pd.DataFrame(snapPct_stats[('Off. Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    snapPct = [snapPct_stats[('Off. Snaps', 'Pct')].mean()]
                else:
                    snapPct = [np.nan]
                if 'ST Snaps' in df.columns:
                    if 'Did Not Play' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    stPct_stats = df[[('ST Snaps', 'Pct')]]
                    stPct_stats = pd.DataFrame(stPct_stats[('ST Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    stPct = [stPct_stats[('ST Snaps', 'Pct')].mean()]
                else:
                    stPct = [np.nan]
                stats = rushing_stats + receiving_stats + fumble_stats + snapPct + stPct
                RB_DataFrame.loc[len(RB_DataFrame.index)] = stats
            except ImportError:
                time.sleep(2)
                stats = [rb, yr, 'RB', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                RB_DataFrame.loc[len(RB_DataFrame.index)] = stats
    #Save DF as .csv
    return RB_DataFrame.to_csv('RB_DataFrame.csv', index=False)

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
                    if 'Physically Unable to Perform' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    snapPct_stats = df[[('Off. Snaps', 'Pct')]]
                    snapPct_stats = pd.DataFrame(snapPct_stats[('Off. Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    snapPct = [snapPct_stats[('Off. Snaps', 'Pct')].mean()]
                else:
                    snapPct = [np.nan]
                if 'ST Snaps' in df.columns:
                    if 'Did Not Play' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    stPct_stats = df[[('ST Snaps', 'Pct')]]
                    stPct_stats = pd.DataFrame(stPct_stats[('ST Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    stPct = [stPct_stats[('ST Snaps', 'Pct')].mean()]
                else:
                    stPct = [np.nan]
                stats = receiving_stats + rushing_stats + fumble_stats + snapPct + stPct
                WR_DataFrame.loc[len(WR_DataFrame.index)] = stats
            except ImportError:
                time.sleep(2)
                stats = [wr, yr, 'WR', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                WR_DataFrame.loc[len(WR_DataFrame.index)] = stats
    #Save DF as .csv
    return WR_DataFrame.to_csv('WR_DataFrame.csv', index=False)

def scrapePFR_TEs_Reg():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    TEs = getPlayerID('TE')
    #Make the DataFrame with TE stats
    TE_DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', 'Rec_Tgt', 'Rec_Rec', 'Rec_Yds', 'Rec_Y/R', 'Rec_TD', 'Rec_Ctch%', 'Rec_Y/Tgt',
                                         'Tkl_Tot', 'Tkl_Ast', 'Tkl_Comb', 'Tkl_TFL', 'Tkl_QBHits',
                                         'F_Fmb', 'F_Fl', 'F_FF', 'F_FR', 'F_Yds', 'F_TD',
                                         'OffSnap%',
                                         'STSnap%'])
    #Do the web scraping
    for yr in years:
        for te in TEs:
            try:
                time.sleep(2)
                full_url = url_head + te + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if 'Receiving' in df.columns:
                    receiving_stats = df[[('Receiving', 'Tgt'), ('Receiving', 'Rec'), ('Receiving', 'Yds'), ('Receiving', 'Y/R'), ('Receiving', 'TD'), ('Receiving', 'Ctch%'), ('Receiving', 'Y/Tgt')]]
                    receiving_stats.insert(0, 'Pos', 'TE')
                    receiving_stats.insert(0, 'Year', yr)
                    receiving_stats.insert(0, 'Player', te)
                    receiving_stats = list(receiving_stats.iloc[-1])
                else:
                    receiving_stats = [te, yr, 'TE', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Tackles' in df.columns:
                    tackle_stats = df[[('Tackles', 'Solo'), ('Tackles', 'Ast'), ('Tackles', 'Comb'), ('Tackles', 'TFL'), ('Tackles', 'QBHits')]]
                    tackle_stats = list(tackle_stats.iloc[-1])
                else:
                    tackle_stats = [np.nan, np.nan, np.nan, np.nan, np.nan]
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
                    if 'Physically Unable to Perform' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    snapPct_stats = df[[('Off. Snaps', 'Pct')]]
                    snapPct_stats = pd.DataFrame(snapPct_stats[('Off. Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    snapPct = [snapPct_stats[('Off. Snaps', 'Pct')].mean()]
                else:
                    snapPct = [np.nan]
                if 'ST Snaps' in df.columns:
                    if 'Did Not Play' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    stPct_stats = df[[('ST Snaps', 'Pct')]]
                    stPct_stats = pd.DataFrame(stPct_stats[('ST Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    stPct = [stPct_stats[('ST Snaps', 'Pct')].mean()]
                else:
                    stPct = [np.nan]
                stats = receiving_stats + tackle_stats + fumble_stats + snapPct + stPct
                TE_DataFrame.loc[len(TE_DataFrame.index)] = stats
            except ImportError:
                time.sleep(2)
                stats = [te, yr, 'TE', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                TE_DataFrame.loc[len(TE_DataFrame.index)] = stats
    #Save DF as .csv
    return TE_DataFrame.to_csv('TE_DataFrame.csv', index=False)




def scrapePFR_DEs_Reg():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    DEs = getPlayerID('DE')
    #Make the DataFrame with DE stats
    DE_DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', 'Def_Sk', 'Tkl_Tot', 'Tkl_Ast', 'Tkl_Comb', 'Tkl_TFL', 'Tkl_QBHits',
                                         'Def_Int', 'Def_Yds', 'Def_TD', 'Def_PD',
                                         'F_Fmb', 'F_Fl', 'F_FF', 'F_FR', 'F_Yds', 'F_TD',
                                         'DefSnap%',
                                         'STSnap%'])
    #Do the web scraping
    for yr in years:
        for de in DEs:
            try:
                time.sleep(2)
                full_url = url_head + de + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if 'Unnamed: 10_level_0' in df.columns:
                    sack_stats = df[[('Unnamed: 10_level_0', 'Sk')]]
                    sack_stats.insert(0, 'Pos', 'DE')
                    sack_stats.insert(0, 'Year', yr)
                    sack_stats.insert(0, 'Player', de)
                    sack_stats = list(sack_stats.iloc[-1])
                else:
                    sack_stats = [de, yr, 'DE', np.nan]
                if 'Tackles' in df.columns:
                    tackle_stats = df[[('Tackles', 'Solo'), ('Tackles', 'Ast'), ('Tackles', 'Comb'), ('Tackles', 'TFL'), ('Tackles', 'QBHits')]]
                    tackle_stats = list(tackle_stats.iloc[-1])
                else:
                    tackle_stats = [np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Def Interceptions' in df.columns:
                    interception_stats = df[[('Def Interceptions', 'Int'), ('Def Interceptions', 'Yds'), ('Def Interceptions', 'TD'), ('Def Interceptions', 'PD')]]
                    interception_stats = list(interception_stats.iloc[-1])
                else:
                    interception_stats = [np.nan, np.nan, np.nan, np.nan]
                if 'Fumbles' in df.columns:
                    fumble_stats = df[[('Fumbles', 'Fmb'), ('Fumbles', 'FL'), ('Fumbles', 'FF'), ('Fumbles', 'FR'), ('Fumbles', 'Yds'), ('Fumbles', 'TD')]]
                    fumble_stats = list(fumble_stats.iloc[-1])
                else:
                    fumble_stats = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Def. Snaps' in df.columns:
                    if 'Did Not Play' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    snapPct_stats = df[[('Def. Snaps', 'Pct')]]
                    snapPct_stats = pd.DataFrame(snapPct_stats[('Def. Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    snapPct = [snapPct_stats[('Def. Snaps', 'Pct')].mean()]
                else:
                    snapPct = [np.nan]
                if 'ST Snaps' in df.columns:
                    if 'Did Not Play' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    stPct_stats = df[[('ST Snaps', 'Pct')]]
                    stPct_stats = pd.DataFrame(stPct_stats[('ST Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    stPct = [stPct_stats[('ST Snaps', 'Pct')].mean()]
                else:
                    stPct = [np.nan]
                stats = sack_stats + tackle_stats + interception_stats + fumble_stats + snapPct + stPct
                DE_DataFrame.loc[len(DE_DataFrame.index)] = stats
            except ImportError:
                time.sleep(2)
                stats = [de, yr, 'DE', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                DE_DataFrame.loc[len(DE_DataFrame.index)] = stats
    #Save DF as .csv
    return DE_DataFrame.to_csv('DE_DataFrame.csv', index=False)

def scrapePFR_Ss_Reg():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    Ss = getPlayerID('S')
    #Make the DataFrame with DE stats
    S_DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', 'Def_Sk', 'Tkl_Tot', 'Tkl_Ast', 'Tkl_Comb', 'Tkl_TFL', 'Tkl_QBHits',
                                         'Def_Int', 'Def_Yds', 'Def_TD', 'Def_PD',
                                         'F_Fmb', 'F_Fl', 'F_FF', 'F_FR', 'F_Yds', 'F_TD',
                                         'DefSnap%',
                                         'STSnap%'])
    #Do the web scraping
    for yr in years:
        for s in Ss:
            try:
                time.sleep(2)
                full_url = url_head + s + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if 'Unnamed: 10_level_0' in df.columns:
                    sack_stats = df[[('Unnamed: 10_level_0', 'Sk')]]
                    sack_stats.insert(0, 'Pos', 'S')
                    sack_stats.insert(0, 'Year', yr)
                    sack_stats.insert(0, 'Player', s)
                    sack_stats = list(sack_stats.iloc[-1])
                else:
                    sack_stats = [s, yr, 'S', np.nan]
                if 'Tackles' in df.columns:
                    tackle_stats = df[[('Tackles', 'Solo'), ('Tackles', 'Ast'), ('Tackles', 'Comb'), ('Tackles', 'TFL'), ('Tackles', 'QBHits')]]
                    tackle_stats = list(tackle_stats.iloc[-1])
                else:
                    tackle_stats = [np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Def Interceptions' in df.columns:
                    interception_stats = df[[('Def Interceptions', 'Int'), ('Def Interceptions', 'Yds'), ('Def Interceptions', 'TD'), ('Def Interceptions', 'PD')]]
                    interception_stats = list(interception_stats.iloc[-1])
                else:
                    interception_stats = [np.nan, np.nan, np.nan, np.nan]
                if 'Fumbles' in df.columns:
                    fumble_stats = df[[('Fumbles', 'Fmb'), ('Fumbles', 'FL'), ('Fumbles', 'FF'), ('Fumbles', 'FR'), ('Fumbles', 'Yds'), ('Fumbles', 'TD')]]
                    fumble_stats = list(fumble_stats.iloc[-1])
                else:
                    fumble_stats = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Def. Snaps' in df.columns:
                    if 'Did Not Play' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    snapPct_stats = df[[('Def. Snaps', 'Pct')]]
                    snapPct_stats = pd.DataFrame(snapPct_stats[('Def. Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    snapPct = [snapPct_stats[('Def. Snaps', 'Pct')].mean()]
                else:
                    snapPct = [np.nan]
                if 'ST Snaps' in df.columns:
                    if 'Did Not Play' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    stPct_stats = df[[('ST Snaps', 'Pct')]]
                    stPct_stats = pd.DataFrame(stPct_stats[('ST Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    stPct = [stPct_stats[('ST Snaps', 'Pct')].mean()]
                else:
                    stPct = [np.nan]
                stats = sack_stats + tackle_stats + interception_stats + fumble_stats + snapPct + stPct
                S_DataFrame.loc[len(S_DataFrame.index)] = stats
            except ImportError:
                time.sleep(2)
                stats = [s, yr, 'S', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                S_DataFrame.loc[len(S_DataFrame.index)] = stats
    #Save DF as .csv
    return S_DataFrame.to_csv('S_DataFrame.csv', index=False)


def scrapePFR_CBs_Reg():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    CBs = getPlayerID('CB')
    #Make the DataFrame with DE stats
    CB_DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', 'Def_Sk', 'Tkl_Tot', 'Tkl_Ast', 'Tkl_Comb', 'Tkl_TFL', 'Tkl_QBHits',
                                         'Def_Int', 'Def_Yds', 'Def_TD', 'Def_PD',
                                         'F_Fmb', 'F_Fl', 'F_FF', 'F_FR', 'F_Yds', 'F_TD',
                                         'DefSnap%',
                                         'STSnap%'])
    #Do the web scraping
    for yr in years:
        for cb in CBs:
            try:
                time.sleep(2)
                full_url = url_head + cb + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if 'Unnamed: 10_level_0' in df.columns:
                    sack_stats = df[[('Unnamed: 10_level_0', 'Sk')]]
                    sack_stats.insert(0, 'Pos', 'CB')
                    sack_stats.insert(0, 'Year', yr)
                    sack_stats.insert(0, 'Player', cb)
                    sack_stats = list(sack_stats.iloc[-1])
                else:
                    sack_stats = [cb, yr, 'CB', np.nan]
                if 'Tackles' in df.columns:
                    tackle_stats = df[[('Tackles', 'Solo'), ('Tackles', 'Ast'), ('Tackles', 'Comb'), ('Tackles', 'TFL'), ('Tackles', 'QBHits')]]
                    tackle_stats = list(tackle_stats.iloc[-1])
                else:
                    tackle_stats = [np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Def Interceptions' in df.columns:
                    interception_stats = df[[('Def Interceptions', 'Int'), ('Def Interceptions', 'Yds'), ('Def Interceptions', 'TD'), ('Def Interceptions', 'PD')]]
                    interception_stats = list(interception_stats.iloc[-1])
                else:
                    interception_stats = [np.nan, np.nan, np.nan, np.nan]
                if 'Fumbles' in df.columns:
                    fumble_stats = df[[('Fumbles', 'Fmb'), ('Fumbles', 'FL'), ('Fumbles', 'FF'), ('Fumbles', 'FR'), ('Fumbles', 'Yds'), ('Fumbles', 'TD')]]
                    fumble_stats = list(fumble_stats.iloc[-1])
                else:
                    fumble_stats = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Def. Snaps' in df.columns:
                    if 'Did Not Play' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    snapPct_stats = df[[('Def. Snaps', 'Pct')]]
                    snapPct_stats = pd.DataFrame(snapPct_stats[('Def. Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    snapPct = [snapPct_stats[('Def. Snaps', 'Pct')].mean()]
                else:
                    snapPct = [np.nan]
                if 'ST Snaps' in df.columns:
                    if 'Did Not Play' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    stPct_stats = df[[('ST Snaps', 'Pct')]]
                    stPct_stats = pd.DataFrame(stPct_stats[('ST Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    stPct = [stPct_stats[('ST Snaps', 'Pct')].mean()]
                else:
                    stPct = [np.nan]
                stats = sack_stats + tackle_stats + interception_stats + fumble_stats + snapPct + stPct
                CB_DataFrame.loc[len(CB_DataFrame.index)] = stats
            except ImportError:
                time.sleep(2)
                stats = [cb, yr, 'CB', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                CB_DataFrame.loc[len(CB_DataFrame.index)] = stats
    #Save DF as .csv
    return CB_DataFrame.to_csv('CB_DataFrame.csv', index=False)


def scrapePFR_LBs_Reg():
    #Create variables to be used
    url_head = 'https://www.pro-football-reference.com/players/M/'
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    LBs = getPlayerID('LB')
    #Make the DataFrame with DE stats
    LB_DataFrame = pd.DataFrame(columns=['Player', 'Year', 'Pos', 'Def_Sk', 'Tkl_Tot', 'Tkl_Ast', 'Tkl_Comb', 'Tkl_TFL', 'Tkl_QBHits',
                                         'Def_Int', 'Def_Yds', 'Def_TD', 'Def_PD',
                                         'F_Fmb', 'F_Fl', 'F_FF', 'F_FR', 'F_Yds', 'F_TD',
                                         'DefSnap%',
                                         'STSnap%'])
    #Do the web scraping
    for yr in years:
        for lb in LBs:
            try:
                time.sleep(2)
                full_url = url_head + lb + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if 'Unnamed: 10_level_0' in df.columns:
                    sack_stats = df[[('Unnamed: 10_level_0', 'Sk')]]
                    sack_stats.insert(0, 'Pos', 'LB')
                    sack_stats.insert(0, 'Year', yr)
                    sack_stats.insert(0, 'Player', lb)
                    sack_stats = list(sack_stats.iloc[-1])
                else:
                    sack_stats = [lb, yr, 'LB', np.nan]
                if 'Tackles' in df.columns:
                    tackle_stats = df[[('Tackles', 'Solo'), ('Tackles', 'Ast'), ('Tackles', 'Comb'), ('Tackles', 'TFL'), ('Tackles', 'QBHits')]]
                    tackle_stats = list(tackle_stats.iloc[-1])
                else:
                    tackle_stats = [np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Def Interceptions' in df.columns:
                    interception_stats = df[[('Def Interceptions', 'Int'), ('Def Interceptions', 'Yds'), ('Def Interceptions', 'TD'), ('Def Interceptions', 'PD')]]
                    interception_stats = list(interception_stats.iloc[-1])
                else:
                    interception_stats = [np.nan, np.nan, np.nan, np.nan]
                if 'Fumbles' in df.columns:
                    fumble_stats = df[[('Fumbles', 'Fmb'), ('Fumbles', 'FL'), ('Fumbles', 'FF'), ('Fumbles', 'FR'), ('Fumbles', 'Yds'), ('Fumbles', 'TD')]]
                    fumble_stats = list(fumble_stats.iloc[-1])
                else:
                    fumble_stats = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                if 'Def. Snaps' in df.columns:
                    if 'Did Not Play' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('Def. Snaps', 'Pct')].values:
                        df[('Def. Snaps', 'Pct')] = df[('Def. Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('Off. Snaps', 'Pct')].values:
                        df[('Off. Snaps', 'Pct')] = df[('Off. Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    snapPct_stats = df[[('Def. Snaps', 'Pct')]]
                    snapPct_stats = pd.DataFrame(snapPct_stats[('Def. Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    snapPct = [snapPct_stats[('Def. Snaps', 'Pct')].mean()]
                else:
                    snapPct = [np.nan]
                if 'ST Snaps' in df.columns:
                    if 'Did Not Play' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Did Not Play'], '0%')
                    if 'Injured Reserve' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Injured Reserve'], '0%')
                    if 'Inactive' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Inactive'], '0%')
                    if 'Suspended' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Suspended'], '0%')
                    if 'Non-Football Injury' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Non-Football Injury'], '0%')
                    if 'COVID-19 List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['COVID-19 List'], '0%')
                    if 'Exempt List' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Exempt List'], '0%')
                    if 'Physically Unable to Perform' in df[('ST Snaps', 'Pct')].values:
                        df[('ST Snaps', 'Pct')] = df[('ST Snaps', 'Pct')].replace(['Physically Unable to Perform'], '0%')
                    stPct_stats = df[[('ST Snaps', 'Pct')]]
                    stPct_stats = pd.DataFrame(stPct_stats[('ST Snaps', 'Pct')].str.rstrip("%").astype(float)/100)
                    stPct = [stPct_stats[('ST Snaps', 'Pct')].mean()]
                else:
                    stPct = [np.nan]
                stats = sack_stats + tackle_stats + interception_stats + fumble_stats + snapPct + stPct
                LB_DataFrame.loc[len(LB_DataFrame.index)] = stats
            except ImportError:
                time.sleep(2)
                stats = [lb, yr, 'LB', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                LB_DataFrame.loc[len(LB_DataFrame.index)] = stats
    #Save DF as .csv
    return LB_DataFrame.to_csv('LB_DataFrame.csv', index=False)
'''
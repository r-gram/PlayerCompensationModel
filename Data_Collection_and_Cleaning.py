import pandas as pd

#Read in data
def draft_2017():
    draft2017DF = pd.read_csv("NFL_2017_Draft.csv")
    return draft2017DF
def salaries_2017():
    salaries2017DF = pd.read_csv("NFL_2017_Player_Salaries.csv")
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
                                         'F_Fmb', 'F_Fl', 'F_FF', 'F_FR', 'F_Yds', 'F_TD'])
    #Do the web scraping
    for yr in years:
        for qb in QBs:
            try:
                full_url = url_head + qb + '/gamelog/' + yr
                df = pd.read_html(full_url)[0]
                if df.shape[1] >= 24:
                    stats = df[['Passing', 'Passing.1', 'Passing.2', 'Passing.3', 'Passing.4', 'Passing.5', 'Passing.6', 'Passing.7', 'Passing.8', 'Passing.9', 'Passing.10',
                                'Rushing', 'Rushing.1', 'Rushing.2', 'Rushing.3',
                                'Fumbles', 'Fumbles.1', 'Fumbles.2', 'Fumbles.3', 'Fumbles.4', 'Fumbles.5']]
                    stats.insert(0, 'Pos', 'QB')
                    stats.insert(0, 'Year', yr)
                    stats.insert(0, 'Player', qb)
                    list_stats = list(stats.iloc[-1])
                    QB_DataFrame.loc[len(QB_DataFrame.index)] = list_stats
            except:
                pass
    #Save DF as .csv
    return QB_DataFrame.to_csv('QB_DataFrame.csv', index=False)

'''
def scrapePFR_RBs():


def scrapePFR_WRs():


def scrapePFR_TEs():


def scrapePFR_Gs():


def scrapePFR_Cs():


def scrapePFR_OLs():


def scrapePFR_FBs():


def scrapePFR_Ks():


def scrapePFR_DEs():


def scrapePFR_Ss():


def scrapePFR_CBs():


def scrapePFR_LBs():


def scrapePFR_Ts():


def scrapePFR_OLBs():


def scrapePFR_DTs():


def scrapePFR_DBs():


def scrapePFR_ILBs():


def scrapePFR_DLs():


def scrapePFR_LSs():


def scrapePFR_NTs():
'''
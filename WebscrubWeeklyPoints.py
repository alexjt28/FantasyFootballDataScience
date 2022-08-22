####################################################################################
# Create dataset of weekly points for a given year
# ----------------------------------------------------------------------------------
# Only need to modify the following inputs from below, the script will do the rest!
# 1. point_scoring
# 2. year
# 3. week_beg
# 4. week_end
####################################################################################

#----------------
# Load packages
#----------------

import pandas as pd
import numpy as np

#----------------
# Define inputs
#----------------

# Modify these!
point_scoring = 'half-ppr'    # Choose between 'ppr', 'half-ppr', or 'standard'
year          = 2020          # Keep as value: ex. 2021 instead of '2021'
week_beg      = 1             # First week to scrub data for, usually 1
week_end      = 16            # Last week to scrub data for; in 2021 this is probably 17, before then it is probably 16

# These will populate based on the inputs above
first_week = np.arange(week_beg,week_end+1) # For 2021, this indexes Weeks 1 to 17
last_week = first_week                      # Loop takes each week as ex. Wk1:Wk1 for Week 1 data

#----------------------------------------------------------------------------------------------------
# Webscrub data from FantasyPros.com 
# example URL: https://www.fantasypros.com/nfl/reports/leaders/half-ppr.php?year=2021&start=1&end=17
#----------------------------------------------------------------------------------------------------

# Initialize empty arrays to input each week to
Weeks = []                # allows for scrubbing data for each week as specified above 
for n in range(week_end):
    Weeks.append([])

# Loop through Weeks beg:end and webscrub data from FantasyPros
for i in range(week_end):                           # Loop through 17 weeks of data for 2021
    Weeks[i] = fantasypros_weeklypoints(point_scoring,year,first_week[i],last_week[i])

#----------------------------------------------------    
# Start with DataFrame of unique player attributes
#----------------------------------------------------    

# Make name list from unique values of all names
plyr_all = Weeks[0]['Player']
team_all = Weeks[0]['Team']
posn_all = Weeks[0]['Position']
for x in range(1,week_end):
    plyr_all = plyr_all.append(Weeks[x]['Player'])
    team_all = team_all.append(Weeks[x]['Team'])
    posn_all = posn_all.append(Weeks[x]['Position'])
    
# Create numpy array of player attributes [Name x Team x Position]
atts_all = np.empty([len(plyr_all),3],dtype=np.dtype('U100'))
atts_all[:,0] = plyr_all
atts_all[:,1] = team_all
atts_all[:,2] = posn_all

# Convert player attributes to Pandas dataframe with unique player values
player_atts = pd.DataFrame(atts_all, columns = ['Player','Team','Position']).drop_duplicates().reset_index().drop(['index'],axis=1)

#-------------------------------------------------------------------
# Use unique player names to populate DataFrame with weekly points
#-------------------------------------------------------------------

# Array of names to lookup values by
player_name = player_atts['Player']

# Initialize array
weekly_points_data = np.empty([len(player_name),week_end],dtype=float)

# Loop through each player for each week
for x in range(0,len(player_name)):
    for y in range(week_end):
        if Weeks[y].loc[Weeks[y]['Player'] == player_name[x]].empty:
            weekly_points_data[x,y] = 0.
        else:
            weekly_points_data[x,y] = Weeks[y].loc[Weeks[y]['Player'] == player_name[x],'Points'].item()

#---------------------------------------------------------------------------------------
# Create dataset by each player: [Player x Team x Pos x Wk_beg:Wk_end pts x Total pts]
#---------------------------------------------------------------------------------------
# Using player_atts from before and appending weekly scores to it
# Example: wk1 = weekly_points_data[:,0], etc.

# Set new name
by_week = player_atts

# Loop through each week to append data
for z in range(week_end):
    by_week['Wk'+str(z+1)] = weekly_points_data[:,z]

# Add Week_beg:Week_end summed score as last column
by_week['Total'] = np.zeros(len(player_name))
for t in range(len(player_name)):
    by_week['Total'][t] = by_week.iloc[t,3:week_end+3].sum(axis=0)

#------------------------------------------
# Perform some post-processing of data
#------------------------------------------

# If value is 0.0 then set to empty value
by_week[by_week.eq(0.)] = np.nan

# Sort by highest total to lowest
final_data = by_week.sort_values('Total',ascending=False,na_position='last')

# Print data to notebook visual
print(final_data)

#------------------------------------------
# Save data to output file: Excel (.xlsx)
#------------------------------------------

final_data.to_excel('~/Downloads/'+str(point_scoring)+'_'+str(year)+'_by_week.xlsx', sheet_name=str(year)+' '+str(point_scoring), index=False)

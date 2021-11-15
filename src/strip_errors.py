import os
import pandas as pd

scaling_groups_export = os.path.abspath(os.path.join(os.path.expanduser('~'), 
                    'Downloads/acs-College Reports-Courses in Scaling Groups.csv'))

with open(scaling_groups_export, 'r') as file:
    scaling_groups_df = pd.read_csv(file)
    without_errors_df = scaling_groups_df.loc[scaling_groups_df['Error1'] != '*Error']
    pd.DataFrame.to_csv(without_errors_df, 'without_errors.csv')




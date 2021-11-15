import os
import pandas as pd
from read_data import load_data

def calculate_aggregate_score(student, past_params, scaling_groups):
    '''
    Calculates the aggregate score for a student

    Parameters
    ----------
    student : dict
        a dict containing student data
    past_params : dict
        a dict containing the scaling parameters for each scaling group
    scaling_groups : dict
        a dict containing the scaling group for each course

    Returns
    -------
    int
        the student's aggregate score rounded to the nearest integer
    '''
    majors = [course for course in student['Courses'] if course['Major'] == True]
    minors = [course for course in student['Courses'] if course['Major'] == False]

    if len(majors) < 3:
        return 0
    else:
        majors.sort(key=lambda m: m['Avg_Unit_Score'], reverse=True)
        best_three = majors[0:3]

        if len(majors) > 3:
            choices_for_fourth = majors[3:] + minors
        else:
            choices_for_fourth = minors

        choices_for_fourth.sort(key=lambda m: m['Avg_Unit_Score'], reverse=True)
        fourth = choices_for_fourth[0]
        best_four = best_three + [fourth]

        scaled_scores = []

        for major in best_four:
            scaling_group = scaling_groups[major['Course_Title']]
            scaled_score = major['Avg_Unit_Score'] * past_params[scaling_group]['b'] + past_params[scaling_group]['a']
            scaled_scores.append(scaled_score)

        return int(round(scaled_scores[0] + scaled_scores[1] + scaled_scores[2] + 0.6 * scaled_scores[3], 0))
    
def predict_atar(aggregate_score, atar_bounds):
    '''
    Predicts an ATAR given an aggregate score and a list of lower bounds

    Parameters
    ----------
    aggregate_score : int
        a student's aggregate score rounded to the nearest integer
    
    atar_bounds : list
        a list of tuples of the form (lower_bound, atar)
    '''
    for lower, atar in atar_bounds:
        if aggregate_score >= lower:
            return atar

def predicted_atar_range(predicted_atar):
    '''
    Creates a string with the predicted ATAR range as a 10 point range

    Parameters
    ----------
    predicted_atar : int
        the student's predicted ATAR to the nearest int
    
    Returns
    -------
    str
        a string containing the ten point ATAR range
    '''
    if predicted_atar > 96:
        return "90 - 100"
    else:
        return str(predicted_atar - 7) + " - " + str(predicted_atar + 3)

def write_atar_estimates_to_csv(student_predictions):
    '''
    Writes the student's predicted ATARs to csv

    Parameters
    ----------
    student_predictions : list
        a list of students with their predicted ATAR range
    '''
    df = pd.DataFrame(student_predictions)
    pd.DataFrame.to_csv(df, os.path.abspath(os.path.join(__file__, '../../output/atar_estimates.csv')))
        
def main():
    data_path = os.path.abspath(os.path.join(__file__, '../../data'))
    acs_export_file = os.path.join(data_path, 'y12-acs-export.csv')
    past_params_file = os.path.join(data_path, 'past_params.csv')
    scaling_groups_file = os.path.join(data_path, 'scaling_groups.csv')
    atar_bounds_file = os.path.join(data_path, 'atar_bounds.csv')

    students, past_params, scaling_groups, atar_bounds = load_data(acs_export_file, 
                                                                past_params_file, 
                                                                scaling_groups_file,
                                                                atar_bounds_file)
    student_predictions = []

    for student in students:
        aggregate_score = calculate_aggregate_score(student, past_params, scaling_groups)
        atar_prediction = predict_atar(aggregate_score, atar_bounds)
        atar_range = predicted_atar_range(atar_prediction)
        student_predictions.append({ 'Full_Name': student['Full_Name'], 
                                    'ATAR_Prediction': atar_prediction,
                                    'Predicted_Range': atar_range 
                                })
    
    write_atar_estimates_to_csv(student_predictions)

if __name__ == '__main__':
    main()
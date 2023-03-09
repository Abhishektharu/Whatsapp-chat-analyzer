import re
import pandas as pd
def preprocess(data):
    pattern = '\d{1,2}\/\d{2,4}\/\d{2,4},\s\d{1,2}:\d{1,2}\s\w{1,2}\s-\s'
    messages = re.split(pattern, data)[1:]

    dates = re.findall(pattern, data)
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    df['dates'] = df['message_date'].str.findall('\d{1,2}/\d{1,2}/\d{2,4}').apply(lambda x: x[0])
    df['time'] = df['message_date'].str.findall('\d{1,2}:\d{1,2}\s[a-z]+').apply(lambda x: x[0])


    def change_to_24hr(x):
        t_splt = x.split(':')
        if t_splt[1][3:] == 'pm' and t_splt[0] != '12':
            t_splt[0] = str(12 + int(t_splt[0]))
        elif int(t_splt[0]) == 12 and t_splt[1][3:] == 'am':
            t_splt[0] = '00'
        t_splt[1] = t_splt[1][:2]
        return ':'.join(t_splt)


    df['time_24'] = df['time'].apply(lambda x: change_to_24hr(x))

    df['message_date'] = df.agg(lambda x: f"{x['dates']} {x['time_24']}", axis=1)
    df = df[['user_message', 'message_date']]

    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y %H:%M')

    df.rename(columns={'message_date': 'date'}, inplace=True)

# seperate users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            # username
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    df.head()

    df['month_name'] = df['date'].dt.day_name()
    df['day_name'] = df['date'].dt.day_name()
    df['date_only'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['dates'] = df['date'].dt.day

    df['dates'] = df['date'].dt.month_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute


    period = []
    for hour in df[['day_name','hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))

        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))

        else:
            period.append(str(hour) +"-" + str(hour + 1))

    df['period'] = period

    
    return df
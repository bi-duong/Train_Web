import flask
import matplotlib as matplotlib
import pypyodbc as odbc
from flask import render_template, flash, redirect, session, url_for, request, g, Markup,Response
import plotly.graph_objs as go
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import locale
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from underthesea import sentiment
drive='SQL SERVER'
SE='LAPTOP-FFL0DTFU'
Da='cuoiky'
app = flask.Flask(__name__)
conn = odbc.connect('DRIVER={SQL Server};SERVER='+SE+';DATABASE='+Da+';Trust_Connecttion=yes;')
suc = conn.cursor()
@app.template_filter('format_currency')
def format_currency(value):
    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
    return locale.currency(value, grouping=True)


def analyze_sentiment_vietnamese(sentence):
    analyzer = SentimentIntensityAnalyzer()
    vader_scores = analyzer.polarity_scores(sentence)
    compound_score = vader_scores['compound']
    print(compound_score)
    if compound_score >= 0.05:
        return "Positive"
    elif compound_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

@app.template_global()
def zip_lists(*args):
    return zip(*args)
def plot(data, conn):
    xTickMarks = []
    counts = []
    for row in data:
        xTickMarks.append(row[0])
        counts.append((row[1]))
    plt.bar(xTickMarks, counts)
    plt.xticks(rotation=0)
    plt.xlabel("Quarter")
    plt.ylabel("Total")
    plt.savefig('static/bar2.png')
    plt.switch_backend('agg')
def plot2(data, conn):
    xTickMarks = []
    counts = []
    for row in data:
        xTickMarks.append(row[0])
        counts.append((row[1]))
    plt.bar(xTickMarks, counts)
    plt.xticks(rotation=0)
    plt.xlabel("Quarter")
    plt.ylabel("Total")
    plt.savefig('static/bar.png')
    plt.switch_backend('agg')
@app.route('/')
def index():
    s5 = "SELECT S1.StationName as tostationname, S2.StationName as fromtationname,P.TrainNumber as train, T1.Date as timeto, T2.Date as timefrom  FROM Station S1 JOIN Trip T ON S1.StationKey = T.ToStationKey  JOIN Train P ON P.TrainKey = T.TrainKey JOIN Station S2 ON S2.StationKey = T.FromStationKey JOIN Time T1 ON T.TimeToKey = T1.TimeKey JOIN Time T2 ON T.TimeFromKey = T2.TimeKey"
    cur5 = conn.cursor()
    cur5.execute(s5)
    list5 = cur5.fetchall()
    s6 = "select e.FirstName as fir,e.LastName as last,e.City as city,e.Country as co, e.PhoneNumber as num,S.TrainNumber as train from Employee e,Trip T, Train S where e.EmployeeKey=T.EmployeeKey and S.TrainKey=T.TrainKey"
    cur6 = conn.cursor()
    cur6.execute(s6)
    list6 = cur6.fetchall()

    s7 = "SELECT s.SeatNumber as seat, e.CustomerName as name, e.PhoneNumber as phone, p.UnitPrice as price,tt1.TrainNumber as train, t1.Date as timeto, t2.Date as timefrom, S1.StationName as tota, S2.StationName as fromta FROM Trip T JOIN Train tt1 ON tt1.TrainKey = T.TrainKey JOIN Customer e ON T.CustomerKey = e.CustomerKey JOIN Seat s ON s.SeatKey = T.SeatKey JOIN Price p ON p.PriceKey = s.PriceKey JOIN Time t1 ON t1.TimeKey = T.TimeToKey JOIN Time t2 ON t2.TimeKey = T.TimeFromKey JOIN Station S1 ON S1.StationKey = T.ToStationKey JOIN Station S2 ON S2.StationKey = T.FromStationKey;"
    cur7 = conn.cursor()
    cur7.execute(s7)
    list7 = cur7.fetchall()
    # cur = conn.cursor()
    # s = "SELECT s.SeatNumber as seat, e.FirstName as first, e.LastName as last, e.Address as addres, e.Country as country, e.PhoneNumber as phone, p.UnitPrice as price, t1.Date as timeto, t2.Date as timefrom, S1.StationName as totation, S2.StationName as fromtation FROM Trip T JOIN Employee e ON T.EmployeeKey = e.EmployeeKey JOIN Seat s ON s.SeatKey = T.SeatKey JOIN Price p ON p.PriceKey = s.PriceKey JOIN Time t1 ON t1.TimeKey = T.TimeToKey JOIN Time t2 ON t2.TimeKey = T.TimeFromKey JOIN Station S1 ON S1.StationKey = T.ToStationKey JOIN Station S2 ON S2.StationKey = T.FromStationKey;"
    # cur.execute(s)  # Execute the SQL
    # list_users = cur.fetchall()
    # cur1 = conn.cursor()
    # s1="select e.FirstName as first,e.LastName as last,e.City as city,e.Country as country, e.PhoneNumber as phone ,S.TrainNumber as train from Employee e,Trip T, Train S where e.EmployeeKey=T.EmployeeKey and S.TrainKey=T.TrainKey"
    # cur1.execute(s1)
    # list_users2=cur1.fetchall()
    return render_template('index.html',list5=list5,list6=list6,list7=list7)

@app.route('/train')
def train():
    cur = conn.cursor()
    s = "select TrainNumber as trainnum,ModelName as modelname,MaxSpeed as maxspeed from Train"
    cur.execute(s)  # Execute the SQL
    list_users = cur.fetchall()
    train_nums = []
    max_speeds = []

    for row in list_users:
        train_nums.append(row['trainnum'])
        max_speeds.append(row['maxspeed'])

    # Tạo biểu đồ cột
    data = [go.Bar(
        x=train_nums,
        y=max_speeds
    )]

    layout = go.Layout(
        title='Max Speed of Trains',
        xaxis=dict(title='Train Number'),
        yaxis=dict(title='Max Speed')
    )

    fig = go.Figure(data=data, layout=layout)

    # Tạo HTML của biểu đồ và dữ liệu
    plot_div = fig.to_html(full_html=False)

    return render_template('train.html',list=list_users, plot_div=plot_div)
@app.route('/count')
def count():
    cur1 = conn.cursor()
    s1 = "select S.TrainNumber as train,SUM(P.TotalPrice) as total from Train S, Trip P where S.Trainkey=P.Trainkey Group by S.TrainNumber"
    cur1.execute(s1)
    list_users2 = cur1.fetchall()
    s2 = "SELECT t1.TrainNumber as train, COUNT(e.LastName) as employee, count(c.CustomerName) as customer FROM Trip t JOIN Train t1 ON t.TrainKey = t1.TrainKey JOIN Employee e ON t.EmployeeKey = e.EmployeeKey JOIN Customer c ON t.CustomerKey = c.CustomerKey GROUP BY t1.TrainNumber;"
    cur2 = conn.cursor()
    cur2.execute(s2)
    list_users1 = cur2.fetchall()
    train_numbers = []
    employees = []
    customers = []

    for row in list_users1:
        train_numbers.append(row['train'])
        employees.append(row['employee'])
        customers.append(row['customer'])

    # Tạo biểu đồ cột
    data = [
        go.Bar(
            x=train_numbers,
            y=employees,
            name='Employees'
        ),
        go.Bar(
            x=train_numbers,
            y=customers,
            name='Customers'
        )
    ]

    layout = go.Layout(
        title='Employee and Customer Count per Train',
        xaxis=dict(title='Train Number'),
        yaxis=dict(title='Count'),
        barmode='group'
    )

    fig = go.Figure(data=data, layout=layout)

    # Tạo HTML của biểu đồ
    plot_div = fig.to_html(full_html=False)

    # s3 = "select s.Description as des,count(s.Description) as soluong from Seat s,Trip T where s.SeatKey=T.SeatKey group by s.Description"
    # cur3 = conn.cursor()
    # cur3.execute(s3)
    # list3 = cur3.fetchall()


    s4 = "SELECT t1.MonthNumber as month, sum(t2.TotalPrice) as doanhthutheothang FROM Time t1, Trip t2 where t1.TimeKey = t2.TimeToKey GROUP BY t1.MonthNumber"
    cur4 = conn.cursor()
    cur4.execute(s4)
    list4 = cur4.fetchall()
    months = []
    revenues = []

    for row in list4:
        months.append(row['month'])
        revenues.append(row['doanhthutheothang'])

    # Tạo biểu đồ đường
    data = [
        go.Scatter(
            x=months,
            y=revenues,
            mode='lines+markers'
        )
    ]

    layout = go.Layout(
        title='Revenue by Month',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Revenue (VND)')
    )

    fig = go.Figure(data=data, layout=layout)

    # Tạo HTML của biểu đồ
    plot_div2 = fig.to_html(full_html=False)

    s5 = "SELECT t1.Year as year, sum(t2.TotalPrice) as doanhthutheonam FROM Time t1, Trip t2 where t1.TimeKey = t2.TimeToKey GROUP BY t1.Year"
    cur5 = conn.cursor()
    cur5.execute(s5)
    list5 = cur5.fetchall()
    years = []
    revenues2 = []

    for row in list5:
        years.append(row['year'])
        revenues2.append(row['doanhthutheonam'])

    # Tạo biểu đồ cột
    data = [
        go.Bar(
            x=years,
            y=revenues2
        )
    ]

    layout = go.Layout(
        title='Revenue by Year',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Revenue (VND)')
    )

    fig = go.Figure(data=data, layout=layout)

    # Tạo HTML của biểu đồ
    plot_div3 = fig.to_html(full_html=False)
    return render_template('count.html',list2=list_users2,list1=list_users1, list4=list4,plot_div=plot_div,plot_div2=plot_div2,list5=list5,plot_div3=plot_div3)
@app.route('/sentiment')
def sentiment():
    cur1 = conn.cursor()
    s1 = "select C.CustomerName as name,T.TrainNumber as trainum,C.Comment as comment from Customer C,Train T ,Trip T2 where C.CustomerKey=T2.CustomerKey"
    cur1.execute(s1)
    list_users2 = cur1.fetchall()

    sentiment_list = []
    for user in list_users2:
        comment = user['comment']
        sentiment = analyze_sentiment_vietnamese(comment)
        sentiment_list.append(sentiment)
    return render_template('sentiment.html',list_users=list_users2,sentiment_list=sentiment_list)

if __name__ == '__main__':

    app.debug = True
    app.run()
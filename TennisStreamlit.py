import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector import Error
import matplotlib.pyplot as plt
import os
st.title("Tennis Data Analytics Application")

st.divider()
#DB Connection
def DB_Connection():
    try:
        connection=mysql.connector.connect(
         host='localhost',
         user='root',
         password='',
         database='TennisStatsPro'
    )

        if connection.is_connected():
            print("Database connected successfully!")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    
#Closing once the Application is closed
def close_db_connection(connection,cursor):
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
        print("Database connection closed.")

#Getting the Data From the DB
def Query_DB(connection,query):
    if connection and connection.is_connected():
        cursor=connection.cursor()
        cursor.execute(query)
        result=cursor.fetchall()
        return result
    else:
        print("Database connection is not established.")
        return None

#Creating a SideBar
def create_sidebar(connection):
    # Navigation
    st.sidebar.markdown(f'Hello {os.getlogin()} !! :smile:')
    st.sidebar.title("Navigation")
    selected_tab = st.sidebar.radio(
        "Go to",
        ["Competition Insights", "Competitor Analytics", "Leaderboards", "About"]
    )
    return selected_tab

#Dynamic Filters Method
def DynamicFilters(connection,selected_tab):
    if selected_tab=="Competition Insights":

        st.sidebar.header("Competitions Filters")

        #Search by Competitions
        CompetitionType=Query_DB(connection,"select distinct(type) from competitions")
        typeresult = [item[0].capitalize() for item in CompetitionType]
        competition_type = st.sidebar.selectbox(
            "Select Competition Type", typeresult
        )
        #Filter By Gender
        GenderType=Query_DB(connection,"select distinct(gender) from competitions")
        genderresult = [item[0].capitalize() for item in GenderType]
        gender = st.sidebar.selectbox("Select Gender", genderresult)

        Category=Query_DB(connection,"select distinct(category_name) from categories")
        Categoryresult = [item[0].capitalize() for item in Category]
        defaultvalues=['Challenger']
        
        #Filter By Category
        Category_Type = st.sidebar.multiselect(
            "Select Competition Type", Categoryresult,default=defaultvalues,
        )

        return  competition_type, gender, Category_Type

    elif selected_tab =="Competitor Analytics":

        st.sidebar.header("Filter Competitors")

        # Search by name
        name_search = st.sidebar.text_input("Search by Competitor Name", "")

        # Filter by rank range
        rank_range = st.sidebar.slider("Filter by Rank Range", min_value=1, max_value=500, value=(1, 100))

        # Filter by country
        
        Country=Query_DB(connection,"select distinct country from competitors order by country asc ")
        Countryresult = [item[0].capitalize() for item in Country] +['All']
        countries = ['India' ,'Japan','Belgium']
        selected_countries = st.sidebar.multiselect("Filter by Country", Countryresult, default=countries)

        # Filter by points threshold
        points_threshold = st.sidebar.slider("Filter by Points Threshold", min_value=0, max_value=10000, value=(0, 5000))
        return name_search,rank_range,selected_countries,points_threshold

    elif selected_tab=="Leaderboards":
        #Changing View Based on the Option in the Leaderboard
        leaderboard_option = st.radio('Choose Leaderboard Type:', ['Top-ranked Competitors', 'Competitors with Highest Points'])

        return leaderboard_option



#1st Page
def Competitions(connection,competition_type, gender, CategoryName):
    st.subheader('Competitions Insights',)

    col1, col2, col3 = st.columns(3)    
    
    TotalCompetitor=Query_DB(connection,"select count(competitor_id) from competitors")
    col1.metric("Total Competitors 👥", TotalCompetitor[0][0])

    HighestPoints=Query_DB(connection,"select max(points) from competitor_rankings;")
    col2.metric("Highest Points 🎉", HighestPoints[0][0])

    TotalCountriesRepresented=Query_DB(connection,"select count(distinct(country)) from competitors")
    col3.metric("Countries Represented 🌍", TotalCountriesRepresented[0][0])

    #Passing first query to the Quer_DB Method
    if CategoryName:
        Category = ",".join([f"'{cat}'" for cat in CategoryName])
    else:
        Category = "''"
    query = f"""
                SELECT comp.competition_name AS CompetitorName,
                    comp.type AS CompetitorType,
                    comp.gender AS Gender,
                    cat.category_name AS CategoryName
                FROM Competitions comp
                LEFT JOIN Categories cat ON comp.category_id = cat.category_id
                WHERE comp.type = '{competition_type}' 
                AND comp.gender = '{gender}' 
                AND cat.category_name IN ({Category})
                LIMIT 2000
            """
    
    TableResult=Query_DB(connection,query)
    st.divider()
    st.subheader('Competition Details ')
    
    df=pd.DataFrame(TableResult,columns=[" Competition Name ", " Competition Type " , "Gender", "Category Name"])

    df_reset = df.reset_index(drop=True)
    df_reset.index = df_reset.index + 1 
    #CometitionsMainTable 
    st.dataframe(df_reset)
    
    #CategoriesTable
    st.subheader('Categories-Wise Analysis')
    st.divider()
    query = f"""
            select cat.category_name as Category ,count(comp.competition_id) as Count from 
            Competitions comp Left join Categories cat 
            on comp.category_id=cat.category_id 
            WHERE comp.type = '{competition_type}' 
            AND comp.gender = '{gender}' 
            AND cat.category_name IN ({Category})
            group by cat.category_name
            LIMIT 2000
        """
    ChartResult=Query_DB(connection,query)
    df2=pd.DataFrame(ChartResult,columns=["Category", "Total Competition" ])
    df2_reset = df2.reset_index(drop=True)
    df2_reset.index = df2_reset.index + 1 

    st.dataframe(df2_reset)
    # Plotting 
        # # st.title("Category-Wise Competition Count")
    query = f"""
            select cat.category_name as Category ,count(comp.competition_id) as Count from 
            Competitions comp Left join Categories cat 
            on comp.category_id=cat.category_id 
            WHERE comp.type = '{competition_type}' 
            AND comp.gender = '{gender}' 
            AND cat.category_name IN ({Category})
            group by cat.category_name
            LIMIT 2000
        """
    ChartResult=Query_DB(connection,query)
    df2=pd.DataFrame(ChartResult,columns=["Category", "Total Competition" ])
    

    # Bar-Line Chart
    fig, ax = plt.subplots(figsize=(12, 6))  # Set figure size

    # Bar chart
    bars = ax.bar(df2['Category'], df2['Total Competition'], label='Competition Count', alpha=0.8)

    # Line chart
    ax.plot(df2['Category'], df2['Total Competition'], color='green', linestyle='-', linewidth=2, label='Trend Line')

    # Add labels and title
    ax.set_xlabel('Category', fontsize=11)
    ax.set_ylabel('Total Competitions', fontsize=11)
    ax.set_title('Competitions Count Per Category', fontsize=13, color='green')

    plt.xticks(rotation=45, ha='right', fontsize=10)

    ax.grid(True, axis='y', linestyle=':', alpha=0.7)

    # Add data labels to bars
    for bar in bars:
        yval = bar.get_height() 
        ax.text(bar.get_x() + bar.get_width() / 2, yval , 
                f'{yval}', ha='center', fontsize=9, color='black')

    # Add legend for bar and line chart
    ax.legend(loc='upper left', fontsize=9)

    # Display the chart in Streamlit
    st.pyplot(fig)
    
#2nd Page
def Competitors(connection,name_search,rank_range,selected_countries,points_threshold):

    col1, col2= st.columns(2)    
    TotalVenues=Query_DB(connection,"SELECT count(distinct(venue_name)) as TotalVenues FROM venues;")
    col1.metric("Total Venues 👥", TotalVenues[0][0])

    TotalComplexes=Query_DB(connection,"SELECT count(distinct(complex_name)) FROM complexes;")
    col2.metric("Total Complexes", TotalComplexes[0][0])
    st.header("Competitor Details")
    #Competitor Details
    query = """
    SELECT DISTINCT 
        cr.rank AS Ranks, 
        c.name AS CompetitorName, 
        cr.points AS Points, 
        cr.movement AS Movement, 
        cr.competitions_played AS Competitions_Played, 
        c.country AS Country
    FROM Competitors c 
    LEFT JOIN Competitor_Rankings cr 
    ON c.competitor_id = cr.competitor_id
    order by cr.rank asc ;
    """

    # Execute query
    TableResult = Query_DB(connection, query)

    # Create DataFrame
    df = pd.DataFrame(TableResult, columns=["Ranks", "CompetitorName", "Points", "Movement", "Competitions Played", "Country"])

    df["Ranks"] = pd.to_numeric(df["Ranks"], errors="coerce")
    df["Points"] = pd.to_numeric(df["Points"], errors="coerce")

    # Applying filters to the Dataframe
    filtered_df = df[
        (df["CompetitorName"].str.contains(name_search, case=False, na=False)) &  # Search by name
        (df["Ranks"] >= rank_range[0]) & (df["Ranks"] <= rank_range[1]) &  # Rank range
        (df["Country"].isin(selected_countries)  | ('All' in selected_countries))  &  
        (df["Points"] >= points_threshold[0]) & (df["Points"] <= points_threshold[1])  # Points threshold
    ]

    # Reset index for filtered DataFrame
    df_reset = filtered_df.reset_index(drop=True)
    df_reset.index = df_reset.index + 1  # Start index from 1

    st.dataframe(df_reset)


    # Table 2 Country Wise Analysis
    st.divider()
    st.subheader('Country-Wise Analysis')
    query = f"""
      select  c.country,count(distinct(c.competitor_id)) as TotalCompetitors,avg(cr.points) as AvgPoints
      from Competitors c left join  Competitor_Rankings cr 
      on c.competitor_id=cr.competitor_id     
      group by  c.country;
    """

    # Execute query
    TableResult = Query_DB(connection, query)

    # Create DataFrame
    df2 = pd.DataFrame(TableResult, columns=["Country","TotalCompetitors","Average Points"])
    filtered_df = df2[
        (df2["Country"].isin(selected_countries)  | ('All' in selected_countries))  
    ]


    # Reset index for filtered DataFrame
    df_reset = filtered_df.reset_index(drop=True)
    df_reset.index = df_reset.index + 1  # Start index from 1

    # Display DataFrame in Streamlit
    st.dataframe(df_reset)
    col1,col2=st.columns([5,5])

    # Plotting the Bar Chart for Total Competitors per Country
    with col1:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        bars=ax.bar(filtered_df ['Country'], filtered_df ['TotalCompetitors'], color='skyblue')
        ax.set_xlabel('Country')
        ax.set_ylabel('Total Competitors')
        ax.set_title('Total Competitors by Country')
        # Add labels on top of each bar
        for bar in bars:
            yval = bar.get_height()  # Get the height of the bar
            ax.text(bar.get_x() + bar.get_width() / 2, yval,  # Position of the label
                    round(yval, 0),  # Label value (rounded)
                    ha='center', va='bottom',  # Alignment
                    fontsize=10, color='black')  # Style
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Plotting the Column Chart for Avg Points per Country
    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        bars=ax.bar(filtered_df['Country'], filtered_df['Average Points'], color='lightgrey')
        ax.set_xlabel('Country')
        ax.set_ylabel('Avgerage Points')
        ax.set_title('Average Points by Country')
        for bar in bars:
            yval = bar.get_height()  # Get the height of the bar
            ax.text(bar.get_x() + bar.get_width() / 2, yval,  # Position of the label
                    round(yval, 0),  # Label value (rounded)
                    ha='center', va='bottom',  # Alignment
                    fontsize=10, color='black') 
        plt.xticks(rotation=45)
        st.pyplot(fig)

    

    
def Leaderboards(connection,option):

    
    if option=='Top-ranked Competitors':
        #1st View 
        query = """
        select distinct cr.rank as Ranks, c.name as CompetitorName, cr.points as Points , c.country as Country
        from Competitors c left join Competitor_Rankings cr 
        on c.competitor_id=cr.competitor_id
        order by cr.rank asc limit 10;

            """

        # Execute query
        TableResult = Query_DB(connection, query)

        # Create DataFrame
        df = pd.DataFrame(TableResult, columns=["Ranks", "CompetitorName", "Points", "Country"])
        st.markdown("### 🏅 **The Top Tier**")
        # Reset index for filtered DataFrame
        df_reset =df.reset_index(drop=True)
        df_reset.index = df_reset.index + 1  # Start index from 1
        st.dataframe(df_reset)
        
        st.markdown("### 🏆 **Champions’ Circle**")
        plt.figure(figsize=(6, 6))
        highest_points_idx = df['Points'].idxmax()

        explode = [0.1 if i == highest_points_idx else 0 for i in range(len(df))]
        plt.pie(df['Points'], labels=df['CompetitorName'], autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors, 
            wedgeprops={'edgecolor': 'Green', 'linewidth': 1},explode=explode,shadow=True)  
        plt.title('Points Distribution Among Top Competitors')
        plt.axis('equal') 
        st.pyplot(plt)

    else:
        #2nd View
        query = """
        select distinct cr.rank as Ranks, c.name as CompetitorName, cr.points as Points , c.country as Country
        from Competitors c left join Competitor_Rankings cr 
        on c.competitor_id=cr.competitor_id
        order by cr.points desc limit 10;

            """

        # Execute query
        TableResult = Query_DB(connection, query)

        # Create DataFrame
        df = pd.DataFrame(TableResult, columns=["Ranks", "CompetitorName", "Points", "Country"])
        st.markdown("### 💯 **Point Masters**")
        # Reset index for filtered DataFrame
        df_reset =df.reset_index(drop=True)
        df_reset.index = df_reset.index + 1  # Start index from 1
        st.dataframe(df_reset)

        # Display DataFrame in Streamlit
        fig, ax = plt.subplots(figsize=(8, 7))
        st.markdown("### 🎯 **The Points Leaders**")
        bars=ax.bar(df['CompetitorName'],df['Points'], color='lightgreen')
        ax.set_xlabel('CompetitorName')
        ax.set_ylabel('Points')
        ax.set_title('Competitors with Highest Points',color="Green")
        for bar in bars:
            yval = bar.get_height()  # Get the height of the bar
            ax.text(bar.get_x() + bar.get_width() / 2, yval,  # Position of the label
                    round(yval, 0),  # Label value (rounded)
                    ha='center', va='bottom',  # Alignment
                    fontsize=10, color='black') 
        plt.xticks(rotation=45)
        st.pyplot(fig)

    


# Main app logic
def main():
    # Call the sidebar method
    connection=DB_Connection()
    selected_tab = create_sidebar(connection)
    # Handle navigation
    if selected_tab == "Competition Insights":
        
        competition_type, gender,category=DynamicFilters(connection,"Competition Insights")
        Competitions(connection,competition_type, gender, category)
         
    elif selected_tab == "Competitor Analytics":
    
        name_search,rank_range,selected_countries,points_threshold=DynamicFilters(connection,"Competitor Analytics")
        Competitors(connection,name_search,rank_range,selected_countries,points_threshold)
    elif selected_tab == "Leaderboards":

        st.header("Leaderboards")
        Leaderboardoption=DynamicFilters(connection,"Leaderboards")
        Leaderboards(connection,Leaderboardoption)

    elif selected_tab == "About":
        st.header("About the App")
        
        st.write("The Tennis Analytics Application is a project designed to track and analyze real-time tennis data using the SportRadar API. The app stores match results, player rankings, and tournament details in a MySQL database called TennisStatsPro.Built with Streamlit, the app provides a user-friendly interface where you can explore data, view player stats, and analyze tournaments through interactive visualizations.")
        st.image("C:/Users/joeli/Downloads/AboutImage.webp", width=1000)
if __name__ == "__main__":
    main()

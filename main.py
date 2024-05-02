import streamlit as st
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
import seaborn as sns

def define_database_schema():
    try:
        conn = sqlite3.connect('player_data.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS PlayerData
                     (player_id INTEGER PRIMARY KEY, `Player’s_information` TEXT, games_played INTEGER, total_winnings REAL)''')
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error occurred while defining database schema: {e}")

def select_columns(data):
    st.write("Please select the columns you want to include in the analysis:")
    selected_columns = st.multiselect("Columns", data.columns.tolist())
    if not selected_columns:
        st.warning("Please select at least one column.")
        return None
    return data[selected_columns]

def read_player_data(file_path):
    try:
        if file_path is not None:
            if file_path.name.endswith('.txt'):
                df = pd.read_csv(file_path, sep='\t')
                csv_path = os.path.splitext(file_path.name)[0] + '.csv'
                df.to_csv(csv_path, index=False)
                return csv_path
            elif file_path.name.endswith('.csv'):
                return file_path
            else:
                st.error("Unsupported file format. Please upload a .txt or .csv file.")
                return None
        else:
            st.warning("No file uploaded.")
            return None
    except Exception as e:
        st.error(f"Error occurred while reading file: {e}")
        return None

def convert_and_store_player_data(file_path):
    try:
        player_data_path = read_player_data(file_path)
        
        if player_data_path is not None:
            player_data = pd.read_csv(player_data_path)
            selected_data = select_columns(player_data)
            
            if selected_data is not None:
                conn = sqlite3.connect('player_data.db')
                selected_data.to_sql('PlayerData', conn, if_exists='replace', index=False)
                conn.commit()
                conn.close()
                
                st.success("Player data has been successfully converted and stored in the database.")
                return player_data_path
    except Exception as e:
        st.error(f"Error occurred while converting and storing player data: {e}")
        return None

def populate_sqlite_database(player_data_path):
    try:
        if player_data_path is not None:
            conn = sqlite3.connect('player_data.db')
            player_data = pd.read_csv(player_data_path)
            player_data.to_sql('PlayerData', conn, if_exists='replace', index=False)
            conn.commit()
            conn.close()

            st.success("SQLite database has been successfully populated with player data.")
        else:
            st.error("No data to populate the database. Please upload player data first.")
    except Exception as e:
        st.error(f"Error occurred while populating SQLite database: {e}")

def execute_sql_query(query):
    try:
        conn = sqlite3.connect('player_data.db')
        c = conn.cursor()
        c.execute(query)
        result = c.fetchall()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error occurred while executing SQL query: {e}")
        return None

def generate_sql_queries(data):
    try:
        columns = [f"`{col}`" for col in data.columns] 
        count_query = "SELECT COUNT(*) FROM PlayerData"
        sum_query = f"SELECT {', '.join(columns)} FROM PlayerData GROUP BY {columns[0]}"  
        return count_query, sum_query
    except Exception as e:
        st.error(f"Error occurred while generating SQL queries: {e}")
        return None, None

def visualize_results(result, query_type):
    try:
        if query_type == "count":
            st.write("Count Visualization")
            counts = [res[0] for res in result]
            sns.barplot(x=range(len(counts)), y=counts, palette="viridis")  
            plt.xlabel("Index")
            plt.ylabel("Count")
            plt.title("Count Visualization")
            plt.xticks(rotation=45) 
            st.pyplot()
            
        elif query_type == "sum":
            st.write("Sum Visualization")
            if len(result[0]) == 1:  
                players = [res[0] for res in result]
                winnings = [0 for _ in range(len(players))]  
                result.sort(key=lambda x: x[1], reverse=True)
                players = [res[0] for res in result]
                winnings = [res[1] for res in result]
            labels = [f"{player}: {winnings}" for player, winnings in zip(players, winnings)]
            st.bar_chart({label: winnings for label, winnings in zip(labels, winnings)})
            
    except Exception as e:
        st.error(f"Error occurred while visualizing results: {e}")

def main():
    st.title('Texas Hold\'em Poker Data Analysis App')
    st.sidebar.header('Upload Player Data')
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=['txt', 'csv'])
    
    if uploaded_file is not None:
        player_data_path = convert_and_store_player_data(uploaded_file)
        
        if player_data_path is not None:
            populate_sqlite_database(player_data_path)

            player_data = pd.read_csv(player_data_path)
            count_query, sum_query = generate_sql_queries(player_data)

            result1 = execute_sql_query(count_query)
            result2 = execute_sql_query(sum_query)

            st.write("SQLite Query Results:")
            st.write("Query 1 Result:")
            if result1:
                st.write(pd.DataFrame(result1, columns=["Count"]))
            else:
                st.write("No data available.")

            st.write("Query 2 Result:")
            if result2:
                if len(result2[0]) == 1:
                    st.write(pd.DataFrame(result2, columns=["Player"]))
                else:
                    st.write(pd.DataFrame(result2, columns=["Player", "Total Winnings"]))
            else:
                st.write("No data available.")

            visualize_results(result1, "count")
            visualize_results(result2, "sum")

if __name__ == '__main__':
    define_database_schema()
    main()

# pylint: disable=missing-module-docstring

import logging
import os
from datetime import date, timedelta

import duckdb
import streamlit as st

if "data" not in os.listdir():  # vérifie si le dossier data existe
    print("creating folder data")
    logging.error(os.listdir())  # affiche les fichiers
    logging.error("creating folder data")  # avertie de la création du dossier data
    os.mkdir("data")  # création du dossier

if "exercises_sql_tables.duckdb" not in os.listdir(
    "data"
):  # vérification de la présence de BD
    exec(open("init_db.py").read())  # Si pas présente, execute le script int_bd
    # subprocess.run(["python", "init_db.py"])

con = duckdb.connect(
    database="data/exercises_sql_tables.duckdb", read_only=False
)  # connection à la BD


def check_users_solution(user_query: str) -> None:
    """
    Checks that user SQL query is correct by:
    1: checking the columns
    2: checking the values
    :param user_query: a string containing the query inserted by the user
    """
    result = con.execute(user_query).df()
    st.dataframe(result)
    try:
        result = result[solution_df.columns]
        st.dataframe(result.compare(solution_df))
        if result.compare(solution_df).shape == (0, 0):
            st.write("Correct !")
            st.balloons()
    except KeyError as e:
        st.write("Some columns are missing")
    n_lines_difference = result.shape[0] - solution_df.shape[0]
    if n_lines_difference != 0:
        st.write(
            f"result has a {n_lines_difference} lines difference with the solution_df"
        )


with st.sidebar:
    available_themes_df = con.execute("SELECT DISTINCT theme FROM memory_state").df()
    theme = st.selectbox(
        "What would you like to review?",
        available_themes_df["theme"].unique(),
        index=None,
        placeholder="Select a theme...",
    )
    if theme:
        st.write(f"You selected {theme}")
        select_exercise_query = f"SELECT * FROM memory_state WHERE theme = '{theme}'"
    else:
        select_exercise_query = f"SELECT * FROM memory_state"

    exercise = (
        con.execute(select_exercise_query)
        .df()
        .sort_values("last_reviewed")
        .reset_index(drop=True)
    )  # affichage des exercices en fonction de la date de la dernière review
    st.write(exercise)
    exercise_name = exercise.loc[
        0, "exercise_name"
    ]  # selection de l'exercie (last_reviewed plus ancien)
    with open(f"answers/{exercise_name}.sql", "r") as f:
        answer = f.read()

    solution_df = con.execute(answer).df()

st.header("enter your code:")
form = st.form("my_form")
query = form.text_area(label="votre code SQL ici", key="user_input")
form.form_submit_button("Submit")

if query:
    check_users_solution(query)

nb_days_to_review = [2, 7, 21]  # proposition nb jours pour revoir l'exo
count_nb_days_to_review = 0
cols_for_days = st.columns(
    [len(nb_days_to_review), 1, len(nb_days_to_review)], vertical_alignment="center"
)  # création des colonnes pour l'affichage

for n_days in [2, 7, 21]:
    with cols_for_days[count_nb_days_to_review]:
        st.button(f"Revoir dans {n_days} jours")
    count_nb_days_to_review += 1
    next_review = date.today() + timedelta(days=n_days)
    con.execute(
        f"UPDATE memory_state SET last_reviewed = '{next_review}' WHERE exercise_name = '{exercise_name}'"
    )
    # st.rerun()

if st.button("Reset"):
    con.execute(f"UPDATE memory_state SET last_reviewed = '1970-01-01'")
    st.rerun()

tab2, tab3 = st.tabs(["Tables", "Solution"])
with tab2:
    exercise_tables = exercise.loc[0, "tables"]
    for table in exercise_tables:
        st.write(f"table: {table}")
        df_table = con.execute(f"SELECT * FROM {table}").df()
        st.dataframe(df_table)

with tab3:
    st.write(answer)

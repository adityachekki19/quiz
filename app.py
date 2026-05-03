import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===============================
# PAGE SETUP
# ===============================
st.set_page_config(page_title="MCQ Dashboard", layout="wide")
st.title("📊 MCQ Quiz Analytics Dashboard")

# ===============================
# LOAD DATA
# ===============================
try:
    df = pd.read_csv("data.csv")

    if len(df.columns) == 1:
        df = df.iloc[:, 0].str.split(",", expand=True)
        df.columns = ["NAME","COLLEGE","DEPARTMENT","Q1","Q2","Q3","Q4","Q5"]

    st.success("✅ Data Loaded Successfully")

except Exception as e:
    st.error(f"❌ Error loading file: {e}")
    st.stop()

# ===============================
# CLEAN DATA
# ===============================
df.columns = df.columns.str.strip().str.upper()
df.fillna("Not Answered", inplace=True)

# ===============================
# FILTERS
# ===============================
st.sidebar.title("📊 Filters")

selected_dept = st.sidebar.selectbox(
    "Department",
    ["All"] + list(df["DEPARTMENT"].unique())
)

has_college = "COLLEGE" in df.columns

if has_college:
    selected_college = st.sidebar.selectbox(
        "College",
        ["All"] + list(df["COLLEGE"].unique())
    )
else:
    selected_college = "All"

# APPLY FILTERS
if selected_dept != "All":
    df = df[df["DEPARTMENT"] == selected_dept]

if has_college and selected_college != "All":
    df = df[df["COLLEGE"] == selected_college]

# 🚨 STOP if no data
if df.empty:
    st.error("❌ No data matches selected filters. Try different options.")
    st.stop()

# ===============================
# ANSWER KEY
# ===============================
answer_key = {
    "Q1": "A",
    "Q2": "C",
    "Q3": "C",
    "Q4": "B",
    "Q5": "D"
}

# ===============================
# CALCULATE SCORE
# ===============================
def calculate_score(row):
    return sum(row[q] == answer_key[q] for q in answer_key)

df["SCORE"] = df.apply(calculate_score, axis=1)

# ===============================
# RANK & RESULT
# ===============================
df["RANK"] = df["SCORE"].rank(ascending=False, method="dense")
df["RESULT"] = df["SCORE"].apply(lambda x: "Pass" if x >= 3 else "Fail")

# ===============================
# STATS
# ===============================
st.subheader("📌 Overall Statistics")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Students", len(df))
col2.metric("Average Score", round(df["SCORE"].mean(), 2))
col3.metric("Highest Score", df["SCORE"].max())
col4.metric("Lowest Score", df["SCORE"].min())

st.markdown("---")

# ===============================
# SCORE DISTRIBUTION
# ===============================
st.subheader("📊 Score Distribution")

fig1, ax1 = plt.subplots()
sns.histplot(df["SCORE"], bins=5, kde=True, ax=ax1)
st.pyplot(fig1)

# ===============================
# PASS / FAIL
# ===============================
st.subheader("✅ Pass vs Fail")

fig_pf, ax_pf = plt.subplots()
sns.countplot(x="RESULT", data=df, ax=ax_pf)
st.pyplot(fig_pf)

# ===============================
# DEPARTMENT PERFORMANCE
# ===============================
st.subheader("🏢 Department Performance")

dept_perf = df.groupby("DEPARTMENT")["SCORE"].mean()

if not dept_perf.empty:
    fig2, ax2 = plt.subplots()
    dept_perf.plot(kind="bar", ax=ax2)
    ax2.set_ylabel("Average Score")
    st.pyplot(fig2)
else:
    st.warning("No department data to plot")

# ===============================
# COLLEGE PERFORMANCE
# ===============================
if has_college:
    st.subheader("🏫 College Performance")

    college_perf = df.groupby("COLLEGE")["SCORE"].mean()

    if not college_perf.empty:
        fig3, ax3 = plt.subplots()
        college_perf.plot(kind="bar", ax=ax3)
        ax3.set_ylabel("Average Score")
        st.pyplot(fig3)
    else:
        st.warning("No college data to plot")

# ===============================
# QUESTION ANALYSIS
# ===============================
st.subheader("❓ Question Analysis")

question_accuracy = {}

for q in answer_key:
    correct = (df[q] == answer_key[q]).sum()
    question_accuracy[q] = correct / len(df) if len(df) > 0 else 0

question_df = pd.DataFrame.from_dict(
    question_accuracy, orient="index", columns=["Accuracy"]
)

fig4, ax4 = plt.subplots()
question_df["Accuracy"].plot(kind="bar", ax=ax4)
st.pyplot(fig4)

# ===============================
# INSIGHTS
# ===============================
st.subheader("🧠 Insights")

best_dept = dept_perf.idxmax()
weak_dept = dept_perf.idxmin()
best_q = question_df["Accuracy"].idxmax()
worst_q = question_df["Accuracy"].idxmin()

st.write(f"✔ Best Performing Department: **{best_dept}**")
st.write(f"⚠ Weak Department: **{weak_dept}**")
st.write(f"✔ Easiest Question: **{best_q}**")
st.write(f"⚠ Most Difficult Question: **{worst_q}**")

# ===============================
# TOP STUDENTS
# ===============================
st.subheader("🏆 Top Students")

top_students = df.sort_values("SCORE", ascending=False).head(5)

if has_college:
    st.dataframe(top_students[["NAME", "RANK", "DEPARTMENT", "COLLEGE", "SCORE"]])
else:
    st.dataframe(top_students[["NAME", "RANK", "DEPARTMENT", "SCORE"]])

# ===============================
# FULL DATA
# ===============================
st.subheader("📋 Full Data")
st.dataframe(df)

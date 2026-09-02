
import streamlit as st
import pandas as pd
import plotly.express as px
import os


# =================================================
# PAGE CONFIGURATION
# =================================================

st.set_page_config(
    page_title="EduPro Predictive Analytics",
    page_icon="📊",
    layout="wide"
)


# =================================================
# LOAD ORIGINAL DATA
# =================================================

@st.cache_data
def load_data():

    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent
    file_path = BASE_DIR / "data" / "EduPro Online Platform.xlsx"


    users = pd.read_excel(
        file_path,
        sheet_name="Users"
    )

    teachers = pd.read_excel(
        file_path,
        sheet_name="Teachers"
    )

    courses = pd.read_excel(
        file_path,
        sheet_name="Courses"
    )

    transactions = pd.read_excel(
        file_path,
        sheet_name="Transactions"
    )

    return users, teachers, courses, transactions


users, teachers, courses, transactions = load_data()


# =================================================
# LOAD FORECAST DATA
# =================================================

@st.cache_data
def load_forecast_data():

    forecast_path = "data/EduPro_Forecast.xlsx"

    if os.path.exists(forecast_path):

        excel_file = pd.ExcelFile(forecast_path)

        forecast_data = pd.read_excel(
            forecast_path,
            sheet_name=excel_file.sheet_names[0]
        )

        return forecast_data, True

    return pd.DataFrame(), False


forecast_data, forecast_file_exists = load_forecast_data()


# =================================================
# SIDEBAR NAVIGATION
# =================================================

st.sidebar.title("📊 EduPro Dashboard")

page = st.sidebar.radio(
    "Select Dashboard Page",
    [
        "Overview",
        "Course Analytics",
        "Teacher Analytics",
        "Revenue & Enrollment Trends",
        "Predictive Analytics"
    ]
)


# =================================================
# OVERVIEW PAGE
# =================================================

if page == "Overview":

    st.title("📊 EduPro Predictive Analytics Dashboard")

    st.write(
        "Interactive analytics dashboard for EduPro users, "
        "teachers, courses, transactions, revenue, and predictions."
    )

    st.divider()

    st.success("EduPro dataset loaded successfully!")

    # -------------------------------------------------
    # KPI OVERVIEW
    # -------------------------------------------------

    st.subheader("Dataset Overview")

    total_revenue = transactions["Amount"].sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Users",
        f"{len(users):,}"
    )

    col2.metric(
        "Total Teachers",
        f"{len(teachers):,}"
    )

    col3.metric(
        "Total Courses",
        f"{len(courses):,}"
    )

    col4.metric(
        "Total Transactions",
        f"{len(transactions):,}"
    )

    col5.metric(
        "Total Revenue",
        f"${total_revenue:,.2f}"
    )

    # -------------------------------------------------
    # DATA PREVIEW
    # -------------------------------------------------

    st.divider()

    st.subheader("Data Preview")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Users",
            "Teachers",
            "Courses",
            "Transactions"
        ]
    )

    with tab1:
        st.dataframe(
            users.head(10),
            use_container_width=True
        )

    with tab2:
        st.dataframe(
            teachers.head(10),
            use_container_width=True
        )

    with tab3:
        st.dataframe(
            courses.head(10),
            use_container_width=True
        )

    with tab4:
        st.dataframe(
            transactions.head(10),
            use_container_width=True
        )


# =================================================
# COURSE ANALYTICS PAGE
# =================================================

if page == "Course Analytics":

    st.title("📚 Course Analytics")

    st.write(
        "Explore course distribution, categories, pricing, "
        "levels, ratings, enrollment, and revenue."
    )

    st.divider()

    # -------------------------------------------------
    # FILTERS
    # -------------------------------------------------

    st.subheader("Filters")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        selected_categories = st.multiselect(
            "Select Course Category",
            options=sorted(
                courses["CourseCategory"].unique()
            ),
            default=sorted(
                courses["CourseCategory"].unique()
            )
        )

    with filter_col2:

        selected_types = st.multiselect(
            "Select Course Type",
            options=sorted(
                courses["CourseType"].unique()
            ),
            default=sorted(
                courses["CourseType"].unique()
            )
        )

    with filter_col3:

        selected_levels = st.multiselect(
            "Select Course Level",
            options=sorted(
                courses["CourseLevel"].unique()
            ),
            default=sorted(
                courses["CourseLevel"].unique()
            )
        )

    # -------------------------------------------------
    # APPLY FILTERS
    # -------------------------------------------------

    filtered_courses = courses[
        (courses["CourseCategory"].isin(
            selected_categories
        ))
        &
        (courses["CourseType"].isin(
            selected_types
        ))
        &
        (courses["CourseLevel"].isin(
            selected_levels
        ))
    ]

    # -------------------------------------------------
    # COMBINE COURSES AND TRANSACTIONS
    # -------------------------------------------------

    course_transactions = transactions.merge(
        courses[
            [
                "CourseID",
                "CourseName",
                "CourseCategory",
                "CourseType",
                "CourseLevel"
            ]
        ],
        on="CourseID",
        how="left"
    )

    filtered_course_transactions = course_transactions[
        (
            course_transactions[
                "CourseCategory"
            ].isin(selected_categories)
        )
        &
        (
            course_transactions[
                "CourseType"
            ].isin(selected_types)
        )
        &
        (
            course_transactions[
                "CourseLevel"
            ].isin(selected_levels)
        )
    ]

    # -------------------------------------------------
    # COURSE KPIs
    # -------------------------------------------------

    st.divider()

    st.subheader("Course Overview")

    total_courses = len(filtered_courses)

    paid_courses = len(
        filtered_courses[
            filtered_courses["CourseType"] == "Paid"
        ]
    )

    free_courses = len(
        filtered_courses[
            filtered_courses["CourseType"] == "Free"
        ]
    )

    average_rating = (
        filtered_courses["CourseRating"].mean()
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric(
        "Total Courses",
        f"{total_courses:,}"
    )

    kpi2.metric(
        "Paid Courses",
        f"{paid_courses:,}"
    )

    kpi3.metric(
        "Free Courses",
        f"{free_courses:,}"
    )

    kpi4.metric(
        "Average Rating",
        f"{average_rating:.2f}"
    )

    # -------------------------------------------------
    # COURSE TYPE AND CATEGORY
    # -------------------------------------------------

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.subheader("Free vs Paid Courses")

        course_type_count = (
            filtered_courses["CourseType"]
            .value_counts()
            .reset_index()
        )

        course_type_count.columns = [
            "Course Type",
            "Number of Courses"
        ]

        fig_type = px.pie(
            course_type_count,
            names="Course Type",
            values="Number of Courses",
            hole=0.4
        )

        st.plotly_chart(
            fig_type,
            use_container_width=True
        )

    with chart_col2:

        st.subheader("Courses by Category")

        category_count = (
            filtered_courses["CourseCategory"]
            .value_counts()
            .reset_index()
        )

        category_count.columns = [
            "Course Category",
            "Number of Courses"
        ]

        fig_category = px.bar(
            category_count,
            x="Course Category",
            y="Number of Courses",
            text_auto=True
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

    # -------------------------------------------------
    # LEVEL AND PRICE
    # -------------------------------------------------

    st.divider()

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:

        st.subheader("Courses by Level")

        level_count = (
            filtered_courses["CourseLevel"]
            .value_counts()
            .reset_index()
        )

        level_count.columns = [
            "Course Level",
            "Number of Courses"
        ]

        fig_level = px.bar(
            level_count,
            x="Course Level",
            y="Number of Courses",
            text_auto=True
        )

        st.plotly_chart(
            fig_level,
            use_container_width=True
        )

    with chart_col4:

        st.subheader(
            "Average Course Price by Category"
        )

        average_price = (
            filtered_courses
            .groupby("CourseCategory")[
                "CoursePrice"
            ]
            .mean()
            .reset_index()
        )

        fig_price = px.bar(
            average_price,
            x="CourseCategory",
            y="CoursePrice",
            text_auto=".2f"
        )

        st.plotly_chart(
            fig_price,
            use_container_width=True
        )

    # -------------------------------------------------
    # ENROLLMENT AND REVENUE
    # -------------------------------------------------

    st.divider()

    st.subheader(
        "Enrollment and Revenue Analytics"
    )

    enrollment_by_category = (
        filtered_course_transactions
        .groupby("CourseCategory")
        .size()
        .reset_index(
            name="Enrollments"
        )
    )

    revenue_by_category = (
        filtered_course_transactions
        .groupby("CourseCategory")[
            "Amount"
        ]
        .sum()
        .reset_index()
    )

    analytics_col1, analytics_col2 = st.columns(2)

    with analytics_col1:

        st.subheader("Enrollment by Category")

        fig_enrollment_category = px.bar(
            enrollment_by_category,
            x="CourseCategory",
            y="Enrollments",
            text_auto=True
        )

        st.plotly_chart(
            fig_enrollment_category,
            use_container_width=True
        )

    with analytics_col2:

        st.subheader("Revenue by Category")

        fig_revenue_category = px.bar(
            revenue_by_category,
            x="CourseCategory",
            y="Amount",
            text_auto=".2f"
        )

        st.plotly_chart(
            fig_revenue_category,
            use_container_width=True
        )

    # -------------------------------------------------
    # TOP COURSES
    # -------------------------------------------------

    st.divider()

    top_enrollment_courses = (
        filtered_course_transactions
        .groupby("CourseName")
        .size()
        .reset_index(
            name="Enrollments"
        )
        .sort_values(
            by="Enrollments",
            ascending=False
        )
        .head(10)
    )

    top_revenue_courses = (
        filtered_course_transactions
        .groupby("CourseName")[
            "Amount"
        ]
        .sum()
        .reset_index()
        .sort_values(
            by="Amount",
            ascending=False
        )
        .head(10)
    )

    analytics_col3, analytics_col4 = st.columns(2)

    with analytics_col3:

        st.subheader(
            "Top 10 Courses by Enrollment"
        )

        fig_top_enrollment = px.bar(
            top_enrollment_courses,
            x="Enrollments",
            y="CourseName",
            orientation="h",
            text_auto=True
        )

        fig_top_enrollment.update_layout(
            yaxis={
                "categoryorder":
                "total ascending"
            }
        )

        st.plotly_chart(
            fig_top_enrollment,
            use_container_width=True
        )

    with analytics_col4:

        st.subheader(
            "Top 10 Courses by Revenue"
        )

        fig_top_revenue = px.bar(
            top_revenue_courses,
            x="Amount",
            y="CourseName",
            orientation="h",
            text_auto=".2f"
        )

        fig_top_revenue.update_layout(
            yaxis={
                "categoryorder":
                "total ascending"
            }
        )

        st.plotly_chart(
            fig_top_revenue,
            use_container_width=True
        )

    # -------------------------------------------------
    # TOP RATED COURSES
    # -------------------------------------------------

    st.divider()

    st.subheader("Top Rated Courses")

    top_rated_courses = (
        filtered_courses
        .sort_values(
            by="CourseRating",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_rated_courses[
            [
                "CourseName",
                "CourseCategory",
                "CourseType",
                "CourseLevel",
                "CoursePrice",
                "CourseRating"
            ]
        ],
        use_container_width=True
    )

    # -------------------------------------------------
    # COURSE DETAILS
    # -------------------------------------------------

    st.divider()

    st.subheader("Course Details")

    st.dataframe(
        filtered_courses,
        use_container_width=True
    )


# =================================================
# TEACHER ANALYTICS PAGE
# =================================================

if page == "Teacher Analytics":

    st.title("👨‍🏫 Teacher Analytics")

    st.write(
        "Analyze teacher activity, course assignments, "
        "transactions, enrollments, and revenue."
    )

    st.divider()

    # -------------------------------------------------
    # COMBINE TEACHERS WITH TRANSACTIONS
    # -------------------------------------------------

    teacher_transactions = transactions.merge(
        teachers,
        on="TeacherID",
        how="left"
    )

    # -------------------------------------------------
    # TEACHER KPIs
    # -------------------------------------------------

    st.subheader("Teacher Overview")

    total_teachers = len(teachers)

    active_teacher_count = (
        transactions["TeacherID"]
        .nunique()
    )

    avg_transactions_per_teacher = (
        len(transactions)
        / active_teacher_count
        if active_teacher_count > 0
        else 0
    )

    total_teacher_revenue = (
        transactions["Amount"].sum()
    )

    teacher_kpi1, teacher_kpi2, teacher_kpi3, teacher_kpi4 = (
        st.columns(4)
    )

    teacher_kpi1.metric(
        "Total Teachers",
        f"{total_teachers:,}"
    )

    teacher_kpi2.metric(
        "Active Teachers",
        f"{active_teacher_count:,}"
    )

    teacher_kpi3.metric(
        "Avg Transactions per Active Teacher",
        f"{avg_transactions_per_teacher:.1f}"
    )

    teacher_kpi4.metric(
        "Total Revenue",
        f"${total_teacher_revenue:,.2f}"
    )

    # -------------------------------------------------
    # TEACHER TRANSACTION ANALYSIS
    # -------------------------------------------------

    st.divider()

    teacher_transactions_summary = (
        transactions
        .groupby("TeacherID")
        .size()
        .reset_index(
            name="Transactions"
        )
        .sort_values(
            by="Transactions",
            ascending=False
        )
    )

    teacher_revenue_summary = (
        transactions
        .groupby("TeacherID")[
            "Amount"
        ]
        .sum()
        .reset_index()
        .sort_values(
            by="Amount",
            ascending=False
        )
    )

    teacher_chart1, teacher_chart2 = st.columns(2)

    with teacher_chart1:

        st.subheader(
            "Top Teachers by Transactions"
        )

        top_teachers_transactions = (
            teacher_transactions_summary
            .head(10)
        )

        fig_teacher_transactions = px.bar(
            top_teachers_transactions,
            x="TeacherID",
            y="Transactions",
            text_auto=True
        )

        st.plotly_chart(
            fig_teacher_transactions,
            use_container_width=True
        )

    with teacher_chart2:

        st.subheader(
            "Top Teachers by Revenue"
        )

        top_teachers_revenue = (
            teacher_revenue_summary
            .head(10)
        )

        fig_teacher_revenue = px.bar(
            top_teachers_revenue,
            x="TeacherID",
            y="Amount",
            text_auto=".2f"
        )

        st.plotly_chart(
            fig_teacher_revenue,
            use_container_width=True
        )

    # -------------------------------------------------
    # TEACHER PERFORMANCE TABLE
    # -------------------------------------------------

    st.divider()

    st.subheader("Teacher Performance Summary")

    teacher_performance = (
        teacher_transactions_summary
        .merge(
            teacher_revenue_summary,
            on="TeacherID",
            how="left"
        )
    )

    teacher_performance = (
        teacher_performance
        .sort_values(
            by="Amount",
            ascending=False
        )
    )

    st.dataframe(
        teacher_performance,
        use_container_width=True
    )

    # -------------------------------------------------
    # TEACHER DATA
    # -------------------------------------------------

    st.divider()

    st.subheader("Teacher Details")

    st.dataframe(
        teachers,
        use_container_width=True
    )


# =================================================
# REVENUE & ENROLLMENT TRENDS PAGE
# =================================================

if page == "Revenue & Enrollment Trends":

    st.title("📈 Revenue & Enrollment Trends")

    st.write(
        "Analyze revenue, transaction activity, and "
        "enrollment trends over time."
    )

    st.divider()

    # -------------------------------------------------
    # PREPARE DATE DATA
    # -------------------------------------------------

    trend_data = transactions.copy()

    trend_data["TransactionDate"] = pd.to_datetime(
        trend_data["TransactionDate"]
    )

    trend_data["Month"] = (
        trend_data["TransactionDate"]
        .dt.to_period("M")
        .astype(str)
    )

    # -------------------------------------------------
    # KPIs
    # -------------------------------------------------

    total_revenue = trend_data["Amount"].sum()

    total_enrollments = len(trend_data)

    paid_enrollments = len(
        trend_data[
            trend_data["Amount"] > 0
        ]
    )

    average_transaction_value = (
        trend_data["Amount"].mean()
    )

    trend_kpi1, trend_kpi2, trend_kpi3, trend_kpi4 = (
        st.columns(4)
    )

    trend_kpi1.metric(
        "Total Revenue",
        f"${total_revenue:,.2f}"
    )

    trend_kpi2.metric(
        "Total Enrollments",
        f"{total_enrollments:,}"
    )

    trend_kpi3.metric(
        "Paid Enrollments",
        f"{paid_enrollments:,}"
    )

    trend_kpi4.metric(
        "Average Transaction Value",
        f"${average_transaction_value:,.2f}"
    )

    # -------------------------------------------------
    # MONTHLY REVENUE
    # -------------------------------------------------

    st.divider()

    monthly_revenue = (
        trend_data
        .groupby("Month")[
            "Amount"
        ]
        .sum()
        .reset_index()
    )

    monthly_enrollments = (
        trend_data
        .groupby("Month")
        .size()
        .reset_index(
            name="Enrollments"
        )
    )

    trend_chart1, trend_chart2 = st.columns(2)

    with trend_chart1:

        st.subheader("Monthly Revenue Trend")

        fig_monthly_revenue = px.line(
            monthly_revenue,
            x="Month",
            y="Amount",
            markers=True
        )

        st.plotly_chart(
            fig_monthly_revenue,
            use_container_width=True
        )

    with trend_chart2:

        st.subheader(
            "Monthly Enrollment Trend"
        )

        fig_monthly_enrollments = px.line(
            monthly_enrollments,
            x="Month",
            y="Enrollments",
            markers=True
        )

        st.plotly_chart(
            fig_monthly_enrollments,
            use_container_width=True
        )

    # -------------------------------------------------
    # PAYMENT METHOD
    # -------------------------------------------------

    st.divider()

    payment_method_count = (
        trend_data["PaymentMethod"]
        .value_counts()
        .reset_index()
    )

    payment_method_count.columns = [
        "Payment Method",
        "Transactions"
    ]

    payment_method_revenue = (
        trend_data
        .groupby("PaymentMethod")[
            "Amount"
        ]
        .sum()
        .reset_index()
    )

    trend_chart3, trend_chart4 = st.columns(2)

    with trend_chart3:

        st.subheader(
            "Transactions by Payment Method"
        )

        fig_payment_count = px.pie(
            payment_method_count,
            names="Payment Method",
            values="Transactions",
            hole=0.4
        )

        st.plotly_chart(
            fig_payment_count,
            use_container_width=True
        )

    with trend_chart4:

        st.subheader(
            "Revenue by Payment Method"
        )

        fig_payment_revenue = px.bar(
            payment_method_revenue,
            x="PaymentMethod",
            y="Amount",
            text_auto=".2f"
        )

        st.plotly_chart(
            fig_payment_revenue,
            use_container_width=True
        )

    # -------------------------------------------------
    # DAILY TRANSACTION TABLE
    # -------------------------------------------------

    st.divider()

    st.subheader("Recent Transactions")

    recent_transactions = (
        trend_data
        .sort_values(
            by="TransactionDate",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        recent_transactions,
        use_container_width=True
    )


# =================================================
# PREDICTIVE ANALYTICS PAGE
# =================================================

if page == "Predictive Analytics":

    st.title("🔮 Predictive Analytics & Forecasting")

    st.write(
        "Course-level predictive analysis for future "
        "enrollment demand and revenue forecasting."
    )

    st.divider()

    # -------------------------------------------------
    # FORECAST FILE CHECK
    # -------------------------------------------------

from pathlib import Path
import pandas as pd
import streamlit as st


@st.cache_data
def load_forecast_data():

    BASE_DIR = Path(__file__).resolve().parent
    file_path = BASE_DIR / "data" / "EduPro_Forecast.xlsx"

    if not file_path.exists():
        return None

    return pd.read_excel(file_path)


# Load forecast data
forecast_df = load_forecast_data()

forecast_file_exists = forecast_df is not None


        # -------------------------------------------------
        # CHECK REQUIRED COLUMNS
        # -------------------------------------------------

required_columns = [
            "CourseID",
            "CourseName",
            "CourseCategory",
            "CourseType",
            "PastEnrollmentCount",
            "PastRevenue",
            "PredictedEnrollment",
            "PredictedRevenue"
        ]

missing_columns = [
            column
            for column in required_columns
            if column not in forecast_data.columns
        ]

if len(missing_columns) > 0:

            st.error(
                "Some required forecast columns are missing."
            )

            st.write(
                "Missing columns:"
            )

            st.write(
                missing_columns
            )

            st.write(
                "Available columns:"
            )

            st.write(
                forecast_data.columns.tolist()
            )

else:

            # -------------------------------------------------
            # FORECAST KPI OVERVIEW
            # -------------------------------------------------

            st.subheader(
                "Predictive Forecast Overview"
            )

            total_courses = len(
                forecast_data
            )

            predicted_enrollment = (
                forecast_data[
                    "PredictedEnrollment"
                ].sum()
            )

            predicted_revenue = (
                forecast_data[
                    "PredictedRevenue"
                ].sum()
            )

            high_enrollment_threshold = (
                forecast_data[
                    "PredictedEnrollment"
                ].quantile(0.75)
            )

            high_revenue_threshold = (
                forecast_data[
                    "PredictedRevenue"
                ].quantile(0.75)
            )

            high_opportunity_courses = (
                forecast_data[
                    (
                        forecast_data[
                            "PredictedEnrollment"
                        ]
                        >= high_enrollment_threshold
                    )
                    &
                    (
                        forecast_data[
                            "PredictedRevenue"
                        ]
                        >= high_revenue_threshold
                    )
                ]
            )

            kpi1, kpi2, kpi3, kpi4 = (
                st.columns(4)
            )

            kpi1.metric(
                "Courses Forecasted",
                f"{total_courses:,}"
            )

            kpi2.metric(
                "Predicted Enrollment",
                f"{predicted_enrollment:,.0f}"
            )

            kpi3.metric(
                "Predicted Revenue",
                f"${predicted_revenue:,.2f}"
            )

            kpi4.metric(
                "High-Opportunity Courses",
                f"{len(high_opportunity_courses):,}"
            )


            # -------------------------------------------------
            # ACTUAL VS PREDICTED FORECAST
            # -------------------------------------------------

            if (
                "FutureEnrollmentCount"
                in forecast_data.columns
                and
                "FutureRevenue"
                in forecast_data.columns
            ):

                st.divider()

                st.subheader(
                    "Actual vs Predicted Forecast"
                )

                actual_enrollment = (
                    forecast_data[
                        "FutureEnrollmentCount"
                    ].sum()
                )

                actual_revenue = (
                    forecast_data[
                        "FutureRevenue"
                    ].sum()
                )

                enrollment_accuracy = (
                    100
                    -
                    (
                        abs(
                            predicted_enrollment
                            -
                            actual_enrollment
                        )
                        /
                        actual_enrollment
                        * 100
                    )
                )

                revenue_accuracy = (
                    100
                    -
                    (
                        abs(
                            predicted_revenue
                            -
                            actual_revenue
                        )
                        /
                        actual_revenue
                        * 100
                    )
                )

                accuracy_col1, accuracy_col2, accuracy_col3, accuracy_col4 = (
                    st.columns(4)
                )

                accuracy_col1.metric(
                    "Actual Future Enrollment",
                    f"{actual_enrollment:,.0f}"
                )

                accuracy_col2.metric(
                    "Enrollment Forecast Accuracy",
                    f"{enrollment_accuracy:.2f}%"
                )

                accuracy_col3.metric(
                    "Actual Future Revenue",
                    f"${actual_revenue:,.2f}"
                )

                accuracy_col4.metric(
                    "Revenue Forecast Accuracy",
                    f"{revenue_accuracy:.2f}%"
                )

                # ---------------------------------------------
                # ACTUAL VS PREDICTED CHARTS
                # ---------------------------------------------

                forecast_chart1, forecast_chart2 = (
                    st.columns(2)
                )

                with forecast_chart1:

                    enrollment_comparison = pd.DataFrame(
                        {
                            "Metric": [
                                "Actual",
                                "Predicted"
                            ],
                            "Enrollment": [
                                actual_enrollment,
                                predicted_enrollment
                            ]
                        }
                    )

                    fig_enrollment_comparison = px.bar(
                        enrollment_comparison,
                        x="Metric",
                        y="Enrollment",
                        text_auto=".2f",
                        title=(
                            "Actual vs Predicted "
                            "Future Enrollment"
                        )
                    )

                    st.plotly_chart(
                        fig_enrollment_comparison,
                        use_container_width=True
                    )

                with forecast_chart2:

                    revenue_comparison = pd.DataFrame(
                        {
                            "Metric": [
                                "Actual",
                                "Predicted"
                            ],
                            "Revenue": [
                                actual_revenue,
                                predicted_revenue
                            ]
                        }
                    )

                    fig_revenue_comparison = px.bar(
                        revenue_comparison,
                        x="Metric",
                        y="Revenue",
                        text_auto=".2f",
                        title=(
                            "Actual vs Predicted "
                            "Future Revenue"
                        )
                    )

                    st.plotly_chart(
                        fig_revenue_comparison,
                        use_container_width=True
                    )


            # -------------------------------------------------
            # TOP PREDICTED ENROLLMENT COURSES
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "Top Forecast Opportunities"
            )

            top_enrollment = (
                forecast_data[
                    [
                        "CourseName",
                        "CourseCategory",
                        "CourseType",
                        "PredictedEnrollment"
                    ]
                ]
                .sort_values(
                    by="PredictedEnrollment",
                    ascending=False
                )
                .head(10)
            )

            top_revenue = (
                forecast_data[
                    [
                        "CourseName",
                        "CourseCategory",
                        "CourseType",
                        "PredictedRevenue"
                    ]
                ]
                .sort_values(
                    by="PredictedRevenue",
                    ascending=False
                )
                .head(10)
            )

            opportunity_col1, opportunity_col2 = (
                st.columns(2)
            )

            with opportunity_col1:

                st.subheader(
                    "Top 10 Courses by Predicted Enrollment"
                )

                fig_top_predicted_enrollment = px.bar(
                    top_enrollment,
                    x="PredictedEnrollment",
                    y="CourseName",
                    orientation="h",
                    text_auto=".2f",
                    title=(
                        "Highest Predicted "
                        "Future Enrollment"
                    )
                )

                fig_top_predicted_enrollment.update_layout(
                    yaxis={
                        "categoryorder":
                        "total ascending"
                    }
                )

                st.plotly_chart(
                    fig_top_predicted_enrollment,
                    use_container_width=True
                )

            with opportunity_col2:

                st.subheader(
                    "Top 10 Courses by Predicted Revenue"
                )

                fig_top_predicted_revenue = px.bar(
                    top_revenue,
                    x="PredictedRevenue",
                    y="CourseName",
                    orientation="h",
                    text_auto=".2f",
                    title=(
                        "Highest Predicted "
                        "Future Revenue"
                    )
                )

                fig_top_predicted_revenue.update_layout(
                    yaxis={
                        "categoryorder":
                        "total ascending"
                    }
                )

                st.plotly_chart(
                    fig_top_predicted_revenue,
                    use_container_width=True
                )


            # -------------------------------------------------
            # CATEGORY FORECAST ANALYSIS
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "Forecast by Course Category"
            )

            category_forecast = (
                forecast_data
                .groupby("CourseCategory")
                .agg(
                    PredictedEnrollments=(
                        "PredictedEnrollment",
                        "sum"
                    ),
                    PredictedRevenue=(
                        "PredictedRevenue",
                        "sum"
                    )
                )
                .reset_index()
            )

            category_col1, category_col2 = (
                st.columns(2)
            )

            with category_col1:

                fig_category_enrollment = px.bar(
                    category_forecast,
                    x="CourseCategory",
                    y="PredictedEnrollments",
                    text_auto=".2f",
                    title=(
                        "Predicted Enrollment "
                        "by Category"
                    )
                )

                st.plotly_chart(
                    fig_category_enrollment,
                    use_container_width=True
                )

            with category_col2:

                fig_category_revenue = px.bar(
                    category_forecast,
                    x="CourseCategory",
                    y="PredictedRevenue",
                    text_auto=".2f",
                    title=(
                        "Predicted Revenue "
                        "by Category"
                    )
                )

                st.plotly_chart(
                    fig_category_revenue,
                    use_container_width=True
                )


            # -------------------------------------------------
            # PREDICTED ENROLLMENT VS REVENUE
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "Course Opportunity Matrix"
            )

            fig_opportunity = px.scatter(
                forecast_data,
                x="PredictedEnrollment",
                y="PredictedRevenue",
                hover_name="CourseName",
                color="CourseType",
                size="CoursePrice",
                title=(
                    "Predicted Enrollment vs "
                    "Predicted Revenue"
                )
            )

            st.plotly_chart(
                fig_opportunity,
                use_container_width=True
            )


            # -------------------------------------------------
            # HIGH OPPORTUNITY COURSES
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "High-Opportunity Courses"
            )

            if len(high_opportunity_courses) > 0:

                high_opportunity_display = (
                    high_opportunity_courses[
                        [
                            "CourseID",
                            "CourseName",
                            "CourseCategory",
                            "CourseType",
                            "PredictedEnrollment",
                            "PredictedRevenue"
                        ]
                    ]
                    .sort_values(
                        [
                            "PredictedRevenue",
                            "PredictedEnrollment"
                        ],
                        ascending=[
                            False,
                            False
                        ]
                    )
                )

                st.success(
                    f"{len(high_opportunity_courses)} "
                    "courses are identified as "
                    "high-opportunity based on both "
                    "predicted enrollment and revenue."
                )

                st.dataframe(
                    high_opportunity_display,
                    use_container_width=True
                )

            else:

                st.info(
                    "No high-opportunity courses "
                    "were identified using the "
                    "current thresholds."
                )


            # -------------------------------------------------
            # PREDICTIVE INSIGHTS
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "Predictive Insights"
            )

            paid_forecast = (
                forecast_data[
                    forecast_data[
                        "CourseType"
                    ] == "Paid"
                ]
            )

            free_forecast = (
                forecast_data[
                    forecast_data[
                        "CourseType"
                    ] == "Free"
                ]
            )

            predicted_paid_revenue = (
                paid_forecast[
                    "PredictedRevenue"
                ].sum()
            )

            predicted_free_enrollment = (
                free_forecast[
                    "PredictedEnrollment"
                ].sum()
            )

            insight_col1, insight_col2 = (
                st.columns(2)
            )

            with insight_col1:

                st.info(
                    f"📈 **Enrollment Insight:** "
                    f"Free courses are predicted to generate "
                    f"{predicted_free_enrollment:,.0f} "
                    f"future enrollments."
                )

            with insight_col2:

                st.info(
                    f"💰 **Revenue Insight:** "
                    f"Paid courses are predicted to generate "
                    f"${predicted_paid_revenue:,.2f} "
                    f"in future revenue."
                )


            # -------------------------------------------------
            # FULL FORECAST DATA
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "Complete Forecast Dataset"
            )

            st.dataframe(
                forecast_data,
                use_container_width=True
            )
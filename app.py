import pandas as pd
import streamlit as st

# Function to load and transform the data
def transform_data(df):
    # Define the ticket categories
    ticket_categories = ['Change Request', 'Task', 'BIBHCR', 'Incident', 'LM', 'CAT', 'IMPL', 'Service Request']
    
    # Initialize a dictionary to store the transformed data
    owner_count = {}

    # Iterate through the raw dataframe
    for _, row in df.iterrows():
        owner = row['Owner']  # PM (owner)
        
        # Skip "Gayathri Shankar" and "None" or "NaN" owners
        if pd.isna(owner) or owner == "Gayathri Shankar":
            continue
        
        ticket_type = row['Type']  # Type of the ticket (CR, TASK, etc.)
        
        # If the owner is not in the dictionary, add them with initial values for each ticket type
        if owner not in owner_count:
            owner_count[owner] = {category: 0 for category in ticket_categories}  # Initialize all categories with 0
        
        # If the ticket type matches one of the categories, increment its count
        if ticket_type in ticket_categories:
            owner_count[owner][ticket_type] += 1
    
    # Convert the dictionary to a DataFrame
    result_df = pd.DataFrame(owner_count).T  # Transpose so that owners are rows and categories are columns
    
    # Ensure the columns are in the correct order
    result_df = result_df[ticket_categories]
    
    # Calculate the Grand Total column for each owner (sum of all ticket types)
    result_df['Grand Total'] = result_df.sum(axis=1)
    
    # Remove rows where the Grand Total is zero (no tickets)
    result_df = result_df[result_df['Grand Total'] > 0]

    # Add a row at the end with totals for each column
    result_df.loc['Total'] = result_df.sum(axis=0)

    return result_df

# Streamlit UI
def main():
    # Customize Streamlit layout with black background and white text
    st.markdown(
        """
        <style>
        .reportview-container {
            background-color: black;
            color: white;
        }
        h1 {
            color: #FF6347;  /* Tomato color */
        }
        .stButton>button {
            background-color: #FF6347;
            color: white;
            border-radius: 5px;
        }
        .stFileUploader>label {
            background-color: #FF6347;
            color: white;
            border-radius: 5px;
        }
        .stText {
            color: white;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Add a custom logo (Make sure to upload a logo in the directory)
    st.image("logo.png", width=100)

    # Title with animation for emphasis
    st.markdown("<h1>Ticket Data Transformation</h1>", unsafe_allow_html=True)
    
    # Description for the transformed data
    st.write("**Note:** The transformed data may not be 100% accurate. Please verify manually.")
    
    # File Upload
    uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")
    if uploaded_file is not None:
        # Read the Excel file
        df = pd.read_excel(uploaded_file)
        
        # Check the structure of the raw data
        st.write("**Raw Data Preview:**")
        st.dataframe(df.head())

        # Transform the data
        transformed_data = transform_data(df)
        
        # Show the transformed data
        st.write("**Transformed Data:**")
        st.dataframe(transformed_data)

        # Provide an option to download the transformed data as an Excel file
        transformed_file = "transformed_output.xlsx"
        transformed_data.to_excel(transformed_file)

        with open(transformed_file, "rb") as f:
            st.download_button(
                label="Download Transformed Data",
                data=f,
                file_name=transformed_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Run the Streamlit app
if __name__ == "__main__":
    main()


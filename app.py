import streamlit as st
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
from datetime import datetime
import tempfile

from ai_engine import generate_ai_response

from storage import (
    load_opportunities,
    create_opportunity,
    update_opportunity,
    delete_opportunity
)

# -----------------------------------
# LOAD ENV
# -----------------------------------

load_dotenv()

client = OpenAI()

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="AI CRM Opportunity Generator",
    layout="wide"
)

# -----------------------------------
# SESSION STATE DEFAULTS
# -----------------------------------

default_values = {
    "edit_mode": False,
    "edit_opportunity_number": "",
    "view_opportunity": None,
    "ai_generated": False,
    "customer_requirement": "",
    "opportunity_name": "",
    "opportunity_type": "",
    "deal_size": "",
    "commit_status": "",
    "estimated_close_date": None,
    "hardware_value": "",
    "software_value": "",
    "services_value": "",
    "solution_bundle": [],
    "last_audio": None
}

for key, value in default_values.items():

    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------------
# TITLE
# -----------------------------------

st.title("AI CRM Opportunity Generator")

# -----------------------------------
# CUSTOMER REQUIREMENT
# -----------------------------------

st.subheader("Describe Customer Need")

customer_requirement = st.text_area(
    "Customer Requirement",
    value=st.session_state.customer_requirement,
    height=180,
    placeholder="Describe customer needs here or use voice input below..."
)

st.session_state.customer_requirement = customer_requirement

# -----------------------------------
# VOICE INPUT
# -----------------------------------

st.write("Voice Input")

audio = mic_recorder(
    start_prompt="Start Recording",
    stop_prompt="Stop Recording",
    just_once=True,
    use_container_width=True,
    key="recorder"
)

if audio:

    audio_bytes = audio["bytes"]

    if audio_bytes != st.session_state.last_audio:

        st.session_state.last_audio = audio_bytes

        with st.spinner("Transcribing audio..."):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav"
            ) as temp_audio:

                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name

            with open(temp_audio_path, "rb") as audio_file:

                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )

            st.session_state.customer_requirement = (
                transcript.text
            )

        st.success("Voice converted to text")

        st.rerun()

# -----------------------------------
# AI FIELD POPULATION
# -----------------------------------

def populate_ai_fields(ai_data):

    st.session_state.opportunity_name = ai_data.get(
        "opportunity_name",
        ""
    )

    st.session_state.opportunity_type = ai_data.get(
        "opportunity_type",
        "Hardware"
    )

    st.session_state.deal_size = ai_data.get(
        "deal_size",
        ""
    )

    st.session_state.commit_status = ai_data.get(
        "commit_status",
        "Pipeline"
    )

    date_string = ai_data.get(
        "estimated_close_date",
        ""
    )

    try:

        parsed_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()

        st.session_state.estimated_close_date = parsed_date

    except:

        st.session_state.estimated_close_date = None

    st.session_state.hardware_value = ai_data.get(
        "estimated_hardware_value",
        ""
    )

    st.session_state.software_value = ai_data.get(
        "estimated_software_value",
        ""
    )

    st.session_state.services_value = ai_data.get(
        "estimated_services_value",
        ""
    )

    st.session_state.solution_bundle = ai_data.get(
        "solution_bundle",
        []
    )

    st.session_state.ai_generated = True

# -----------------------------------
# AI BUTTONS
# -----------------------------------

col1, col2 = st.columns(2)

with col1:

    if st.session_state.edit_mode:

        regenerate_clicked = st.button(
            "Regenerate Opportunity & Solution with AI",
            use_container_width=True
        )

        if regenerate_clicked:

            try:

                with st.spinner("Generating AI solution..."):

                    ai_data = generate_ai_response(
                        st.session_state.customer_requirement
                    )

                populate_ai_fields(ai_data)

                st.success(
                    "Opportunity regenerated successfully"
                )

            except Exception as e:

                st.error(str(e))

    else:

        generate_clicked = st.button(
            "Generate New Opportunity & Solution with AI",
            use_container_width=True
        )

        if generate_clicked:

            try:

                with st.spinner("Generating AI solution..."):

                    ai_data = generate_ai_response(
                        st.session_state.customer_requirement
                    )

                populate_ai_fields(ai_data)

                st.success(
                    "Opportunity generated successfully"
                )

            except Exception as e:

                st.error(str(e))

with col2:

    if st.session_state.edit_mode:

        new_clicked = st.button(
            "Generate New Opportunity & Solution with AI",
            use_container_width=True
        )

        if new_clicked:

            st.session_state.edit_mode = False
            st.session_state.edit_opportunity_number = ""
            st.session_state.ai_generated = False

            st.session_state.customer_requirement = ""
            st.session_state.opportunity_name = ""
            st.session_state.opportunity_type = "Hardware"
            st.session_state.deal_size = ""
            st.session_state.commit_status = "Pipeline"
            st.session_state.estimated_close_date = None
            st.session_state.hardware_value = ""
            st.session_state.software_value = ""
            st.session_state.services_value = ""
            st.session_state.solution_bundle = []

            st.rerun()

# -----------------------------------
# OPPORTUNITY DETAILS
# -----------------------------------

st.divider()

st.subheader("Opportunity Details")

st.text_input(
    "Opportunity Name",
    key="opportunity_name"
)

opportunity_types = [
    "Select Opportunity Type",
    "Hardware",
    "Software",
    "Networking",
    "Cloud Infrastructure",
    "Security",
    "Services"
]

selected_index = 0

if st.session_state.opportunity_type in opportunity_types:
    selected_index = opportunity_types.index(
        st.session_state.opportunity_type
    )

st.selectbox(
    "Opportunity Type",
    opportunity_types,
    index=selected_index,
    key="opportunity_type"
)

col3, col4 = st.columns(2)

with col3:

    st.text_input(
        "Deal Size",
        key="deal_size"
    )

with col4:

    st.selectbox(
        "Commit Status",
        [
            "Committed",
            "Pipeline",
            "Upside"
        ],
        key="commit_status"
    )

st.date_input(
    "Estimated Close Date",
    key="estimated_close_date"
)

col5, col6, col7 = st.columns(3)

with col5:

    st.text_input(
        "Estimated Hardware Value",
        key="hardware_value"
    )

with col6:

    st.text_input(
        "Estimated Software Value",
        key="software_value"
    )

with col7:

    st.text_input(
        "Estimated Services Value",
        key="services_value"
    )

# -----------------------------------
# SUBMIT BUTTON
# -----------------------------------

st.divider()

submit_label = (
    "Resubmit Opportunity Manually"
    if st.session_state.edit_mode
    else "Submit Opportunity Manually"
)

submit_clicked = st.button(
    submit_label,
    use_container_width=True
)

if submit_clicked:

    opportunity_data = {
        "customer_requirement":
            st.session_state.customer_requirement,

        "opportunity_name":
            st.session_state.opportunity_name,

        "opportunity_type":
            st.session_state.opportunity_type,

        "deal_size":
            st.session_state.deal_size,

        "commit_status":
            st.session_state.commit_status,

        "estimated_close_date":
            str(st.session_state.estimated_close_date),

        "hardware_value":
            st.session_state.hardware_value,

        "software_value":
            st.session_state.software_value,

        "services_value":
            st.session_state.services_value,

        "solution_bundle":
            st.session_state.solution_bundle
    }

    if st.session_state.edit_mode:

        opportunity_data["opportunity_number"] = (
            st.session_state.edit_opportunity_number
        )

        existing_opportunities = load_opportunities()

        for opp in existing_opportunities:

            if (
                opp["opportunity_number"]
                ==
                st.session_state.edit_opportunity_number
            ):

                opportunity_data["created_on"] = (
                    opp["created_on"]
                )

                break

        update_opportunity(opportunity_data)

        st.success("Opportunity updated successfully")

        st.session_state.edit_mode = False

    else:

        create_opportunity(opportunity_data)

        st.success("Opportunity created successfully")

# -----------------------------------
# AI SOLUTION
# -----------------------------------

if st.session_state.ai_generated:

    st.divider()

    st.subheader("AI Suggested Solution")

    table_data = []

    for item in st.session_state.solution_bundle:

        table_data.append({

            "Category": item.get(
                "category",
                "Hardware"
            ),

            "Item": item.get(
                "item",
                item.get("product", "")
            ),

            "Quantity": item.get(
                "quantity",
                ""
            )
        })

    st.table(table_data)

    st.subheader("AI Reasoning")

    for item in st.session_state.solution_bundle:

        reason = item.get(
            "reason",
            ""
        )

        item_name = item.get(
            "item",
            item.get("product", "")
        )

        st.markdown(
            f"""
### {item_name}

- {reason}
"""
        )

# -----------------------------------
# CREATED OPPORTUNITIES
# -----------------------------------

st.divider()

st.subheader("Created Opportunities")

opportunities = load_opportunities()

for opp in opportunities:

    col8, col9, col10, col11 = st.columns(
        [5, 1, 1, 1]
    )

    with col8:

        st.write(
            f"{opp['opportunity_number']} | "
            f"{opp['opportunity_name']}"
        )

    with col9:

        if st.button(
            "View",
            key=f"view_{opp['opportunity_number']}"
        ):

            st.session_state.view_opportunity = opp

    with col10:

        if st.button(
            "Edit",
            key=f"edit_{opp['opportunity_number']}"
        ):

            st.session_state.edit_mode = True

            st.session_state.edit_opportunity_number = (
                opp["opportunity_number"]
            )

            st.session_state.customer_requirement = (
                opp["customer_requirement"]
            )

            st.session_state.opportunity_name = (
                opp["opportunity_name"]
            )

            st.session_state.opportunity_type = (
                opp["opportunity_type"]
            )

            st.session_state.deal_size = (
                opp["deal_size"]
            )

            st.session_state.commit_status = (
                opp["commit_status"]
            )

            st.session_state.hardware_value = (
                opp["hardware_value"]
            )

            st.session_state.software_value = (
                opp["software_value"]
            )

            st.session_state.services_value = (
                opp["services_value"]
            )

            st.session_state.solution_bundle = (
                opp["solution_bundle"]
            )

            st.session_state.ai_generated = True

            st.rerun()

    with col11:

        if st.button(
            "Delete",
            key=f"delete_{opp['opportunity_number']}"
        ):

            delete_opportunity(
                opp["opportunity_number"]
            )

            st.success("Opportunity deleted")

            st.rerun()

# -----------------------------------
# VIEW OPPORTUNITY
# -----------------------------------

if st.session_state.view_opportunity:

    st.divider()

    st.subheader("Opportunity Details View")

    selected = st.session_state.view_opportunity

    st.write(
        f"Opportunity Number: "
        f"{selected['opportunity_number']}"
    )

    st.write(
        f"Opportunity Name: "
        f"{selected['opportunity_name']}"
    )

    st.write(
        f"Opportunity Type: "
        f"{selected['opportunity_type']}"
    )

    st.write(
        f"Deal Size: "
        f"{selected['deal_size']}"
    )

    st.write(
        f"Commit Status: "
        f"{selected['commit_status']}"
    )

    st.write(
        f"Estimated Close Date: "
        f"{selected['estimated_close_date']}"
    )

    st.write(
        f"Hardware Value: "
        f"{selected['hardware_value']}"
    )

    st.write(
        f"Software Value: "
        f"{selected['software_value']}"
    )

    st.write(
        f"Services Value: "
        f"{selected['services_value']}"
    )

    st.write(
        f"Created On: "
        f"{selected['created_on']}"
    )

    st.subheader("Associated AI Solution")

    table_data = []

    for item in selected["solution_bundle"]:

        table_data.append({

            "Category": item.get(
                "category",
                "Hardware"
            ),

            "Item": item.get(
                "item",
                item.get("product", "")
            ),

            "Quantity": item.get(
                "quantity",
                ""
            )
        })

    st.table(table_data)

    st.subheader("AI Reasoning")

    for item in selected["solution_bundle"]:

        item_name = item.get(
            "item",
            item.get("product", "")
        )

        reason = item.get(
            "reason",
            ""
        )

        st.markdown(
            f"""
### {item_name}

- {reason}
"""
        )

    if st.button(
        "Close Opportunity View",
        key="close_opportunity_view",
        use_container_width=True
    ):

        st.session_state.view_opportunity = None

        st.rerun()
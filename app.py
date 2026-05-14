import streamlit as st
import json
import random
import datetime
import os
from openai import OpenAI

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Opportunity Generator",
    layout="wide"
)

st.title("AI Opportunity Generator")

# -----------------------------
# OPENAI CLIENT
# -----------------------------
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# -----------------------------
# JSON STORAGE FILE
# -----------------------------
DATA_FILE = "opportunities.json"

# -----------------------------
# LOAD OPPORTUNITIES
# -----------------------------
def load_opportunities():

    if os.path.exists(DATA_FILE):

        with open(DATA_FILE, "r") as file:
            return json.load(file)

    return []

# -----------------------------
# SAVE OPPORTUNITIES
# -----------------------------
def save_opportunities(data):

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# -----------------------------
# SAFE SOLUTION FORMATTER
# -----------------------------
def display_solution_products(solution_products):

    if isinstance(solution_products, str):

        try:
            solution_products = json.loads(solution_products)

        except:
            solution_products = [solution_products]

    if not solution_products:
        st.info("No solution products available.")
        return

    for item in solution_products:

        # CASE 1 -> DICTIONARY FORMAT
        if isinstance(item, dict):

            product = item.get(
                "product",
                "Unknown Product"
            )

            quantity = item.get(
                "quantity",
                "N/A"
            )

            st.write(
                f"- {product} : {quantity}"
            )

        # CASE 2 -> STRING FORMAT
        else:

            st.write(f"- {item}")

# -----------------------------
# SESSION STATE
# -----------------------------
if "opportunities" not in st.session_state:
    st.session_state.opportunities = load_opportunities()

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if "view_index" not in st.session_state:
    st.session_state.view_index = None

if "generated" not in st.session_state:
    st.session_state.generated = False

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

# -----------------------------
# DEFAULT FORM VALUES
# -----------------------------
default_data = {
    "opportunity_name": "",
    "opportunity_type": "",
    "deal_size": "",
    "commit_status": "No",
    "estimated_close_date": "",
    "estimated_hardware_value": "",
    "estimated_software_value": "",
    "estimated_services_value": "",
    "customer_need": "",
    "solution_products": []
}

if "form_data" not in st.session_state:
    st.session_state.form_data = default_data.copy()

# -----------------------------
# VOICE TO TEXT SECTION
# -----------------------------
st.subheader("Opportunity Quick Create")

st.markdown("### Describe Customer Need")

customer_need = st.text_area(
    "",
    value=st.session_state.form_data["customer_need"],
    height=150
)

# -----------------------------
# VOICE INPUT
# -----------------------------
st.markdown("#### Voice Input")

audio_file = st.audio_input("Click to record voice")

if audio_file is not None:

    with st.spinner("Transcribing voice to text..."):

        try:

            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file
            )

            transcribed_text = transcript.text

            st.session_state.form_data[
                "customer_need"
            ] = transcribed_text

            st.success(
                "Voice converted to text successfully"
            )

            st.text_area(
                "Transcribed Text",
                value=transcribed_text,
                height=120
            )

            customer_need = transcribed_text

        except Exception as e:

            st.error(
                f"Voice transcription failed: {e}"
            )

# -----------------------------
# BUTTON SECTION
# -----------------------------
col1, col2 = st.columns([3, 3])

with col1:

    generate_clicked = st.button(
        "Generate New Opportunity and Solution with AI",
        use_container_width=True
    )

with col2:

    if st.session_state.edit_index is not None:

        regenerate_clicked = st.button(
            "Regenerate Opportunity and Solution with AI",
            use_container_width=True
        )

    else:

        regenerate_clicked = False

# -----------------------------
# AI GENERATION
# -----------------------------
if generate_clicked or regenerate_clicked:

    if customer_need.strip() == "":

        st.warning(
            "Please enter customer requirement"
        )

    else:

        with st.spinner(
            "Generating opportunity using AI..."
        ):

            try:

                prompt = f"""
                You are a CRM sales assistant.

                Based on this customer requirement:
                {customer_need}

                Generate:
                1. Opportunity Name
                2. Opportunity Type
                3. Deal Size
                4. Commit Status
                5. Estimated Close Date
                6. Estimated Hardware Value
                7. Estimated Software Value
                8. Estimated Services Value
                9. Suggested Solution Products

                Return ONLY valid JSON.
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content":
                            "You are a CRM sales assistant."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={
                        "type": "json_object"
                    }
                )

                ai_data = json.loads(
                    response.choices[0]
                    .message.content
                )

                st.session_state.form_data = {

                    "opportunity_name":
                    ai_data.get(
                        "Opportunity Name",
                        "School Infrastructure Setup"
                    ),

                    "opportunity_type":
                    ai_data.get(
                        "Opportunity Type",
                        "Hardware"
                    ),

                    "deal_size":
                    ai_data.get(
                        "Deal Size",
                        "500000"
                    ),

                    "commit_status":
                    ai_data.get(
                        "Commit Status",
                        "No"
                    ),

                    "estimated_close_date":
                    ai_data.get(
                        "Estimated Close Date",
                        "2026-06-30"
                    ),

                    "estimated_hardware_value":
                    ai_data.get(
                        "Estimated Hardware Value",
                        "300000"
                    ),

                    "estimated_software_value":
                    ai_data.get(
                        "Estimated Software Value",
                        "100000"
                    ),

                    "estimated_services_value":
                    ai_data.get(
                        "Estimated Services Value",
                        "100000"
                    ),

                    "customer_need":
                    customer_need,

                    "solution_products":
                    ai_data.get(
                        "Suggested Solution Products",
                        [
                            {
                                "product":
                                "Dell Monitor",

                                "quantity":
                                50
                            },
                            {
                                "product":
                                "HP Keyboard",

                                "quantity":
                                50
                            }
                        ]
                    )
                }

                st.session_state.generated = True

                st.success(
                    "AI generated opportunity "
                    "and solution successfully"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"AI Generation Failed: {e}"
                )

# -----------------------------
# OPPORTUNITY DETAILS
# -----------------------------
st.header("Opportunity Details")

fd = st.session_state.form_data

fd["opportunity_name"] = st.text_input(
    "Opportunity Name",
    value=fd["opportunity_name"]
)

opportunity_types = [
    "Hardware",
    "Software",
    "Networking",
    "Cloud Infra",
    "Services"
]

selected_type = fd["opportunity_type"]

if selected_type not in opportunity_types:
    selected_type = "Hardware"

fd["opportunity_type"] = st.selectbox(
    "Opportunity Type",
    opportunity_types,
    index=opportunity_types.index(
        selected_type
    )
)

fd["deal_size"] = st.text_input(
    "Deal Size",
    value=fd["deal_size"]
)

fd["commit_status"] = st.selectbox(
    "Commit Opportunity",
    ["Yes", "No"],
    index=0 if
    fd["commit_status"] == "Yes"
    else 1
)

fd["estimated_close_date"] = st.text_input(
    "Estimated Close Date",
    value=fd["estimated_close_date"]
)

fd["estimated_hardware_value"] = st.text_input(
    "Estimated Hardware Value",
    value=fd["estimated_hardware_value"]
)

fd["estimated_software_value"] = st.text_input(
    "Estimated Software Value",
    value=fd["estimated_software_value"]
)

fd["estimated_services_value"] = st.text_input(
    "Estimated Services Value",
    value=fd["estimated_services_value"]
)

# -----------------------------
# SUBMIT BUTTON
# -----------------------------
submit_label = (

    "Resubmit Opportunity Manually"

    if st.session_state.edit_index
    is not None

    else

    "Submit Opportunity Manually"
)

submit_clicked = st.button(
    submit_label,
    use_container_width=True
)

# -----------------------------
# AI SUGGESTED SOLUTION
# -----------------------------
if st.session_state.generated:

    st.header("AI Suggested Solution")

    solution_products = fd.get(
        "solution_products",
        []
    )

    display_solution_products(
        solution_products
    )

# -----------------------------
# SUBMIT LOGIC
# -----------------------------
if submit_clicked:

    opportunity_number = (
        f"OPP-{random.randint(10000,99999)}"
    )

    created_when = str(
        datetime.datetime.now()
    )

    record = {
        "opportunity_number":
        opportunity_number,

        "created_when":
        created_when,

        **fd
    }

    if st.session_state.edit_index is not None:

        old_record = (
            st.session_state.opportunities[
                st.session_state.edit_index
            ]
        )

        record["opportunity_number"] = (
            old_record["opportunity_number"]
        )

        record["created_when"] = (
            old_record["created_when"]
        )

        st.session_state.opportunities[
            st.session_state.edit_index
        ] = record

        st.success(
            "Opportunity updated successfully"
        )

        st.session_state.edit_index = None

    else:

        st.session_state.opportunities.append(
            record
        )

        st.success(
            "Opportunity created successfully"
        )

    save_opportunities(
        st.session_state.opportunities
    )

    st.session_state.form_data = (
        default_data.copy()
    )

    st.session_state.generated = False

    st.rerun()

# -----------------------------
# CREATED OPPORTUNITIES
# -----------------------------
st.header("Created Opportunities")

for index, opp in enumerate(
    st.session_state.opportunities
):

    c1, c2, c3, c4 = st.columns(
        [6, 1, 1, 1]
    )

    with c1:

        st.write(
            f"{opp['opportunity_number']} - "
            f"{opp['opportunity_name']}"
        )

    with c2:

        if st.button(
            "View",
            key=f"view_{index}"
        ):

            st.session_state.view_index = index

            st.rerun()

    with c3:

        if st.button(
            "Edit",
            key=f"edit_{index}"
        ):

            st.session_state.form_data = opp

            st.session_state.edit_index = index

            st.session_state.generated = True

            st.rerun()

    with c4:

        if st.button(
            "Delete",
            key=f"delete_{index}"
        ):

            st.session_state.opportunities.pop(
                index
            )

            save_opportunities(
                st.session_state.opportunities
            )

            st.success(
                "Opportunity deleted"
            )

            st.rerun()

# -----------------------------
# VIEW OPPORTUNITY
# -----------------------------
if st.session_state.view_index is not None:

    st.divider()

    selected = (
        st.session_state.opportunities[
            st.session_state.view_index
        ]
    )

    st.header(
        "Opportunity Details View"
    )

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
        f"Estimated Hardware Value: "
        f"{selected['estimated_hardware_value']}"
    )

    st.write(
        f"Estimated Software Value: "
        f"{selected['estimated_software_value']}"
    )

    st.write(
        f"Estimated Services Value: "
        f"{selected['estimated_services_value']}"
    )

    st.write(
        f"Customer Need: "
        f"{selected['customer_need']}"
    )

    st.subheader("Associated Solution")

    solution_products = selected.get(
        "solution_products",
        []
    )

    display_solution_products(
        solution_products
    )

    if st.button(
        "Close Opportunity View"
    ):

        st.session_state.view_index = None

        st.rerun()
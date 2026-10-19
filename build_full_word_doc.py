"""Build professional, publication-quality Word (.docx) report for FitTrack MongoDB project."""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_styled_table(doc, headers, data, col_widths=None):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1F4E79")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=150, right=150)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(9.5)
            run.font.name = "Arial"

    # Data Rows
    for r_idx, row in enumerate(data):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F2F4F7" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=90, bottom=90, left=140, right=140)
            p = row_cells[c_idx].paragraphs[0]
            for run in p.runs:
                run.font.size = Pt(9)
                run.font.name = "Arial"

    # Set Column Widths if provided
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

    doc.add_paragraph() # Spacing
    return table

def add_callout_box(doc, text, title=""):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    # Set left border thick blue, others none
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="36" w:space="0" w:color="1F4E79"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    if title:
        r_title = p.add_run(f"{title}\n")
        r_title.bold = True
        r_title.font.name = "Arial"
        r_title.font.size = Pt(10)
        r_title.font.color.rgb = RGBColor(31, 78, 121)

    r_text = p.add_run(text)
    r_text.font.name = "Arial"
    r_text.font.size = Pt(9.5)
    r_text.font.italic = True
    r_text.font.color.rgb = RGBColor(44, 62, 80)
    doc.add_paragraph()

def add_code_block(doc, code_str):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_background(cell, "252526")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(code_str)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(212, 212, 212)
    doc.add_paragraph()

def add_figure(doc, img_path, caption, width=Inches(6.0)):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run = p_img.add_run()
        run.add_picture(img_path, width=width)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = "Arial"
        r_cap.font.size = Pt(9.5)
        r_cap.font.bold = True
        r_cap.font.color.rgb = RGBColor(52, 73, 94)

def build_report():
    doc = Document()

    # Page Margins (Standard 1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base Styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Arial'
    style_normal.font.size = Pt(10.5)
    style_normal.font.color.rgb = RGBColor(40, 40, 40)
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # COVER / TITLE PAGE
    # -------------------------------------------------------------
    logo_path = os.path.join("report_assets", "lpu_logo.jpeg")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(10)
        p_logo.paragraph_format.space_after = Pt(15)
        p_logo.add_run().add_picture(logo_path, width=Inches(3.8))

    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_univ = p_univ.add_run("LOVELY PROFESSIONAL UNIVERSITY, PHAGWARA, PUNJAB\nSCHOOL OF COMPUTER SCIENCE AND ENGINEERING\nINTELLIGENT NOSQL DATABASES (CSE494)")
    r_univ.font.size = Pt(11)
    r_univ.font.bold = True
    r_univ.font.color.rgb = RGBColor(31, 78, 121)

    p_rep = doc.add_paragraph()
    p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep.paragraph_format.space_before = Pt(15)
    r_rep = p_rep.add_run("ACADEMIC TASK 2 – PROJECT REPORT")
    r_rep.font.size = Pt(13)
    r_rep.font.bold = True
    r_rep.font.color.rgb = RGBColor(192, 57, 43)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(30)
    r_title = p_title.add_run("FITTRACK – HEALTH & DIET TRACKER\nUSING MONGODB AND PYMONGO")
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(26, 82, 118)

    # Student & Supervisor Info Box Table
    info_table = doc.add_table(rows=1, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.autofit = False
    c_left = info_table.rows[0].cells[0]
    c_right = info_table.rows[0].cells[1]
    c_left.width = Inches(3.2)
    c_right.width = Inches(3.2)
    set_cell_background(c_left, "F8F9FA")
    set_cell_background(c_right, "F8F9FA")
    set_cell_margins(c_left, 120, 120, 150, 150)
    set_cell_margins(c_right, 120, 120, 150, 150)

    p_sub = c_left.paragraphs[0]
    r_sub = p_sub.add_run("Submitted by:\n")
    r_sub.bold = True
    r_sub.font.color.rgb = RGBColor(31, 78, 121)
    p_sub.add_run(
        "Akhil\n"
        "Registration No.: 12307177\n"
        "Programme: B.Tech (CSE)\n"
        "Section: K3P23WA\n"
        "Course Code: CSE494"
    )

    p_guid = c_right.paragraphs[0]
    r_guid = p_guid.add_run("Under the Guidance of:\n")
    r_guid.bold = True
    r_guid.font.color.rgb = RGBColor(31, 78, 121)
    p_guid.add_run(
        "Jaffar Amin Chacket\n"
        "Assistant Professor\n"
        "School of Computer Science & Engg.\n"
        "Lovely Professional University\n"
        "Date: 19th October, 2026"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CERTIFICATE
    # -------------------------------------------------------------
    h_cert = doc.add_heading("CERTIFICATE", level=1)
    h_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()

    doc.add_paragraph(
        "This is to certify that the project report entitled “FitTrack – Health & Diet Tracker using MongoDB and PyMongo” "
        "has been prepared and submitted by Akhil (Registration No.: 12307177) in partial fulfillment of the requirements for "
        "the course CSE494 – Intelligent NoSQL Databases in the School of Computer Science and Engineering, Lovely Professional University, "
        "Phagwara, Punjab."
    )
    doc.add_paragraph(
        "The project demonstrates the end-to-end design, implementation, and empirical validation of a high-performance "
        "document database system. The work features strict database-level schema constraints using MongoDB $jsonSchema, "
        "a hybrid data architecture combining embedded sub-documents and referenced time-series collections, compound query indexing, "
        "and nine real-time analytical aggregation pipelines executed through the Python PyMongo driver."
    )
    doc.add_paragraph(
        "The work is submitted for academic evaluation under my guidance. The final approval and certification are subject to verification "
        "by the faculty supervisor."
    )

    doc.add_paragraph("\n\n")
    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_sig = p_sig.add_run(
        "_____________________________\n"
        "Jaffar Amin Chacket\n"
        "Assistant Professor\n"
        "School of Computer Science and Engineering\n"
        "Lovely Professional University, Phagwara, Punjab\n"
        "Date: 19-10-2026"
    )
    r_sig.font.size = Pt(10)

    doc.add_page_break()

    # -------------------------------------------------------------
    # DECLARATION & ACKNOWLEDGEMENT
    # -------------------------------------------------------------
    h_decl = doc.add_heading("DECLARATION", level=1)
    h_decl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()

    doc.add_paragraph(
        "I hereby declare that this project report entitled “FitTrack – Health & Diet Tracker using MongoDB and PyMongo” is an authentic "
        "record of my own academic work carried out for the course CSE494 – Intelligent NoSQL Databases under the supervision of "
        "Mr. Jaffar Amin Chacket, Assistant Professor, School of Computer Science and Engineering, Lovely Professional University."
    )
    doc.add_paragraph(
        "The implementation, schemas, queries, and analytical outputs reported herein represent genuine executions performed against a live "
        "MongoDB Community Server (v8.2.3) environment via PyMongo. Any external documentation, standards, or code libraries utilized have "
        "been appropriately acknowledged and cited."
    )

    p_decl_sig = doc.add_paragraph()
    p_decl_sig.paragraph_format.space_before = Pt(20)
    p_decl_sig.add_run(
        "Date: 19-10-2026\n"
        "Registration No.: 12307177\n"
        "Name: Akhil\n"
        "Section: K3P23WA"
    )

    doc.add_paragraph("\n")
    h_ack = doc.add_heading("ACKNOWLEDGEMENT", level=1)
    h_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()

    doc.add_paragraph(
        "I would like to express my sincere gratitude to my supervisor, Mr. Jaffar Amin Chacket, Assistant Professor, "
        "School of Computer Science and Engineering, Lovely Professional University, for his continuous guidance, technical insights, "
        "and encouragement throughout the design and realization of this NoSQL database project."
    )
    doc.add_paragraph(
        "I also extend my sincere appreciation to the faculty members and laboratory staff of the School of Computer Science and Engineering "
        "for providing the academic environment and computing resources necessary to complete this assessment. "
        "Finally, I acknowledge the extensive documentation and resources provided by the MongoDB Open Source Community and the PyMongo "
        "engineering team, which significantly aided my understanding of document modeling, indexing strategies, and aggregation pipeline design."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # TABLE OF CONTENTS, LIST OF FIGURES & TABLES
    # -------------------------------------------------------------
    doc.add_heading("TABLE OF CONTENTS", level=1)
    toc_items = [
        ("Certificate", "2"),
        ("Declaration & Acknowledgement", "3"),
        ("List of Figures", "4"),
        ("List of Tables", "5"),
        ("1. Introduction", "6"),
        ("2. Problem Domain and System Requirements", "8"),
        ("3. Data Source and Data Description", "10"),
        ("4. Database Design and Data Modeling", "13"),
        ("5. MongoDB Implementation", "16"),
        ("6. Advanced MongoDB Operations", "19"),
        ("7. Application Integration", "24"),
        ("8. Results and Output Analysis", "26"),
        ("9. Discussion & Technical Trade-offs", "31"),
        ("10. Conclusion", "33"),
        ("11. Future Scope", "34"),
        ("12. References", "35"),
    ]
    create_styled_table(doc, ["Section / Chapter Title", "Page No."], toc_items, col_widths=[5.0, 1.5])

    doc.add_heading("LIST OF FIGURES", level=2)
    figures_list = [
        ("Figure 1", "FitTrack Multi-Tier System Architecture (Client to Storage Engine)"),
        ("Figure 2", "FitTrack Hybrid Data Model – Embedded Profile & Referenced Activity Logs"),
        ("Figure 3", "MongoDB Database Initialization and 30-Day Activity Seed Output"),
        ("Figure 4", "Server-Side Schema Validation Test Execution Trace (MongoDB Code 121)"),
        ("Figure 5", "Aggregation Pipeline 1 – Rolling 7-Day Macronutrient & Calorie Breakdown"),
        ("Figure 6", "Aggregation Pipeline 3 – Platform Demographic BMI Distribution"),
        ("Figure 7", "Aggregation Pipeline 4 – Popular Workout Disciplines and Energy Expenditure"),
        ("Figure 8", "Aggregation Pipeline 5 – Real-Time Goal Progress Completion ($lookup)"),
        ("Figure 9", "Aggregation Pipeline 8 – Cross-Collection Net Calorie Balance ($unionWith)"),
    ]
    create_styled_table(doc, ["Figure No.", "Caption / Description"], figures_list, col_widths=[1.5, 5.0])

    doc.add_heading("LIST OF TABLES", level=2)
    tables_list = [
        ("Table 1", "Technologies used and architectural roles"),
        ("Table 2", "Functional requirements (FR-01 to FR-10)"),
        ("Table 3", "Database collection inventory and document statistics (1,746 total records)"),
        ("Table 4", "Schema specifications and boundary constraints for all 8 collections"),
        ("Table 5", "Database indexing strategy and access pattern justification"),
        ("Table 6", "Summary of implemented MongoDB operators and aggregation stages"),
        ("Table 7", "Application methods in crud.py and aggregations.py"),
        ("Table 8", "Validation test case matrix and engine enforcement results"),
        ("Table 9", "Architectural challenges, root risks, and implemented mitigations"),
    ]
    create_styled_table(doc, ["Table No.", "Caption / Description"], tables_list, col_widths=[1.5, 5.0])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 1. INTRODUCTION
    # -------------------------------------------------------------
    doc.add_heading("1. INTRODUCTION", level=1)
    
    doc.add_heading("1.1 Background & Motivation", level=2)
    doc.add_paragraph(
        "Modern health and wellness tracking requires logging multi-dimensional, continuous behavioral events. "
        "A single individual routinely logs diverse meal types with varying nutritional breakdowns, physical exercises "
        "spanning distinct disciplines (e.g., endurance running, resistance training, flexibility yoga), multiple hydration events, "
        "and periodic anthropometric measurements. Relational database architectures (RDBMS) historically enforced rigid tabular schemas, "
        "requiring extensive multi-table JOIN operations, artificial bridge tables, and frequent schema alterations to accommodate "
        "new wellness tags or exercise metrics."
    )
    doc.add_paragraph(
        "FitTrack is a centralized, document-oriented health and nutrition management platform developed using MongoDB and PyMongo. "
        "By leveraging the flexible Binary JSON (BSON) document model, FitTrack demonstrates how modern database architectures eliminate "
        "impedance mismatch, combine embedded documents for cohesive profile retrieval, utilize normalized references for high-volume logs, "
        "and execute real-time analytics directly inside the database engine."
    )

    doc.add_heading("1.2 Problem Statement", level=2)
    doc.add_paragraph(
        "Individuals trying to stay fit keep meal logs, workout notes, hydration tallies, and weight logs across disconnected mobile applications "
        "or paper notebooks. Consequently, users cannot correlate dietary habits with physical progress or receive personalized guidance "
        "tailored to their Body Mass Index (BMI) and metabolic goals. FitTrack centralizes this data in MongoDB to answer essential operational "
        "and analytical questions:"
    )
    doc.add_paragraph("• What is the user's daily net energy balance (Calories In vs. Calories Out)?")
    doc.add_paragraph("• How consistently does the user meet protein, carbohydrate, and fat targets over rolling 7-day windows?")
    doc.add_paragraph("• What is the exact percentage completion of a weight loss or gain goal based on real-time weigh-ins?")
    doc.add_paragraph("• Which certified diet plans dynamically match the user's calculated BMI category, active goal, and dietary preference?")

    doc.add_heading("1.3 Objectives", level=2)
    doc.add_paragraph("1. Design and implement a robust, production-grade schema across 8 specialized MongoDB collections.")
    doc.add_paragraph("2. Enforce strict server-side schema integrity using MongoDB $jsonSchema validators (validationLevel: strict, validationAction: error).")
    doc.add_paragraph("3. Implement high-performance data access patterns utilizing single-field, compound, and unique BSON indexes.")
    doc.add_paragraph("4. Provide comprehensive Create, Read, Update, and Delete (CRUD) operations via PyMongo with granular error handling.")
    doc.add_paragraph("5. Engineer 9 advanced MongoDB aggregation pipelines featuring multi-stage operations ($lookup, $facet, $unionWith, $switch).")
    doc.add_paragraph("6. Develop a modular Python architecture comprising configuration, schema migration, seed generation, and CLI interface.")

    doc.add_heading("1.4 Scope of the Project", level=2)
    doc.add_paragraph(
        "The project encompasses the end-to-end database design, implementation, and Python integration for health and fitness tracking. "
        "It includes embedded user profiles, goal lifecycle management, meal tracking with macronutrients, multi-category workout logging, "
        "hydration tracking, time-series progress records, expert diet catalogs, and exercise libraries. The scope emphasizes operational data "
        "integrity, index coverage, and real-time analytical computation."
    )

    doc.add_heading("1.5 Significance of the Project", level=2)
    add_callout_box(
        doc,
        "FitTrack highlights key architectural paradigms of NoSQL engineering:\n"
        "1. Hybrid Modeling: Combines embedded sub-documents (1:1 static data) with referenced collections (1:N time-series logs) to prevent the 16MB BSON limit.\n"
        "2. Dynamic Computation: Non-static metrics like BMI are derived dynamically in aggregation pipelines from authoritative base attributes.\n"
        "3. Engine-Level Validation: Proves that MongoDB's schema flexibility can coexist with strict database-level integrity via $jsonSchema.",
        title="Key Architectural Highlights"
    )

    doc.add_heading("1.6 Technologies Used", level=2)
    tech_data = [
        ("MongoDB Community Server", "v8.2.3 (WiredTiger)", "Core document database engine managing BSON persistence, indexes, and aggregation execution"),
        ("Python", "v3.14 / v3.10+", "Primary backend programming language implementing business logic and data access"),
        ("PyMongo", "v4.19.0", "Official Python driver providing client connection pooling, error handling, and BSON serialization"),
        ("MongoDB Shell (mongosh)", "v2.x", "Administrative CLI environment used for interactive query verification and script execution (queries.js)"),
        ("JSON Schema", "Draft 4 ($jsonSchema BSON)", "Database-level constraint definition and validation rules (validationAction: error)"),
        ("PBKDF2-HMAC-SHA256", "10,000 Iterations", "Cryptographic salted hashing for user credentials"),
    ]
    create_styled_table(doc, ["Technology", "Version", "Architectural Role"], tech_data, col_widths=[1.8, 1.4, 3.3])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2. PROBLEM DOMAIN AND SYSTEM REQUIREMENTS
    # -------------------------------------------------------------
    doc.add_heading("2. PROBLEM DOMAIN AND SYSTEM REQUIREMENTS", level=1)

    doc.add_heading("2.1 Domain Overview", level=2)
    doc.add_paragraph(
        "Personal wellness tracking applications handle heterogeneous, continuous streams of user-generated events. "
        "Unlike e-commerce transactions that follow predictable tabular structures, health data includes variable ingredients, "
        "distinct exercise parameters (e.g., distance, repetitions, duration, pace), and diverse dietary constraints. "
        "Capturing this information requires a data model capable of ingesting semi-structured data without constant database migrations."
    )

    doc.add_heading("2.2 Limitations of Existing Relational Implementations", level=2)
    doc.add_paragraph("Traditional relational implementations exhibit several critical architectural bottlenecks:")
    doc.add_paragraph("• Relational Impedance Mismatch: User profiles, physical attributes, and preferences are fragmented across multiple tables, requiring joins for basic profile loading.")
    doc.add_paragraph("• Schema Inflexibility: Introducing specialized workout disciplines or dynamic dietary tags requires schema alterations and table locks.")
    doc.add_paragraph("• High Query Latency: Assembling daily summaries requires multi-table JOIN queries across meals, workouts, and hydration logs that degrade under scale.")
    doc.add_paragraph("• Data Redundancy: Relational systems often store precomputed metrics like BMI, creating data anomalies when underlying weight attributes change.")

    doc.add_heading("2.3 Proposed Document-Oriented System", level=2)
    doc.add_paragraph(
        "FitTrack addresses these constraints through a document-centric architecture: "
        "biometric profile attributes reside directly within the user document for single-read retrieval; high-volume activity logs "
        "are partitioned into referenced collections; and multi-value tags and muscle groups are persisted as native BSON arrays. "
        "Real-time analytics (such as net calorie balance and goal completion) are computed directly within MongoDB's C++ aggregation framework."
    )

    doc.add_heading("2.4 Functional Requirements", level=2)
    fr_data = [
        ("FR-01", "User Registration & Profile Creation", "Securely register users with hashed credentials and an embedded profile containing age, gender, height, weight, activity level, and dietary preference."),
        ("FR-02", "Strict Schema Enforcement", "Reject any document insert or update that violates data types, boundary constraints, regex patterns, or enumeration lists via $jsonSchema."),
        ("FR-03", "Meal Logging & Macro Tracking", "Record meal name, type (breakfast, lunch, dinner, snack), calories, protein, carbohydrates, fat, and timestamp."),
        ("FR-04", "Workout Logging", "Record workout title, category (cardio, strength, yoga, running, cycling), duration in minutes, and estimated calories burned."),
        ("FR-05", "Hydration & Progress Tracking", "Record water consumption events in milliliters and periodic body weight measurements."),
        ("FR-06", "Goal Lifecycle Management", "Define weight and caloric targets, update goal status (active, completed, abandoned), and evaluate progress percentage."),
        ("FR-07", "Dynamic Macro Aggregation", "Compute daily and weekly totals and averages for calories, protein, carbs, and fat over arbitrary date ranges."),
        ("FR-08", "Dynamic BMI & Plan Recommendation", "Calculate user BMI on the fly and match active goals with suitable expert diet plans."),
        ("FR-09", "Cross-Collection Dashboard Analytics", "Synthesize meal intake and workout burn using $facet and $unionWith to present a 360-degree daily net balance."),
        ("FR-10", "Admin Platform Reporting", "Provide administrative aggregations summarizing user engagement, logged activity days, and average caloric trends."),
    ]
    create_styled_table(doc, ["Req ID", "Requirement Title", "Detailed Functional Specification"], fr_data, col_widths=[0.9, 1.8, 3.8])

    doc.add_heading("2.5 Non-Functional Requirements", level=2)
    doc.add_paragraph("• Data Integrity: Enforced at the engine level with validationAction: error, preventing schema violations from persisting.")
    doc.add_paragraph("• Query Performance: All high-frequency queries filter and sort on indexed fields (IXSCAN), avoiding collection scans (COLLSCAN).")
    doc.add_paragraph("• Maintainability: Modular codebase separating configuration (config.py), schema initialization (db.py), data manipulation (crud.py), and analytics (aggregations.py).")
    doc.add_paragraph("• Security: Sensitive user passwords are protected with cryptographic PBKDF2-SHA256 hashing; unique indexes prevent duplicate accounts.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # 3. DATA SOURCE AND DATA DESCRIPTION
    # -------------------------------------------------------------
    doc.add_heading("3. DATA SOURCE AND DATA DESCRIPTION", level=1)

    doc.add_heading("3.1 Source of Data & Seeding Strategy", level=2)
    doc.add_paragraph(
        "FitTrack includes an automated data generation engine implemented in seed.py. The dataset models a realistic fitness community "
        "comprising 7 distinct user personas (spanning varying ages, genders, starting weights, activity tiers, and dietary preferences), "
        "each accompanied by 30 continuous days of historical activity logs (meals, workouts, water intake, and weight progression)."
    )

    doc.add_heading("3.2 Collection Inventory & Statistics", level=2)
    doc.add_paragraph("Execution against local MongoDB Server v8.2.3 confirms the following live collection inventory:")
    coll_data = [
        ("users", "7", "~380 bytes", "_id (ObjectId), email (Unique Index)"),
        ("goals", "6", "~220 bytes", "_id, (user_id, status) Compound Index"),
        ("meals", "679", "~190 bytes", "_id, (user_id, date DESC) Compound Index"),
        ("workouts", "113", "~180 bytes", "_id, (user_id, date DESC) Compound Index"),
        ("water_intakes", "858", "~120 bytes", "_id, (user_id, date DESC) Compound Index"),
        ("progress_logs", "66", "~130 bytes", "_id, (user_id, date DESC) Compound Index"),
        ("diet_plans", "7", "~310 bytes", "_id, (goal_type, dietary_preference) Index"),
        ("exercises", "10", "~240 bytes", "_id, name (Unique Index)"),
        ("TOTAL DATABASE", "1,746 Docs", "~295 KB", "8 Collections Active"),
    ]
    create_styled_table(doc, ["Collection Name", "Live Count", "Avg Doc Size", "Primary Access Indexes"], coll_data, col_widths=[1.5, 1.1, 1.2, 2.7])

    doc.add_heading("3.3 Schema Specifications for all 8 Collections", level=2)
    schema_data = [
        ("users", "name, email, password_hash, role, profile, created_at", "email regex, role in [user, admin], profile.age 10-120, height 50-260, weight 20-400"),
        ("goals", "user_id, goal_type, start_weight_kg, target_weight_kg, daily_calorie_target, status", "goal_type enum, weights 20-400, calories 800-6000, status in [active, completed, abandoned]"),
        ("meals", "user_id, meal_name, meal_type, calories, protein_g, carbs_g, fat_g, date", "meal_type enum [breakfast, lunch, dinner, snack], calories 0-5000, macros >= 0, date: ISODate"),
        ("workouts", "user_id, title, workout_type, duration_minutes, calories_burned, date", "workout_type enum [cardio, strength, yoga, running, cycling], duration 1-600, calories >= 0"),
        ("water_intakes", "user_id, amount_ml, date", "amount_ml int 1-5000, date: ISODate"),
        ("progress_logs", "user_id, weight_kg, date", "weight_kg number 20-400, date: ISODate"),
        ("diet_plans", "name, goal_type, bmi_categories, dietary_preference, daily_calories, tags", "bmi_categories non-empty array of enums, calories 800-6000, meals_suggestion array"),
        ("exercises", "name, category, muscle_groups, difficulty, calories_per_minute", "name unique string, muscle_groups non-empty array, difficulty enum, calories 0-50"),
    ]
    create_styled_table(doc, ["Collection", "Required Fields", "Validation & Boundary Rules"], schema_data, col_widths=[1.2, 2.3, 3.0])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 4. DATABASE DESIGN AND DATA MODELING
    # -------------------------------------------------------------
    doc.add_heading("4. DATABASE DESIGN AND DATA MODELING", level=1)

    doc.add_heading("4.1 Multi-Tier System Architecture", level=2)
    doc.add_paragraph(
        "FitTrack follows a layered architecture where the user interaction tier communicates with the application tier, "
        "which translates business operations into PyMongo calls executed against the MongoDB database engine."
    )
    add_figure(doc, "report_assets/figure1_architecture.png", "Figure 1: FitTrack Multi-Tier System Architecture (Client to MongoDB Storage)")

    doc.add_heading("4.2 Hybrid Data Modeling Strategy: Embedding vs. Referencing", level=2)
    doc.add_paragraph(
        "The architecture applies a deliberate hybrid data modeling strategy based on cardinality and query access patterns:"
    )
    doc.add_paragraph("• 1:1 Embedding (User Profile): Biometric attributes (age, gender, height, current weight, target weight, activity tier, dietary preference) reside directly within users.profile. Because these attributes are always co-retrieved during authentication and dashboard rendering, embedding delivers zero-join, single-read performance.")
    doc.add_paragraph("• 1:N Referencing (Activity Logs): Daily records (meals, workouts, water intake, progress logs) reference users._id. Embedding these unbounded arrays into user documents would violate document size best practices and risk reaching the 16MB BSON limit.")
    doc.add_paragraph("• Dynamic Metric Computation: Non-static values like BMI are calculated on the fly during aggregation rather than stored statically, ensuring they never go stale.")

    add_figure(doc, "report_assets/figure2_er_diagram.png", "Figure 2: FitTrack Hybrid Data Model – Embedded Profile & Referenced Activity Logs")

    doc.add_heading("4.3 Sample BSON Document Structures", level=2)
    doc.add_paragraph("The following code snippets illustrate the actual document structure across core collections:")
    sample_json = (
        "// 1. users Collection (Embedded Profile)\n"
        "{\n"
        '  "_id": ObjectId("6713b1942d4a0a58ef86b001"),\n'
        '  "name": "Akshat Rana", "email": "user@fittrack.test", "role": "user",\n'
        '  "created_at": ISODate("2026-10-19T12:53:20.100Z"),\n'
        '  "profile": {\n'
        '    "age": 21, "gender": "male", "height_cm": 175.0, "weight_kg": 82.0,\n'
        '    "goal_weight_kg": 74.0, "activity_level": "moderate", "dietary_preference": "any"\n'
        "  }\n"
        "}\n\n"
        "// 2. meals Collection (Referenced Log)\n"
        "{\n"
        '  "_id": ObjectId("6713b1942d4a0a58ef86b050"),\n'
        '  "user_id": ObjectId("6713b1942d4a0a58ef86b001"),\n'
        '  "meal_name": "Dal rice", "meal_type": "lunch", "calories": 520.0,\n'
        '  "protein_g": 18.0, "carbs_g": 90.0, "fat_g": 8.0,\n'
        '  "date": ISODate("2026-10-19T00:00:00.000Z")\n'
        "}\n\n"
        "// 3. diet_plans Collection (Catalog with Embedded Arrays)\n"
        "{\n"
        '  "_id": ObjectId("6713b1942d4a0a58ef86b400"),\n'
        '  "name": "Weight Loss Diet", "goal_type": "weight_loss",\n'
        '  "bmi_categories": ["Overweight", "Obese"], "dietary_preference": "any",\n'
        '  "daily_calories": 1800.0,\n'
        '  "meals_suggestion": ["Oats", "Grilled chicken salad", "Veg soup"],\n'
        '  "tags": ["low-calorie", "beginner-friendly"]\n'
        "}"
    )
    add_code_block(doc, sample_json)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 5. MONGODB IMPLEMENTATION
    # -------------------------------------------------------------
    doc.add_heading("5. MONGODB IMPLEMENTATION", level=1)

    doc.add_heading("5.1 Connection Setup & Collection Creation", level=2)
    doc.add_paragraph(
        "The application establishes a connection pool to MongoDB via MongoClient in db.py. "
        "Collections are initialized using setup_database(db, drop_existing=False), which applies $jsonSchema validators "
        "using collMod if the collection exists, or db.create_collection if initializing from scratch."
    )
    add_figure(doc, "report_assets/figure3_seed_counts.png", "Figure 3: MongoDB Database Initialization and 30-Day Activity Seed Output")

    doc.add_heading("5.2 Schema Validation Implementation ($jsonSchema)", level=2)
    doc.add_paragraph(
        "Each collection is bound to a strict validator in SCHEMAS dictionary. For example, the meals validator enforces BSON types, "
        "enumerated meal categories, and non-negative values:"
    )
    schema_code = (
        '"meals": {\n'
        '    "$jsonSchema": {\n'
        '        "bsonType": "object",\n'
        '        "required": ["user_id", "meal_name", "meal_type", "calories", "date"],\n'
        '        "properties": {\n'
        '            "user_id": {"bsonType": "objectId"},\n'
        '            "meal_name": {"bsonType": "string", "minLength": 1, "maxLength": 120},\n'
        '            "meal_type": {"enum": ["breakfast", "lunch", "dinner", "snack"]},\n'
        '            "calories": {"bsonType": "number", "minimum": 0, "maximum": 5000},\n'
        '            "protein_g": {"bsonType": "number", "minimum": 0},\n'
        '            "carbs_g": {"bsonType": "number", "minimum": 0},\n'
        '            "fat_g": {"bsonType": "number", "minimum": 0},\n'
        '            "date": {"bsonType": "date"}\n'
        "        }\n"
        "    }\n"
        "}"
    )
    add_code_block(doc, schema_code)

    doc.add_heading("5.3 CRUD Operations Implementation", level=2)
    doc.add_paragraph(
        "crud.py implements the complete CRUD lifecycle using PyMongo methods:\n"
        "• CREATE: insert_one (for single meals, workouts, water logs) and insert_many (batch snack entries).\n"
        "• READ: find with projections to exclude unnecessary fields, sort by date descending, and limit result size.\n"
        "• UPDATE: update_one and update_many leveraging $set, $inc for atomic hydration increments, $push for meal suggestions, and $addToSet for unique tags.\n"
        "• DELETE: delete_one (single meal deletion) and delete_many with date range filtering ($lt) for purging historical logs."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # 6. ADVANCED MONGODB OPERATIONS
    # -------------------------------------------------------------
    doc.add_heading("6. ADVANCED MONGODB OPERATIONS", level=1)

    doc.add_heading("6.1 Indexing Strategy & Performance Optimization", level=2)
    doc.add_paragraph(
        "Indexes avoid full collection scans (COLLSCAN) by creating B-tree structures in memory. "
        "Compound indexes on (user_id ASC, date DESC) ensure that queries retrieving recent activity logs "
        "execute as index-covered scans (IXSCAN) with zero in-memory sort overhead."
    )
    idx_data = [
        ("users", "email: 1", "Unique Single-Field", "Guarantees global uniqueness of email addresses and accelerates authentication lookups."),
        ("goals", "user_id: 1, status: 1", "Compound Index", "Optimizes retrieval of a user's active goal (find({user_id, status: 'active'}))."),
        ("meals", "user_id: 1, date: -1", "Compound Index", "Covers queries filtering by user and sorting chronologically for daily logs and aggregations."),
        ("workouts", "user_id: 1, date: -1", "Compound Index", "Accelerates retrieval of workout history and date-range aggregations."),
        ("water_intakes", "user_id: 1, date: -1", "Compound Index", "Speeds up hydration lookups and historical log cleanup ($lt date purges)."),
        ("progress_logs", "user_id: 1, date: -1", "Compound Index", "Optimizes sub-pipeline lookups fetching the user's latest weigh-in."),
        ("diet_plans", "goal_type: 1, dietary_preference: 1", "Compound Index", "Speeds up matching queries during personalized diet recommendation pipelines."),
        ("exercises", "name: 1", "Unique Single-Field", "Enforces unique exercise naming across the movement library."),
    ]
    create_styled_table(doc, ["Collection", "Indexed Key(s)", "Index Type", "Performance Justification"], idx_data, col_widths=[1.2, 1.8, 1.3, 2.2])

    doc.add_heading("6.2 Schema Validation Verification Trace", level=2)
    doc.add_paragraph(
        "Executing validation tests in crud.py confirms that invalid documents are rejected by the database engine with error code 121:"
    )
    add_figure(doc, "report_assets/figure4_validation_rejections.png", "Figure 4: MongoDB Server-Side Schema Validation Test Execution Trace (Code 121)")

    doc.add_heading("6.3 Detailed Aggregation Pipelines (1 through 9)", level=2)

    doc.add_paragraph("Pipeline 1: Rolling 7-Day Nutrition Breakdown")
    doc.add_paragraph(
        "Filters meals for the user over the past 7 days, groups by calendar date, sums calories and macros, "
        "and projects formatted ISO dates ($dateToString)."
    )
    add_figure(doc, "report_assets/figure5_daily_nutrition.png", "Figure 5: Aggregation Pipeline 1 – Rolling 7-Day Macronutrient & Calorie Breakdown")

    doc.add_paragraph("Pipeline 3: Platform Demographic BMI Distribution")
    doc.add_paragraph(
        "Dynamically computes BMI from profile.weight_kg and profile.height_cm using $divide and $pow, "
        "classifies users into BMI tiers using $switch, and calculates the user count and average BMI per tier."
    )
    add_figure(doc, "report_assets/figure6_bmi_distribution.png", "Figure 6: Aggregation Pipeline 3 – Platform Demographic BMI Distribution")

    doc.add_paragraph("Pipeline 4: Workout Discipline Popularity & Expenditure")
    doc.add_paragraph(
        "Groups workout records by discipline, calculates total sessions, total minutes, and average calorie expenditure, "
        "and sorts descending by popularity."
    )
    add_figure(doc, "report_assets/figure7_workout_popularity.png", "Figure 7: Aggregation Pipeline 4 – Popular Workout Disciplines and Energy Expenditure")

    doc.add_paragraph("Pipeline 5: Real-Time Goal Progress Completion ($lookup)")
    doc.add_paragraph(
        "Matches active goals, performs a correlated $lookup sub-pipeline into progress_logs to fetch the latest weigh-in, "
        "and calculates progress percentage toward target weight using $cond, $subtract, and $divide."
    )
    add_figure(doc, "report_assets/figure8_goal_progress.png", "Figure 8: Aggregation Pipeline 5 – Real-Time Goal Progress Completion ($lookup)")

    doc.add_paragraph("Pipeline 6: Dynamic Personalized Diet Recommendation")
    doc.add_paragraph(
        "Calculates the user's BMI category on the fly, joins their active goal, and queries diet_plans "
        "matching goal_type, user's BMI category within bmi_categories array, and dietary preference ($in operator)."
    )

    doc.add_paragraph("Pipeline 7: Multi-Faceted User Dashboard ($facet)")
    doc.add_paragraph(
        "In a single pass over meals, $facet produces overall macro totals, breakdown by meal timing category, "
        "and the highest caloric day, combined with workout and hydration metrics."
    )

    doc.add_paragraph("Pipeline 8: Cross-Collection Net Calories ($unionWith)")
    doc.add_paragraph(
        "Unifies daily meals and workouts using $unionWith, grouping by date and subtracting burned calories from consumed calories "
        "to calculate net daily energy balance."
    )
    add_figure(doc, "report_assets/figure10_net_calories.png", "Figure 9: Aggregation Pipeline 8 – Cross-Collection Net Calorie Balance ($unionWith)")

    doc.add_paragraph("Pipeline 9: Administrator Platform Statistics")
    doc.add_paragraph(
        "Groups meals by user_id, counts unique active days via $addToSet, joins user details, "
        "and computes average daily calories logged across the active period."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # 7. APPLICATION INTEGRATION
    # -------------------------------------------------------------
    doc.add_heading("7. APPLICATION INTEGRATION", level=1)

    doc.add_heading("7.1 Driver Architecture & Exception Handling", level=2)
    doc.add_paragraph(
        "FitTrack uses PyMongo to manage database communication. The application handles two primary exception types:\n"
        "• pymongo.errors.WriteError: Raised when an inserted or modified document violates collection $jsonSchema constraints (code 121).\n"
        "• pymongo.errors.DuplicateKeyError: Raised when an insert violates a unique index (e.g., duplicate user email or exercise name)."
    )

    doc.add_heading("7.2 Application Operations & Method Mapping", level=2)
    method_data = [
        ("create_user()", "db.users.insert_one()", "Inserts new user account with embedded profile sub-document"),
        ("get_user()", "db.users.find_one()", "Fetches user document by indexed email"),
        ("add_meal()", "db.meals.insert_one()", "Logs single meal with macronutrients and UTC midnight timestamp"),
        ("add_many_snacks()", "db.meals.insert_many()", "Demonstrates bulk insertion of snack records"),
        ("meals_on_day()", "db.meals.find() + projection", "Retrieves daily meals with projection excluding _id"),
        ("update_weight()", 'db.users.update_one({"$set"})', "Updates embedded profile.weight_kg using dot-notation"),
        ("add_water_to_latest()", 'db.water_intakes.update_one({"$inc"})', "Atomically increments volume on the latest hydration entry"),
        ("tag_diet_plan()", 'db.diet_plans.update_one({"$addToSet"})', "Adds unique search tag to diet plan array"),
        ("push_meal_suggestion()", 'db.diet_plans.update_one({"$push"})', "Appends meal suggestion to diet plan array"),
        ("delete_old_water_logs()", 'db.water_intakes.delete_many({"$lt"})', "Purges hydration records older than 60 days"),
        ("daily_nutrition()", "Pipeline 1 ($match, $group, $sort)", "Computes 7-day nutritional breakdown"),
        ("bmi_category_counts()", "Pipeline 3 (Dynamic BMI, $switch)", "Computes platform-wide BMI category distribution"),
        ("goal_progress()", "Pipeline 5 ($lookup sub-pipeline)", "Calculates goal completion percentage against latest weigh-in"),
        ("recommend_diet_plans()", "Pipeline 6 ($lookup, $expr, $in)", "Generates personalized diet recommendations"),
        ("dashboard_summary()", "Pipeline 7 ($facet multi-facet)", "Assembles 360-degree user dashboard in a single scan"),
        ("net_calories()", "Pipeline 8 ($unionWith cross-collection)", "Computes daily net energy balance"),
        ("admin_statistics()", "Pipeline 9 ($group, $lookup, $size)", "Calculates admin user engagement metrics"),
    ]
    create_styled_table(doc, ["Application Function", "Underlying MongoDB Operation", "Operational Role & Behavior"], method_data, col_widths=[1.8, 2.2, 2.5])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 8. RESULTS AND OUTPUT ANALYSIS
    # -------------------------------------------------------------
    doc.add_heading("8. RESULTS AND OUTPUT ANALYSIS", level=1)

    doc.add_heading("8.1 Database Environment Verification", level=2)
    doc.add_paragraph(
        "All tests and aggregation queries were executed against a local MongoDB Community Server v8.2.3 deployment. "
        "The database was seeded with 1,746 documents across 8 collections, representing 7 user personas with 30 days of activity."
    )

    doc.add_heading("8.2 Validation Test Matrix & Results", level=2)
    val_data = [
        ("meals", "meal_type: 'brunch'", "Enum constraint violated", "REJECTED: code 121 Document failed validation", "PASS"),
        ("meals", "calories: -50", "minimum: 0 constraint violated", "REJECTED: code 121 Document failed validation", "PASS"),
        ("workouts", "duration_minutes: 0", "minimum: 1 constraint violated", "REJECTED: code 121 Document failed validation", "PASS"),
        ("progress_logs", "weight_kg: 5", "minimum: 20 constraint violated", "REJECTED: code 121 Document failed validation", "PASS"),
        ("meals", "Missing user_id", "required: ['user_id', ...] omitted", "REJECTED: code 121 Document failed validation", "PASS"),
        ("users", "Duplicate email address", "Unique index email_1 violated", "REJECTED: E11000 DuplicateKeyError", "PASS"),
    ]
    create_styled_table(doc, ["Collection", "Injected Anomaly", "Rule Violated", "Live Engine Response", "Status"], val_data, col_widths=[1.1, 1.4, 1.5, 2.0, 0.5])

    doc.add_heading("8.3 Live Execution Outputs of Aggregation Pipelines", level=2)
    doc.add_paragraph("Below are actual JSON output samples returned by the aggregation pipelines:")

    out_p1 = (
        "// Pipeline 1: Daily Nutrition Breakdown (Sample Output)\n"
        "[\n"
        '  { "date": "2026-10-17", "calories": 1400, "protein_g": 54, "carbs_g": 224, "fat_g": 29, "meals": 4 },\n'
        '  { "date": "2026-10-18", "calories": 1280, "protein_g": 72, "carbs_g": 117, "fat_g": 50, "meals": 4 },\n'
        '  { "date": "2026-10-19", "calories": 1680, "protein_g": 108, "carbs_g": 155, "fat_g": 52, "meals": 7 }\n'
        "]\n\n"
        "// Pipeline 5: Goal Progress Evaluation Output\n"
        "[\n"
        '  { "user": "Anita Desai", "goal_type": "maintenance", "start_weight_kg": 62.0, "current_weight": 61.9, "progress_pct": 100.0 },\n'
        '  { "user": "Akshat Rana", "goal_type": "weight_loss", "start_weight_kg": 82.0, "current_weight": 79.2, "progress_pct": 35.0 },\n'
        '  { "user": "Priya Sharma", "goal_type": "weight_gain", "start_weight_kg": 48.0, "current_weight": 50.0, "progress_pct": 33.3 }\n'
        "]\n\n"
        "// Pipeline 6: Personalized Diet Recommendation Output\n"
        "[\n"
        "  {\n"
        '    "user": "Akshat Rana", "bmi": 26.6, "bmi_category": "Overweight", "goal": "weight_loss",\n'
        '    "preference": "any", "plan": "Weight Loss Diet", "daily_calories": 1800,\n'
        '    "suggested_meals": ["Oats", "Grilled chicken salad", "Veg soup", "Moong dal chilla"]\n'
        "  }\n"
        "]\n\n"
        "// Pipeline 7: Dashboard Summary ($facet Output)\n"
        "{\n"
        '  "period_days": 7,\n'
        '  "meals": {\n'
        '    "totals": [{ "calories": 9470, "protein_g": 515, "carbs_g": 1088, "fat_g": 276 }],\n'
        '    "by_meal_type": [{ "_id": "lunch", "calories": 3360 }, { "_id": "dinner", "calories": 2950 }],\n'
        '    "highest_day": [{ "_id": "2026-10-19T00:00:00Z", "calories": 1680 }]\n'
        "  },\n"
        '  "workouts": { "sessions": 2, "minutes": 90, "calories_burned": 540 },\n'
        '  "water": { "avg_ml_per_day": 2179.0 }\n'
        "}"
    )
    add_code_block(doc, out_p1)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 9. DISCUSSION & TECHNICAL TRADE-OFFS
    # -------------------------------------------------------------
    doc.add_heading("9. DISCUSSION & TECHNICAL TRADE-OFFS", level=1)

    doc.add_heading("9.1 Advantages of MongoDB for Health Systems", level=2)
    doc.add_paragraph("1. Schema Flexibility: Readily accommodates varied meal compositions, workout attributes, and dietary guidelines without costly schema alterations.")
    doc.add_paragraph("2. Native Array Operations: Multikey indexing and array operators ($in, $push, $addToSet) eliminate artificial bridge tables.")
    doc.add_paragraph("3. In-Database Analytics: MongoDB's C++ aggregation engine processes complex multi-stage pipelines directly on the server, minimizing data transfer to the application layer.")

    doc.add_heading("9.2 Architectural Challenges & Mitigations", level=2)
    chal_data = [
        ("Schema Inconsistency", "Loose documents could permit corrupt types or negative values.", "Implemented strict $jsonSchema validators with validationAction: error."),
        ("Unbounded Growth", "Embedding daily logs would exceed the 16MB document size limit.", "Partitioned logs into referenced collections linked via user_id: ObjectId."),
        ("NoSQL Join Complexity", "Correlating goals, progress logs, and diet plans requires cross-collection joins.", "Engineered correlated $lookup sub-pipelines with internal sorting and limiting."),
        ("Duplicate Identity", "Concurrent registrations could produce duplicate email accounts.", "Established a database-level unique index on users.email."),
        ("Timezone Grouping Discrepancy", "Mixed timestamps can lead to inaccurate daily grouping.", "Normalized all logging timestamps to UTC midnight ISODate('YYYY-MM-DDT00:00:00Z')."),
    ]
    create_styled_table(doc, ["Technical Challenge", "Root Risk", "Engineering Mitigation Implemented"], chal_data, col_widths=[1.5, 2.3, 2.7])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 10. CONCLUSION, 11. FUTURE SCOPE, 12. REFERENCES
    # -------------------------------------------------------------
    doc.add_heading("10. CONCLUSION", level=1)
    doc.add_paragraph(
        "FitTrack successfully demonstrates the design and implementation of a document-oriented database for personal health tracking. "
        "By combining embedded 1:1 user profiles with referenced time-series collections, the architecture achieves high single-read performance "
        "while preventing document bloat. Strict $jsonSchema validation rules enforce data integrity directly in the database engine, "
        "and compound indexes ensure that queries execute as efficient index scans."
    )
    doc.add_paragraph(
        "Nine advanced aggregation pipelines demonstrate the power of MongoDB's analytics engine: computing rolling nutritional breakdowns, "
        "evaluating BMI dynamically, tracking goal completion against historical weigh-ins, and generating personalized dietary recommendations. "
        "Empirical testing on a live MongoDB v8.2.3 deployment confirmed that invalid records are reliably rejected, indexes eliminate unnecessary "
        "collection scans, and aggregation queries deliver responsive, actionable insights across all 8 collections."
    )

    doc.add_heading("11. FUTURE SCOPE", level=1)
    doc.add_paragraph("1. RESTful API Service: Expose database operations over secure HTTP endpoints using FastAPI or Flask.")
    doc.add_paragraph("2. Interactive Web Dashboard: Build a modern React and Tailwind CSS frontend with real-time charts backed by the aggregation pipelines.")
    doc.add_paragraph("3. Automated TTL Archival: Implement MongoDB Time-To-Live (TTL) indexes to automatically purge or archive historical logs older than 180 days.")
    doc.add_paragraph("4. Machine Learning Recommendations: Extend Pipeline 6 with MongoDB Atlas Vector Search ($vectorSearch) to recommend meals based on semantic similarity to users' past food logs.")
    doc.add_paragraph("5. Wearable Health Integration: Ingest real-time step counts and heart rate data via Apple HealthKit and Google Fit APIs.")

    doc.add_heading("12. REFERENCES", level=1)
    refs = [
        "1. MongoDB, Inc., 'MongoDB Documentation: The Document Data Model & BSON Specification,' https://www.mongodb.com/docs/manual/core/document/",
        "2. MongoDB, Inc., 'Schema Validation with $jsonSchema,' https://www.mongodb.com/docs/manual/core/schema-validation/",
        "3. MongoDB, Inc., 'Aggregation Pipeline Stages and Operators,' https://www.mongodb.com/docs/manual/reference/operator/aggregation/",
        "4. PyMongo Team, 'PyMongo: Python Driver for MongoDB Documentation (v4.19),' https://pymongo.readthedocs.io/",
        "5. Chodorow, K., 'MongoDB: The Definitive Guide - Powerful and Scalable Data Storage,' 3rd Edition, O'Reilly Media.",
        "6. Banker, K., Bakkum, P., Verch, S., Garrett, D., and Hawkins, T., 'MongoDB in Action,' 2nd Edition, Manning Publications.",
        "7. World Health Organization (WHO), 'Body Mass Index (BMI) Classification & Cut-offs,' Geneva.",
        "8. FitTrack Project Repository and Source Code (fittrack_mongo/): db.py, crud.py, aggregations.py, seed.py, main.py, queries.js."
    ]
    for r in refs:
        p_ref = doc.add_paragraph(r)
        p_ref.paragraph_format.space_after = Pt(4)

    # Save document
    out_file = os.path.join(r"C:\Users\mishr\Downloads\fittrack_mongo\fittrack_mongo", "FitTrack_Project_Report.docx")
    doc.save(out_file)
    print(f"Report successfully saved to {out_file}")

if __name__ == "__main__":
    build_report()

import fitz
import os
import datetime

def generate_student_pdf(student_name, student_id, set_idx, questions_data, student_answers, grading_results, output_dir):
    """
    Generates a beautifully structured PDF document summarizing student answers,
    reference answers, autograder scores, and overall feedback.
    
    File naming format: StudentNAMEs - Student ID.pdf
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Naming convention: StudentNAMEs - Student ID.pdf
    pdf_filename = f"{student_name} - {student_id}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    # Create PDF document
    doc = fitz.open()
    
    # Calculate totals
    total_score = sum(res['score'] for res in grading_results.values())
    total_max = sum(res['max_marks'] for res in grading_results.values())
    pct = (total_score / total_max * 100) if total_max > 0 else 0.0
    
    # ------------------ PAGE 1: OVERVIEW ------------------
    page1 = doc.new_page()
    
    # Build HTML summary
    html_overview = f"""
    <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1e293b; padding: 15px;">
        <div style="text-align: center; border-bottom: 2px solid #1e3a8a; padding-bottom: 12px; margin-bottom: 20px;">
            <h1 style="color: #1e3a8a; margin: 0; font-size: 20px; font-weight: bold; letter-spacing: 0.5px;">
                STA334 – INTRODUCTION TO STATISTICAL PROGRAMMING
            </h1>
            <h2 style="color: #475569; margin: 5px 0 0 0; font-size: 14px; font-weight: 500; text-transform: uppercase;">
                Practice Set {set_idx} Assessment Report
            </h2>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 12px; border: 1px solid #e2e8f0;">
            <tr style="background-color: #f8fafc;">
                <th style="border: 1px solid #e2e8f0; padding: 10px; text-align: left; width: 30%; font-weight: bold; color: #475569;">Student Name</th>
                <td style="border: 1px solid #e2e8f0; padding: 10px; font-weight: bold; color: #0f172a;">{student_name}</td>
            </tr>
            <tr>
                <th style="border: 1px solid #e2e8f0; padding: 10px; text-align: left; font-weight: bold; color: #475569;">Student ID</th>
                <td style="border: 1px solid #e2e8f0; padding: 10px; font-weight: bold; color: #0f172a;">{student_id}</td>
            </tr>
            <tr style="background-color: #f8fafc;">
                <th style="border: 1px solid #e2e8f0; padding: 10px; text-align: left; font-weight: bold; color: #475569;">Practice Set</th>
                <td style="border: 1px solid #e2e8f0; padding: 10px; color: #0f172a;">Practice Set {set_idx}</td>
            </tr>
            <tr>
                <th style="border: 1px solid #e2e8f0; padding: 10px; text-align: left; font-weight: bold; color: #475569;">Submission Date</th>
                <td style="border: 1px solid #e2e8f0; padding: 10px; color: #0f172a;">{datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")}</td>
            </tr>
            <tr style="background-color: #f0fdf4;">
                <th style="border: 1px solid #e2e8f0; padding: 10px; text-align: left; font-weight: bold; color: #166534;">Final Score</th>
                <td style="border: 1px solid #e2e8f0; padding: 10px; font-weight: bold; font-size: 16px; color: #166534;">
                    {total_score:.1f} / {total_max:.1f} marks ({pct:.1f}%)
                </td>
            </tr>
        </table>
        
        <h3 style="color: #1e3a8a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin: 20px 0 10px 0; font-size: 14px; font-weight: 600;">
            Question Performance Summary
        </h3>
        
        <table style="width: 100%; border-collapse: collapse; font-size: 11px; border: 1px solid #e2e8f0;">
            <thead>
                <tr style="background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                    <th style="border: 1px solid #e2e8f0; padding: 8px; text-align: left; color: #475569; font-weight: bold;">Question No.</th>
                    <th style="border: 1px solid #e2e8f0; padding: 8px; text-align: center; color: #475569; font-weight: bold;">Sub-question</th>
                    <th style="border: 1px solid #e2e8f0; padding: 8px; text-align: center; color: #475569; font-weight: bold;">Marks Awarded</th>
                    <th style="border: 1px solid #e2e8f0; padding: 8px; text-align: center; color: #475569; font-weight: bold;">Result Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Sort and iterate results
    sorted_keys = sorted(grading_results.keys())
    for (q_no, sub_no) in sorted_keys:
        res = grading_results[(q_no, sub_no)]
        score = res['score']
        max_m = res['max_marks']
        
        if score == max_m:
            status_text = "Correct"
            status_color = "#15803d" # dark green
            bg_color = "#f0fdf4" # light green
        elif score > 0:
            status_text = "Partial"
            status_color = "#b45309" # dark amber
            bg_color = "#fffbeb" # light amber
        else:
            status_text = "Incorrect"
            status_color = "#b91c1c" # dark red
            bg_color = "#fef2f2" # light red
            
        html_overview += f"""
                <tr style="background-color: {bg_color};">
                    <td style="border: 1px solid #e2e8f0; padding: 8px; font-weight: 500; color: #334155;">Question {q_no}</td>
                    <td style="border: 1px solid #e2e8f0; padding: 8px; text-align: center; font-weight: bold; color: #334155;">{sub_no}</td>
                    <td style="border: 1px solid #e2e8f0; padding: 8px; text-align: center; font-weight: bold; color: #0f172a;">{score:.1f} / {max_m:.1f}</td>
                    <td style="border: 1px solid #e2e8f0; padding: 8px; text-align: center; font-weight: bold; color: {status_color};">{status_text}</td>
                </tr>
        """
        
    html_overview += """
            </tbody>
        </table>
        
        <div style="margin-top: 40px; text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px dashed #e2e8f0; padding-top: 10px;">
            STA334 Introduction to Statistical Programming Assessment Engine. © 2026. All rights reserved.
        </div>
    </div>
    """
    
    # Insert overview card
    rect = fitz.Rect(36, 36, 559, 806)
    page1.insert_htmlbox(rect, html_overview)
    
    # ------------------ PAGES 2+: DETAILS ------------------
    # We will print one main question per page for maximum readability and structure
    for q_no in sorted(list(set(k[0] for k in grading_results.keys()))):
        # find matching question in questions_data
        q_data = next((q for q in questions_data if q['question_no'] == q_no), None)
        if not q_data:
            continue
            
        page = doc.new_page()
        
        # Build HTML content for this page
        html_q = f"""
        <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1e293b; padding: 15px;">
            <h2 style="color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 8px; margin: 0 0 15px 0; font-size: 16px; font-weight: bold; letter-spacing: 0.5px;">
                Question {q_no} Review Details
            </h2>
        """
        
        if q_data.get('context'):
            # Escape double quotes and clean paragraphs
            clean_context = q_data['context'].replace('\n', '<br>')
            html_q += f"""
            <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 10px; border-radius: 0 4px 4px 0; margin-bottom: 20px; font-size: 11px; line-height: 1.5; color: #475569;">
                <strong>Context/Instructions:</strong><br>
                {clean_context}
            </div>
            """
            
        for sq in q_data['subquestions']:
            sub_no = sq['sub_no']
            ref_key = (q_no, sub_no)
            res = grading_results.get(ref_key, {'score': 0.0, 'max_marks': 0, 'feedback': 'No results'})
            
            score = res['score']
            max_m = res['max_marks']
            student_ans = student_answers.get(ref_key, "").strip()
            ref_ans = sq.get('reference_answer', "").strip()
            feedback = res['feedback']
            
            if score == max_m:
                status_title = "CORRECT"
                status_color = "#15803d" # dark green
                box_border = "#bbf7d0" # light green
                box_bg = "#f0fdf4"
            elif score > 0:
                status_title = "PARTIALLY CORRECT"
                status_color = "#b45309" # dark amber
                box_border = "#fde68a" # light amber
                box_bg = "#fffbeb"
            else:
                status_title = "INCORRECT"
                status_color = "#b91c1c" # dark red
                box_border = "#fecaca" # light red
                box_bg = "#fef2f2"
                
            clean_text = sq['text'].replace('\n', '<br>')
            html_q += f"""
            <div style="margin-bottom: 20px; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px;">
                <div style="font-weight: bold; font-size: 12px; color: #0f172a; margin-bottom: 8px;">
                    {sub_no}) {clean_text} 
                    <span style="color: #64748b; font-weight: normal; font-size: 11px;">({max_m} marks)</span>
                </div>
            """
            
            # Render student answer
            display_student = student_ans.replace('\n', '<br>') if student_ans else "<i>(Empty / No answer submitted)</i>"
            html_q += f"""
                <div style="font-size: 11px; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: #475569;">Student's Submission:</span>
                    <div style="font-family: 'Courier New', Courier, monospace; background-color: #f1f5f9; border: 1px solid #cbd5e1; padding: 8px; border-radius: 4px; margin-top: 4px; font-size: 11px; color: #0f172a; line-height: 1.4;">
                        {display_student}
                    </div>
                </div>
            """
            
            # Show Reference Answer if student did not get full marks
            if score < max_m:
                display_ref = ref_ans.replace('\n', '<br>')
                html_q += f"""
                <div style="font-size: 11px; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: #b45309;">Correct Answer Scheme:</span>
                    <div style="font-family: 'Courier New', Courier, monospace; background-color: #fffbeb; border: 1px solid #fde68a; padding: 8px; border-radius: 4px; margin-top: 4px; font-size: 11px; color: #78350f; line-height: 1.4;">
                        {display_ref}
                    </div>
                </div>
                """
                
            # Render marks & grading notes
            html_q += f"""
                <div style="display: flex; justify-content: space-between; align-items: center; background-color: {box_bg}; border: 1px solid {box_border}; padding: 8px; border-radius: 4px; margin-top: 8px;">
                    <span style="font-weight: bold; font-size: 11px; color: {status_color};">
                        {status_title} &nbsp; ({score:.1f} / {max_m:.1f} Marks)
                    </span>
                    <span style="font-size: 10px; color: #475569; font-style: italic;">
                        Feedback: {feedback}
                    </span>
                </div>
            </div>
            """
            
        html_q += "</div>"
        
        # Draw onto page
        rect = fitz.Rect(36, 36, 559, 806)
        page.insert_htmlbox(rect, html_q)
        
    # Save the compiled document
    doc.save(pdf_path)
    doc.close()
    
    return pdf_path

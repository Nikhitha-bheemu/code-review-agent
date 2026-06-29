import datetime
from fpdf import FPDF

# Generates both a Markdown string report and a PDF file summarizing the code review results.
def generate_report(code: str, bugs: list, fixes: list) -> str:
    """
    Creates a detailed Markdown code review report and compiles a PDF version.
    
    Parameters:
    - code (str): The original Python code reviewed.
    - bugs (list): List of detected bugs (dicts).
    - fixes (list): List of evolved fix strings.
    
    Returns:
    - str: Generated report in Markdown format.
    """
    try:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine Recommendation
        severities = [b.get("severity", "").lower() for b in bugs]
        if "high" in severities:
            recommendation = "CRITICAL"
        elif "medium" in severities:
            recommendation = "NEEDS FIX"
        else:
            recommendation = "PASS"
            
        # Build Markdown
        md = []
        md.append("# Code Review Report")
        md.append(f"**Date:** {date_str}\n")
        md.append("## Summary")
        md.append(f"- **Total Bugs Found:** {len(bugs)}")
        md.append(f"- **Total Fixes Generated:** {len(fixes)}")
        md.append(f"- **Final Recommendation:** {recommendation}\n")
        
        md.append("## Bug Details")
        md.append("| Line | Type | Severity | Description |")
        md.append("|---|---|---|---|")
        for bug in bugs:
            line = bug.get("line_number", "")
            b_type = bug.get("bug_type", "")
            sev = bug.get("severity", "")
            desc = bug.get("description", "")
            md.append(f"| {line} | {b_type} | {sev} | {desc} |")
        md.append("")
        
        md.append("## Fix Details")
        for i, (bug, fix) in enumerate(zip(bugs, fixes), 1):
            line = bug.get("line_number", "")
            desc = bug.get("description", "")
            md.append(f"### Fix {i} (Line {line} - {desc})")
            md.append("**Original Code Context:**")
            md.append("```python")
            # Show original code segment or entire code
            md.append(code)
            md.append("```")
            md.append("**Evolved Fix:**")
            md.append("```python")
            md.append(fix)
            md.append("```\n")
            
        markdown_report = "\n".join(md)
        
        # Build PDF inside separate try/except
        try:
            print("[DEBUG] Generating PDF report...")
            pdf = FPDF()
            pdf.add_page()
            
            # Title
            pdf.set_font("helvetica", style="B", size=16)
            pdf.cell(text="Code Review Report", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
            
            # Date
            pdf.set_font("helvetica", size=10)
            pdf.cell(text=f"Date: {date_str}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
            
            # Summary
            pdf.set_font("helvetica", style="B", size=12)
            pdf.cell(text="Summary", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", size=10)
            pdf.cell(text=f"- Total Bugs Found: {len(bugs)}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(text=f"- Total Fixes Generated: {len(fixes)}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(text=f"- Final Recommendation: {recommendation}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            # Bug Table Title
            pdf.set_font("helvetica", style="B", size=12)
            pdf.cell(text="Bug Details", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            # Bug Table using modern table API
            pdf.set_font("helvetica", size=9)
            with pdf.table() as table:
                header_row = table.row()
                header_row.cell("Line")
                header_row.cell("Type")
                header_row.cell("Severity")
                header_row.cell("Description")
                for bug in bugs:
                    row = table.row()
                    row.cell(str(bug.get("line_number", "")))
                    row.cell(str(bug.get("bug_type", "")))
                    row.cell(str(bug.get("severity", "")))
                    row.cell(str(bug.get("description", "")))
                    
            pdf.output("code_review_report.pdf")
            print("[DEBUG] PDF report generated successfully as 'code_review_report.pdf'.")
        except Exception as pdf_err:
            print(f"[DEBUG] PDF generation failed: {pdf_err}")
            
        return markdown_report
        
    except Exception as e:
        print(f"[DEBUG] Error during report generation: {e}")
        return "Report generation failed."

# Application Usage Instructions

## Starting the Application

### Launch the Streamlit Dashboard

Navigate to the project directory and run:

```bash
streamlit run dashboard/app.py
```

The application will start and provide a local URL:
- Local URL: `http://localhost:8501`
- Network URL: `http://<your-ip>:8501`

Open the local URL in your web browser to access the dashboard.

### Run Batch Validation

For automated processing of all cases without the UI:

```bash
python batch_validation.py
```

For rule-based validation only (no AI):
```bash
# Windows PowerShell
$env:SKIP_AI="true"
python batch_validation.py

# Linux/Mac
export SKIP_AI=true
python batch_validation.py
```

## Dashboard Navigation

The dashboard has 7 main pages accessible via the sidebar:

1. **Case Selection** - Select and view cases
2. **Rule Checks** - Run deterministic rule analysis
3. **AI Diagnosis** - Run AI-powered diagnosis
4. **Human Review** - Review and approve AI diagnoses
5. **Verification** - Track fix verification
6. **Responsible AI** - View AI performance metrics
7. **Analytics Dashboard** - Comprehensive system analytics

## Page-by-Page Usage

### Page 1: Case Selection

**Purpose**: Select a network troubleshooting case to analyze.

**Steps**:
1. Navigate to "Case Selection" from sidebar
2. Use the dropdown to select a case (NET-001 to NET-030)
3. Review the case information displayed:
   - Case ID
   - Symptom
   - Topology note
   - Show command outputs
   - OSI layer
   - Concept tag
   - Severity

**Developer Mode**:
- Toggle "Developer Mode" to show expected fault
- Use for evaluator testing only
- Hidden in normal use to avoid bias

**Tips**:
- Read the symptom carefully to understand the reported issue
- Review the topology note to understand network layout
- Examine show outputs for actual evidence
- Note the expected fault in developer mode for reference

### Page 2: Rule Checks

**Purpose**: Run deterministic rule-based analysis on the selected case.

**Steps**:
1. Ensure a case is selected on the "Case Selection" page
2. Navigate to "Rule Checks" from sidebar
3. Click "Run Rule Checks" button
4. Review the results for all 6 rules:
   - Duplicate IP detection
   - Subnet mask validation
   - Gateway mismatch detection
   - Interface down detection
   - Missing VLAN detection
   - Missing route detection

**Understanding Results**:
- **DETECTED**: Rule found evidence of the issue
- **NOT_DETECTED**: Rule found no evidence of the issue
- **INSUFFICIENT_EVIDENCE**: Not enough information to determine

**Each result shows**:
- Status (color-coded)
- Explanation message
- Supporting evidence from case data
- Confidence level

**Tips**:
- Rule checks provide immediate deterministic analysis
- Results are fast and don't require API access
- Use rule results as baseline before AI diagnosis
- Evidence shown helps you understand the detection

### Page 3: AI Diagnosis

**Purpose**: Run AI-powered diagnosis using OpenAI's GPT-3.5-turbo.

**Steps**:
1. Ensure a case is selected and rule checks have been run
2. Navigate to "AI Diagnosis" from sidebar
3. Click "Run AI Diagnosis" button
4. Wait for AI to process (may take 10-30 seconds)
5. Review the AI diagnosis output

**AI Diagnosis Includes**:
- **Root Cause**: Primary diagnosis of the issue
- **Confidence**: high/medium/low based on evidence quality
- **Evidence**: Array of evidence items with source, content, and type
- **Next Command**: Recommended next diagnostic command
- **Fix Steps**: Sequential steps to fix the issue
- **OSI Layer**: Layer where issue occurs
- **Issue Type**: Network issue category
- **Severity**: Issue severity level
- **Alternative Causes**: Other possible causes with likelihood
- **Limitations**: Known limitations of the diagnosis
- **Notes**: Additional context

**Error Handling**:
- If API is unavailable, an error message will display
- The system will not fabricate a diagnosis
- You can still use rule-based analysis

**Tips**:
- AI requires OpenAI API key configured in .env
- Review the evidence to understand AI's reasoning
- Check confidence level - low confidence means uncertain
- Alternative causes show other possibilities
- Limitations indicate what AI couldn't determine

### Page 4: Human Review

**Purpose**: Expert review and approval of AI diagnosis.

**Steps**:
1. Ensure AI diagnosis has been run
2. Navigate to "Human Review" from sidebar
3. Review the original AI diagnosis (preserved)
4. Select your review decision:
   - **ACCEPT**: AI diagnosis is correct as-is
   - **EDIT**: AI diagnosis needs correction
   - **REJECT**: AI diagnosis is incorrect
5. Provide reviewer notes explaining your decision
6. If EDIT or REJECTED, provide reason for correction
7. If EDITED, modify the diagnosis JSON as needed
8. Click "Save Review" to record your decision

**Decision Guidelines**:

**ACCEPT** when:
- AI correctly identifies the issue
- Evidence cited is accurate
- Fix steps are appropriate
- Confidence level is appropriate

**EDIT** when:
- AI identifies the issue but with incorrect details
- Confidence level is wrong
- Fix steps need adjustment
- Minor corrections needed

**REJECT** when:
- AI misidentifies the issue completely
- AI hallucinates evidence not present
- AI provides harmful recommendations
- Major corrections needed

**Tips**:
- Always review the original AI diagnosis carefully
- Provide specific, actionable notes
- Explain why corrections are needed
- Be honest about AI's accuracy
- Your review teaches the system's limitations

### Page 5: Verification

**Purpose**: Track fix verification in Packet Tracer.

**Steps**:
1. After human review, navigate to "Verification" from sidebar
2. Review the final diagnosis (after review)
3. Apply the fix in Packet Tracer
4. Select verification status:
   - **VERIFIED**: Fix worked as expected
   - **NOT VERIFIED**: Fix did not work
   - **NOT YET TESTED**: Fix not yet tested
5. Provide verification notes
6. Click "Save Verification" to record status

**Verification Workflow**:
1. Apply fix steps in Packet Tracer
2. Test the fix (ping, traceroute, etc.)
3. Verify the symptom is resolved
4. Record verification status
5. Document any issues encountered

**Tips**:
- Always test fixes in Packet Tracer before marking verified
- Provide detailed notes on what worked or didn't
- If not verified, explain why the fix failed
- Verification is the final step in the workflow

### Page 6: Responsible AI

**Purpose**: View AI performance and accountability metrics.

**Features**:
- AI review distribution chart (Accepted/Edited/Rejected)
- AI-vs-human agreement rate
- Number of corrected AI diagnoses
- Cases with insufficient evidence
- Links to Responsible AI documentation

**Understanding Metrics**:
- **Agreement Rate**: Percentage of reviews where AI was accepted
- **Corrected Cases**: Cases where AI was edited or rejected
- **Insufficient Evidence**: Cases where AI couldn't diagnose

**Tips**:
- Use this page to track AI performance over time
- High agreement rate indicates AI accuracy
- Many corrections indicate AI limitations
- Review patterns help identify improvement areas

### Page 7: Analytics Dashboard

**Purpose**: Comprehensive system performance insights.

**Metrics Displayed**:
- Total cases in dataset
- Cases by issue type (concept_tag)
- Cases by severity (High/Medium/Low)
- AI review distribution
- AI-vs-human agreement rate
- Corrected diagnosis count
- Insufficient evidence count
- OSI layer distribution
- Rule checker findings by category

**Visualization**:
- Interactive Plotly charts
- Metric cards with counts
- Tables for detailed data
- Color-coded severity levels

**Tips**:
- Hover over charts for detailed information
- Use zoom and pan on charts
- Filter by clicking on legend items
- Export charts using Plotly tools

## Complete Workflow Example

### Example: Troubleshooting NET-001

**Step 1: Case Selection**
- Select "NET-001" from dropdown
- Review: "PC1 cannot reach Server1 in VLAN 30"
- Note topology: "PC1 on Fa0/1 (VLAN 10)"
- Show output: "GigabitEthernet0/0.10 is administratively down"

**Step 2: Rule Checks**
- Click "Run Rule Checks"
- View results:
  - Interface down: DETECTED (administratively down)
  - Other rules: NOT_DETECTED

**Step 3: AI Diagnosis**
- Click "Run AI Diagnosis"
- AI identifies: "Router sub-interface administratively down"
- Confidence: high
- Fix steps: enable interface

**Step 4: Human Review**
- Review AI diagnosis
- Decision: ACCEPT (AI correctly identified issue)
- Notes: "AI correctly identified interface down issue"
- Save review

**Step 5: Verification**
- Apply fix in Packet Tracer (no shutdown)
- Test connectivity
- Status: VERIFIED
- Notes: "PC1 can now reach Server1"
- Save verification

**Step 6: Analytics**
- View updated metrics
- Agreement rate increased
- Case count increased

## Tips for Effective Use

### For Students

1. **Read Carefully**: Always read case information thoroughly
2. **Use Rules First**: Start with rule checks for immediate insights
3. **Review AI**: Don't blindly accept AI - review critically
4. **Learn from Corrections**: Use edited/rejected cases to learn
5. **Verify Fixes**: Always test in Packet Tracer

### For Evaluators

1. **Use Developer Mode**: Toggle to see expected fault
2. **Review Thoroughly**: Provide detailed review notes
3. **Document Corrections**: Explain why AI was wrong
4. **Track Patterns**: Look for recurring AI errors
5. **Provide Feedback**: Use notes to improve the system

### For Researchers

1. **Export Data**: Use batch validation for large datasets
2. **Analyze Metrics**: Use analytics dashboard for insights
3. **Study Patterns**: Analyze correction patterns
4. **Document Findings**: Use review data for research
5. **Improve Prompts**: Learn from corrections to improve AI

## Troubleshooting Application Issues

### Issue: Dashboard Won't Start

**Solution**:
- Ensure virtual environment is activated
- Check Streamlit is installed: `pip list | grep streamlit`
- Try reinstalling: `pip install streamlit>=1.28.0`

### Issue: AI Diagnosis Fails

**Solution**:
- Check OPENAI_API_KEY in .env file
- Verify API key is valid and has quota
- Set SKIP_AI=true to use rule-based analysis only
- Check internet connection

### Issue: Case Not Loading

**Solution**:
- Verify cases.csv exists in data/ directory
- Check file permissions
- Ensure CSV has correct format
- Run data loader tests: `pytest tests/test_data.py`

### Issue: Rule Checks Not Running

**Solution**:
- Ensure a case is selected first
- Check rule checker module: `pytest tests/test_rules.py`
- Verify case data is valid
- Check for error messages in console

### Issue: Review Not Saving

**Solution**:
- Ensure all required fields are filled
- Check review manager permissions
- Verify file system write access
- Check for error messages

## Keyboard Shortcuts

Streamlit supports some keyboard shortcuts:
- `Ctrl + Enter`: Run the current cell (if using Streamlit code editor)
- `Ctrl + /`: Toggle comment (if editing code)
- Use browser navigation for page switching

## Performance Tips

1. **Cache Results**: Rule results are cached in session state
2. **Batch Processing**: Use batch_validation.py for many cases
3. **Skip AI**: Use SKIP_AI=true for faster processing
4. **Close Unused Tabs**: Streamlit uses resources per connection
5. **Clear Cache**: Refresh page to clear session state

## Security Considerations

1. **API Keys**: Never share your .env file
2. **Developer Mode**: Disable in production
3. **Network Access**: Use firewall for Streamlit port
4. **Data Privacy**: Cases.csv contains network information
5. **Access Control**: Restrict dashboard access if needed

## Getting Help

If you encounter issues:

1. **Check Documentation**: Read relevant documentation files
2. **Run Tests**: Use pytest to identify issues
3. **Check Logs**: Review console output for errors
4. **Review FAQ**: Check troubleshooting section
5. **Contact Support**: Provide error details and steps to reproduce

## Conclusion

The NetSage AI dashboard provides a comprehensive interface for network troubleshooting analysis. By following these usage instructions, you can effectively use all features including case selection, rule checking, AI diagnosis, human review, verification, and analytics. The system is designed to be intuitive while maintaining responsible AI practices and data integrity.